import {chromium} from 'playwright';
import {mkdtemp,readFile,writeFile,mkdir,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve,dirname} from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {createServer} from './server.mjs';
const root=fileURLToPath(new URL('../',import.meta.url));
function run(command,args){const r=spawnSync(command,args,{stdio:'inherit'});if(r.error)throw r.error;if(r.status!==0)throw new Error(`${command} failed (${r.status})`);}
export function validateJob(job){
 if(!job||typeof job!=='object')throw new Error('Expected job object');
 for(const [key,fallback,max] of [['width',720,2160],['height',1280,3840],['fps',30,60]]){const n=job[key]??fallback;if(!Number.isInteger(n)||n<1||n>max)throw new Error(`Invalid ${key}`);job[key]=n;}
 if(job.width%2||job.height%2)throw new Error('Dimensions must be even for yuv420p');
 if(!Number.isFinite(job.duration)||job.duration<=0||job.duration>600)throw new Error('duration must be >0 and <=600 seconds');
 const paths=[job.video,job.walkthrough,job.previous,job.next,job.background,job.foregroundFrames,...(job.effects||[]).filter(e=>e.src).map(e=>e.src),...(job.effects||[]).flatMap(e=>e.mediaSources||e.params?.mediaSources||[])].filter(Boolean);
 for(const p of paths)if(typeof p!=='string'||p.includes('..')||p.startsWith('/')||p.includes('://')||p.includes('\\'))throw new Error('Media must be a relative path inside public/');
 for(const e of job.effects||[]){
   if(typeof e.id!=='string'||!Number.isFinite(e.start)||e.start<0||!Number.isFinite(e.duration)||e.duration<=0)throw new Error('Invalid effect timing');
   for(const source of [e,e.params||{}])for(const key of ['scale','offsetX','offsetY'])if(source[key]!==undefined){const value=source[key],low=key==='scale'?.1:-2000,high=key==='scale'?4:2000;if(!Number.isFinite(value)||value<low||value>high)throw new Error(`Invalid effect ${key}: expected ${low}..${high}`);}
 }
 return job;
}
export async function renderJob(input,out,{browser:sharedBrowser,server:sharedServer}={}){
 const job=validateJob(structuredClone(input));await mkdir(dirname(resolve(out)),{recursive:true});
 const frames=await mkdtemp(join(tmpdir(),'linea-render-'));const server=sharedServer||await createServer(0);let browser=sharedBrowser;
 try{browser ||=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:job.width,height:job.height}});
 await page.goto(`http://127.0.0.1:${server.address().port}/src/stage.html`);await page.waitForFunction(()=>window.ready);await page.evaluate(j=>window.setJob(j),job);
 const count=Math.ceil(job.duration*job.fps);for(let n=0;n<count;n++){const png=await page.evaluate(t=>window.frame(t),n/job.fps);await writeFile(join(frames,`${String(n).padStart(6,'0')}.png`),Buffer.from(png,'base64'));}
 await page.close();const args=['-hide_banner','-loglevel','error','-y','-framerate',String(job.fps),'-i',join(frames,'%06d.png')];
 if(job.video)args.push('-i',resolve(root,'public',job.video));
 args.push('-map','0:v:0');if(job.video)args.push('-map','1:a?');
 args.push('-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p');if(job.video)args.push('-c:a','aac','-b:a','160k');args.push('-t',String(count/job.fps),'-movflags','+faststart',resolve(out));run('ffmpeg',args);
 console.log(`Rendered ${out} (${count} frames)`);return {frames:count,fps:job.fps,duration:count/job.fps};
 }finally{await rm(frames,{recursive:true,force:true});if(!sharedBrowser&&browser)await browser.close();if(!sharedServer)await new Promise(r=>server.close(r));}
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const [props,out='out/edit.mp4']=process.argv.slice(2);if(!props)throw new Error('Usage: npm run render -- path/job.json out/edit.mp4');const data=JSON.parse(await readFile(props));await renderJob(data.job||data,out);
}
