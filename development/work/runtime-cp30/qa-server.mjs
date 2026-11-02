import http from 'node:http';import {readFile,mkdir,appendFile,writeFile} from 'node:fs/promises';import {resolve} from 'node:path';
const round=Number(process.env.TOWN_CAPTURE_ROUND||1);if(!Number.isInteger(round)||round<1||round>9)throw Error('invalid round');const dir=resolve('work/runtime-cp30/capture-round'+round);await mkdir(dir,{recursive:true});let began=false,ended=false,first=true,meta=null,header=false;
http.createServer(async(req,res)=>{const send=(code,body,type='application/json')=>{res.writeHead(code,{'Content-Type':type,'Cache-Control':'no-store'});res.end(body);};try{
 const path=new URL(req.url,'http://127.0.0.1').pathname;
 if(path==='/audio'){send(200,'<!doctype html><meta charset="utf-8"><title>Borrowed Wind music preview</title><button id="run">生成掌机音乐试听</button><pre id="status">待生成</pre><audio id="preview" controls></audio><script type="module" src="/audio-preview.mjs"></script>','text/html');return;}
 if(path==='/audio-preview.mjs'){send(200,await readFile('work/runtime-cp30/audio-preview.mjs'),'text/javascript');return;}
 if(path==='/audio-result'&&req.method==='POST'){if(req.headers.origin!=='http://127.0.0.1:4251'){send(403,'{}');return;}const chunks=[];let size=0;for await(const chunk of req){chunks.push(chunk);size+=chunk.length;if(size>10000000)throw Error('large');}await writeFile('outputs/runtime-checkpoint-26/借风町-掌机音色试听.wav',Buffer.concat(chunks));send(200,'{}');return;}
 if(path==='/qa'){send(200,'<!doctype html><meta charset="utf-8"><title>CP30 local motion verification</title><style>body{background:#24232b;color:#fff;font:14px system-ui}button{padding:12px}iframe{width:1100px;height:760px;border:0;transform-origin:top left}pre{white-space:pre-wrap}</style><button id="run">开始实际模型运动检查</button><pre id="status">等待小镇加载</pre><iframe id="town" src="/"></iframe><script type="module" src="/qa-client.mjs"></script>','text/html; charset=utf-8');return;}
 if(path==='/perf'){send(200,'<!doctype html><meta charset="utf-8"><title>CP30 rendering check</title><button id="run">检查两档绘制开销</button><pre id="status">等待小镇</pre><iframe id="town" src="/" style="width:996px;height:874px;border:0"></iframe><script type="module" src="/qa-perf.mjs"></script>','text/html; charset=utf-8');return;}
 if(path==='/qa-perf.mjs'){send(200,await readFile('work/runtime-cp30/qa-perf.mjs'),'text/javascript');return;}
 if(path==='/qa-perf-result'&&req.method==='POST'){if(req.headers.origin!=='http://127.0.0.1:4251'){send(403,'{}');return;}let body='';for await(const chunk of req){body+=chunk;if(body.length>1000000)throw Error('too large');}JSON.parse(body);await writeFile('outputs/runtime-checkpoint-26/render-cost.json',body);send(200,'{}');return;}
 if(path==='/qa-client.mjs'){send(200,await readFile('work/runtime-cp30/qa-client.mjs'),'text/javascript');return;}
 if(path==='/qa-chunk'&&req.method==='POST'){
  if(req.headers.origin!=='http://127.0.0.1:4251'){send(403,'{}');return;}let body='';for await(const c of req){body+=c;if(body.length>24000000)throw Error('chunk too large');}const data=JSON.parse(body);
  if(data.type==='begin'){if(began)throw Error('capture already started');began=true;meta={meshes:data.value.meshes,geometries:{}};}
  else if(data.type==='geometry'){if(!began||header)throw Error('metadata phase required');Object.assign(meta.geometries,data.value);}
  else if(data.type==='metadata_done'){await writeFile(dir+'/browser-mesh-motion.json',JSON.stringify(meta).slice(0,-1)+',"frames":[');header=true;meta=null;}
  else if(data.type==='frames'){if(!header||ended)throw Error('capture not open');await appendFile(dir+'/browser-mesh-motion.json',(first?'':',')+data.value.map(x=>JSON.stringify(x)).join(','));first=false;}
  else if(data.type==='end'){if(!began||ended)throw Error('capture not open');await appendFile(dir+'/browser-mesh-motion.json',']}');await writeFile(dir+'/capture-summary.json',JSON.stringify(data.value,null,2));ended=true;}
  else throw Error('invalid chunk');send(200,'{"ok":true}');return;
 }
 if(path==='/api/health'){send(200,'{"ok":true,"semantic":false}');return;}
 if(req.method!=='GET'||!['/','/index.html'].includes(path)&&!['/src/','/assets/','/vendor/three/'].some(p=>path.startsWith(p))){send(404,'{}');return;}
 const response=await fetch('http://127.0.0.1:4250'+req.url);send(response.status,Buffer.from(await response.arrayBuffer()),response.headers.get('content-type'));
}catch(e){send(500,JSON.stringify({error:e.message}));}}).listen(4251,'127.0.0.1',()=>console.log('Local geometry QA http://127.0.0.1:4251/qa'));
