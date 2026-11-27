import http from 'node:http';
import {readFile, stat} from 'node:fs/promises';
import {resolve, sep, extname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root = fileURLToPath(new URL('../', import.meta.url));
const mime={'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.json':'application/json','.css':'text/css','.png':'image/png','.jpg':'image/jpeg','.mp4':'video/mp4','.svg':'image/svg+xml','.wav':'audio/wav'};
export function createServer(port=4173) {
  const server=http.createServer(async(req,res)=>{
    try {
      let pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
      if(pathname==='/') pathname='/src/review.html';
      const file=resolve(root, '.'+pathname);
      const relative=file.slice(root.length);
      if(!file.startsWith(root) || relative.split(sep).some(x=>x.startsWith('.')) || /(?:^|\/)(node_modules|\.git)(?:\/|$)/.test(pathname)) {res.writeHead(403).end();return;}
      const info=await stat(file);
      if(!info.isFile()) {res.writeHead(404).end();return;}
      const data=await readFile(file);
      const headers={'Content-Type':mime[extname(file)]||'application/octet-stream','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'};
      if(req.headers.range){
        const match=/^bytes=(\d+)-(\d*)$/.exec(req.headers.range);
        if(!match){res.writeHead(416).end();return;}
        const start=Number(match[1]),end=match[2]?Math.min(Number(match[2]),data.length-1):data.length-1;
        if(start>end||start>=data.length){res.writeHead(416).end();return;}
        res.writeHead(206,{...headers,'Content-Range':`bytes ${start}-${end}/${data.length}`,'Content-Length':end-start+1,'Accept-Ranges':'bytes'}).end(data.subarray(start,end+1));
      } else res.writeHead(200,{...headers,'Content-Length':data.length,'Accept-Ranges':'bytes'}).end(data);
    }catch {res.writeHead(404).end('Not found');}
  });
  return new Promise((resolve,reject)=>{server.once('error',reject);server.listen(port,'127.0.0.1',()=>resolve(server));});
}
if(process.argv[1]===fileURLToPath(import.meta.url)){const s=await createServer(Number(process.env.PORT||4173));console.log(`Reel Kit review: http://127.0.0.1:${s.address().port}`);}
