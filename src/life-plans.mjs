import {eventKind} from './scene-events.mjs?v=cp37-paper-1dbadc3fdf78';
import {stimulateTown} from './town-response.mjs?v=cp37-paper-1dbadc3fdf78';
import {RESIDENT_ACTIONS,RESIDENT_CAPABILITIES,requestResidentAction} from './resident-actions.mjs?v=cp37-paper-1dbadc3fdf78';
import {requestPassengerAction} from './passengers.mjs?v=cp37-paper-1dbadc3fdf78';
import {requestObjectAction} from './object-actions.mjs?v=cp37-paper-1dbadc3fdf78';
import {validateDecision} from './catalog.mjs?v=cp37-paper-1dbadc3fdf78';

// Compound goals reuse tested movements, with real completion/occupation checks between steps.
export const LIFE_PLANS={
 reading_break:{label:'合书喝茶，再读几页',actors:['resident.quiet_reader'],steps:['close_book','sip_tea',{wait:2},'read_pages']},
 pond_company:{label:'喂鱼、指给同伴看，再聊几句',actors:['resident.water_visitor'],steps:['feed_pond','look_pond','converse']},
 garden_round:{label:'检查花叶、浇水，再招呼邻居',actors:['resident.gardener'],steps:['inspect_leaf','water_plants','greet']},
 counter_service:{label:'擦好柜台，端起点心迎客',actors:['resident.vendor_bread','resident.vendor_flower','resident.vendor_lamp'],steps:['wipe_counter','offer_food','greet']},
 supper_and_rest:{label:'出来吃点心、喝茶，再回帘内',actors:['resident.upper_diner_0','resident.upper_diner_1'],steps:['dine','taste_food','sip_tea','inside']},
 overlook_round:{label:'上露台眺望，再走回街边',actors:['resident.returning_resident'],steps:['go_terrace','shade_eyes',{wait:4},'go_street']},
 letter_round:{label:'核对信件，再沿街走一段',actors:['resident.postman'],steps:['check_letter','walk_street']},
 music_interlude:{label:'弹一小段琴，歇下来打招呼',actors:['resident.musician'],steps:['play_music',{wait:14},'rest_music','greet']}
};
const EXTRA={inside:['resident.upper_diner_0','resident.upper_diner_1'],dine:['resident.upper_diner_0','resident.upper_diner_1'],ride_once:['resident.station_traveler'],stay:['resident.station_traveler'],alight:['resident.station_traveler'],play_music:['resident.musician'],rest_music:['resident.musician'],cycle_trip:['resident.cyclist'],cycle_rest:['resident.cyclist'],hop:['resident.garden_child','resident.child_runner'],kite_play:['resident.kite_child'],watch_child:['resident.child_parent']};
export function supportsResident(id,action){return !!(RESIDENT_CAPABILITIES[id]?.includes(action)||EXTRA[action]?.includes(id)||LIFE_PLANS[action]?.actors.includes(id));}
const blockedInRain=new Set(['read_pages','feed_pond','water_plants','walk_street','visit_market','listen_music','seek_neighbor','watch_pond','hop','kite_play','cycle_trip']);
export function createIntentRuntime(){return {jobs:[],seen:[],sequence:0,lastDay:'dusk',daily:[],lastReceipt:null};}
export function queueIntent(s,items,{id=`local-plan-${s.revision+1}-${s.intentRuntime.sequence+1}`,expectedRevision=s.revision,source='words',sourceText=''}={},catalog={}){
 if(expectedRevision!==s.revision)return{accepted:false,reason:'stale'};
 if(s.intentRuntime.seen.includes(id))return{accepted:false,reason:'duplicate'};
 if(!Array.isArray(items)||items.length>60)throw Error('计划项数无效');
 for(const x of items){if(!x||typeof x.target!=='string'||typeof x.action!=='string')throw Error('动作格式无效');if(x.kind==='resident'&&!supportsResident(x.target,x.action))throw Error('角色没有这个已实现动作');if(x.kind==='object'&&!catalog[x.target]?.actions.some(a=>a.id===x.action))throw Error('物件没有这个已实现动作');if(x.kind==='macro')validateDecision({[x.target]:x.action});if(!['resident','object','macro'].includes(x.kind))throw Error('不允许的动作类型');}
 items=items.map(item=>{if(item.kind!=='object')return item;const object=catalog[item.target],action=object.actions.find(a=>a.id===item.action);let owner=action.owner,goal=item.action;
  if(object.kind==='watering_can'){owner='resident.gardener';goal=item.action==='pour'?'water_plants':'inspect_leaf';}
  if(object.kind==='instrument'){owner='resident.musician';goal=item.action==='play'?'play_music':'rest_music';}
  if(object.kind==='seat'&&item.target.includes('dining_chair')){owner='resident.upper_diner_'+item.target.at(-1);goal=item.action==='pull_out'?'inside':'dine';}
  if(owner){if(!supportsResident(owner,goal))throw Error('这个物件尚未连接到使用者动作');return{...item,origin_object:item.target,kind:'resident',target:owner,action:goal};}return item;});
 if(source==='words'&&s.sceneEvent){for(const item of items)if(item.kind==='resident'){if(!s.sceneEvent.protectedIds.includes(item.target))s.sceneEvent.protectedIds.push(item.target);delete s.sceneEvent.slots[item.target];}}
 s.intentRuntime.seen.push(id);s.intentRuntime.seen=s.intentRuntime.seen.slice(-50);
 const receipt={id,source,started:s.time,targets:items.map(x=>x.target),count:items.length};
 for(const item of items){for(const j of s.intentRuntime.jobs)if(j.target===item.target&&!['done','cancelled','failed'].includes(j.status))j.status='cancelled';const definition=LIFE_PLANS[item.action];s.intentRuntime.jobs.push({...item,id:`${id}/${++s.intentRuntime.sequence}`,requestId:id,status:'pending',step:0,steps:definition?structuredClone(definition.steps):[item.action],started:s.time,updated:s.time,source,sourceText:String(sourceText||'').slice(0,160),reason:'等当前动作安全结束'});}
 s.intentRuntime.jobs=s.intentRuntime.jobs.filter(j=>!['done','cancelled','failed'].includes(j.status)||s.time-j.updated<90).slice(-80);
 if(source!=='day_rhythm'){s.intentRuntime.lastReceipt=receipt;s.revision++;if(!eventKind(Object.fromEntries(items.filter(i=>i.kind==='macro').map(i=>[i.target,i.action]))))stimulateTown(s,items,{id});}return{accepted:true,receipt};
}
function startResident(s,j,action,apply){const id=j.target;
 if(['inside','dine'].includes(action)){const d=s.diners[id];d.manualPolicy=action;d.policy=action;d.effectivePolicy=action;d.wait=Math.min(d.wait,1.0);return{type:'diner',value:action==='inside'?'inside':'dine'};}
 if(['ride_once','stay','alight'].includes(action)){if(action==='alight'&&s.passengers[id].phase==='waiting')throw Error('他已经在站台，无需下车');const p=s.passengers[id];const before=p.completedTrips;requestPassengerAction(s,id,action);return{type:'passenger',value:action,before};}
 if(['play_music','rest_music'].includes(action)){apply(s,{music:action==='play_music'?'play':'rest'});return{type:'immediate'};}
 if(['cycle_trip','cycle_rest'].includes(action)){apply(s,{cycling:action==='cycle_trip'?'ride':'rest'});return{type:'immediate'};}
 if(['hop','kite_play','watch_child'].includes(action)){const a=s.actors.find(a=>a.id===id);a.manual=false;a.manualActivity={hop:'hop',kite_play:'kite',watch_child:'follow'}[action];a.activityUntil=s.time+35;a.taskRevision=-1;a.wait=.2;s.planRevision++;return{type:'activity',until:s.time+18};}
 const def=RESIDENT_ACTIONS[action];if(def.destination&&s.localWalkers[id]?.anchor===def.destination&&!s.localWalkers[id].clip)return{type:'immediate'};
 const r=s.residentActions[id],before=r.completed;requestResidentAction(s,id,action);return{type:'resident',action,before};
}
function complete(s,j){const m=j.monitor;if(!m)return false;if(m.type==='immediate')return true;if(m.type==='wait'||m.type==='activity')return s.time>=m.until;if(m.type==='diner')return s.diners[j.target].phase===m.value;if(m.type==='resident'){const r=s.residentActions[j.target];return r.completed>m.before&&r.lastAction===m.action;}
 if(m.type==='passenger'){const p=s.passengers[j.target];return m.value==='ride_once'?p.completedTrips>m.before:p.phase==='waiting';}return false;
}
export function advanceIntentRuntime(s,nav,dt,apply,emit){
 const runtime=s.intentRuntime,catalog=nav.activities.objectCatalog||{};
 if(s.day_phase!==runtime.lastDay){runtime.lastDay=s.day_phase;const jobs=s.day_phase==='night'?[['resident.quiet_reader','close_book'],['resident.elder','sip_tea'],['resident.upper_diner_0','inside']]:s.day_phase==='dawn'?[['resident.gardener','inspect_leaf'],['resident.vendor_bread','wipe_counter'],['resident.quiet_reader','read_pages']]:s.day_phase==='day'?[['resident.gardener','water_plants'],['resident.vendor_flower','offer_food']]:[['resident.musician','play_music'],['resident.vendor_lamp','greet']];runtime.daily=jobs.map(([target,action],i)=>({target,action,at:s.time+2+i*2.8}));}
 for(const item of runtime.daily){if(item.done||s.time<item.at)continue;if(s.sceneEvent&&s.sceneEvent.phase!=='release'||s.weather==='rain'||s.residentActions[item.target]?.requested||s.residentActions[item.target]?.queuedByUser||runtime.jobs.some(j=>j.target===item.target&&!['done','failed','cancelled'].includes(j.status))){item.done=true;continue;}queueIntent(s,[{...item,kind:'resident'}],{source:'day_rhythm'},catalog);item.done=true;}
 // Apply the macros from one utterance atomically: the event policy sees the
 // complete request, rather than treating each field as another new event.
 const groups=new Map();for(const j of runtime.jobs)if(j.kind==='macro'&&j.status==='pending'&&j.step===0){if(!groups.has(j.requestId))groups.set(j.requestId,[]);groups.get(j.requestId).push(j);}
 for(const[id,jobs]of groups){const revision=s.revision;try{apply(s,Object.fromEntries(jobs.map(j=>[j.target,j.action])),{id:'macro-batch:'+id,expectedRevision:revision,sourceText:jobs[0].sourceText||''});for(const j of jobs){j.status='done';j.step=j.steps.length;j.updated=s.time;}}catch(e){for(const j of jobs){j.status='failed';j.reason=e.message;}}finally{s.revision=revision;}}
 for(const j of runtime.jobs){if(['done','cancelled','failed'].includes(j.status))continue;
  if(j.status==='running'){if(!complete(s,j)){if(s.time-j.updated>220){j.status='failed';j.reason='当前路径或动作尚未完成，取消后续步骤';emit('有一项安排暂时没有完成，小镇会继续自己的生活。');}continue;}j.step++;j.monitor=null;j.status='pending';j.updated=s.time;}
  if(j.step>=j.steps.length){j.status='done';j.updated=s.time;j.reason='这一段生活已经完成';continue;}
  if(j.kind==='resident'&&s.eventGuests?.[j.target]?.active){s.eventGuests[j.target].returnRequested=true;j.status='waiting';j.reason='先走回适合完成这件事的位置';continue;}
  const action=j.steps[j.step];
  if(typeof action==='object'){j.monitor={type:'wait',until:s.time+action.wait};j.status='running';j.updated=s.time;continue;}
  if(s.weather==='rain'&&j.kind==='resident'&&blockedInRain.has(action)){j.status='waiting';j.reason='等雨停后继续';if(s.time-j.started>240){j.status='cancelled';j.reason='等待过久，保留当前日常';}continue;}
  if(j.kind==='resident'&&s.passengers[j.target]?.phase!=='waiting'&&s.passengers[j.target]&&!['alight','stay','ride_once'].includes(action)){j.status='waiting';j.reason='等旅客回到站台';continue;}
  if(j.kind==='resident'&&s.residentActions[j.target]?.action){const r=s.residentActions[j.target],current=RESIDENT_ACTIONS[r.action];
   if(r.action===action){j.monitor={type:'resident',action,before:r.completed};j.status='running';j.updated=s.time;j.reason='已经在做这件事，顺着完成';continue;}
   if(current&&!current.route&&!current.navTask&&!j.target.startsWith('resident.upper_diner')&&!['sip_tea','taste_food','feed_pond','look_pond'].includes(r.action)){r.cancelRemaining=r.cancelRemaining||.65;j.reason='轻轻收住当前动作，再响应你';}
   else j.reason='先完成手里的动作';j.status='waiting';continue;}
  const revision=s.revision,applyJob=(state,input)=>apply(state,input,{id:`intent:${j.id}:${j.step}`,expectedRevision:state.revision});try{
   if(j.kind==='macro'){applyJob(s,{[j.target]:action});j.monitor={type:'immediate'};}
   else if(j.kind==='object'){requestObjectAction(s,j.target,action,catalog,applyJob);j.monitor={type:'immediate'};}
   else j.monitor=startResident(s,j,action,applyJob);
   j.status='running';j.updated=s.time;j.reason=typeof action==='string'?(RESIDENT_ACTIONS[action]?.label||j.label||action):'稍作停留';
  }catch(e){j.status='failed';j.updated=s.time;j.reason=e.message;emit(e.message);}finally{s.revision=revision;}
 }
}
export function cancelIntentJobs(s,targets){for(const j of s.intentRuntime.jobs)if(!targets||targets.includes(j.target)||targets.includes(j.origin_object)){if(!['done','failed'].includes(j.status)){j.status='cancelled';j.updated=s.time;}}}
export function validateIntentRuntime(s){const r=s.intentRuntime;if(!r||!Array.isArray(r.jobs)||r.jobs.length>80||!Array.isArray(r.seen)||!Array.isArray(r.daily))throw Error('生活计划存档无效');for(const j of r.jobs)if(!['pending','waiting','running','done','failed','cancelled'].includes(j.status)||!Number.isInteger(j.step)||!Array.isArray(j.steps)||!Number.isFinite(j.started)||!Number.isFinite(j.updated))throw Error('计划状态无效');}
