import {readFile,mkdir,writeFile,copyFile} from 'node:fs/promises';
import {decide} from '../../app/runtime-cp24/decision-api.mjs';
const split=process.argv[2]||'dev',name=process.argv[3]||'scope-v2';
const file=split==='final'?'outputs/runtime-checkpoint-24/final-fixtures.json':split==='acceptance'?'outputs/runtime-checkpoint-24/acceptance-fixtures.json':split==='confirmation'?'outputs/jev-cp23/confirmation-frozen.json':'outputs/jev-cp23/dataset-frozen.json';
const data=JSON.parse(await readFile(file,'utf8')).cases.filter(c=>c.split===split);
const folder='outputs/runtime-checkpoint-24/'+name+'-'+split;await mkdir(folder,{recursive:true});await copyFile('app/runtime-cp24/decision-api.mjs',folder+'/source.mjs');await copyFile(file,folder+'/fixtures.json');const results=[];
for(const c of data){try{const r=await decide(c.text,c.state),actual=Object.fromEntries(r.plan.items.map(x=>[x.field,x.action])),errors=[];
 for(const[k,v]of Object.entries(c.expected))if(k!=='intent_status'&&!(c.optional?.[k]||[v]).includes(actual[k]||'keep'))errors.push({target:k,expected:v,actual:actual[k]||'keep'});
 for(const[k,v]of Object.entries(actual))if(k!=='intent_status'&&!(c.optional?.[k]||[c.expected[k]||'keep']).includes(v))errors.push({target:k,expected:c.expected[k]||'keep',actual:v});
 const extras=Object.entries(actual).filter(([k,v])=>!(c.optional?.[k]||[c.expected[k]||'keep']).includes(v));
 const out={id:c.id,text:c.text,category:c.category,request_id:r.id,ms:r.ms,cost:r.cost,pass:!errors.length,extras,errors,plan:r.plan};results.push(out);console.log(JSON.stringify({id:c.id,pass:out.pass,ms:r.ms,errors,skipped:r.plan.skipped.filter(x=>x.reason!=='已经是这个状态').map(x=>[x.target,x.reason])}));
 }catch(e){results.push({id:c.id,error:e.message});console.log('ERROR '+c.id+' '+e.message);break;}}
await writeFile(folder+'/results.json',JSON.stringify(results,null,2));const summary={name,split,posts:results.length,pass:results.filter(r=>r.pass).length,extra_requests:results.filter(r=>r.extras?.length).length,cost:results.reduce((n,r)=>n+(r.cost||0),0),median_ms:results.map(r=>r.ms).sort((a,b)=>a-b)[Math.floor(results.length/2)]};await writeFile(folder+'/summary.json',JSON.stringify(summary,null,2));console.log(summary);
