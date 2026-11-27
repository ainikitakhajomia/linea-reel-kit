// Execute on the isolated Linux runner: real MP4 exports, stream probes and decoded-frame sheets.
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {resolve,relative,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {renderJob} from './render.mjs';
import {createServer} from './server.mjs';
const root=fileURLToPath(new URL('../',import.meta.url));
const catalog=JSON.parse(await readFile(new URL('./catalog.json',import.meta.url)));
const brand=JSON.parse(await readFile(new URL('../brands/studio-linea.json',import.meta.url)));
const out=process.argv[2]||'public/renders';await mkdir(out,{recursive:true});
function run(command,args){const r=spawnSync(command,args,{encoding:'utf8',maxBuffer:1024*1024});if(r.error)throw r.error;if(r.status)throw new Error(`${command}: ${r.stderr}`);return r.stdout;}
const browser=await chromium.launch(),server=await createServer(0),results=[];
try{
 for(const e of catalog){
  const job={width:360,height:640,fps:24,duration:2.4,brand,effects:[{id:e.id,start:0,duration:2.4,...e.parameters}]};
  const file=`${out}/${e.id}.mp4`;
  const result=await renderJob(job,file,{browser,server});
  const probe=JSON.parse(run('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',file]));
  const video=probe.streams.find(s=>s.codec_type==='video');
  const rate=video?.avg_frame_rate?.split('/').map(Number)||[];
  if(!video||video.width!==job.width||video.height!==job.height||video.pix_fmt!=='yuv420p'||Number(video.nb_read_frames)!==result.frames||Math.abs(rate[0]/rate[1]-job.fps)>.01||Math.abs(Number(probe.format.duration)-result.duration)>.05)throw new Error(`Export probe mismatch: ${e.id}`);
  // These six frames are decoded from the delivered MP4, not redrawn from the recipe.
  run('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',file,'-vf','fps=5/2,scale=120:-2,tile=6x1','-frames:v','1',`${out}/${e.id}-contact.jpg`]);
  run('ffmpeg',['-hide_banner','-loglevel','error','-y','-ss','0.7','-i',file,'-frames:v','1',`${out}/${e.id}-poster.jpg`]);
  results.push({id:e.id,...result,status:'technical-export-verified; visual acceptance pending',sha256:createHash('sha256').update(await readFile(file)).digest('hex'),video,format:probe.format,contact:`${e.id}-contact.jpg`,poster:`${e.id}-poster.jpg`});
  // Persist progress so failed later effects do not erase earlier evidence.
  await writeFile(`${out}/render-report.json`,JSON.stringify(results,null,2)+'\n');
 }
 // Four readable sheets cover every exported effect, with IDs for a reviewer.
 const assetPath=relative(root,resolve(out)).split(sep).join('/');
 if(assetPath.startsWith('../'))throw new Error('Contact sheets require output inside the repository');
 const page=await browser.newPage({viewport:{width:1280,height:900},deviceScaleFactor:1});
 for(let offset=0;offset<results.length;offset+=18){
  const rows=results.slice(offset,offset+18);
  await page.setContent(`<html><head><style>body{margin:0;padding:28px;background:#f6f5f1;font:16px Arial;color:#27335f}h1{font-size:26px}main{display:grid;grid-template-columns:1fr 1fr;gap:18px}article{padding:12px;background:white;border:1px solid #dfe2eb;border-radius:10px}h2{font-size:17px;margin:0 0 8px}img{display:block;width:100%;height:auto}p{font-size:12px;margin:5px 0}</style></head><body><h1>Linea Reel Kit — decoded MP4 frames ${offset+1}–${offset+rows.length} / ${results.length}</h1><p>Independent synthetic recipes. Export integrity checked; visual/reference acceptance remains a review decision.</p><main>${rows.map(row=>`<article><h2>${row.id}</h2><img src="http://127.0.0.1:${server.address().port}/${assetPath}/${row.contact}"><p>${row.frames} frames · ${row.fps} fps · 360 × 640</p></article>`).join('')}</main></body></html>`);
  await page.evaluate(()=>Promise.all([...document.images].map(im=>im.decode())));
  await page.screenshot({path:`${out}/export-contact-${Math.floor(offset/18)+1}.jpg`,fullPage:true,type:'jpeg',quality:90});
 }
 await page.close();
}finally{await browser.close();await new Promise(r=>server.close(r));}
