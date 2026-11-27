// Publish only public source code and explicitly generated, synthetic review assets.
import {readFile,writeFile,mkdir,copyFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
const destination=resolve(process.argv[2]||'out/site');
const prefix=process.argv[3]||'';
if(prefix&&!/^\/[a-zA-Z0-9_-]+$/.test(prefix))throw new Error('Base path must be empty or one URL-safe segment');
let exportsReport;try{exportsReport=JSON.parse(await readFile('public/renders/render-report.json','utf8'));}catch(error){if(error.code!=='ENOENT')throw error;}
const sourceFiles=['src/review.html','src/review.css','src/review.mjs','src/effects.mjs','src/media.mjs','src/stage.html','src/catalog.json','brands/studio-linea.json','vendor/motion-video-styles/timing.mjs','vendor/motion-video-styles/LICENSE','LICENSE'];
async function emit(file,text){const target=resolve(destination,file);await mkdir(dirname(target),{recursive:true});await writeFile(target,text);}
for(const file of sourceFiles){let content=await readFile(file,'utf8');if(/\.(html|mjs|css)$/.test(file)){for(const root of ['src','public','brands'])content=content.replaceAll(`/${root}/`,`${prefix}/${root}/`);if(file==='src/review.html'){content=content.replace('href="/"',`href="${prefix}/"`);if(exportsReport)content=content.replace('<script>function loadError',`<script>window.REEL_STATIC_EXPORTS=${exportsReport.length};</script><script>function loadError`);}}await emit(file,content);if(file==='src/review.html')await emit('index.html',content);}
await emit('.nojekyll','');
if(exportsReport){
 const catalog=JSON.parse(await readFile('src/catalog.json','utf8')),ids=new Set(catalog.map(e=>e.id));
 if(exportsReport.length!==67||new Set(exportsReport.map(e=>e.id)).size!==67)throw new Error('Expected 67 unique technical exports');
 const clean=[];for(const entry of exportsReport){if(!ids.has(entry.id)||!/^[-a-z0-9]+$/.test(entry.id))throw new Error('Unknown export ID');for(const suffix of ['.mp4','-poster.jpg']){const file=`public/renders/${entry.id}${suffix}`;await mkdir(dirname(resolve(destination,file)),{recursive:true});await copyFile(file,resolve(destination,file));}clean.push({id:entry.id,frames:entry.frames,fps:entry.fps,duration:entry.duration,sha256:entry.sha256,status:entry.status});}await emit('public/renders/render-report.json',JSON.stringify(clean,null,2)+'\n');
}
let manifest;try{manifest=JSON.parse(await readFile('public/demos/manifest.json','utf8'));}catch(error){if(error.code!=='ENOENT')throw error;}
if(manifest){
 const safe=[];
 for(const demo of manifest){if(!/^\d{2}-[a-z0-9-]+$/.test(demo.id)||demo.video!==`demos/${demo.id}/final.mp4`)throw new Error('Unexpected demo output path');
  const folder=`public/demos/${demo.id}`;const provenance=demo.provenance;
  if(!JSON.stringify(provenance).toLowerCase().includes('synthetic'))throw new Error('Only marked synthetic demonstration media may be automatically published');
  for(const name of ['final.mp4','poster.jpg']){const file=`${folder}/${name}`;await mkdir(dirname(resolve(destination,file)),{recursive:true});await copyFile(file,resolve(destination,file));}
  safe.push({id:demo.id,title:demo.title,video:demo.video,duration:demo.duration,provenance:'Original synthetic demonstration; see source repository. No client media.'});
 }
 await emit('public/demos/manifest.json',JSON.stringify(safe,null,2)+'\n');
}
await emit('build.json',JSON.stringify({sourceCommit:process.env.SOURCE_COMMIT||null,syntheticDemos:manifest?.length||0,basePath:prefix},null,2)+'\n');
console.log(`Static review assembled in ${destination}; ${manifest?.length||0} synthetic films. No arbitrary public/ files copied.`);
