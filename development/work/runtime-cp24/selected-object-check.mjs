import {decide} from '../../app/runtime-cp24/decision-api.mjs';import {writeFile} from 'node:fs/promises';
const cases=[
 ['这盏灯先熄下来。','light.street_lantern_05','dark'],
 ['把这本书合上。','book.terrace_reader_book','close_book'],
 ['端起这杯茶喝一口。','cup.upper_table_0','sip_tea'],
 ['看看这里的花叶长得怎样。','workstation.greenhouse_potting_table','inspect_leaf'],
 ['让这个风筝平稳一点，别改别的。','kite.plaza_kite','calm'],
 ['这只纸鸟舒展翅膀滑翔。','bird.paper_bird_1','glide']
];await writeFile('outputs/runtime-checkpoint-24/selected-object-fixtures.json',JSON.stringify(cases,null,2));const results=[];
for(const[text,id,action]of cases){const r=await decide(text,{selected_entity:id}),pass=r.plan.items.length===1&&r.plan.items[0].target===id&&r.plan.items[0].action===action;const out={text,selected:id,expected:action,pass,request_id:r.id,ms:r.ms,plan:r.plan};results.push(out);console.log(JSON.stringify(out));}
await writeFile('outputs/runtime-checkpoint-24/selected-object-results-round2.json',JSON.stringify(results,null,2));
