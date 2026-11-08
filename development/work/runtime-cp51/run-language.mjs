import {readFileSync,writeFileSync,mkdirSync,statSync} from 'node:fs';
import {resolve} from 'node:path';
import {randomUUID,createHash} from 'node:crypto';
import {makeRequest,parsePlan,MODEL} from '../../app/echoing-green-api/server/decision-core.mjs';
import {setup,context,execute} from '../runtime-cp50/audit-utils.mjs';
const root=process.cwd(),out=resolve(root,'outputs/runtime-checkpoint-51');
const run=process.argv[2]||'baseline',split=process.argv[3]||'development,control';
const cases=[...JSON.parse(readFileSync(resolve(out,'frozen-cases.json'))).cases,...JSON.parse(readFileSync(resolve(out,'final-holdout.json'))).cases].filter(c=>split==='all'||split.split(',').includes(c.split)||split.split(',').includes(c.id));
const dir=resolve(out,'semantic-runs',run);mkdirSync(dir,{recursive:true});
const keyPath=resolve(root,'work/private/openrouter.key');if(statSync(keyPath).mode&0o077)throw Error('Private credential permissions are too broad');
const token=readFileSync(keyPath,'utf8').trim();
let rows=[];try{rows=JSON.parse(readFileSync(resolve(out,run+'.json')))}catch{}
for(const c of cases){
 if(rows.some(r=>r.id===c.id))continue;
 const {s,nav}=setup(62417,10),state=context(s),request=makeRequest(c.text,state),id=randomUUID();
 const record={id,case:c.id,run,created:new Date().toISOString(),request,requestHash:createHash('sha256').update(JSON.stringify(request)).digest('hex')};
 const file=resolve(dir,c.id+'-'+id+'.json');let row={...c,state,requestId:id};
 try{
  const start=performance.now();record.requestSent=true;writeFileSync(file,JSON.stringify(record,null,2));
  const response=await fetch('https://openrouter.ai/api/alpha/decisions',{method:'POST',redirect:'error',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify(request),signal:AbortSignal.timeout(25000)});
  record.status=response.status;record.rawResponse=await response.text();record.ms=Math.round(performance.now()-start);
  record.response=JSON.parse(record.rawResponse);if(!response.ok)throw Error('Provider status '+response.status);
  record.plan=parsePlan(record.response,request);row={...row,model:MODEL,ms:record.ms,cost:record.response.usage?.cost??null,rawIntent:record.response.answers?.intent_status,rawMoodIntent:record.response.answers?.mood_intent,rawAtmosphere:record.response.answers?.atmosphere,rawReply:record.response.answers?.gentle_reply,plan:record.plan};
  row.execution=record.plan.items.length?execute(s,nav,record.plan.items,c.text):null;
 }catch(error){record.error=String(error.message).replace(/sk-[A-Za-z0-9_-]+/g,'[REDACTED]');row.error=record.error;}
 writeFileSync(file,JSON.stringify(record,null,2));rows.push(row);writeFileSync(resolve(out,run+'.json'),JSON.stringify(rows,null,2));
 console.log(JSON.stringify({id:c.id,intent:row.rawIntent?.choice,moodIntent:row.rawMoodIntent?.choice,mood:row.rawAtmosphere?.choice,reply:row.rawReply?.choice,items:row.plan?.items.map(i=>[i.target,i.action]),source:row.plan?.resolution?.source,ms:row.ms,cost:row.cost,execution:row.execution&&{seconds:row.execution.seconds,progress:row.execution.progress,outcome:row.execution.outcome,moved:row.execution.actorsMoved?.length,scenes:row.execution.scenes,recipes:row.execution.recipes?.map(j=>[j.recipe,j.status])},error:row.error}));
}
