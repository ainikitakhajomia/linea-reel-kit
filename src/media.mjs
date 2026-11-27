// Shared loader for preview and export; owned local assets only.
export function assetUrl(path){if(typeof path!=='string'||path.startsWith('/')||path.includes('..')||path.includes('://')||path.includes('\\'))throw new Error('Media must be a relative path inside public/');return '/public/'+path;}
export async function loadVideo(path){
 const v=document.createElement('video');v.muted=true;v.preload='auto';v.playsInline=true;
 await new Promise((ok,bad)=>{const timer=setTimeout(()=>bad(new Error('Video load timeout: '+path)),20000);v.onloadeddata=()=>{clearTimeout(timer);ok();};v.onerror=()=>{clearTimeout(timer);bad(new Error('Cannot load video: '+path));};v.src=assetUrl(path);});return v;
}
async function loadImage(path){const im=new Image();im.src=assetUrl(path);await im.decode();return im;}
const imagePath=path=>/\.(png|jpe?g|webp)$/i.test(path);
export async function loadMedia(job){
 const media={};for(const key of ['video','walkthrough','previous','next','background'])if(job[key])media[key]=imagePath(job[key])?await loadImage(job[key]):await loadVideo(job[key]);
 for(const e of job.effects||[])if(e.id==='broll'&&e.src)media[e.src]=e.mediaType==='image'?await loadImage(e.src):await loadVideo(e.src);
 for(const e of job.effects||[])for(const path of e.mediaSources||e.params?.mediaSources||[])if(!media[path])media[path]=imagePath(path)?await loadImage(path):await loadVideo(path);
 return media;
}
export async function seekVideo(v,time){
 const target=Math.min(Math.max(0,time),Math.max(0,v.duration-.035));if(Math.abs(v.currentTime-target)<.0001&&v.readyState>=2)return;
 await new Promise((ok,bad)=>{const cleanup=()=>{clearTimeout(timer);v.removeEventListener('seeked',ready);v.removeEventListener('error',failed);};const ready=()=>{cleanup();ok();};const failed=()=>{cleanup();bad(new Error('Video seek failed'));};const timer=setTimeout(()=>{cleanup();bad(new Error('Video seek timeout'));},10000);v.addEventListener('seeked',ready,{once:true});v.addEventListener('error',failed,{once:true});v.currentTime=target;});
}
export async function updateMedia(media,job,time,{playing=false}={}){
 for(const [key,v]of Object.entries(media))if(v instanceof HTMLVideoElement){const e=job.effects?.find(x=>x.src===key);if(!playing||key!=='video')await seekVideo(v,e?Math.max(0,time-e.start):time);}
 if(job.foregroundFrames){const safeTime=Math.min(Math.max(0,time),Math.max(0,job.duration-1/(job.fps||30))),path=job.foregroundFrames.replace('%06d',String(Math.floor(safeTime*(job.fps||30)+1e-6)).padStart(6,'0'));if(media._foregroundPath!==path){media.foreground=await loadImage(path);media._foregroundPath=path;}}
 return media;
}
