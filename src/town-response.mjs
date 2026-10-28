import {PROFILES} from './community.mjs?v=cp28-1336fccff9e2';
import {RESIDENT_ACTIONS,RESIDENT_CAPABILITIES,requestResidentAction} from './resident-actions.mjs?v=cp28-1336fccff9e2';
import {stableUnit} from './cadence.mjs?v=cp28-1336fccff9e2';

const live=j=>!['done','failed','cancelled'].includes(j.status);
const safeToBlend=action=>action&&!RESIDENT_ACTIONS[action]?.route&&!RESIDENT_ACTIONS[action]?.navTask&&!['sip_tea','taste_food','feed_pond','look_pond'].includes(action);
export function responseTheme(s,items){
 const d=Object.fromEntries(items.filter(x=>x.kind==='macro').map(x=>[x.target,x.action]));
 if(d.festival==='fireworks')return 'festival';
 if(d.weather==='rain')return 'rain';if(d.weather==='snow')return 'snow';
 if(d.occasion==='quiet'||d.street==='quiet')return 'quiet';
 if(d.weather==='clear')return 'clear';
 if(d.occasion&&d.occasion!=='ordinary')return d.occasion;
 if(d.day_phase)return d.day_phase;
 if(d.music==='play')return 'music';
 if(d.light||d.breeze||d.occasion==='ordinary'||d.street==='wander')return 'lively';
 return null;
}
// Each wish causes one bounded, staggered response. This does not invent new routes,
// replace explicit personal goals or continuously interrupt somebody's current work.
export function stimulateTown(s,items,{id='opening',opening=false}={}){
 const theme=opening?(s.weather==='rain'?'rain':s.worldEvent.kind==='festival'?'festival':s.occasion==='quiet'||s.street==='quiet'?'quiet':s.weather==='snow'?'snow':'opening'):responseTheme(s,items);
 if(!theme)return null;
 const protectedIds=new Set(items.filter(i=>i.kind==='resident').map(i=>i.target));
 const pending=[];let n=0;
 for(const a of s.actors){if(!a.mobile||protectedIds.has(a.id)||theme==='quiet'&&s.street==='quiet')continue;
  const role=PROFILES[a.id],cycle=s.residents[a.id].cycle;
  // A new town-wide event supersedes earlier mobile errands, not same-request
  // explicit exceptions or fixed-role residents. Carried gestures finish safely.
  if(!opening&&['rain','snow','festival','market','supper','reunion'].includes(theme)){
   for(const j of s.intentRuntime.jobs)if(j.target===a.id&&live(j)){j.status='cancelled';j.updated=s.time;j.reason='跟随最新的全镇活动';}
   const r=s.residentActions[a.id];r.requested=false;r.queuedByUser=false;r.queued=null;
   if(RESIDENT_ACTIONS[r.action]?.navTask){r.action=null;r.clock=0;}
   a.manual=false;a.manualActivity=null;a.activityUntil=0;
  }

  let task=theme==='rain'?'shelter':theme==='festival'?'fireworks':theme==='quiet'?'lotus':theme==='snow'?'snow':null;
  if(!task&&['market','supper'].includes(theme))task='browse';
  if(!task&&theme==='reunion')task='chat';if(!task&&theme==='delivery'&&/postman|courier/.test(a.id))task='mail';
  if(!task&&theme==='music')task='listen';
  if(!task)task=role.routine[(cycle+1+n)%role.routine.length];
  if(task==='rest')task='stroll';
  if(a.id==='resident.kite_child'&&!['rain','snow','festival','market','supper','reunion'].includes(theme))task='kite';
  if(a.id==='resident.child_parent'&&!['rain','festival','market','supper','reunion'].includes(theme))task='follow';
  pending.push({id:a.id,task,revisit:s.occasion==='market',at:s.time+.10+n++*(['rain','snow','festival','market','supper','reunion'].includes(theme)?.12:.22),done:false});
 }
 const actions=theme==='rain'?[
  ['quiet_reader','close_book'],['vendor_bread','cover_food'],['water_companion','umbrella_open'],['water_visitor','converse'],['porch_resident','return_porch']
 ]:theme==='festival'?[
  ['quiet_reader','watch_sky'],['water_companion','watch_sky'],['water_visitor','bridge_walk'],['returning_resident','go_terrace'],['porch_resident','go_window'],['vendor_bread','greet'],['listener','applaud']
 ]:theme==='quiet'?[
  ['quiet_reader','read_pages'],['elder','sip_tea'],['water_visitor','look_pond']
 ]:[
  ['porch_resident',s.localWalkers['resident.porch_resident']?.anchor==='window'?'return_porch':'go_window'],
  ['returning_resident',s.localWalkers['resident.returning_resident']?.anchor==='terrace'?'go_street':'go_terrace'],
  ['water_visitor','bridge_walk'],['gardener',theme==='snow'?'watch_sky':'water_plants'],
  ['vendor_bread','offer_food'],['vendor_flower','greet'],['quiet_reader',theme==='night'?'close_book':'read_pages'],['station_attendant','signal_train']
 ];
 for(const [short,action]of actions){const target='resident.'+short;if(!protectedIds.has(target))pending.push({id:target,action,at:s.time+.7+(n++%8)*.45,done:false});}
 s.townResponse={id,theme,started:s.time,until:s.time+(opening?16:48),pending};
 return s.townResponse;
}
export function advanceTownResponse(s){
 const pulse=s.townResponse;if(!pulse||s.time>pulse.until)return;
 for(const item of pulse.pending){if(item.done||s.time<item.at)continue;
  const id=item.id,r=s.residentActions[id],a=s.actors.find(a=>a.id===id);
  if(s.intentRuntime.jobs.some(j=>j.target===id&&live(j))||r?.requested||r?.queuedByUser||a?.manual){item.done=true;item.skipped='保留明确的个人安排';continue;}
  if(s.passengers[id]?.phase&&s.passengers[id].phase!=='waiting'){item.done=true;continue;}
  if(item.task){
   if(r?.action){if(safeToBlend(r.action))r.cancelRemaining=r.cancelRemaining||.65;else if(RESIDENT_ACTIONS[r.action]?.navTask){item.done=true;continue;}continue;}
   if(a.atHome||!a.path.length||pulse.theme!=='opening'){
    a.responseTask=s.weather==='rain'?'shelter':item.task;a.responseUntil=pulse.until;
    if(item.task==='browse'&&pulse.theme!=='opening'&&item.revisit)a.marketVisit=(a.marketVisit||0)+1;
    a.responseDestination=null;a.responseReplan=true;a.taskRevision=-1;a.wait=Math.min(a.wait,.2+stableUnit(id)*.3);a.localActionUntil=0;
    a.responseMinTravel=(id==='resident.kite_child'||['kite','follow','hop'].includes(a.responseTask))?.8:pulse.theme==='rain'?1.4:pulse.theme==='festival'?2.25:1.45;
    r.nextAt=Math.max(r.nextAt,s.time+3);item.dispatched=s.time;
   }
   item.done=true;continue;
  }
  if(!RESIDENT_CAPABILITIES[id]?.includes(item.action)||RESIDENT_ACTIONS[item.action]?.route&&!s.availableRoutes.includes(id)){item.done=true;continue;}
  if(item.action==='read_pages'&&r.bookManualUntil>s.time&&r.bookTarget===0){item.done=true;item.skipped='保留你刚刚合书的安排';continue;}
  if(s.localWalkers[id]?.clip){item.done=true;continue;}
  if(RESIDENT_ACTIONS[item.action]?.destination===s.localWalkers[id]?.anchor){item.done=true;continue;}
  if(r.action){if(safeToBlend(r.action)&&PROFILES[id].role!=='diner')r.cancelRemaining=r.cancelRemaining||.65;continue;}
  const revision=s.revision;
  try{requestResidentAction(s,id,item.action);r.reason=pulse.theme==='opening'?'开始今天的日常':'回应小镇刚刚的变化';item.dispatched=s.time;}catch(e){item.skipped=e.message;}finally{s.revision=revision;item.done=true;}
 }
}
export function validateTownResponse(s){
 const p=s.townResponse;if(!p)return;
 if(!Array.isArray(p.pending)||p.pending.length>50||![p.started,p.until].every(Number.isFinite)||p.pending.some(i=>!PROFILES[i.id]||!Number.isFinite(i.at)))throw Error('小镇响应存档无效');
}
