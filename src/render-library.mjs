import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {chromium} from 'playwright';
import {renderJob} from './render.mjs';
import {createServer} from './server.mjs';
const catalog=JSON.parse(await readFile(new URL('./catalog.json',import.meta.url)));
const brand=JSON.parse(await readFile(new URL('../brands/studio-linea.json',import.meta.url)));
const out=process.argv[2]||'public/renders';await mkdir(out,{recursive:true});
const browser=await chromium.launch(),server=await createServer(0);let results=[];
try{for(const e of catalog){const job={width:360,height:640,fps:24,duration:2.4,brand,effects:[{id:e.id,start:0,duration:2.4,...e.parameters}]};const result=await renderJob(job,`${out}/${e.id}.mp4`,{browser,server});results.push({id:e.id,...result});}await writeFile(`${out}/render-report.json`,JSON.stringify(results,null,2));}finally{await browser.close();await new Promise(r=>server.close(r));}
