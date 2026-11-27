// Independent visual recipes, original Canvas implementation. No reference assets.
import {easeOutCubic, typeText, countValue} from '../vendor/motion-video-styles/timing.mjs';
export const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
export const ease=easeOutCubic;
const spring=x=>1-Math.exp(-7*Math.max(0,x))*Math.cos(11*Math.max(0,x));
export function roundRect(c,x,y,w,h,r=18){c.beginPath();c.roundRect(x,y,w,h,r);}
function box(c,x,y,w,h,color,r=18){c.fillStyle=color;roundRect(c,x,y,w,h,r);c.fill();}
function line(c,x,y,x2,y2,color,width=3){c.strokeStyle=color;c.lineWidth=width;c.beginPath();c.moveTo(x,y);c.lineTo(x2,y2);c.stroke();}
function text(c,str,x,y,size=40,color='#111',align='left',weight=700){c.fillStyle=color;c.font=`${weight} ${size}px Arial, sans-serif`;c.textAlign=align;c.textBaseline='middle';c.fillText(String(str),x,y);}
function fit(c,str,x,y,max=560,size=72,color='#111',align='center'){while(size>16){c.font=`800 ${size}px Arial`;if(c.measureText(str).width<=max)break;size-=2;}text(c,str,x,y,size,color,align,800);}
function card(c,x,y,w,h,b,heading='Studio Linea'){c.save();c.shadowColor='#0002';c.shadowBlur=25;c.shadowOffsetY=12;box(c,x,y,w,h,b.surface||'#fff');c.restore();text(c,heading,x+24,y+35,23,b.foreground);line(c,x+24,y+64,x+w-24,y+64,b.accent+'35',2);}
function cursor(c,x,y,b){c.fillStyle=b.accent;c.beginPath();c.moveTo(x,y);c.lineTo(x+6,y+35);c.lineTo(x+15,y+24);c.lineTo(x+27,y+24);c.closePath();c.fill();}
// Media is scoped to this draw call through its local brand object; no shared state.
function mediaSize(source){return [source?.videoWidth||source?.naturalWidth||source?.width||0,source?.videoHeight||source?.naturalHeight||source?.height||0];}
function drawOwned(c,source,x,y,w,h,{contain=false}={}){
 const [sw,sh]=mediaSize(source);if(!sw||!sh||w<=0||h<=0)return false;
 const k=(contain?Math.min:Math.max)(w/sw,h/sh);c.save();c.beginPath();c.rect(x,y,w,h);c.clip();c.drawImage(source,x+(w-sw*k)/2,y+(h-sh*k)/2,sw*k,sh*k);c.restore();return true;
}
function selectedMedia(b,n=0){const m=b._media||{},sources=b._sources||[];const key=sources.length?sources[((n%sources.length)+sources.length)%sources.length]:null;return (key&&m[key])||m.walkthrough||m.video||null;}
function portrait(c,x,y,scale,b){
 const m=b._media||{};c.save();c.translate(x,y);c.scale(scale,scale);
 if(m.foreground){drawOwned(c,m.foreground,-110,-90,220,360,{contain:true});c.restore();return;}
 if(m.video){c.beginPath();c.ellipse(0,65,110,155,0,0,Math.PI*2);c.clip();drawOwned(c,m.video,-110,-90,220,310);c.restore();return;}
 c.fillStyle=b.accent;c.beginPath();c.ellipse(0,110,100,130,0,0,7);c.fill();c.fillStyle='#d7ac91';c.beginPath();c.ellipse(0,0,57,72,0,0,7);c.fill();c.fillStyle=b.foreground;c.beginPath();c.ellipse(0,-41,60,34,0,Math.PI,Math.PI*2);c.fill();c.restore();
}
function scene(c,x,y,w,h,b,n=0){
 const source=selectedMedia(b,n);if(source){c.save();roundRect(c,x,y,w,h,12);c.clip();drawOwned(c,source,x,y,w,h);c.restore();return;}
 box(c,x,y,w,h,n%2?b.accent:'#dfe2eb',12);for(let j=0;j<4;j++)box(c,x+w*.12,y+h*(.18+j*.16),w*(.65-j*.08),h*.07,n%2?'#ffffff60':b.accent+'40',3);
}
function makeLayer(c,w=720,h=1280){const layer=typeof OffscreenCanvas!=='undefined'?new OffscreenCanvas(w,h):c.canvas.ownerDocument.createElement('canvas');layer.width=w;layer.height=h;return layer;}
function words(s){return String(s).split(/\s+/);}
export const defaultBrand={background:'#f6f5f1',foreground:'#111316',accent:'#27335f',surface:'#fff'};
// Shared camera model: the stage, review and media jobs use exactly this transform.
export function cameraTransform(id,time,duration=2.4,params={}){
 const q=clamp(time/Math.max(.01,duration)),enter=ease(time/(params.attack||.24));
 if(id==='dolly-zoom')return {zoom:1+(params.amount??.28)*ease(q),subjectZoom:1-(params.subjectAmount??.06)*ease(q),x:0,y:0,rotation:0};
 if(id==='camera-transitions'){
   const settle=1-ease(time/(params.attack||.5)),direction=params.direction==='left'?-1:1;
   return {zoom:1+.09*settle,x:direction*720*settle,y:params.mode==='drop'?-1280*settle:0,rotation:params.mode==='spin'?direction*Math.PI*.3*settle:0};
 }
 return {zoom:1+(params.amount??.13)*enter,x:0,y:0,rotation:0};
}
function applyCamera(c,transform){c.translate(360+transform.x,640+transform.y);c.rotate(transform.rotation);c.scale(transform.zoom,transform.zoom);c.translate(-360,-640);}
export function drawEffect(c,id,time,p={},brand=defaultBrand){
 const b={...defaultBrand,...brand,_media:p.media||{},_sources:p.mediaSources||[]}, t=Math.max(0,time), a=ease(t/.6), s=spring(t/.65), title=p.text||'Meer tijd. Meer impact.', W=720,H=1280;
 c.save();
 const fade=clamp((p.duration===undefined?100:p.duration)-t,0,.3)/.3;c.globalAlpha=fade*ease(t/.45);c.translate(0,24*(1-ease(t/.45)));
 switch(id){
 case 'title-reveal': case 'kinetic-hook': {words(title).slice(0,5).forEach((w,i)=>{const at=p.wordTimes?.[i]?.start??(p.wordTimes?.[i]?.startMs!==undefined?p.wordTimes[i].startMs/1000:i*.12),q=ease((t-at)/.55);c.save();c.translate(W/2,380+i*88+(1-q)*65);c.globalAlpha*=q;fit(c,w,0,0,620,80,b.foreground);c.restore();});break;}
 case 'icon-strike': {
   const labels=Array.isArray(p.labels)?p.labels.slice(0,3):['Knippen','Herhalen','Wachten'];
   labels.forEach((label,i)=>{const enter=ease((t-i*.16)/.35),strike=ease((t-.45-i*.30)/.22),drop=ease((t-1.7-i*.12)/.5);c.save();c.translate(150+i*210,560+(1-enter)*65+drop*650);c.rotate((i-1)*drop*.6);c.globalAlpha*=enter*(1-drop);box(c,-78,-78,156,156,b.accent,28);text(c,['✂','↻','◷'][i],0,-8,76,'white','center');text(c,label,0,115,24,b.foreground,'center');c.lineCap='round';line(c,-90,60,-90+180*strike,60-120*strike,'#e16d63',9);c.restore();});
   c.save();c.globalAlpha*=ease((t-2)/.4);fit(c,title,360,560,630,64,b.accent);c.restore();break;}

 case 'prompt-bar': case 'search-suggest': {card(c,54,500+(1-a)*90,612,id==='search-suggest'?270:160,b,id==='search-suggest'?'Zoeken':'Prompt');text(c,'⌕',82,602,36,b.accent);fit(c,typeText(title,t,0,24),395,602,470,30,b.foreground);if(id==='search-suggest')for(let i=0;i<3;i++)text(c,['Snel een idee uitwerken','Meer tijd voor klanten','Van script naar video'][i],90,660+i*36,23,b.foreground);break;}
 case 'grade-slider': {const source=selectedMedia(b);scene(c,72,370,576,380,b);c.save();c.beginPath();c.rect(72,370,576*a,380);c.clip();if(source){c.filter=p.filter||'sepia(.35) saturate(1.2) contrast(1.08)';drawOwned(c,source,72,370,576,380);}else{c.fillStyle='#efa85c55';c.fillRect(72,370,576,380);}c.restore();line(c,72+576*a,350,72+576*a,775,b.accent,5);box(c,47+576*a,530,50,50,'white',25);text(c,'↔',72+576*a,555,27,b.accent,'center');break;}
 case 'magazine-cover': case 'press-front': {box(c,70,230,580,790,'#fff');fit(c,id==='press-front'?'LINEA DAILY':'LINEA',360,310,520,100,b.accent);text(c,'IDEAS / PEOPLE / PROGRESS',360,385,19,b.foreground,'center');c.save();if(id==='press-front')c.filter='grayscale(1) contrast(1.3)';scene(c,100,420,520,350,b);c.restore();fit(c,title,360,845,500,50,b.foreground);line(c,100,910,620,910,b.accent,2);text(c,'Nieuwe perspectieven, elke dag.',360,950,22,b.foreground,'center');break;}
 case 'nle-timeline': {card(c,35,430,650,375,b,'De juiste take. Op de juiste plek.');for(let r=0;r<3;r++)for(let j=0;j<4;j++)box(c,62+j*145,540+r*66,130*a,48,[b.accent,'#8a9bc4','#899e80'][r],7);line(c,65+565*((t*.17)%1),510,65+565*((t*.17)%1),780,'#ee6f51',4);break;}
 case 'file-drop': {const y=260+310*a;for(let i=0;i<3;i++){c.save();c.translate(260+i*90,y-i*22);c.rotate((i-1)*.13*a);card(c,-85,-100,170,210,b,['SCRIPT','VIDEO','AUDIO'][i]);if(i===1&&selectedMedia(b))scene(c,-65,-20,130,110,b);else text(c,['Aa','▶','♫'][i],0,30,60,b.accent,'center');c.restore();}box(c,95,780,530,130,b.accent+'15');text(c,'Drop je idee hier',360,845,32,b.accent,'center');break;}
 case 'odometer-recursion': case 'counter': {
   if(id==='odometer-recursion'&&selectedMedia(b)){for(let depth=0;depth<4;depth++){const k=Math.pow(.58,depth)*(1+.12*ease((t-.7)/1.3));scene(c,360-280*k,650-370*k,560*k,740*k,b,depth);}box(c,100,210,520,130,b.surface,12);fit(c,String(Math.round(countValue(p.value||128,t,0,.6))).padStart(3,'0'),360,275,480,90,b.accent);}
   else{fit(c,String(Math.round(countValue(p.value||128,t,0,.6))).padStart(3,'0'),360,570,620,170,b.accent);text(c,p.label||'minuten teruggewonnen',360,710,30,b.foreground,'center');}break;}
 case 'mood-curtain': {const source=p.media?.video;if(source){c.save();c.beginPath();c.rect(0,0,W,H*a);c.clip();c.filter=p.filter||'brightness(.62) saturate(.7) contrast(1.1)';drawOwned(c,source,0,0,W,H);c.restore();const g=c.createRadialGradient(360,640,90,360,640,780);g.addColorStop(0,'#0000');g.addColorStop(1,'#0009');c.fillStyle=g;c.fillRect(0,0,W,H);}else for(let i=0;i<10;i++){const q=ease((t-i*.035)/.8);box(c,i*72,0,74,H*q,i%2?b.accent:'#1c2547',0);}fit(c,title,360,600,600,68,'#fff');break;}
 case 'grid-collapse': case 'contact-sheet-hook': case 'playing-grid': {for(let i=0;i<9;i++){let x=55+(i%3)*210,y=280+Math.floor(i/3)*240;let k=id==='grid-collapse'?ease((t-.8)/.9):0;x+=(255-x)*k;y+=(510-y)*k;scene(c,x,y,190,210,b,i);if(id==='playing-grid')line(c,x+15,y+175,x+175,y+175,'#ffffff',3+3*Math.sin(t*2+i));}break;}
 case 'page-scroll': {c.save();c.beginPath();c.rect(80,300,560,680);c.clip();card(c,80,300-400*a,560,1200,b,'Van idee naar resultaat');for(let i=0;i<8;i++)scene(c,110,400+i*155-400*a,500,120,b,i);c.restore();break;}
 case 'comment-thread': case 'comment-cta': case 'comment-drop': {for(let i=0;i<(id==='comment-cta'?1:3);i++){const q=ease((t-i*.22)/.5);c.save();c.globalAlpha*=q;card(c,65+i*20,430+i*140+(1-q)*150,570,110,b,['@studio.linea','@team','@jij'][i]);text(c,i===0?title:['Wat een verschil!','Dit wil ik ook.'][i-1],95+i*20,505+i*140+(1-q)*150,26,b.foreground);c.restore();}break;}
 case 'word-stamp': {c.translate(360,580);c.rotate(-.09*a);c.scale(1+(1-a)*1.2,1+(1-a)*1.2);c.strokeStyle=b.accent;c.lineWidth=8;roundRect(c,-305,-90,610,180,8);c.stroke();fit(c,title.toUpperCase(),0,0,550,70,b.accent);break;}
 case 'giant-captions': {words(title).slice(0,6).forEach((w,i)=>{const at=p.wordTimes?.[i]?.start??(p.wordTimes?.[i]?.startMs!==undefined?p.wordTimes[i].startMs/1000:i*.14),q=ease((t-at)/.4);fit(c,w.toUpperCase(),360,414+i*95+(1-q)*30,620,84,b.accent);});break;}
 case 'knockout-captions': {
   // Punch through an isolated plate; never erase the already composited footage.
   const plate=makeLayer(c,W,H),pc=plate.getContext('2d');
   const reveal=ease(t/.45);pc.fillStyle=b.accent;pc.fillRect(0,270,W,660*reveal);pc.globalCompositeOperation='destination-out';
   words(title).slice(0,5).forEach((w,i)=>{const q=ease((t-i*.16)/.4);pc.globalAlpha=q;fit(pc,w.toUpperCase(),360,360+i*112,660,108,'#000');});
   c.drawImage(plate,0,0);break;}
 case 'video-card': {c.save();c.translate(360,610);c.rotate((1-a)*.16);c.scale(.8+.2*a,.8+.2*a);card(c,-285,-260,570,520,b,'Studio Linea / Product update');scene(c,-255,-175,510,300,b);fit(c,title,0,190,500,38,b.foreground);c.restore();break;}
 case 'camera-transitions': case 'zoom-punch': case 'dolly-zoom': {
   const motion=cameraTransform(id,t,p.duration,p);c.save();applyCamera(c,motion);scene(c,50,270,620,700,b);c.restore();
   if(id==='dolly-zoom')portrait(c,360,560,motion.subjectZoom,b);fit(c,title,360,1050,610,52,b.accent);break;}
 case 'receipt-printer': {c.save();c.beginPath();c.rect(115,330,490,700*a);c.clip();box(c,115,330,490,700,'#fff',0);text(c,'STUDIO LINEA',360,390,35,b.foreground,'center');for(let i=0;i<5;i++){text(c,['Handwerk','Herhaling','Wachttijd','Automatisering','TIJD TERUG'][i],145,490+i*85,25,b.foreground);text(c,['−30m','−20m','−10m','+60m','∞'][i],560,490+i*85,25,b.accent,'right');}line(c,140,820,580,820,b.accent,2);c.restore();box(c,90,295,540,65,b.accent,14);break;}
 case 'jiggle-delete': {for(let i=0;i<3;i++){c.save();c.translate(160+i*200,580);c.rotate(Math.sin(t*18+i)*.07);c.scale(i===1?1-ease((t-1)/.5):1,i===1?1-ease((t-1)/.5):1);box(c,-75,-75,150,150,b.accent,30);text(c,['Aa','×','▶'][i],0,0,64,'white','center');box(c,48,-90,44,44,'#e66b58',22);text(c,'−',70,-68,32,'white','center');c.restore();}break;}
 case 'keycaps': case 'predict-keys': {const letters=id==='predict-keys'?'LINEA':(p.text||'CMD K');words(letters).join('').slice(0,7).split('').forEach((letter,i)=>{const n=Math.min(letters.length,7),x=360+(i-(n-1)/2)*82,down=Math.sin(t*6-i)>0.7?10:0;box(c,x-34,545,68,90,b.accent+'70',12);box(c,x-34,535+down,68,80,'white',12);text(c,letter,x,575+down,35,b.foreground,'center');});break;}
 case 'projected-film': case 'film-look': {c.fillStyle='#39261618';c.fillRect(0,0,W,H);for(let i=0;i<20;i++)box(c,18,20+i*68,18,36,b.foreground,3);line(c,80+((Math.floor(t*30)*37)%560),0,80+((Math.floor(t*30)*37)%560),H,'#ffffff55',1);const g=c.createRadialGradient(360,640,100,360,640,750);g.addColorStop(0,'#0000');g.addColorStop(1,'#0009');c.fillStyle=g;c.fillRect(0,0,W,H);if(id==='projected-film'){scene(c,100,430,520,390,b);text(c,'01 / IN THE MAKING',360,880,23,b.foreground,'center');}break;}
 case 'eyedropper-grade': {const colors=['#27335f','#8a9bc4','#dfe9d3','#f6f5f1'];scene(c,75,300,570,410,b);colors.forEach((col,i)=>box(c,90+i*140,780+(1-a)*70,120,120,col,20));cursor(c,100+480*a,620,b);break;}
 case 'reel-cascade': case 'reel-feed': case 'post-wall': {for(let i=0;i<5;i++){c.save();if(id==='post-wall'){c.translate(100+(i%2)*300,260+Math.floor(i/2)*280);scene(c,0,0,250,240,b,i);}else{c.translate(360+(i-2)*80*a,610+(i-2)*(id==='reel-feed'?250:55));c.rotate((i-2)*.07*a);scene(c,-140,-220,280,440,b,i);}c.restore();}break;}
 case 'intertitle': case 'title-card-dive': {const k=id==='title-card-dive'?1+Math.pow(clamp((t-1.5)/1),3)*10:1;c.translate(360,640);c.scale(k,k);box(c,-330,-180,660,360,b.accent,0);fit(c,title,0,0,600,68,'white');text(c,'STUDIO LINEA',0,100,20,'#ffffff90','center');break;}
 case 'screenplay-page': {card(c,65,230,590,820,b,'INT. STUDIO — DAY');const lines=['Een idee verschijnt.','De handmatige stappen verdwijnen.','TEAM','“Nu kunnen we weer creëren.”','FADE OUT.'];lines.forEach((v,i)=>text(c,v.slice(0,Math.max(0,Math.floor(t*35)-i*28)),110,410+i*100,23,b.foreground));break;}
 case 'orbit-ring': {
   const glyphs=(p.orbitText||title+' • ').toUpperCase().split('').slice(0,64),radius=p.radius||265,cy=p.centerY||520;
   const renderPass=pass=>{glyphs.forEach((glyph,i)=>{const angle=i/glyphs.length*Math.PI*2+t*(p.speed||.75),depth=Math.sin(angle);if((pass==='rear')!==(depth<0))return;const scale=.74+.22*depth,x=360+Math.cos(angle)*radius,y=cy+depth*72;c.save();c.globalAlpha*=.6+.4*(depth+1)/2;c.translate(x,y);c.scale(scale,scale);text(c,glyph,0,0,35,b.accent,'center');c.restore();});};
   if(p.orbitPass){renderPass(p.orbitPass);}else{renderPass('rear');portrait(c,360,cy-45,.9,b);renderPass('front');}break;}
 case 'lens-ring': case 'day-dial': {c.translate(360,620);c.save();c.rotate(t*.4);c.strokeStyle=b.accent;c.lineWidth=3;c.beginPath();c.arc(0,0,230,0,Math.PI*2);c.stroke();for(let j=0;j<24;j++)line(c,Math.cos(j*Math.PI/12)*205,Math.sin(j*Math.PI/12)*205,Math.cos(j*Math.PI/12)*225,Math.sin(j*Math.PI/12)*225,b.accent,j%3?2:5);c.restore();text(c,id==='day-dial'?`${String(Math.floor(8+9*a)).padStart(2,'0')}:00`:'FOCUS',0,0,52,b.foreground,'center');break;}
 case 'grease-pencil-sheet': case 'live-markup': case 'finger-draw': case 'sketch-words': {fit(c,title,360,550,600,65,b.foreground);c.strokeStyle=b.accent;c.lineWidth=id==='finger-draw'?12:5;c.lineCap='round';c.beginPath();if(id==='sketch-words'){c.setLineDash([500*a,500]);c.moveTo(65,605);c.quadraticCurveTo(340,650,650,600);}else{c.ellipse(360,550,310,95,-.04,0,Math.PI*2*a);}c.stroke();if(id==='grease-pencil-sheet'){for(let i=0;i<5;i++)line(c,100+i*110,760,140+i*110,720,b.accent,5);}break;}
 case 'picture-dive': {const k=1+4*ease((t-.9)/1.5);c.translate(360,620);c.scale(k,k);for(let depth=0;depth<4;depth++){const w=540*Math.pow(.54,depth),h=760*Math.pow(.54,depth);box(c,-w/2-7,-h/2-7,w+14,h+14,b.surface,4);scene(c,-w/2,-h/2,w,h,b,depth);}break;}
 case 'storyboard-deck': {for(let i=2;i>=0;i--){c.save();c.translate(360+(i-1)*85*a,610-i*20);c.rotate((i-1)*.08*a);card(c,-230,-260,460,520,b,`SCÈNE ${i+1}`);scene(c,-200,-170,400,270,b,i);text(c,['Hook','Bewijs','Actie'][i],0,175,36,b.foreground,'center');c.restore();}break;}
 case 'gravity-drop': {const y=200+430*clamp(s);c.save();c.translate(360,y);c.rotate(.15*Math.sin(t*6)*Math.exp(-t*2));box(c,-150,-110,300,220,b.accent,35);fit(c,title,0,0,270,46,'white');c.restore();break;}
 case 'video-backdrop': {const background=p.media?.walkthrough||selectedMedia(b);if(background)drawOwned(c,background,0,0,W,H,{contain:p.contain===true});else{for(let i=0;i<5;i++){c.save();c.translate(360,640);c.rotate((i-2)*.12);scene(c,-250+i*15,-300+i*25,500,600,b,i);c.restore();}}break;}
 case 'shape-transitions': {
   const q=ease(t/(p.attack||.95)),variant=p.variant||'iris',next=p.media?.next||selectedMedia(b);c.save();c.beginPath();
   if(variant==='blinds'){for(let i=0;i<8;i++)c.rect(0,i*160,W,161*q);}
   else if(variant==='doors'){c.rect(0,0,W*q/2,H);c.rect(W-W*q/2,0,W*q/2,H);}
   else if(variant==='clock'){c.moveTo(360,640);c.arc(360,640,900,-Math.PI/2,-Math.PI/2+Math.PI*2*q);c.closePath();}
   else c.arc(360,640,900*q,0,Math.PI*2);
   c.clip();if(next)drawOwned(c,next,0,0,W,H);else{box(c,0,0,W,H,b.accent,0);fit(c,title,360,640,620,64,'white');}c.restore();break;}
 case 'paper-tear': {
   const q=ease((t-.18)/.72),edge=Array.from({length:41},(_,i)=>({y:i*32,x:360+Math.sin(i*2.37)*11+Math.cos(i*.83)*7}));
   for(const side of [-1,1]){c.save();c.translate(side*q*480,-q*35);c.translate(side<0?0:W,H/2);c.rotate(side*q*.09);c.scale(1-.18*q,1);c.translate(side<0?0:-W,-H/2);
     c.beginPath();c.moveTo(side<0?0:W,0);c.lineTo(edge[0].x,0);for(const pt of edge)c.lineTo(pt.x,pt.y);c.lineTo(side<0?0:W,H);c.closePath();c.shadowColor='#0007';c.shadowBlur=20;c.shadowOffsetX=-side*15;c.fillStyle='#f3eddf';c.fill();c.shadowColor='transparent';c.clip();
     if(p.media?.previous){const v=p.media.previous,vw=v.videoWidth||v.width,vh=v.videoHeight||v.height,k=Math.max(W/vw,H/vh);c.drawImage(v,(W-vw*k)/2,(H-vh*k)/2,vw*k,vh*k);}else{
       fit(c,'THE LINEA JOURNAL',360,135,660,57,b.foreground);line(c,35,190,685,190,b.foreground,2);fit(c,title.toUpperCase(),360,280,650,57,b.accent);for(let col=0;col<4;col++)for(let row=0;row<32;row++)line(c,35+col*172,390+row*23,175+col*172,390+row*23,'#847d6c80',2);
     }
     c.beginPath();edge.forEach((pt,i)=>i?c.lineTo(pt.x,pt.y):c.moveTo(pt.x,pt.y));c.strokeStyle='#fffdf7';c.lineWidth=8;c.stroke();c.restore();
   }break;}
 case 'blade-slice': {
   const source=p.media?.video||selectedMedia(b),bands=6,phase=clamp(t/(p.duration||2.4)),shift=Math.sin(phase*Math.PI)**2*(p.distance||115);
   if(source){box(c,0,0,W,H,b.background,0);for(let i=0;i<bands;i++){c.save();c.beginPath();c.rect(0,i*H/bands,W,H/bands+1);c.clip();c.translate((i%2?1:-1)*shift,0);drawOwned(c,source,0,0,W,H);c.restore();}}
   else for(let i=0;i<bands;i++){const q=ease((t-i*.06)/.6);c.save();c.beginPath();c.rect(0,350+i*90,720,90);c.clip();fit(c,title,360+(1-q)*(i%2?720:-720),620,650,100,b.accent);c.restore();}break;}
 case 'impact-frame': case 'comic-burst': case 'shockwave': {c.translate(360,640);if(id==='shockwave'){c.strokeStyle=b.accent;c.lineWidth=10*(1-clamp(t/2));c.beginPath();c.arc(0,0,50+400*clamp(t/2),0,Math.PI*2);c.stroke();}else{c.fillStyle=b.accent;c.beginPath();for(let i=0;i<32;i++){let angle=i*Math.PI/16,r=(i%2?190:320)*Math.min(1.2,s);c.lineTo(Math.cos(angle)*r,Math.sin(angle)*r);}c.closePath();c.fill();fit(c,title,0,0,420,60,'white');}break;}
 case 'banknote': {c.save();c.translate(360,610);c.rotate((1-a)*.5-.08);box(c,-325,-170,650,340,'#dfe9d3',10);c.strokeStyle='#3d5a2a';c.lineWidth=3;roundRect(c,-300,-145,600,290,5);c.stroke();
   if(p.media?.foreground||p.media?.video){c.save();c.beginPath();c.ellipse(-130,0,100,125,0,0,Math.PI*2);c.clip();c.filter='grayscale(1) sepia(.6) contrast(1.55)';const subject=p.media.foreground||p.media.video;drawOwned(c,subject,-230,-125,200,250,{contain:!!p.media.foreground});c.restore();c.strokeStyle='#3d5a2a';c.beginPath();c.ellipse(-130,0,103,128,0,0,Math.PI*2);c.stroke();text(c,String(Math.round(countValue(p.value||60,t,0,1.2))),145,0,88,'#3d5a2a','center');text(c,p.label||'MINUTEN',145,90,19,'#3d5a2a','center');}
   else{text(c,'TIJD IS WAARDE',0,-75,24,'#3d5a2a','center');text(c,'60',0,20,110,'#3d5a2a','center');text(c,'MINUTEN',0,105,20,'#3d5a2a','center');}c.restore();break;}
 case 'voice-note': {card(c,55,495,610,220,b,'Spraakbericht / 0:12');for(let i=0;i<52;i++){const h=12+60*Math.abs(Math.sin(i*2.13+t*4));box(c,86+i*10.5,645-h/2,5,h,i/52<clamp(t/3)?b.accent:'#dfe2eb',3);}break;}
 case 'letter-dive': {
   const layer=makeLayer(c),lc=layer.getContext('2d'),label=String(p.text||'OPEN').toUpperCase().split(/\s+/)[0].slice(0,10),dive=ease((t-.65)/1.3),k=1+24*dive**3;
   // Keep the late dive useful: blend from the enlarged text window into the full
   // source rather than zooming a gap between letters into an empty white frame.
   lc.save();lc.translate(360,640);lc.scale(k,k);fit(lc,label,0,0,660,280,b.accent);lc.restore();lc.globalCompositeOperation='source-in';
   const source=selectedMedia(b),fillSource=target=>{if(source)drawOwned(target,source,0,0,W,H);else{const g=target.createLinearGradient(0,0,W,H);g.addColorStop(0,b.accent);g.addColorStop(.5,'#8a9bc4');g.addColorStop(1,b.foreground);target.fillStyle=g;target.fillRect(0,0,W,H);}};
   fillSource(lc);c.drawImage(layer,0,0);const complete=ease((dive-.5)/.4);if(complete){c.save();c.globalAlpha*=complete;fillSource(c);c.restore();}break;}
 case 'blow-away': {words(title).join(' ').split('').slice(0,28).forEach((letter,i)=>{c.save();const q=ease((t-i*.025)/.7),away=clamp((t-.7)/1.4);c.translate(80+i*23+away**2*i*30,590-Math.sin(i)*200*away);c.rotate((1-q)*(i%2?.8:-.8)+away*(i%2?1:-1));c.globalAlpha*=1-away*.8;text(c,letter,0,0,40,b.foreground);c.restore();});break;}
 case 'live-cursor': {card(c,55,420,610,350,b,'Je volgende stap');box(c,170,580,380,85,b.accent);text(c,title,360,623,30,'white','center');cursor(c,550-180*a,800-160*a,b);if(t>1){c.strokeStyle=b.accent;c.lineWidth=3;c.beginPath();c.arc(370,640,65*clamp((t-1)/.6),0,7);c.stroke();}break;}
 case 'head-stack': case 'clone-row': {for(let i=0;i<3;i++){c.save();c.globalAlpha*=clamp((t-i*.2)/.4);portrait(c,160+i*200,id==='head-stack'?510+i*80:600,.65,b);c.restore();}break;}
 case 'rack-focus': {c.save();c.filter=`blur(${a*(p.blur||15)}px)`;
   if(p.media?.video&&p.media?.foreground){const v=p.media.video,vw=v.videoWidth||v.width,vh=v.videoHeight||v.height,k=Math.max(W/vw,H/vh);c.drawImage(v,(W-vw*k)/2,(H-vh*k)/2,vw*k,vh*k);}else{scene(c,80,360,560,370,b);}
   c.restore();if(!p.media?.foreground)portrait(c,360,750,1.1,b);break;}
 case 'code-body': {
   const code=p.code||'const idea = yourStory; await reel.create({brand: "studio-linea", language: "nl", effects: "intentional"});';
   if(p.media?.foreground){const layer=makeLayer(c),lc=layer.getContext('2d');drawOwned(lc,p.media.foreground,0,0,W,H);lc.globalCompositeOperation='source-in';lc.fillStyle='#172038';lc.fillRect(0,0,W,H);lc.globalCompositeOperation='source-atop';for(let row=0;row<85;row++){const offset=(row*31+Math.floor(t*18))%code.length;text(lc,(code+code).slice(offset,offset+76),0,row*16,13,row%3?'#c6cce6':'#dfe9d3');}c.save();c.beginPath();c.rect(0,0,W,H*a);c.clip();c.drawImage(layer,0,0);c.restore();line(c,0,H*a,W,H*a,b.accent,4);}
   else{box(c,55,320,610,600,'#172038');const lines=['const idea = yourStory;','const edit = await reel.create({','  brand: "studio-linea",','  language: "nl",','  effects: "intentional",','});','await edit.render();'];lines.forEach((str,i)=>{text(c,String(i+1),78,400+i*62,19,'#7181a8');text(c,str.slice(0,Math.max(0,Math.floor(t*65)-i*25)),115,400+i*62,21,i%2?'#c6cce6':'#dfe9d3');});}break;}
 case 'layer-explode': {for(let i=0;i<4;i++){c.save();c.translate(360+(i-1.5)*55*a,640-(i-1.5)*105*a);c.transform(1,-.28,.4,.8,0,0);box(c,-220,-145,440,290,[b.accent+'55','#c6cce6','#fff',b.accent][i]);if((i===0||i===1)&&selectedMedia(b)){if(i===1)c.filter='grayscale(1)';scene(c,-220,-145,440,290,b);}else if(i===2&&p.media?.foreground)drawOwned(c,p.media.foreground,-220,-145,440,290,{contain:true});else text(c,['BRON','KLEUR','TEKST','CAPTIONS'][i],0,0,36,i===3?'#fff':b.foreground,'center');c.restore();}break;}
 case 'incoming-call': {box(c,110,290,500,720,b.accent,50);portrait(c,360,480,.6,{...b,accent:'#8a9bc4'});text(c,title,360,720,34,'white','center');text(c,'inkomende oproep…',360,785,24,'#c6cce6','center');box(c,190,865,100,100,'#e56d67',50);box(c,430,865,100,100,'#7eaa7e',50);text(c,'×',240,915,52,'white','center');text(c,'↗',480,915,52,'white','center');break;}
 case 'double-exposure': {
   const m=p.media||{},inside=selectedMedia(b);
   if(m.foreground&&inside){const layer=makeLayer(c),lc=layer.getContext('2d');drawOwned(lc,m.foreground,0,0,W,H);lc.globalCompositeOperation='source-in';lc.filter='grayscale(.7) contrast(1.2)';drawOwned(lc,inside,0,0,W,H);lc.filter='none';lc.globalCompositeOperation='source-atop';lc.globalAlpha=.22;lc.fillStyle=b.accent;lc.fillRect(0,0,W,H);c.globalAlpha*=.95;c.drawImage(layer,0,0);}
   else{
     // Authored silhouette + landscape: explicit synthetic fixture, visible on ivory.
     const layer=makeLayer(c),lc=layer.getContext('2d');lc.fillStyle=b.accent;lc.beginPath();lc.ellipse(360,470,116,150,0,0,Math.PI*2);lc.fill();lc.fillRect(310,565,100,130);lc.beginPath();lc.ellipse(360,835,245,220,0,Math.PI,Math.PI*2);lc.lineTo(605,1010);lc.lineTo(115,1010);lc.closePath();lc.fill();
     lc.globalCompositeOperation='source-in';const g=lc.createLinearGradient(0,300,0,1010);g.addColorStop(0,'#27335f');g.addColorStop(.52,'#7d90bd');g.addColorStop(1,'#18223c');lc.fillStyle=g;lc.fillRect(0,0,W,H);
     lc.globalCompositeOperation='source-atop';lc.fillStyle='#f1d9a8';lc.beginPath();lc.arc(440+Math.sin(t*.7)*22,470,65,0,Math.PI*2);lc.fill();
     for(let j=0;j<4;j++){const offset=Math.sin(t*.6+j)*22;lc.fillStyle=['#b1bbd0','#788db1','#475c85','#203253'][j];lc.beginPath();lc.moveTo(0,740+j*80);for(let i=0;i<=9;i++)lc.lineTo(i*90+offset,650+j*75-Math.sin(i*1.9+j)*75);lc.lineTo(W,H);lc.lineTo(0,H);lc.closePath();lc.fill();}
     c.drawImage(layer,0,0);text(c,'SYNTHETISCHE DUBBELE BELICHTING',360,1090,18,b.accent,'center');
   }break;}
 case 'room-doors': {
   const inside=p.media?.walkthrough||selectedMedia(b),outside=p.media?.video;
   if(inside)drawOwned(c,inside,70,300,580,680);else box(c,70,300,580,680,b.accent,0);
   for(let i=0;i<2;i++){const side=i?1:-1;c.save();c.beginPath();c.rect(70,300,580,680);c.clip();c.translate(side*a*270,0);c.translate(i?650:70,300);c.scale(1-.7*a,1);c.translate(i?-650:-70,-300);c.beginPath();c.rect(i?360:70,300,290,680);c.clip();if(outside)drawOwned(c,outside,70,300,580,680);else box(c,70,300,580,680,i?'#c6cce6':'#dfe2eb',0);c.restore();}
   if(!inside)fit(c,title,360,640,480,54,'white');break;}
 case 'follow-chip': {c.save();c.translate(360,650+(1-a)*80);c.scale(s,s);box(c,-270,-65,540,130,b.accent,65);text(c,'+',-205,0,52,'white','center');fit(c,p.text||'Volg Studio Linea',30,0,400,36,'white');c.restore();break;}
 case 'broll': break; // Actual owned media is composited by drawFrame.
 default: throw new Error(`Unknown effect: ${id}`);
 }
 c.restore();
}
// Greedy two-line caption layout measures actual glyphs and keeps all text in the safe area.
export function captionLines(tokens,measure,maxWidth=590,maxWords=5){
 const groups=[];let group=[],line=[],width=0;
 for(const token of tokens){const value=String(token.text||'').trim();if(!value)continue;
   const tokenWidth=measure(value),gap=line.length?measure(' '):0;
   if(line.length&&(width+gap+tokenWidth>maxWidth||line.length>=maxWords)){group.push(line);line=[];width=0;}
   if(group.length===2){groups.push(group);group=[];}
   line.push(token);width+=tokenWidth+(line.length>1?measure(' '):0);
   if(/[.!?]$/.test(value)){group.push(line);line=[];width=0;groups.push(group);group=[];}
 }
 if(line.length)group.push(line);if(group.length)groups.push(group);return groups;
}
export function drawCaptions(c,captions,time,brand=defaultBrand){
 const ms=time*1000,active=captions.find(x=>x.startMs<=ms&&x.endMs>ms);if(!active)return;
 const b={...defaultBrand,...brand},fontSize=42,font=`800 ${fontSize}px ${b.fontFamily||'Arial, sans-serif'}`;
 c.save();c.font=font;const groups=captionLines(captions,v=>c.measureText(v).width),group=groups.find(lines=>lines.some(line=>line.includes(active)));if(!group){c.restore();return;}
 const top=1090-(group.length-1)*62;group.forEach((tokens,row)=>{
   const gap=14,widths=tokens.map(token=>Math.min(590,c.measureText(String(token.text).trim()).width)),total=widths.reduce((sum,w)=>sum+w,0)+gap*(tokens.length-1),y=top+row*62;let x=(720-total)/2;
   // A dark plate protects contrast on both bright footage and the ivory gallery.
   box(c,x-18,y-29,total+36,58,'#111316e8',13);
   tokens.forEach((token,i)=>{const selected=token===active,age=clamp((ms-token.startMs)/110),pulse=selected?1+.055*Math.sin(age*Math.PI):1;c.save();c.translate(x+widths[i]/2,y);c.scale(pulse,pulse);if(selected)box(c,-widths[i]/2-7,-26,widths[i]+14,52,b.accent,9);fit(c,String(token.text).trim(),0,0,widths[i],fontSize,'#fff');c.restore();x+=widths[i]+gap;});
 });c.restore();
}
export function drawFrame(c,job,time,media={}){
 const b={...defaultBrand,...job.brand},w=job.width||720,h=job.height||1280;
 c.save();c.clearRect(0,0,w,h);c.scale(w/720,h/1280);
 c.fillStyle=b.background;c.fillRect(0,0,720,1280);
 const camera=(job.effects||[]).find(e=>['zoom-punch','camera-transitions','dolly-zoom'].includes(e.id)&&time>=e.start&&time<e.start+e.duration),motion=camera?cameraTransform(camera.id,time-camera.start,camera.duration,{...camera.params,...camera}):null;
 if(media.previous&&camera?.id==='camera-transitions')drawOwned(c,media.previous,0,0,720,1280);
 if(media.background||media.video){c.save();if(motion)applyCamera(c,motion);drawOwned(c,media.background||media.video,0,0,720,1280);c.restore();}
 if(media.walkthrough){box(c,40,250,640,480,'#fff');const v=media.walkthrough;const ratio=Math.min(610/(v.videoWidth||v.width),420/(v.videoHeight||v.height));const dw=(v.videoWidth||v.width)*ratio,dh=(v.videoHeight||v.height)*ratio;c.drawImage(v,360-dw/2,490-dh/2,dw,dh);}
 for(const e of job.effects||[]){if(time<e.start||time>=e.start+e.duration)continue;if(e.id==='broll'){if(media[e.src]){const v=media[e.src];c.drawImage(v,40,320,640,480);}continue;}if(media.video&&['zoom-punch','camera-transitions','dolly-zoom'].includes(e.id))continue;const localWords=(e.params?.syncWords||e.syncWords)?(job.captions||[]).filter(word=>word.startMs>=e.start*1000&&word.startMs<(e.start+e.duration)*1000).map(word=>({...word,startMs:word.startMs-e.start*1000})):undefined;drawEffect(c,e.id,time-e.start,{...e.params,...e,duration:e.duration,media,wordTimes:e.wordTimes||e.params?.wordTimes||localWords,orbitPass:e.id==='orbit-ring'?'rear':undefined},b);}
 const transformedSubject=(job.effects||[]).some(e=>{
   if(time<e.start||time>=e.start+e.duration)return false;
   return ['blade-slice','banknote','paper-tear','room-doors','code-body'].includes(e.id)||(e.id==='double-exposure'&&media.foreground)||e.foregroundOnTop===false||e.params?.foregroundOnTop===false;
 });
 if(media.foreground&&!transformedSubject){c.save();if(motion){const subject=camera.id==='dolly-zoom'?{...motion,zoom:motion.subjectZoom}:motion;applyCamera(c,subject);}drawOwned(c,media.foreground,0,0,720,1280);c.restore();}
 for(const e of job.effects||[])if(e.id==='orbit-ring'&&time>=e.start&&time<e.start+e.duration)drawEffect(c,e.id,time-e.start,{...e.params,...e,duration:e.duration,orbitPass:'front'},b);
 if(!media.video&&!job.noBrand){line(c,45,75,91,75,b.accent,4);text(c,(b.name||'Studio Linea').toUpperCase(),110,75,18,b.accent);text(c,'REEL KIT / INDEPENDENT MOTION SYSTEM',45,1210,16,b.accent);}
 drawCaptions(c,job.captions||[],time,b);
 c.restore();
}
