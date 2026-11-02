import{decide}from'../../app/runtime-cp25/decision-api.mjs';import{mkdir,writeFile,copyFile}from'node:fs/promises';
const cases=[
 ['flower-snow-dawn','让大家找好位置，一起等一场花火。',{weather:'snow',day_phase:'dawn',festival:'quiet',festival_auto:true},{festival:'fireworks'}],
 ['flower-night','一起等一场花火。',{day_phase:'night',festival:'quiet'},{festival:'fireworks'}],
 ['flower-rain','雨停之后再看花火吧。',{weather:'rain',festival:'quiet'},{festival:'fireworks'}],
 ['flower-no','不要放烟花，大家各自忙自己的。',{festival:'quiet',festival_auto:true},{festival:'quiet'}],
 ['flower-past','昨晚的烟花很好看。',{},{}],
 ['flower-market','晚市热闹一点，有人逛摊，也有人聊聊天。',{}, {'occasion':'market'}],
 ['repeat-market','晚市再热闹一点。',{occasion:'market'},{occasion:'market'}],
 ['dawn','清晨第一缕光落到小镇。',{day_phase:'night'},{day_phase:'dawn'}],
 ['night','夜幕降临，灯火温暖一些。',{day_phase:'dawn',light:'warm'},{day_phase:'night',light:'warm'}],
 ['reader','只让露台上的读者合上书。',{}, {'resident.quiet_reader':'close_book'}]
].map(([id,text,state,expected])=>({id,text,state,expected}));
const out='outputs/runtime-checkpoint-25/semantic-round2';await mkdir(out,{recursive:true});await writeFile(out+'/semantic-fixtures.json',JSON.stringify(cases,null,2));await copyFile('app/runtime-cp25/decision-api.mjs',out+'/semantic-source.mjs');const rows=[];
for(const c of cases){const r=await decide(c.text,c.state);const actual=Object.fromEntries(r.plan.items.map(i=>[i.field,i.action]));const missing=Object.entries(c.expected).filter(([k,v])=>actual[k]!==v);const extras=Object.entries(actual).filter(([k])=>!(k in c.expected));rows.push({...c,...r,case_id:c.id,actual,missing,extras,pass:!missing.length&&!extras.length});console.log(JSON.stringify({id:c.id,pass:rows.at(-1).pass,actual,skipped:r.plan.skipped}));}
await writeFile(out+'/semantic-regression.json',JSON.stringify(rows,null,2));
