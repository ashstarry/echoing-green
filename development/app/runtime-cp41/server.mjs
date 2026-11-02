import http from 'node:http';
import {execFile} from 'node:child_process';
import {available,decide,MODEL} from './decision-api.mjs';
import {readFile,stat} from 'node:fs/promises';
import {resolve,dirname,extname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=dirname(fileURLToPath(import.meta.url));
const mime={'.wav':'audio/wav','.html':'text/html; charset=utf-8','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json','.wasm':'application/wasm','.glb':'model/gltf-binary','.jpg':'image/jpeg','.jpeg':'image/jpeg','.txt':'text/plain; charset=utf-8','.csv':'text/csv; charset=utf-8','.png':'image/png','.css':'text/css','.svg':'image/svg+xml'};
export async function createServer({port=Number(process.env.PORT||4240)}={}){
 const server=http.createServer(async(req,res)=>{
  try{
   const url=new URL(req.url,'http://127.0.0.1');
   if(url.pathname==='/api/health'){res.setHeader('Content-Type','application/json');res.end(JSON.stringify({ok:true,application:'borrowed-wind-town',checkpoint:41,decision_model:MODEL,semantic:await available()}));return;}
   if(url.pathname==='/api/decision'&&req.method==='POST'){
    const host=req.headers.host,origin=req.headers.origin;
    if(!/^127\.0\.0\.1:\d+$/.test(host||'')||origin&&origin!==`http://${host}`){res.writeHead(403);res.end();return;}
    let body='';try{for await(const chunk of req){body+=chunk;if(Buffer.byteLength(body)>12000)throw Error('输入太长');}const input=JSON.parse(body);const result=await decide(input.poem,input.state);res.writeHead(200,{'Content-Type':'application/json'});res.end(JSON.stringify(result));}catch(e){res.writeHead(400,{'Content-Type':'application/json'});res.end(JSON.stringify({error:String(e.message).replace(/sk-or-[A-Za-z0-9_-]+/g,'[REDACTED]')}));}return;
   }
   if(req.method!=='GET'&&req.method!=='HEAD'){res.writeHead(405);res.end();return;}
   let base,rel;
   if(url.pathname.startsWith('/vendor/three/')){base=resolve(root,'node_modules/three');rel=url.pathname.slice(14);}
   else if(url.pathname.startsWith('/src/')){base=resolve(root,'src');rel=url.pathname.slice(5);}
   else if(url.pathname.startsWith('/assets/')){base=resolve(root,'public/assets');rel=url.pathname.slice(8);}
   else if(url.pathname==='/'||url.pathname==='/index.html'){base=root;rel='index.html';}
   else{res.writeHead(404);res.end();return;}
   const file=resolve(base,decodeURIComponent(rel));if(!file.startsWith(base+'/')){res.writeHead(403);res.end();return;}
   const data=await readFile(file);res.writeHead(200,{'Content-Type':mime[extname(file)]||'application/octet-stream','Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'});res.end(req.method==='HEAD'?undefined:data);
  }catch{res.writeHead(404);res.end('Not found');}
 });
 await new Promise((ok,fail)=>{server.once('error',fail);server.listen(port,'127.0.0.1',ok)});return server;
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const port=Number(process.env.PORT||4240),url=`http://127.0.0.1:${port}`;
 try{await createServer({port});console.log(`言外已准备好：${url}\n关闭此窗口会停止本地服务，小镇存档仍保留在浏览器里。`);}
 catch(e){if(e.code!=='EADDRINUSE')throw e;const h=await fetch(url+'/api/health').then(r=>r.json()).catch(()=>null);if(h?.application!=='borrowed-wind-town'||h?.checkpoint!==38)throw e;console.log(`言外已经在运行：${url}`);}
 if(process.argv.includes('--open'))execFile('/usr/bin/open',[url]);
}
