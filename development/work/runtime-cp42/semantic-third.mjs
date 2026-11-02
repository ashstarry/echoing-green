import{writeFile}from'node:fs/promises';import{decide}from'../../app/runtime-cp42/decision-api.mjs';
const cases=[
['fox','给橘色的小家伙一点调皮劲儿。','animal.garden_fox',['play']],
['parcel','让电车捎来一份小礼物，回来交到街坊手里。','journey',['deliver']],
['parcel-en','Could the tram bring a little parcel to a neighbor?','journey',['deliver']],
['tea','让一双手被一杯热茶暖一暖。','craft',['tea']],
['tea-en','A little warmth passed from hand to hand, over a cup of tea.','craft',['tea']],
['snack','揭开蒸笼，让路过的人尝一口热腾腾的点心。','craft',['snack']],
['umbrella','这把伞，分一半给身旁的人吧。','craft',['umbrella']],
['umbrella-en','Let two neighbors share an umbrella for a little walk.','craft',['umbrella']],
['leaves','秋天落在脚边，替晚风收拾一下吧。','craft',['leaves']],
['leaves-en','Let a few leaves drift down, then sweep them into a basket.','craft',['leaves']],
['memory','把刚才那一点温柔，留作柜台角落的小纪念。','craft',['remember']],
['memory-en','Keep a little memento of this evening.','craft',['remember']],
['recall','拿起柜台上那件小纪念，看看再放回。','craft',['recall']],
['putaway','把那件纪念仔细收起来。','craft',['putaway']],
['laundry','让小布巾也闻一闻晚风。','craft',['laundry']],
['laundry-en','Hang a little laundry in the breeze.','craft',['laundry']],
['bring-in','雨要来了，把晾着的布收回来吧。','craft',['bring_in']],
['cloud','小云去街巷散散步，只在自己下面落一点雨。','cloud',['wander']],
['cloud-garden','给花园一小片雨就好，其他地方照旧。','cloud',['garden']],
['cloud-en','Let that little cloud wander over the lanes with a tiny shower underneath.','cloud',['wander']],
['boat','让小船看看池塘另一边，然后慢慢回家。','boat.pond_boat',['cruise']],
['dock','小船该回到泊位了。','boat.pond_boat',['dock']],
['boat-en','Let the little boat drift across the pond and return to its berth.','boat.pond_boat',['cruise']],
['past','刚才的茶真温暖，保持现在这样，不用再安排。',null,[]],
['boundary','让小船载着所有居民穿过海洋去京都，别做其他变化。',null,[]]
];
const rows=[];for(const[id,text,target,actions]of cases){const state={weather:'clear',day_phase:'dusk',paper_count:2,memory_count:2,selected_entity:null,passenger_phase:'waiting'};try{const result=await decide(text,state),items=result.plan.items;const expected=target?items.some(i=>i.target===target&&actions.includes(i.action)):!items.length;const local=['craft','cloud'].includes(target);const scoped=!local||!items.some(i=>['occasion','street','festival','paper','neighborhood'].includes(i.target)||target==='cloud'&&i.target==='weather'&&i.action==='rain');const pass=expected&&scoped;rows.push({id,text,target,actions,state,pass,expected,scoped,result});console.log(JSON.stringify({id,pass,items:items.map(i=>[i.target,i.action]),status:result.plan.status}));}catch(e){rows.push({id,text,pass:false,error:e.message});console.log(JSON.stringify({id,error:e.message}));}await writeFile('outputs/runtime-checkpoint-42/semantic-third.json',JSON.stringify(rows,null,2));}
