import{decide}from'../../app/runtime-cp27/decision-api.mjs';import{readFile,writeFile,copyFile,mkdir}from'node:fs/promises';
import{createWorld,step,serialize,restore}from'../../app/runtime-cp27/src/simulation.mjs';import{queueIntent}from'../../app/runtime-cp27/src/life-plans.mjs';import{objectCatalog}from'../../app/runtime-cp27/src/object-actions.mjs';
const out='outputs/runtime-checkpoint-27/integrated-poetry',cases=[
 ['soft-landing','今晚想被这个世界温柔地接住。',['light','occasion','breeze','day_phase']],
 ['lonely-street','这里像是很久没有人等谁了。',['occasion','light']],
 ['weary-day','想把今天的疲惫留在门外。',['occasion','light','day_phase','breeze']],
 ['reunion-air','空气里像有一场久别重逢。',['occasion']],
 ['celebrate','总觉得今晚值得庆祝一下。',['occasion','festival','light']],
 ['together','热闹不必很大，彼此靠近一点就好。',['occasion']],
 ['unfinished-letter','让这一刻像一封没有写完的信。',['occasion','light']],
 ['sky-secret','今晚的天空，想藏一点惊喜。',['festival','day_phase']],
 ['light-dream','万物都轻一点，像一场快醒来的梦。',['breeze','light','occasion','day_phase']],
 ['spring-feeling','街角有一点说不清的春意。',['occasion','breeze','light']],
 ['homecoming','愿每一个晚归的人都有一盏灯。',['light','day_phase','occasion']],
 ['encounters','感觉这里更适合大家慢慢相遇。',['occasion']],
 ['en-tender','It feels like the world could use a little tenderness tonight.',['light','occasion','breeze','day_phase']],
 ['en-reunion','There is a reunion waiting in the air.',['occasion']],
 ['en-celebration','Let the evening feel like a tiny celebration.',['occasion','festival','light']],
 ['en-secret','The night has a secret it is almost ready to tell.',['festival','day_phase']],
 ['praise-only','真漂亮。',[]],['hold-still','别改动，保持现在这样。',[]],['hypothetical','如果下雨了，会是什么样子？',[]],['en-praise','This town looks lovely.',[]]
].map(([id,text,allowedDomains])=>({id,text,allowedDomains,control:allowedDomains.length===0}));
await mkdir(out,{recursive:true});await writeFile(out+'/poetry-fixtures-frozen.json',JSON.stringify({frozenBeforeRequests:true,criterion:'Ambiguous poems have no unique correct answer. Allowed macro domains are a preregistered plausibility check, not an objective gold label. Noticeable proxy: changed weather/time/festival or >=3 mobile residents displaced >1 model unit relative to no-input control at20s or45s. Lighting/wind alone are mild, not automatically noticeable.',cases},null,2));await copyFile('app/runtime-cp27/decision-api.mjs',out+'/poetry-model-source.mjs');
const read=async n=>JSON.parse(await readFile('app/runtime-cp27/public/assets/'+n,'utf8'));const nav=await read('navigation.json');nav.activities=await read('motion-activities.json');Object.assign(nav.activities,{rail:await read('rail-path.json'),diners:await read('diner-clips.json'),spaces:await read('activity-spaces.json'),localRoutes:await read('local-routes.json'),boarding:await read('boarding-config.json'),objectCatalog:objectCatalog(await read('runtime-registry.json'))});
const initial=createWorld(nav,62417);initial.festivalAuto=false;for(let i=0;i<600;i++)step(initial,nav);const current={weather:initial.weather,day_phase:initial.day_phase,light:initial.light,breeze:initial.breeze,occasion:initial.occasion,festival:'quiet',festival_auto:false,reader_book:'open',passenger_phase:'waiting'};
const control=restore(serialize(initial),nav),controlFrames={};for(let i=1;i<=900;i++){step(control,nav);if(i===400||i===900)controlFrames[i]=structuredClone(control);}const results=[];
for(const c of cases){const r=await decide(c.text,current),s=restore(serialize(initial),nav),observations=[];if(r.plan.items.length)queueIntent(s,r.plan.items,{id:r.id},nav.activities.objectCatalog);for(let i=1;i<=900;i++){step(s,nav);if(i===400||i===900){const b=controlFrames[i],changed=s.actors.filter(a=>{const old=b.actors.find(x=>x.id===a.id);return Math.hypot(a.p[0]-old.p[0],a.p[1]-old.p[1])>1;}).map(a=>a.id);const macro=['weather','day_phase','light','breeze','occasion'].filter(k=>s[k]!==b[k]);const festival=s.worldEvent.kind!==b.worldEvent.kind;observations.push({after:i/20,actorsDifferentFromControl:changed,macroDifferences:macro,festivalDifferent:festival,noticeableProxy:changed.length>=3||macro.includes('weather')||macro.includes('day_phase')||festival});}}
const domains=r.plan.items.map(x=>x.field||x.target),extra=domains.filter(k=>!c.allowedDomains.includes(k)),nonempty=r.plan.items.length>0;const row={...c,request_id:r.id,ms:r.ms,cost:r.cost,plan:r.plan,nonempty,scopePlausible:!extra.length,extraDomains:extra,observations,noticeableProxy:observations.some(x=>x.noticeableProxy),failedJobs:s.intentRuntime.jobs.filter(j=>j.status==='failed')};results.push(row);await writeFile(out+'/poetry-results.json',JSON.stringify(results,null,2));console.log(JSON.stringify({id:c.id,nonempty,noticeable:row.noticeableProxy,scopePlausible:row.scopePlausible,items:r.plan.items.map(i=>[i.target,i.action])}));}
