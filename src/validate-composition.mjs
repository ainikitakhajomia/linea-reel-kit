// Isolated Linux runner only. Actual alpha/media pixel regressions, beyond gallery thumbnails.
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {createServer} from './server.mjs';
const server=await createServer(0),browser=await chromium.launch();
try{
 await mkdir('out',{recursive:true});const page=await browser.newPage({viewport:{width:1440,height:1100}});
 await page.goto(`http://127.0.0.1:${server.address().port}/src/stage.html`);await page.waitForFunction(()=>window.ready);
 const results=await page.evaluate(async()=>{
   const {drawFrame}=await import('/src/effects.mjs');
   const make=(color,alpha=false)=>{const canvas=document.createElement('canvas');canvas.width=720;canvas.height=1280;const c=canvas.getContext('2d');c.fillStyle=color;if(alpha){c.beginPath();c.ellipse(360,640,140,290,0,0,Math.PI*2);c.fill();}else{c.fillRect(0,0,720,1280);c.fillStyle='#fff';for(let x=30;x<720;x+=80)c.fillRect(x,0,4,1280);}return canvas;};
   const blue=make('#2040c0'),red=make('#e33828'),subject=make('#ffcf55',true),media={video:blue,background:blue,walkthrough:red,foreground:subject,next:red,previous:blue};
   const canvas=document.querySelector('canvas');canvas.width=720;canvas.height=1280;const c=canvas.getContext('2d'),shots=[];
   for(const id of ['kinetic-hook','camera-transitions','zoom-punch','dolly-zoom','letter-dive','double-exposure','rack-focus','shape-transitions']){
     const job={duration:2.4,noBrand:true,effects:[{id,start:0,duration:2.4,text:id==='letter-dive'?'OPEN':'Jouw verhaal. Helder verteld.'}]};
     for(const time of [.2,1.2]){drawFrame(c,job,time,media);shots.push({id,time,png:canvas.toDataURL(),center:[...c.getImageData(360,640,1,1).data]});}
   }
   const exposure=shots.find(s=>s.id==='double-exposure'&&s.time===1.2);
   const captionJob={duration:2.4,noBrand:true,captions:[{text:'Een',startMs:0,endMs:500},{text:'helder',startMs:500,endMs:1500},{text:'verhaal.',startMs:1500,endMs:2400}]};
   drawFrame(c,captionJob,.8,{video:blue});shots.push({id:'captions',time:.8,png:canvas.toDataURL()});
   drawFrame(c,{duration:2.4,noBrand:true,effects:[{id:'double-exposure',start:0,duration:2.4}]},1.2,{});const syntheticExposurePixel=[...c.getImageData(360,700,1,1).data];shots.push({id:'double-exposure-synthetic',time:1.2,png:canvas.toDataURL()});
   drawFrame(c,{duration:2.4,noBrand:true,effects:[{id:'letter-dive',start:0,duration:2.4,text:'OPEN'}]},1.6,media);const diveEdgePixel=[...c.getImageData(50,50,1,1).data];
   return {shots,exposurePixel:exposure.center,syntheticExposurePixel,diveEdgePixel};
 });
 assert.ok(results.exposurePixel[0]>results.exposurePixel[2]*1.5,'Double exposure must retain red secondary footage instead of opaque blue accent');
 assert.ok(results.syntheticExposurePixel[2]<220,'Synthetic exposure silhouette must contrast with ivory background');
 assert.ok(results.diveEdgePixel[0]>results.diveEdgePixel[2]*1.5,'Late letter dive must complete to full secondary image, including edges');
 const byId=Object.groupBy(results.shots.filter(s=>!['captions','double-exposure-synthetic'].includes(s.id)),s=>s.id);for(const [id,shots]of Object.entries(byId))assert.notEqual(shots[0].png,shots[1].png,id+' media path must animate');
 for(const shot of results.shots)await writeFile(`out/composition-${shot.id}-${shot.time}.png`,Buffer.from(shot.png.split(',')[1],'base64'));
 await page.setContent('<body style="margin:0;background:#f6f5f1;font:15px Arial;padding:24px"><h1>Owned synthetic media · compositing regressions</h1><div id="shots" style="display:grid;grid-template-columns:repeat(9,1fr);gap:12px"></div></body>');
 await page.evaluate(shots=>{for(const shot of shots){const card=document.createElement('div'),label=document.createElement('p'),img=document.createElement('img');label.textContent=`${shot.id} / ${shot.time}s`;img.src=shot.png;img.style.width='100%';card.append(label,img);document.querySelector('#shots').append(card);}},results.shots);
 await page.screenshot({path:'out/composition-contact-sheet.png',fullPage:true});
 await writeFile('out/composition-validation.json',JSON.stringify({secondaryImageRetained:true,exposurePixel:results.exposurePixel,syntheticExposurePixel:results.syntheticExposurePixel,diveEdgePixel:results.diveEdgePixel,animatedMediaPaths:Object.keys(byId),fixtures:'Owned procedural RGB sources and subject alpha; no real portrait quality claim'},null,2));
 console.log('Media-backed camera, mask, exposure, alpha and caption fixtures passed');
}finally{await browser.close();await new Promise(r=>server.close(r));}
