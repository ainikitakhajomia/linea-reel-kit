// Browser acceptance runs only on the isolated Linux GitHub runner.
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {createServer} from './server.mjs';
import {spawnSync} from 'node:child_process';
import {resolve} from 'node:path';
await mkdir('out/studio-qa',{recursive:true});
const server=process.argv[2]?null:await createServer(4173),url=process.argv[2]||'http://127.0.0.1:4173/';
const browser=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']}),page=await browser.newPage({viewport:{width:1600,height:1100}}),errors=[],failed=[];
page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push('console: '+m.text());});page.on('response',r=>{if(r.status()>=400)failed.push({url:r.url(),status:r.status()});});
const report={url,effects:0,filmExports:0,sourceVideos:0,referenceVideos:0,audioDecoded:0,fullscreen:false,navigation:[],errors,failed};
async function play(v){await v.scrollIntoViewIfNeeded();await v.evaluate(async v=>{v.muted=true;v.currentTime=0;await v.play();});await page.waitForTimeout(180);await v.evaluate(v=>new Promise((resolve,reject)=>{const deadline=performance.now()+10000;function check(){if(v.currentTime>0&&v.videoWidth>0)resolve();else if(performance.now()>deadline)reject(Error('Video did not advance'));else requestAnimationFrame(check);}check();}));assert.ok(await v.evaluate(v=>v.videoHeight>0));await v.evaluate(v=>v.pause());}
try{
 await page.goto(url,{waitUntil:'networkidle'});await page.waitForSelector('.card');assert.equal(await page.locator('.card').count(),67);
 const manifest=await page.evaluate(async()=>{const r=await fetch(new URL('public/review-manifest.json',location.href));return r.json();});
 for(const v of await page.locator('.card video').all()){await play(v);report.effects++;}
 const paths=new Set();function collect(x){if(typeof x==='string'&&x.startsWith('review-media/'))paths.add(x);else if(Array.isArray(x))x.forEach(collect);else if(x&&typeof x==='object')Object.values(x).forEach(collect);}collect(manifest);
 const allPaths=[...paths];for(let i=0;i<allPaths.length;i+=6)await Promise.all(allPaths.slice(i,i+6).map(async p=>{const r=await page.request.head(new URL('public/'+p,url).href);assert.ok(r.ok(),'Missing media: '+p);assert.ok(Number(r.headers()['content-length'])>0,'Empty media: '+p);}));report.mediaFilesVerified=paths.size;

 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:'out/studio-qa/library.png'});
 await page.locator('.open').first().click();await page.waitForSelector('dialog[open]');
 for(const v of await page.locator('#comparison video').all())await play(v);
 const refs=await page.evaluate(async()=>{const r=await fetch(new URL('src/catalog.json',location.href));return r.json();});
 for(const e of refs){await page.locator('#comparison video').last().evaluate((v,url)=>{v.src=url;v.load();},e.reference);await play(page.locator('#comparison video').last());report.referenceVideos++;}
 await page.locator('#comparison video').last().evaluate((v,url)=>{v.src=url;v.load();},refs[0].reference);
 await page.locator('#fullscreen').click();await page.waitForFunction(()=>!!document.fullscreenElement);report.fullscreen=true;await page.evaluate(()=>document.exitFullscreen());
 await page.locator('#favorite').click();await page.locator('[data-decision="approved"]').click();await page.locator('#feedback').fill('QA review persists');await page.locator('#verdict').selectOption('improve');
 await page.locator('#parameters summary').click();const first=await page.locator('#detail').evaluate(c=>c.toDataURL());await page.locator('#dtext').fill('Visuele review');await page.waitForFunction(first=>document.querySelector('#detail').toDataURL()!==first,first);
 await page.screenshot({path:'out/studio-qa/comparison.png'});await page.locator('#close').click();
 await page.reload();await page.waitForSelector('.card');await page.locator('.open').first().click();assert.equal(await page.locator('#feedback').inputValue(),'QA review persists');await page.locator('#close').click();
 for(const pane of ['films','styles','workflows','compare','favorites','decisions','effects']){await page.locator(`nav [data-pane="${pane}"]`).click();assert.ok((await page.locator('#content').innerText()).length>0);report.navigation.push(pane);}
 await page.locator('nav [data-pane="films"]').click();await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:'out/studio-qa/films.png'});
 // Decode every unique existing film export and source, including older versions.
 const films=[...manifest.films.flatMap(f=>f.versions.map(v=>v.video)),...manifest.extras.map(e=>e.video)];const sources=[...new Set([...manifest.films.flatMap(f=>f.versions.map(v=>v.source)),...manifest.extras.map(e=>e.source)].filter(Boolean))];
 for(const [type,paths] of [['filmExports',films],['sourceVideos',sources]])for(const path of paths){
  const data=await page.evaluate(async path=>{const v=document.createElement('video');v.src=new URL('public/'+path,location.href).href;v.muted=false;v.volume=.4;v.controls=true;document.body.append(v);await v.play();await new Promise(r=>setTimeout(r,160));const result={time:v.currentTime,width:v.videoWidth,audio:v.audioTracks?.length||v.webkitAudioDecodedByteCount||0};v.pause();v.remove();return result;},path);
  assert.ok(data.time>0&&data.width>0,path);report[type]++;if(data.audio>0)report.audioDecoded++;
 }
 // Web Audio actually decodes non-silent audio; no claim about a human listening.
 report.audioSignal=await page.evaluate(async path=>{const ctx=new AudioContext();const b=await ctx.decodeAudioData(await (await fetch(new URL('public/'+path,location.href))).arrayBuffer());const samples=b.getChannelData(0);let peak=0;for(const s of samples)peak=Math.max(peak,Math.abs(s));await ctx.close();return {channels:b.numberOfChannels,duration:b.duration,peak};},films[0]);assert.ok(report.audioSignal.peak>.001);
 report.audioStreams=[];
 for(const path of [...new Set(films)]){
  const probe=spawnSync('ffprobe',['-v','error','-show_streams','-of','json',resolve('public',path)],{encoding:'utf8'});if(probe.status!==0)throw Error('Cannot inspect audio streams: '+path);
  const decoded=spawnSync('ffmpeg',['-v','error','-i',resolve('public',path),'-f','null','-'],{encoding:'utf8',timeout:60000});assert.equal(decoded.status,0,'Full export must decode through its final frame: '+path+' '+decoded.stderr);
  const streams=JSON.parse(probe.stdout).streams.filter(s=>s.codec_type==='audio');
  if(!streams.length){report.audioStreams.push({path,audio:false});continue;}
  const signal=await page.evaluate(async path=>{const ctx=new AudioContext();const buffer=await ctx.decodeAudioData(await (await fetch(new URL('public/'+path,location.href))).arrayBuffer());let peak=0;for(const value of buffer.getChannelData(0))peak=Math.max(peak,Math.abs(value));await ctx.close();return {channels:buffer.numberOfChannels,peak,duration:buffer.duration};},path);
  assert.ok(signal.peak>.001,'Existing audio must decode and contain signal: '+path);report.audioStreams.push({path,audio:true,...signal});
 }

 await page.locator('.open').first().click();await page.getByRole('button',{name:'Bron naast eindresultaat'}).click();assert.equal(await page.locator('#comparison video').count(),2);assert.ok(await page.locator('.storyboard article').count()>0);await page.screenshot({path:'out/studio-qa/workflow.png'});await page.locator('#close').click();
 await page.setViewportSize({width:390,height:844});await page.locator('nav [data-pane="effects"]').click();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:'out/studio-qa/mobile.png'});
 assert.equal(errors.length,0,errors.join('\n'));assert.equal(failed.length,0,JSON.stringify(failed));console.log(JSON.stringify(report));
}catch(e){report.error=e.message;await page.screenshot({path:'out/studio-qa/failure.png',fullPage:true});throw e;}finally{await writeFile('out/studio-qa/report.json',JSON.stringify(report,null,2));await browser.close();if(server)await new Promise(r=>server.close(r));}
