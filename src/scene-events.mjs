import {assignGroup,GROUP_KINDS} from './group-layout.mjs?v=cp32-events-dea0a76ba5ff';
import {FIREWORK_FOCUS} from './event-design.mjs?v=cp32-events-dea0a76ba5ff';
import {eventGuestCandidates,ensureEventTravel} from './event-travel.mjs?v=cp32-events-dea0a76ba5ff';
import {stableUnit} from './cadence.mjs?v=cp32-events-dea0a76ba5ff';
import {stimulateTown} from './town-response.mjs?v=cp32-events-dea0a76ba5ff';
import {navigationGraph,pathTo} from './navigation.mjs?v=cp32-events-dea0a76ba5ff';
import {moverBlocks} from './motion.mjs?v=cp32-events-dea0a76ba5ff';

export const EVENT_TIMING={snow:{gather:0,active:38,closing:7},rain:{gather:0,active:42,closing:7},festival:{gather:24,active:38,closing:7},market:{gather:22,active:38,closing:8},supper:{gather:22,active:38,closing:8},reunion:{gather:22,active:34,closing:7},delivery:{gather:3,active:28,closing:5},quiet:{gather:3,active:28,closing:5}};
const live=j=>!['done','failed','cancelled'].includes(j.status);
const distance=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
export function ensureSceneEvents(s){
 if(!Object.hasOwn(s,'sceneEvent')){
  const kind=['rain','snow'].includes(s.weather)?s.weather:s.worldEvent?.kind==='festival'?'festival':Object.hasOwn(EVENT_TIMING,s.occasion)?s.occasion:null;
  s.sceneEvent=null;
  if(kind){const old=s.worldEvent,show=kind==='festival'&&old.phase==='show'&&old.until>s.time,phase=kind==='festival'&&!show?'gather':'active';
   s.sceneEvent={id:'legacy-'+s.tick,kind,phase,phaseAt:s.time,started:s.time,until:show?old.until:s.time+(phase==='gather'?EVENT_TIMING[kind].gather:EVENT_TIMING[kind].active),slots:{},ready:0,next:null,protectedIds:s.actors.filter(a=>a.manual).map(a=>a.id),explicitDay:true};
   s.weather=['rain','snow'].includes(kind)?kind:'clear';s.occasion=['rain','snow','festival'].includes(kind)?'ordinary':kind;s.lastWeather=s.weather;s.lastOccasion=s.occasion;s.planRevision++;
   if(kind!=='festival'){s.worldEvent={kind:'ordinary',phase:'ongoing',started:s.time,until:0,revision:old.revision+1};s.festivalUntil=0;s.festivalStop=s.time;}
   else if(!show){s.worldEvent={kind:'festival',phase:'prepare',started:s.time,until:s.sceneEvent.until,revision:old.revision+1};s.festivalUntil=0;}
  }
 }
 s.eventSequence??=0;s.eventWeather??={rain:s.weather==='rain'?1:0,snow:s.weather==='snow'?1:0,cover:0};
}
export function eventKind(d){if(d.festival==='fireworks')return 'festival';if(d.weather==='snow'||d.weather==='rain')return d.weather;if(EVENT_TIMING[d.occasion])return d.occasion;return null;}
function clearPulse(s){s.townResponse=null;for(const a of s.actors){a.responseUntil=0;a.responseDestination=null;a.responseReplan=false;}}
function finishSky(s){if(s.festivalUntil>s.time){s.festivalStop=s.time;s.festivalUntil=Math.min(s.festivalUntil,s.time+5.5);}s.worldEvent={kind:'ordinary',phase:'ongoing',started:s.time,until:0,revision:s.worldEvent.revision+1};}
function closeEvent(s,e,emit,next=null){
 if(e.phase==='closing'){e.next=next;return;}
 e.phase='closing';e.phaseAt=s.time;e.until=s.time+(next?7:EVENT_TIMING[e.kind].closing);e.next=next;e.returnSlots=Object.fromEntries(Object.entries(e.slots).filter(([id])=>!s.eventGuests?.[id]));e.slots={};e.slotsAssigned=true;clearPulse(s);
 if(['rain','snow'].includes(e.kind)){s.weather='clear';s.rainActive=false;s.afterRainUntil=0;emit(e.kind==='snow'?'雪势渐歇，屋顶的薄雪慢慢融化。':'雨势渐歇，居民收好雨具。');}
 if(e.kind==='festival'){s.festivalStop=s.time;s.festivalUntil=Math.min(s.festivalUntil,s.time+5.5);s.worldEvent={kind:'festival',phase:'linger',started:s.time,until:e.until,revision:s.worldEvent.revision+1};emit('最后一束花火散去，大家鼓掌道别。');}
 if(['market','supper'].includes(e.kind))emit('摊主收好餐具，最后的客人互相道别，晚市准备收摊。');
 if(e.kind==='reunion')emit('邻居们挥手道别，准备回到各自的日常。');
 s.planRevision++;
}
function startEvent(s,descriptor,emit){
 const timing=EVENT_TIMING[descriptor.kind],kind=descriptor.kind;
 finishSky(s);clearPulse(s);if(!descriptor.automatic)s.festivalAuto=false;s.afterRainUntil=0;
 s.weather=['snow','rain'].includes(kind)?kind:'clear';s.rainActive=s.weather==='rain';s.lastWeather=s.weather;s.weatherChangedAt=s.time;
 s.occasion=['market','supper','reunion','delivery','quiet'].includes(kind)?kind:'ordinary';s.lastOccasion=s.occasion;s.occasionUntil=s.time+timing.gather+timing.active;
 if(['festival','market'].includes(kind)&&!descriptor.explicitDay)s.day_phase='night';
 const e=s.sceneEvent={...descriptor,phase:timing.gather?'gather':'active',phaseAt:s.time,started:s.time,until:s.time+(timing.gather||timing.active),slots:{},ready:0,next:null};
 if(kind==='festival'){s.worldEvent={kind:'festival',phase:'prepare',started:s.time,until:e.until,revision:s.worldEvent.revision+1};s.festivalStarted=s.time;s.festivalUntil=s.time+timing.gather+timing.active+5.5;s.festivalStop=null;}
 const items=[{kind:'macro',target:kind==='festival'?'festival':['rain','snow'].includes(kind)?'weather':'occasion',action:kind==='festival'?'fireworks':kind},...(e.protectedIds||[]).map(target=>({kind:'resident',target,action:'keep'}))];
 stimulateTown(s,items,{id:e.id});if(s.townResponse)s.townResponse.until=e.until+timing.active+12;
 for(const a of s.actors){if(e.protectedIds?.includes(a.id))continue;a.reservation=null;a.manual=false;a.manualActivity=null;a.activityUntil=0;a.taskRevision=-1;a.localActionUntil=0;a.path=[];a.wait=.08+stableUnit(a.id)*.6;const r=s.residentActions[a.id];if(r&&!r.requested){r.action=null;r.queued=null;r.cancelRemaining=0;r.nextAt=s.time+.5;}}
 s.planRevision++;
 const text={snow:'大一些的纸雪落下，屋檐和路边渐渐留下一层白。',rain:'雨来了，街坊收住手里的事，分头找地方等雨停。',festival:'花火即将开始，街坊往广场空位聚拢。',market:'晚市开张，大家走向酒楼摊前，排队等一份热食。',supper:'热饭端上柜台，街坊往餐厅聚拢。',reunion:'邻居们相约走近，找一处地方聊聊。',delivery:'邮差开始送信，街坊留意门前的动静。',quiet:'小镇放轻脚步，留一段安静的晚风。'};
 emit(text[kind]);return e;
}
// One foreground event owns weather/crowd choreography. A newer event replaces
// the pending one, but only starts after the current event's visible closing.
export function requestSceneEvent(s,input,emit,{automatic=false}={}){
 ensureSceneEvents(s);const d={...input},kind=eventKind(d),e=s.sceneEvent;
 if(!kind){
  const stops=e&&((['rain','snow'].includes(e.kind)&&d.weather==='clear')||(e.kind==='festival'&&d.festival==='quiet')||(!['rain','snow','festival'].includes(e.kind)&&d.occasion==='ordinary'));
  if(stops)closeEvent(s,e,emit);
  if(e?.next&&((['rain','snow'].includes(e.next.kind)&&d.weather==='clear')||(e.next.kind==='festival'&&d.festival==='quiet')||d.occasion==='ordinary'))e.next=null;
  return d;
 }
 const protectedIds=s.intentRuntime.jobs.filter(j=>j.kind==='resident'&&live(j)&&j.requestId===s.intentRuntime.lastReceipt?.id).map(j=>j.target);
 const descriptor={id:'scene-'+(++s.eventSequence),kind,protectedIds,automatic,explicitDay:d.day_phase&&d.day_phase!=='keep'};
 if(e&&e.kind===kind&&!['closing','release'].includes(e.phase)){
  e.until=Math.min(e.started+EVENT_TIMING[kind].gather+EVENT_TIMING[kind].active+12,Math.max(e.until,s.time+12));
  if(e.kind==='festival'){if(s.time-s.festivalStarted>4)s.festivalStarted=s.time;s.festivalStop=null;s.festivalUntil=e.until+(e.phase==='gather'?EVENT_TIMING.festival.active:0)+5.5;s.worldEvent.until=e.until;}
  emit('这场活动正在进行，大家继续留在自己的位置。');
 }else if(e&&!['release'].includes(e.phase))closeEvent(s,e,emit,descriptor);
 else if((s.weather!=='clear'&&s.weather!==kind)||s.worldEvent.kind==='festival'){
  const previous={id:'scene-'+(++s.eventSequence),kind:s.worldEvent.kind==='festival'?'festival':s.weather,phase:'active',phaseAt:s.time,started:s.time,until:s.time,slots:{},protectedIds:[]};s.sceneEvent=previous;closeEvent(s,previous,emit,descriptor);
 }else startEvent(s,descriptor,emit);
 // Managed fields are activated by the episode, not independently by each job.
 if(d.weather!=='keep')d.weather='keep';if(d.occasion!=='keep')d.occasion='keep';if(d.festival!=='keep')d.festival='keep';
 return d;
}
export function assignEventSlots(s,nav,e){
 if(!GROUP_KINDS.has(e.kind)||e.slotsAssigned)return;
 const guests=eventGuestCandidates(s,nav,e),ids=new Set(guests.map(a=>a.id));
 const candidates=[...s.actors.filter(a=>a.mobile&&!a.eventOnly&&!ids.has(a.id)&&!e.protectedIds?.includes(a.id)),...guests];
 e.slots={};e.slotsAssigned=true;e.openRideLane=true;e.layout='cp32';assignGroup(s,nav,e,candidates);s.planRevision++;
 for(const a of s.actors)if(e.slots[a.id]!==undefined){a.manual=false;a.manualActivity=null;a.path=[];a.wait=.10+stableUnit(a.id)*.7;a.localActionUntil=0;a.taskRevision=-1;a.reservation=null;}
}
function adaptGathering(){} // Event destinations stay fixed: a queue cannot dissolve into arbitrary nearby cells.
export function sceneTask(s,a){const e=s.sceneEvent;if(!e||e.protectedIds?.includes(a.id))return null;if(e.phase==='release')return e.returnSlots?.[a.id]!==undefined?'chat':null;
 if(e.phase==='gather'&&!e.slotsAssigned)return a.task;
 if(e.phase==='closing')return e.kind==='festival'?'fireworks':['market','supper'].includes(e.kind)?'browse':null;
 return e.kind==='festival'?'fireworks':['market','supper'].includes(e.kind)?'browse':e.kind==='reunion'?'chat':e.kind==='snow'?'snow':e.kind==='rain'?'shelter':null;
}
export function holdsEventPlace(s,a){if(a.guestReturnNode!==undefined&&a.node===a.guestReturnNode&&!a.path.length)return true;const e=s.sceneEvent;if(e&&['closing','release'].includes(e.phase)&&e.returnSlots?.[a.id]!==undefined&&a.node===e.returnSlots[a.id]&&!a.path.length)return true;return !!(e&&['gather','active','closing'].includes(e.phase)&&e.slots[a.id]!==undefined&&a.reservation===e.slots[a.id]&&a.node===e.slots[a.id]&&!a.path.length);}
export function advanceSceneEvent(s,nav,dt,emit){
 ensureSceneEvents(s);const w=s.eventWeather;w.rain+=(Number(s.weather==='rain')-w.rain)*Math.min(1,dt*(s.weather==='rain'?1.4:.65));w.snow+=(Number(s.weather==='snow')-w.snow)*Math.min(1,dt*(s.weather==='snow'?1.1:.55));w.cover=Math.max(0,Math.min(.58,w.cover+(s.weather==='snow'?.022:-.055)*dt));
 const e=s.sceneEvent;if(!e)return;assignEventSlots(s,nav,e);adaptGathering(s,nav,e);
 if(e.phase==='gather'){
  const ids=Object.keys(e.slots);e.ready=ids.filter(id=>{const a=s.actors.find(a=>a.id===id),g=s.eventGuests?.[id];return a?!a.path.length&&a.reservation===e.slots[id]&&distance(a.p,nav.nodes[e.slots[id]])<.18:g?.phase==='hold'&&distance(g.p,nav.nodes[e.slots[id]])<.18;}).length;
  const farGuests=['resident.quiet_reader','resident.water_visitor','resident.water_companion'].filter(id=>ids.includes(id));const enough=ids.length&&e.ready>=Math.ceil(ids.length*.80)&&farGuests.every(id=>s.eventGuests?.[id]?.phase==='hold');
  if((s.time-e.phaseAt>=8&&enough)||s.time>=e.until){e.phase='active';e.phaseAt=s.time;e.until=s.time+EVENT_TIMING[e.kind].active;s.planRevision++;
   if(e.kind==='festival'){s.worldEvent={kind:'festival',phase:'show',started:s.time,until:e.until,revision:s.worldEvent.revision+1};s.festivalUntil=e.until+5.5;s.festivalStop=null;emit('大家站定看向夜空，第一束红金花火升起。');}
   else if(['market','supper'].includes(e.kind))emit('摊前排起了小队，热食一份份递到客人手里。');
  }
 }else if(e.phase==='active'&&s.time>=e.until)closeEvent(s,e,emit);
 else if(e.phase==='closing'&&s.time>=e.until){if(e.next){startEvent(s,e.next,emit);return;}finishSky(s);s.weather='clear';s.lastWeather='clear';s.occasion='ordinary';s.lastOccasion='ordinary';s.afterRainUntil=0;e.phase='release';e.phaseAt=s.time;e.until=s.time+13;clearPulse(s);s.planRevision++;
  for(const a of s.actors){if(e.protectedIds?.includes(a.id))continue;a.taskRevision=-1;a.reservation=null;a.responseReplan=true;a.wait=.15+stableUnit(a.id)*2.7;}
  stimulateTown(s,[],{id:e.id+'-return',opening:true});emit('这一场热闹结束，街坊分头散开，小镇回到日常。');
 }else if(e.phase==='release'&&s.time>=e.until){if(Object.values(s.eventGuests||{}).some(g=>g.active)&&s.time-e.phaseAt<30){e.until=s.time+1;return;}for(const g of Object.values(s.eventGuests||{}))if(g.active)g.returnRequested=true;s.sceneEvent=null;s.festivalNextAt=s.time+180;s.planRevision++;for(const a of s.actors)if(a.mobile){a.taskRevision=-1;a.reservation=null;a.wait=.2+stableUnit(a.id)*1.5;}stimulateTown(s,[],{id:e.id+'-daily',opening:true});}
}
export function validateSceneEvents(s,nav){ensureSceneEvents(s);const e=s.sceneEvent;if(e&&(!Object.hasOwn(EVENT_TIMING,e.kind)||!['gather','active','closing','release'].includes(e.phase)||![e.phaseAt,e.started,e.until].every(Number.isFinite)||!e.slots||e.next&&!Object.hasOwn(EVENT_TIMING,e.next.kind)))throw Error('Scene event save is invalid');if(e&&Object.entries(e.slots).some(([id,n])=>!s.actors.some(a=>a.id===id)&&!s.eventGuests?.[id]||!Number.isInteger(n)||!nav.nodes[n]))throw Error('Scene event slot is invalid');if(Object.values(s.eventWeather).some(x=>!Number.isFinite(x)||x<0||x>1))throw Error('Weather blend save is invalid');}
