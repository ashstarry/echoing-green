import{decide}from'../../app/runtime-cp32/decision-api.mjs';import{writeFileSync}from'node:fs';
const cases=[
 ['下雨了，大家赶快找地方避雨','weather','rain'],
 ['大伙儿去摊位前排队，晚市开始啦','occasion','market'],
 ['烟花亮起来吧，让大家一起仰头看','festival','fireworks'],
 ['Open the evening market and let everyone line up for warm food.','occasion','market'],
 ['Let it snow over the whole town.','weather','snow'],
 ['雨停了，出来走走吧','weather','clear'],
 ['别下雪了，让大家继续逛街','weather','clear'],
 ['让夜色再暖一点，大家慢慢聚过来','occasion','reunion'],
 ['保持现在的天气，不要变',null,null],
 ['刚才的晚市很漂亮',null,null],
 ['如果明天下雨再考虑避雨',null,null],
 ['把城镇变成一条龙',null,null]
];
writeFileSync('outputs/runtime-checkpoint-32/semantic-final-cases.json',JSON.stringify(cases,null,2));const rows=[];for(const[poem,target,action]of cases){const result=await decide(poem,{});const pass=target?result.plan.items.some(i=>i.target===target&&i.action===action):result.plan.items.length===0;rows.push({poem,expected:{target,action},pass,...result});writeFileSync('outputs/runtime-checkpoint-32/semantic-final.json',JSON.stringify(rows,null,2));console.log(JSON.stringify({poem,pass,items:result.plan.items.map(i=>[i.target,i.action]),ms:result.ms}));}
