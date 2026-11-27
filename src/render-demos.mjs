// Shared isolated browser, sequential exports keep memory and disk bounded.
import {readFile,writeFile,mkdir,rm} from 'node:fs/promises';
import {resolve} from 'node:path';
import {spawnSync} from 'node:child_process';
import {chromium} from 'playwright';
import {createServer} from './server.mjs';
import {renderJob} from './render.mjs';
const folder=process.argv[2]||'public/demos';
const demos=JSON.parse(await readFile(`${folder}/manifest.json`));
const browser=await chromium.launch(),server=await createServer(0);
const run=(args)=>{const result=spawnSync(args[0],args.slice(1),{stdio:'inherit'});if(result.error)throw result.error;if(result.status)throw new Error(`Failed: ${args[0]}`);};
const report=[];
try{
 for(const demo of demos){
  const file=resolve('public',demo.job),dir=resolve(file,'..');
  const {job}=JSON.parse(await readFile(file));
  await renderJob(job,`${dir}/silent-sfx.mp4`,{browser,server});
  run(['python3','scripts/audio.py','mix',`${dir}/silent-sfx.mp4`,'--sfx-job',file,'--out',`${dir}/final.mp4`]);
  run(['python3','scripts/validate-media.py',`${dir}/final.mp4`,'--out',`${dir}/qa.json`]);
  const qa=JSON.parse(await readFile(`${dir}/qa.json`));
  if(!qa.audio.present||qa.video.width!==job.width||qa.video.height!==job.height||Math.abs((qa.video.averageFPS||0)-job.fps)>.01||Math.abs(qa.durationSeconds-job.duration)>.12||Math.abs(qa.containerAudioMinusVideoStartMs||0)>100)throw new Error(`Export stream mismatch: ${demo.id}`);
  // Full export contact sheet for visual inspection, rather than gallery-only evidence.
  run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',`${dir}/final.mp4`,'-vf',`fps=1/${job.duration/6},scale=180:-2,tile=6x1`,'-frames:v','1',`${dir}/contact.jpg`]);
  run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',String(Math.min(1,job.duration/3)),'-i',`${dir}/final.mp4`,'-frames:v','1',`${dir}/poster.jpg`]);
  await rm(`${dir}/silent-sfx.mp4`);
  report.push({id:demo.id,output:demo.video,...qa});
 }
 await mkdir('out',{recursive:true});
 await writeFile('out/demonstration-report.json',JSON.stringify(report,null,2)+'\n');
}finally{await browser.close();await new Promise(r=>server.close(r));}
