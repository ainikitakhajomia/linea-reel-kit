import {drawFrame} from './effects.mjs';
import {loadMedia,updateMedia} from './media.mjs';
const $=id=>document.getElementById(id);
async function json(url){const response=await fetch(url);if(!response.ok)throw new Error(`${url}: HTTP ${response.status}`);return response.json();}
const [catalog,brand]=await Promise.all([json(new URL('./catalog.json',import.meta.url)),json('/brands/studio-linea.json')]);
const categories=[...new Set(catalog.map(e=>e.category))].sort();
for(const name of categories){const o=document.createElement('option');o.value=name;o.textContent=name.replaceAll('-',' ');$('category').append(o);}
let saved=new Set();try{saved=new Set(JSON.parse(localStorage.getItem('linea-saved-effects')||'[]'));}catch{}
let views=[],paused=matchMedia('(prefers-reduced-motion: reduce)').matches,active=null,start=performance.now(),detailPaused=false,detailTime=0,job=null,jobtime=0,playing=false,jobmedia={},customParams={},onlySaved=false,currentPane='librarypane';
$('pause').textContent=paused?'Speel previews':'Pauzeer previews';$('pause').setAttribute('aria-pressed',String(paused));
const observer=new IntersectionObserver(entries=>entries.forEach(e=>e.target._visible=e.isIntersecting));
function persist(){try{localStorage.setItem('linea-saved-effects',JSON.stringify([...saved]));}catch{}}
function populate(){
 $('loadstatus').classList.add('hidden');observer.disconnect();views=[];$('grid').replaceChildren();
 const query=$('search').value.trim().toLowerCase(),category=$('category').value;
 let filtered=catalog.filter(e=>(!category||e.category===category)&&(!$('maturity').value||e.maturity===$('maturity').value)&&(!onlySaved||saved.has(e.id))&&`${e.name} ${e.id} ${e.category} ${e.referenceAnalysis}`.toLowerCase().includes(query));
 if($('sort').value==='name')filtered.sort((a,b)=>a.name.localeCompare(b.name));
 for(const effect of filtered){
  const el=document.createElement('article');el.className='card';el.tabIndex=0;el.setAttribute('role','button');el.setAttribute('aria-label',effect.name);el.dataset.effect=effect.id;
  const canvas=document.createElement('canvas');canvas.width=288;canvas.height=512;canvas.setAttribute('aria-hidden','true');
  const number=document.createElement('span');number.className='number';number.textContent=String(catalog.indexOf(effect)+1).padStart(2,'0');
  const save=document.createElement('button');save.className='save';save.textContent=saved.has(effect.id)?'♥':'♡';save.setAttribute('aria-label',`${effect.name} bewaren`);save.setAttribute('aria-pressed',String(saved.has(effect.id)));save.onclick=event=>{event.stopPropagation();saved.has(effect.id)?saved.delete(effect.id):saved.add(effect.id);persist();if(onlySaved)populate();else{save.textContent=saved.has(effect.id)?'♥':'♡';save.setAttribute('aria-pressed',String(saved.has(effect.id)));}};save.onkeydown=event=>event.stopPropagation();
  const meta=document.createElement('div');meta.className='meta';const title=document.createElement('b');title.textContent=effect.name;
  const foot=document.createElement('div');foot.className='metafoot';const tag=document.createElement('span');tag.className='tag';tag.textContent=effect.maturityLabel||effect.category.replaceAll('-',' ');tag.title=effect.quality;const duration=document.createElement('span');duration.className='duration';duration.textContent=`${effect.duration.toFixed(1)}s ↗`;foot.append(tag,duration);meta.append(title,foot);el.append(canvas,number,save,meta);
  el.onclick=()=>inspect(effect);el.onkeydown=event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();inspect(effect);}};
  $('grid').append(el);const ctx=canvas.getContext('2d');drawFrame(ctx,preview(effect),.85);observer.observe(el);views.push({el,ctx,effect});
 }
 $('resultcount').textContent=`${views.length} van ${catalog.length} effecten${onlySaved?' · bewaard':''}`;$('empty').classList.toggle('hidden',views.length>0);
}
function preview(effect,width=288,height=512,params=effect.parameters){return {width,height,brand:{...brand,...(active&&effect.id===active.id?{accent:$('daccent').value}:{})},duration:Number(params.duration)||effect.duration,effects:[{...params,id:effect.id,start:0,duration:Number(params.duration)||effect.duration}]};}
function activeJob(){return preview(active,720,1280,{...customParams,text:$('dtext').value,duration:Number($('dduration').value)||active.duration});}
function inspect(effect){
 active=effect;customParams={...effect.parameters};$('daccent').value=brand.accent;start=performance.now();detailTime=.01;detailPaused=false;$('detailpause').textContent='Pauze';$('detailpause').setAttribute('aria-pressed','false');
 $('dname').textContent=effect.name;$('dcategory').textContent=`${effect.category} / ${effect.maturityLabel||'zelfstandig basisrecept'}`;$('dquality').textContent=effect.quality;$('drequirements').textContent='Benodigd: '+(effect.inputRequirements||['Eigen bronmateriaal voor de uiteindelijke edit.']).join(' · ');
 $('dtext').value=effect.parameters.text||'';$('dduration').value=effect.duration;$('detailscrub').max=effect.duration;$('dref').href=effect.reference;$('dorigin').textContent=`${effect.implementation} — ${effect.origin} ${effect.license}`;$('dparams').value=JSON.stringify(effect.parameters,null,2);$('dprompt').textContent=effect.prompt;$('paramstatus').textContent='';$('dexport').classList.toggle('hidden',!window.REEL_STATIC_EXPORTS);$('dexport').href='/public/renders/'+effect.id+'.mp4';$('dialog').showModal();
}
function pane(id){currentPane=id;for(const name of ['librarypane','jobpane','demopane'])$(name).classList.toggle('hidden',name!==id);for(const [button,name] of [['librarybutton','librarypane'],['jobbutton','jobpane'],['demobutton','demopane']])$(button).classList.toggle('selected',name===id);if(id!=='jobpane'){playing=false;for(const v of Object.values(jobmedia))if(v instanceof HTMLVideoElement)v.pause();$('playjob').textContent='Afspelen';}if(id!=='demopane')document.querySelectorAll('#demogrid video').forEach(v=>v.pause());}
$('clearfilters').onclick=()=>{$('search').value='';$('category').value='';$('maturity').value='';onlySaved=false;$('favoritefilter').setAttribute('aria-pressed','false');populate();};
$('favoritefilter').onclick=()=>{onlySaved=!onlySaved;$('favoritefilter').setAttribute('aria-pressed',String(onlySaved));populate();};
for(const [id,event] of [['search','input'],['category','change'],['maturity','change'],['sort','change']])$(id).addEventListener(event,populate);
$('applyparams').onclick=()=>{try{const data=JSON.parse($('dparams').value);if(!data||typeof data!=='object'||Array.isArray(data))throw new Error('Gebruik een JSON-object met effectparameters.');if(data.duration!==undefined&&(!Number.isFinite(data.duration)||data.duration<.3||data.duration>10))throw new Error('Duur moet tussen 0,3 en 10 seconden liggen.');customParams=data;if(data.text!==undefined)$('dtext').value=String(data.text);if(data.duration!==undefined)$('dduration').value=data.duration;start=performance.now();detailTime=0;$('paramstatus').textContent='Parameters toegepast.';}catch(error){$('paramstatus').textContent=error.message;}};
$('dduration').onchange=()=>{const value=Number($('dduration').value);$('dduration').value=Math.max(.3,Math.min(10,Number.isFinite(value)?value:2.4));start=performance.now();detailTime=0;};
$('close').onclick=()=>$('dialog').close();$('dialog').addEventListener('close',()=>active=null);
$('replay').onclick=()=>{start=performance.now();detailTime=0;};
$('detailpause').onclick=()=>{detailPaused=!detailPaused;$('detailpause').textContent=detailPaused?'Afspelen':'Pauze';$('detailpause').setAttribute('aria-pressed',String(detailPaused));};
$('detailscrub').oninput=()=>{detailTime=Number($('detailscrub').value);detailPaused=true;$('detailpause').textContent='Afspelen';$('detailpause').setAttribute('aria-pressed','true');};
$('pause').onclick=()=>{paused=!paused;$('pause').textContent=paused?'Speel previews':'Pauzeer previews';$('pause').setAttribute('aria-pressed',String(paused));};
$('copyjob').onclick=async()=>{try{await navigator.clipboard.writeText(JSON.stringify(activeJob(),null,2));$('paramstatus').textContent='Job gekopieerd. Gebruik dezelfde job voor preview en export.';}catch{$('paramstatus').textContent='Kopiëren is hier niet beschikbaar. Gebruik Download job.';}};
$('downloadjob').onclick=()=>{const href=URL.createObjectURL(new Blob([JSON.stringify(activeJob(),null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=href;link.download=`${active.id}.job.json`;link.click();setTimeout(()=>URL.revokeObjectURL(href),1000);$('paramstatus').textContent='Job gedownload; render met npm run render -- bestand.job.json out/effect.mp4';};
$('librarybutton').onclick=$('back').onclick=()=>pane('librarypane');$('jobbutton').onclick=()=>pane('jobpane');
let demosLoaded=false;
$('demobutton').onclick=async()=>{pane('demopane');if(demosLoaded)return;try{const demos=await json('/public/demos/manifest.json');for(const demo of demos){const card=document.createElement('article');card.className='democard';const video=document.createElement('video');video.controls=true;video.preload='none';video.playsInline=true;video.src='/public/'+demo.video;video.poster='/public/'+demo.video.replace('final.mp4','poster.jpg');const title=document.createElement('h3');title.textContent=demo.title;const note=document.createElement('p');note.textContent=`Synthetische demonstratie · ${demo.duration.toFixed(1)} sec · Studio Linea`;const download=document.createElement('a');download.href=video.src;download.download=demo.id+'.mp4';download.textContent='Download MP4 ↗';card.append(video,title,note,download);$('demogrid').append(card);}demosLoaded=true;$('demostatus').textContent='Eigen synthetische presentator, lokale spraak en getekende conceptinterface. Geen opname van het echte product.';}catch{$('demostatus').textContent='De voorbeeldfilms zijn nog niet aanwezig op deze server. Download het render-artifact bij de groene GitHub Actions-run en pak public/demos uit naast deze bibliotheek.';}};
let mediaGeneration=0;
$('jobfile').onchange=async()=>{const generation=++mediaGeneration;playing=false;for(const value of Object.values(jobmedia))if(value instanceof HTMLVideoElement)value.pause();try{const file=$('jobfile').files[0];if(!file)return;const data=JSON.parse(await file.text()),candidate=data.job||data;if(!Number.isFinite(candidate.duration)||candidate.duration<=0||!Number.isInteger(candidate.width)||candidate.width<2||candidate.width>2160||!Number.isInteger(candidate.height)||candidate.height<2||candidate.height>3840)throw new Error('Ongeldige duur of beeldafmetingen in job.');const loaded=await loadMedia(candidate);if(generation!==mediaGeneration)return;job=candidate;jobmedia=loaded;if(jobmedia.video)jobmedia.video.muted=false;$('jobcanvas').width=job.width;$('jobcanvas').height=job.height;$('scrub').max=job.duration;jobtime=0;$('playjob').textContent='Afspelen';$('jobstatus').textContent=`${job.title||'Jouw edit'} · ${job.duration.toFixed(2)} sec`;}catch(error){$('jobstatus').textContent=error.message;job=null;}};
$('playjob').onclick=async()=>{if(!job){$('jobstatus').textContent='Laad eerst een job.json-bestand.';return;}playing=!playing;try{for(const v of Object.values(jobmedia).filter(v=>v instanceof HTMLVideoElement))if(playing){v.currentTime=Math.min(jobtime,Math.max(0,v.duration-.035));await v.play();}else v.pause();$('playjob').textContent=playing?'Pauze':'Afspelen';}catch(error){playing=false;$('jobstatus').textContent=error.message;}};
$('scrub').oninput=()=>{jobtime=Number($('scrub').value);for(const v of Object.values(jobmedia).filter(v=>v instanceof HTMLVideoElement))v.currentTime=Math.min(jobtime,Math.max(0,v.duration-.035));};
document.addEventListener('keydown',event=>{if(event.key==='/'&&!$('dialog').open&&!['INPUT','TEXTAREA','SELECT'].includes(event.target.tagName)){event.preventDefault();pane('librarypane');$('search').focus();}});
let previewBusy=false,prev=performance.now(),lastDraw=0;
function loop(now){
 const dt=Math.min(.1,(now-prev)/1000);prev=now;
 if(active&&!detailPaused&&!document.hidden)detailTime=(detailTime+dt)%(Number($('dduration').value)||active.duration);
 if(!document.hidden&&now-lastDraw>1000/24){lastDraw=now;const time=(now-start)/1000;
  if(!paused&&currentPane==='librarypane'&&!active)for(const {el,ctx,effect}of views)if(el._visible)drawFrame(ctx,preview(effect),time%effect.duration);
  if(active){const model=activeJob(),duration=model.duration;detailTime=Math.min(detailTime,duration);$('detailscrub').max=duration;$('detailscrub').value=detailTime;$('detailtime').textContent=`${detailTime.toFixed(2)} s`;drawFrame($('detail').getContext('2d'),model,detailTime);}
 }
 if(job&&currentPane==='jobpane'){if(playing){jobtime=jobmedia.video?jobmedia.video.currentTime:jobtime+dt;if(jobtime>=job.duration-.04){playing=false;for(const v of Object.values(jobmedia))if(v instanceof HTMLVideoElement)v.pause();$('playjob').textContent='Afspelen';}}$('scrub').value=jobtime;if(!previewBusy){previewBusy=true;updateMedia(jobmedia,job,jobtime,{playing}).then(()=>drawFrame($('jobcanvas').getContext('2d'),job,jobtime,jobmedia)).catch(error=>{$('jobstatus').textContent=error.message;playing=false;}).finally(()=>previewBusy=false);}}
 requestAnimationFrame(loop);
}
populate();requestAnimationFrame(loop);
