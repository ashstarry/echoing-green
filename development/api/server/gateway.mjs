import {makeRequest,parsePlan,MODEL} from './decision-core.mjs';
const buckets=new Map();let concurrent=0;
const MAX_BODY=16_384,WINDOW=60_000,LIMIT=12,MAX_CONCURRENT=6;
const fail=(error,status)=>({error,status});
function allowedOrigin(request,env){const origin=request.headers.get('origin');return [env.ALLOWED_ORIGIN||'https://ashstarry.github.io','https://koyoi.fun','https://www.koyoi.fun'].includes(origin);}
function cors(request,env){const origin=request.headers.get('origin');return allowedOrigin(request,env)?{'Access-Control-Allow-Origin':origin,'Vary':'Origin'}:{'Vary':'Origin'};}
function reply(request,env,data,status=200,extra={}){return Response.json(data,{status,headers:{...cors(request,env),'Cache-Control':'no-store','X-Content-Type-Options':'nosniff',...extra}});}
async function readBody(request){let size=0;const pieces=[],reader=request.body?.getReader();if(!reader)throw fail('Please enter a wish.',400);for(;;){const{done,value}=await reader.read();if(done)break;size+=value.length;if(size>MAX_BODY){await reader.cancel();throw fail('This wish is too long.',413);}pieces.push(value);}const bytes=new Uint8Array(size);let offset=0;for(const p of pieces){bytes.set(p,offset);offset+=p.length;}try{return JSON.parse(new TextDecoder().decode(bytes));}catch{throw fail('The request was not valid JSON.',400);}}
function reserve(ip,now){for(const[k,v]of buckets)if(now-v.start>=WINDOW)buckets.delete(k);let b=buckets.get(ip);if(!b){if(buckets.size>=10_000)return false;b={start:now,count:0};buckets.set(ip,b);}if(b.count>=LIMIT)return false;b.count++;return true;}
export async function handleApi(request,env={},upstreamFetch=fetch){
 const path=new URL(request.url).pathname;
 if(!['/api/health','/api/decision'].includes(path))return reply(request,env,{error:'Not found.'},404);
 if(request.method==='OPTIONS'){
  if(!allowedOrigin(request,env))return reply(request,env,{error:'Origin not allowed.'},403);
  return new Response(null,{status:204,headers:{...cors(request,env),'Access-Control-Allow-Methods':'GET, POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type','Access-Control-Max-Age':'600'}});
 }
 if(path==='/api/health')return request.method==='GET'?reply(request,env,{ok:true,application:'echoing-green',semantic:!!env.OPENROUTER_API_KEY,decision_model:MODEL}):reply(request,env,{error:'Method not allowed.'},405);
 if(request.method!=='POST')return reply(request,env,{error:'Method not allowed.'},405);
 if(!allowedOrigin(request,env))return reply(request,env,{error:'Origin not allowed.'},403);
 if(!/^application\/json(?:\s*;|$)/i.test(request.headers.get('content-type')||''))return reply(request,env,{error:'JSON is required.'},415);
 if(!env.OPENROUTER_API_KEY)return reply(request,env,{error:'The wish service is not ready yet.'},503);
 let counted=false,stage='input';
 try{
  if(Number(request.headers.get('content-length')||0)>MAX_BODY)throw fail('This wish is too long.',413);
  const input=await readBody(request);
  if(!input||typeof input!=='object'||Array.isArray(input)||typeof input.poem!=='string'||!input.poem.trim()||input.poem.length>600||input.state!=null&&(typeof input.state!=='object'||Array.isArray(input.state)))throw fail('Please enter a wish of 1–600 characters.',400);
  // Neither provider URLs, model IDs nor arbitrary questions can come from a visitor.
  stage='planning';const modelRequest=makeRequest(input.poem,input.state||{});
  const ip=request.headers.get('cf-connecting-ip')||'anonymous';
  if(concurrent>=MAX_CONCURRENT||!reserve(ip,Date.now()))throw fail('A few wishes are arriving together. Please try again shortly.',429);
  concurrent++;counted=true;const started=performance.now();
  stage='provider';const response=await upstreamFetch('https://openrouter.ai/api/alpha/decisions',{method:'POST',redirect:'manual',headers:{Authorization:`Bearer ${env.OPENROUTER_API_KEY}`,'Content-Type':'application/json'},body:JSON.stringify(modelRequest),signal:AbortSignal.timeout(20_000)});
  if(!response.ok)throw {...fail('Your wish could not reach the town. Please try again shortly.',502),providerStatus:response.status};
  stage='validation';const raw=await response.json();const plan=parsePlan(raw,modelRequest);
  return reply(request,env,{id:crypto.randomUUID(),model:MODEL,ms:Math.round(performance.now()-started),plan});
 }catch(error){console.warn('decision_failure',{stage,status:error?.status||502,providerStatus:error?.providerStatus||null,type:error instanceof Error?error.name:'ControlledError'});const status=[400,413,429,502,503].includes(error?.status)?error.status:502;return reply(request,env,{error:error?.status?error.error:'Your wish could not reach the town. Please try again shortly.'},status,status===429?{'Retry-After':'60'}:{});
 }finally{if(counted)concurrent--;}
}
