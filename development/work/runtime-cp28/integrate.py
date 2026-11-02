from pathlib import Path
root=Path('app/runtime-cp28/src')
p=root/'simulation.mjs';s=p.read_text();s="import {requestSceneEvent,sceneTask,holdsEventPlace,validateSceneEvents} from './scene-events.mjs';\n"+s
s=s.replace('const s={intentRuntime:',"const s={sceneEvent:null,eventSequence:0,eventWeather:{rain:0,snow:0,cover:0},intentRuntime:")
s=s.replace('festivalAuto:true','festivalAuto:false')
s=s.replace('expectedRevision=s.revision}={}){const d=validateDecision(input);','expectedRevision=s.revision,eventPolicy=true}={}){let d=validateDecision(input);')
s=s.replace('s.revision++;\n if(s.townResponse',"s.revision++;if(eventPolicy)d=requestSceneEvent(s,d,text=>event(s,text));\n if(s.townResponse")
s=s.replace("const zone=ACTIVITIES[task]?.zone", "const assigned=s.sceneEvent?.slots?.[a.id];if(assigned!==undefined&&['gather','active'].includes(s.sceneEvent.phase)){a.responseDestination=assigned;a.responseUntil=Math.max(a.responseUntil||0,s.sceneEvent.until+30);}\n const zone=ACTIVITIES[task]?.zone")
s=s.replace("if(zone==='chat'){const lonely=", "if(assigned!==undefined&&['gather','active'].includes(s.sceneEvent.phase))center=nav.nodes[assigned];\n if(zone==='chat'&&assigned===undefined){const lonely=")
s=s.replace("['rain','festival'].includes(s.townResponse?.theme)","['rain','festival','market','supper','reunion'].includes(s.townResponse?.theme)")
s=s.replace("updateDirector(s,dt,text=>event(s,text));","updateDirector(s,dt,text=>event(s,text),nav);")
s=s.replace("if(!a.path.length){a.mode='idle';if(['shelter','fireworks']", "if(!a.path.length){a.mode='idle';if(holdsEventPlace(s,a)){a.wait=.4;continue;}if(['shelter','fireworks']")
s=s.replace("validateTownResponse(s);validateIntentRuntime(s);", "validateSceneEvents(s);validateTownResponse(s);validateIntentRuntime(s);")
s=s.replace('return{intentJobs:structuredClone', 'return{capturedAt:s.time,sceneEvent:structuredClone(s.sceneEvent),intentJobs:structuredClone')
s=s.replace('const out=applyDecision(s,snapshot.choices);',"const out=applyDecision(s,snapshot.choices,{eventPolicy:false});s.sceneEvent=snapshot.sceneEvent?structuredClone(snapshot.sceneEvent):null;if(s.sceneEvent){const delta=s.time-(snapshot.capturedAt||s.time);for(const key of ['phaseAt','started','until'])s.sceneEvent[key]+=delta;}")
p.write_text(s)
p=root/'community.mjs';s=p.read_text();s="import {advanceSceneEvent,requestSceneEvent,sceneTask} from './scene-events.mjs';\n"+s
start=s.index('export function updateDirector(');end=s.index('export function wantedTask(',start)
s=s[:start]+'''export function updateDirector(s,dt,emit,nav){
 advanceSceneEvent(s,nav,dt,emit);
 if(s.festivalAuto&&!s.sceneEvent&&['dusk','night'].includes(s.day_phase)&&s.time>=s.festivalNextAt)requestSceneEvent(s,{festival:'fireworks'},emit);
 s.effectiveMusic=s.weather==='rain'&&!s.musicManual||s.sceneEvent?.kind==='festival'&&s.sceneEvent.phase==='active'?'rest':s.music;
 for(const[id,d]of Object.entries(s.diners)){const festival=s.sceneEvent?.kind==='festival'&&['gather','active'].includes(s.sceneEvent.phase);const policy=d.manualPolicy||(s.dining!=='auto'?s.dining:s.weather==='rain'?'inside':festival||s.occasion==='supper'?'dine':'auto');if(d.effectivePolicy!==policy){d.effectivePolicy=policy;d.policy=policy;d.wait=Math.min(d.wait,varied([1,4],id,s.planRevision));}}
}
'''+s[end:]
s=s.replace("if(s.weather==='rain')return 'shelter';", "const foreground=sceneTask(s,a);if(foreground)return foreground;\n if(s.weather==='rain')return 'shelter';")
s=s.replace("if(s.occasion==='market'||s.occasion==='supper'){if(a.id.includes('customer')||a.id==='resident.market_browser')return 'browse';if(['resident.postman','resident.courier'].includes(a.id))return 'mail';return s.occasion==='market'?'stroll':'listen';}","if(s.occasion==='market'||s.occasion==='supper')return 'browse';")
s=s.replace("let next=null,reason='按自己的习惯过晚间生活';", "let next=null,reason='按自己的习惯过晚间生活';")
s=s.replace("else if(p.role==='vendor'){const guest=", "else if(p.role==='vendor'&&s.sceneEvent?.phase==='closing'&&['market','supper'].includes(s.sceneEvent.kind)){next='tidy';reason='收好餐具，和最后的客人道别';}\n   else if(p.role==='vendor'){const guest=")
p.write_text(s)
p=root/'life-plans.mjs';s=p.read_text();s="import {eventKind} from './scene-events.mjs';\n"+s
s=s.replace("s.revision++;stimulateTown(s,items,{id});", "s.revision++;if(!eventKind(Object.fromEntries(items.filter(i=>i.kind==='macro').map(i=>[i.target,i.action]))))stimulateTown(s,items,{id});")
s=s.replace(" for(const j of runtime.jobs){if(['done','cancelled','failed'].includes(j.status))continue;", """ // Apply the macros from one utterance atomically: the event policy sees the
 // complete request, rather than treating each field as another new event.
 const groups=new Map();for(const j of runtime.jobs)if(j.kind==='macro'&&j.status==='pending'&&j.step===0){if(!groups.has(j.requestId))groups.set(j.requestId,[]);groups.get(j.requestId).push(j);}
 for(const[id,jobs]of groups){const revision=s.revision;try{apply(s,Object.fromEntries(jobs.map(j=>[j.target,j.action])),{id:'macro-batch:'+id,expectedRevision:revision});for(const j of jobs){j.status='done';j.step=j.steps.length;j.updated=s.time;}}catch(e){for(const j of jobs){j.status='failed';j.reason=e.message;}}finally{s.revision=revision;}}
 for(const j of runtime.jobs){if(['done','cancelled','failed'].includes(j.status))continue;""")
p.write_text(s)
p=root/'town-response.mjs';s=p.read_text().replace("['rain','festival'].includes(theme)","['rain','snow','festival','market','supper','reunion'].includes(theme)")
s=s.replace("task=a.id.includes('customer')||a.id.includes('browser')?'browse':a.id.includes('postman')||a.id.includes('courier')?'mail':['stroll','chat','listen'][n%3]","task='browse'")
s=s.replace("if(a.id==='resident.kite_child'&&!['rain','festival'].includes(theme))task='kite';","if(a.id==='resident.kite_child'&&!['rain','festival','market','supper'].includes(theme))task='kite';")
s=s.replace("if(a.id==='resident.child_parent'&&!['rain','festival','reunion'].includes(theme))task='follow';","if(a.id==='resident.child_parent'&&!['rain','festival','market','supper','reunion'].includes(theme))task='follow';")
p.write_text(s)
p=root/'intent-view.mjs';s=p.read_text().replace("r.activity==='fireworks'?-.035:0","r.activity==='fireworks'?-.12:0");p.write_text(s)
