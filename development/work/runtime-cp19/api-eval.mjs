import fs from'node:fs';import{decide}from'../../app/runtime-cp19/decision-api.mjs';
const cases=[
{id:'rain',poem:'雨丝飘过屋檐，街上的人找个地方躲躲雨吧。',expected:{weather:'rain',street:'keep'}},
{id:'festival',poem:'今夜请让火红的花火盛放，街坊们找个空位一起看吧。',expected:{festival:'fireworks',street:'keep'}},
{id:'market',poem:'把晚市唤醒吧，让摊主和客人都热闹起来。',expected:{occasion:'market'}},
{id:'reunion',poem:'邻里们聚在一起聊聊天，分享今天的小事。',expected:{occasion:'reunion'}},
{id:'supper',poem:'晚饭时间到了，想让大家闻着饭香去吃东西。',expected:{occasion:'supper'}},
{id:'compound',poem:'雪停一停，风也轻一点；楼上的客人先回门帘后歇着。',state:{weather:'snow',breeze:'gentle'},expected:{weather:'clear',breeze:'calm',dining:'inside'}},
{id:'no_spawn',poem:'在池塘中央造一座摩天大楼，再变出十条龙。',expected:{weather:'keep',occasion:'keep',festival:'keep'}},
{id:'no_nest',poem:'两只鸟归巢吧，别的都不变。',expected:{birds:'keep',street:'keep',occasion:'keep'}}];
fs.writeFileSync('outputs/runtime-checkpoint-19/api-eval-cases.json',JSON.stringify(cases,null,2));const rows=[];for(const c of cases){try{const r=await decide(c.poem,c.state||{weather:'clear',breeze:'gentle'});const passed=Object.entries(c.expected).every(([k,v])=>r.decision[k]===v);rows.push({...c,...r,passed});console.log(c.id,passed,r.ms,JSON.stringify(Object.fromEntries(Object.entries(r.decision).filter(([k,v])=>v!=='keep'))));}catch(e){rows.push({...c,passed:false,error:e.message});console.log(c.id,e.message);}}fs.writeFileSync('outputs/runtime-checkpoint-19/api-eval-results.json',JSON.stringify({frozen_before_calls:true,tuning_or_feature_check:true,rows},null,2));
