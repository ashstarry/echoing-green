import {writeFile,mkdir} from 'node:fs/promises';import {decide} from '../../app/runtime-cp17/decision-api.mjs';
const dir=new URL('../../outputs/runtime-checkpoint-17/',import.meta.url),state={weather:'clear',breeze:'gentle',music:'play',light:'warm',street:'wander',birds:'fly'};
const cases=[
 ['h1','把雪收起来，借树下几根琴弦替今晚说话。',{weather:['clear'],music:['play']}],
 ['h2','晚风打个盹，灯别熄，柔和些就好。',{breeze:['calm'],light:['soft']}],
 ['h3','想看火花像纸花一样开满夜空。',{festival:['fireworks']}],
 ['h4','送信人的路先歇一歇，红衣小孩继续沿街走。',{courier:['quiet'],child:['wander']}],
 ['h5','让街上的人各走各的，别再围成一团。',{street:['wander']}],
 ['h6','只让餐厅门前的红衣大人去听琴，别人照旧。',{shopper:['gather'],music:['keep','play']}],
 ['h7','天空别落雨雪，让纸鸟留在空中慢慢飞。',{weather:['clear'],birds:['fly']}],
 ['h8','让小船开到月亮上去。',{}]
].map(([id,poem,expected])=>({id,poem,expected,state:{...state,...(id==='h1'?{weather:'snow',music:'rest'}:id==='h7'?{weather:'rain'}:{})}}));
await writeFile(new URL('holdout-cases-frozen.json',dir),JSON.stringify({scope:'New holdout phrasings created after prompt tuning, fixed before their first execution. No subsequent tuning against this set. Small task-specific sample, not a universal benchmark. Unspecified domains must keep except explicitly allowed alternatives.',cases},null,2));const results=[];
for(const c of cases){try{const r=await decide(c.poem,c.state);const checks=Object.entries(r.decision).map(([k,v])=>({domain:k,actual:v,allowed:c.expected[k]||['keep'],pass:(c.expected[k]||['keep']).includes(v)}));results.push({case_id:c.id,...r,passed:checks.every(x=>x.pass),checks});console.log(c.id,results.at(-1).passed,r.ms);}catch(e){results.push({id:c.id,error:e.message,passed:false});console.log(c.id,e.message);}}
const times=results.filter(r=>r.ms).map(r=>r.ms).sort((a,b)=>a-b);await writeFile(new URL('holdout-evaluation.json',dir),JSON.stringify({cases:results.length,passed:results.filter(r=>r.passed).length,cost_usd:results.reduce((n,r)=>n+(r.cost||0),0),latency_ms:{min:times[0],median:times[Math.floor(times.length/2)],max:times.at(-1)},results},null,2));
