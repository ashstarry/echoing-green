import {FIREWORK_FOCUS} from './event-design.mjs?v=cp31-sound-dea918b266ec';
import {eventGuestCandidates,ensureEventTravel} from './event-travel.mjs?v=cp31-sound-dea918b266ec';
import {stableUnit} from './cadence.mjs?v=cp31-sound-dea918b266ec';
import {stimulateTown} from './town-response.mjs?v=cp31-sound-dea918b266ec';
import {navigationGraph,pathTo} from './navigation.mjs?v=cp31-sound-dea918b266ec';
import {moverBlocks} from './motion.mjs?v=cp31-sound-dea918b266ec';

export const EVENT_TIMING={snow:{gather:0,active:38,closing:7},rain:{gather:0,active:42,closing:7},festival:{gather:80,active:28,closing:7},market:{gather:72,active:34,closing:8},supper:{gather:72,active:34,closing:8},reunion:{gather:70,active:28,closing:7},delivery:{gather:3,active:28,closing:5},quiet:{gather:3,active:28,closing:5}};
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
 e.phase='closing';e.phaseAt=s.time;e.until=s.time+(next?6:EVENT_TIMING[e.kind].closing);e.next=next;e.returnSlots=Object.fromEntries(Object.entries(e.slots).filter(([id])=>!s.eventGuests?.[id]));e.slots={};e.slotsAssigned=true;clearPulse(s);
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
 if(kind==='festival'){s.worldEvent={kind:'festival',phase:'prepare',started:s.time,until:e.until,revision:s.worldEvent.revision+1};s.festivalUntil=0;}
 const items=[{kind:'macro',target:kind==='festival'?'festival':['rain','snow'].includes(kind)?'weather':'occasion',action:kind==='festival'?'fireworks':kind},...(e.protectedIds||[]).map(target=>({kind:'resident',target,action:'keep'}))];
 stimulateTown(s,items,{id:e.id});if(s.townResponse)s.townResponse.until=e.until+timing.active+12;
 for(const a of s.actors){if(e.protectedIds?.includes(a.id))continue;a.reservation=null;a.manual=false;a.manualActivity=null;a.activityUntil=0;a.taskRevision=-1;a.wait=Math.min(a.wait,.15+stableUnit(a.id)*1.3);}
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
  emit('这场活动正在进行，大家继续留在自己的位置。');
 }else if(e&&!['release'].includes(e.phase))closeEvent(s,e,emit,descriptor);
 else if((s.weather!=='clear'&&s.weather!==kind)||s.worldEvent.kind==='festival'){
  const previous={id:'scene-'+(++s.eventSequence),kind:s.worldEvent.kind==='festival'?'festival':s.weather,phase:'active',phaseAt:s.time,started:s.time,until:s.time,slots:{},protectedIds:[]};s.sceneEvent=previous;closeEvent(s,previous,emit,descriptor);
 }else startEvent(s,descriptor,emit);
 // Managed fields are activated by the episode, not independently by each job.
 if(d.weather!=='keep')d.weather='keep';if(d.occasion!=='keep')d.occasion='keep';if(d.festival!=='keep')d.festival='keep';
 return d;
}
const festivalSpots=[[.15,-2.9],[1.5,-2.6],[2.9,-2.0],[3.3,-.6],[2.0,.25],[.8,.9],[-.7,.4],[-2.0,-.35],[-3.0,-1.5],[-1.8,-2.6],[-.5,-3.5]];
const marketSpots=[[-3.0,1.1],[-1.6,1.9],[-.2,2.7],[1.1,3.4],[-2.1,.05],[-.7,.85],[.7,1.65],[2.1,2.4],[-1.1,-1.1],[.3,-.25],[2.7,.1]];
function minimumAssignment(cost){
 const n=cost.length,m=cost[0].length,u=Array(n+1).fill(0),v=Array(m+1).fill(0),p=Array(m+1).fill(0),way=Array(m+1).fill(0);
 for(let i=1;i<=n;i++){p[0]=i;let j0=0;const min=Array(m+1).fill(Infinity),used=Array(m+1).fill(false);do{used[j0]=true;const i0=p[j0];let delta=Infinity,j1=0;for(let j=1;j<=m;j++)if(!used[j]){const cur=cost[i0-1][j-1]-u[i0]-v[j];if(cur<min[j]){min[j]=cur;way[j]=j0;}if(min[j]<delta){delta=min[j];j1=j;}}for(let j=0;j<=m;j++)if(used[j]){u[p[j]]+=delta;v[j]-=delta;}else min[j]-=delta;j0=j1;}while(p[j0]);do{const j1=way[j0];p[j0]=p[j1];j0=j1;}while(j0);}
 const result=Array(n).fill(-1);for(let j=1;j<=m;j++)if(p[j])result[p[j]-1]=j-1;return result;
}
export function assignEventSlots(s,nav,e){
 const bike=s.movers?.['bicycle.street_bicycle'],parked=bike?.tripState==='parked';
 if(e.slotsAssigned&&!e.openRideLane&&parked&&e.phase==='gather'&&['festival','market','supper','reunion'].includes(e.kind)){e.slotsAssigned=false;e.slots={};for(const a of s.actors)if(!e.protectedIds?.includes(a.id)){a.responseReplan=true;a.taskRevision=-1;a.reservation=null;}s.planRevision++;}
 if(!['festival','market','supper','reunion'].includes(e.kind)||e.slotsAssigned)return;if(['festival','market','supper','reunion'].includes(e.kind)&&!parked&&s.time-e.phaseAt<7)return;e.slotsAssigned=true;e.openRideLane=parked&&['festival','market','supper','reunion'].includes(e.kind);s.planRevision++;
 const allowed=p=>Object.entries(nav.activities.clips||{}).filter(([,c])=>['creature_walk','ride'].includes(c.motion)).every(([id,c])=>(c.motion==='creature_walk'||c.motion==='ride'&&e.openRideLane)?!moverBlocks(p,{...s.movers[id],footDown:1},c,nav.radius):!c.samples.some((q,k)=>k%8===0&&distance(p,q)<(c.motion==='ride'?.72:(c.dynamic_clearance||c.radius||.3)+.50)));
 const portalClear=p=>Object.values(nav.activities.eventTrips||{}).every(c=>distance(p,nav.nodes[c.portal])>1.65&&c.entry.every(q=>Math.abs(p[2]-q[2])>1.4||distance(p,q)>.94));
 const standing=new Set(nav.nodes.flatMap((p,i)=>!nav.noStopping.has(i)||e.openRideLane&&allowed(p)?[i]:[]));
 const candidates=eventGuestCandidates(s,nav,e),candidateIds=new Set(candidates.map(a=>a.id));const actors=[...s.actors.filter(a=>a.mobile&&!a.eventOnly&&!candidateIds.has(a.id)&&!e.protectedIds?.includes(a.id)),...candidates],kite=actors.find(a=>a.id==='resident.kite_child');
 const graph=navigationGraph(nav),used=[],pool=[];
 if(kite){const k=nav.nodes.map((p,i)=>({p,i})).filter(({p,i})=>graph.components[i]===graph.components[kite.node]&&p[0]>2.3&&p[0]<3.8&&p[1]>-1.7&&p[1]<.65).sort((a,b)=>distance(a.p,[2.55,-1.35])-distance(b.p,[2.55,-1.35]))[0]?.i??kite.node;e.slots[kite.id]=k;used.push(nav.nodes[k]);}
 const guestHints={'resident.water_companion':[2.4,1.4],'resident.water_visitor':[2.4,.15],'resident.assistant_gardener':[2.4,2.75],'resident.gardener':[.55,3.1],'resident.quiet_reader':[1.6,4.0],'resident.returning_resident':[-.7,2.4],'resident.child_listener':[-3.5,-1.7],'resident.listener':[-.5,-2.8]};
 for(const a of actors.filter(a=>s.eventGuests?.[a.id])){const hint=guestHints[a.id]||a.p;const candidate=nav.nodes.map((p,i)=>({p,i,score:distance(p,hint)})).filter(({p,i})=>graph.components[i]===graph.components[a.node]&&standing.has(i)&&portalClear(p)&&used.every(q=>distance(p,q)>1.10)).sort((a,b)=>a.score-b.score)[0];if(candidate){e.slots[a.id]=candidate.i;used.push(candidate.p);}}
 const rest=actors.filter(a=>a!==kite&&!s.eventGuests?.[a.id]);if(!rest.length)return;const points=[...(e.kind==='festival'||e.kind==='reunion'?festivalSpots:festivalSpots.map(([x,y])=>[x-.2,y+(nav.activities.marketLayoutForward??.65)])),...Array.from({length:30},(_,i)=>[-4.0+(i%6)*1.25,-2.8+Math.floor(i/6)*1.2])];
 for(const hint of points){
  const candidates=nav.nodes.map((p,i)=>({p,i,score:distance(p,hint)})).filter(({p,i})=>graph.components[i]===graph.components[rest[0]?.node]&&standing.has(i)&&p[0]<1.0&&p[1]<2.6&&portalClear(p)&&used.every(q=>distance(p,q)>1.08)&&Object.values(s.localWalkers||{}).every(w=>Math.abs(w.root[2]-p[2])>1.4||distance(p,w.root)>1.15));
  candidates.sort((a,b)=>a.score-b.score);if(candidates[0]){pool.push(candidates[0].i);used.push(candidates[0].p);}if(pool.length>=rest.length)break;
 }
 if(pool.length<rest.length)return;
 const chosen=minimumAssignment(rest.map(a=>pool.map(i=>distance(a.p,nav.nodes[i]))));
 for(let i=0;i<rest.length;i++)e.slots[rest[i].id]=pool[chosen[i]];
}
function adaptGathering(s,nav,e){
 if(!['gather','active'].includes(e.phase)||s.time-e.started<9||s.time<(e.nextAdapt||0))return;e.nextAdapt=s.time+1.5;
 const market=['market','supper'].includes(e.kind),inZone=p=>market?((p[0]+1)*.8+(p[1]-2)*.6>-4.5&&(p[0]+1)*.8+(p[1]-2)*.6<4.5&&(p[0]+1)*.6-(p[1]-2)*.8>-.65&&(p[0]+1)*.6-(p[1]-2)*.8<4.4):distance(p,[-.3,-.6])<4;
 for(const a of s.actors){if(!a.mobile||e.slots[a.id]===undefined||a.id==='resident.kite_child'||a.node===e.slots[a.id]&&a.reservation===a.node&&!a.path.length)continue;
  const c=nav.nodes[a.node],others=s.actors.filter(b=>b!==a&&Math.abs(b.p[2]-a.p[2])<1.4);
  const clear=p=>(s.eventGuests?.[a.id]||p[0]<1.0&&p[1]<2.6)&&Object.entries(e.slots).every(([id,n])=>id===a.id||distance(p,nav.nodes[n])>1.02)&&Object.entries(s.movers).every(([id,m])=>!['creature_walk','ride'].includes(nav.activities.clips[id].motion)||!moverBlocks(p,m,nav.activities.clips[id],nav.radius))&&others.every(b=>distance(p,b.p)>nav.radius*2+.02)&&Object.values(nav.activities.eventTrips||{}).every(t=>distance(p,nav.nodes[t.portal])>1.65&&t.entry.every(q=>Math.abs(q[2]-p[2])>1.4||distance(q,p)>.93));
  // A physically reached, clear nearby place can replace an obstructed reserved
  // spot. The resident is never teleported or counted as arriving off screen.
  if(inZone(a.p)&&distance(a.p,c)<.16&&clear(a.p)&&(a.blocked>.3||!a.path.length||s.time-e.started>16)){
   e.slots[a.id]=a.node;a.reservation=a.node;a.path=[];a.target=null;a.wait=.4;a.mode='idle';a.task=e.kind==='festival'?'fireworks':'browse';a.lookTarget=e.kind==='festival'?FIREWORK_FOCUS.slice():[-1,3,1.4];s.residents[a.id].activity=a.task;s.residents[a.id].reason='在这里也看得清，给后来的人留一条路';continue;
  }
  if(a.blocked<.3&&a.path.length)continue;
  const blocked=new Set(nav.nodes.flatMap((p,i)=>others.some(b=>distance(p,b.p)<.96)?[i]:[]));blocked.delete(a.node);
  const candidates=nav.nodes.map((p,i)=>({p,i})).filter(({p,i})=>inZone(p)&&clear(p)&&navigationGraph(nav).components[i]===navigationGraph(nav).components[a.node]).sort((x,y)=>distance(x.p,a.p)-distance(y.p,a.p));
  for(const c of candidates.slice(0,16)){const path=pathTo(nav,a.node,c.i,blocked);if(path.length<2)continue;e.slots[a.id]=c.i;a.reservation=null;a.responseDestination=c.i;a.taskRevision=-1;a.responseReplan=true;a.path=[];a.wait=.15;break;}
 }
}
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
   if(e.kind==='festival'){s.worldEvent={kind:'festival',phase:'show',started:s.time,until:e.until,revision:s.worldEvent.revision+1};s.festivalStarted=s.time;s.festivalUntil=e.until;s.festivalStop=null;emit('大家站定看向夜空，第一束红金花火升起。');}
   else if(['market','supper'].includes(e.kind))emit('摊前排起了小队，热食一份份递到客人手里。');
  }
 }else if(e.phase==='active'&&s.time>=e.until)closeEvent(s,e,emit);
 else if(e.phase==='closing'&&s.time>=e.until){if(e.next){startEvent(s,e.next,emit);return;}finishSky(s);s.weather='clear';s.lastWeather='clear';s.occasion='ordinary';s.lastOccasion='ordinary';s.afterRainUntil=0;e.phase='release';e.phaseAt=s.time;e.until=s.time+13;clearPulse(s);s.planRevision++;
  for(const a of s.actors){if(e.protectedIds?.includes(a.id))continue;a.taskRevision=-1;a.reservation=null;a.responseReplan=true;a.wait=.15+stableUnit(a.id)*2.7;}
  stimulateTown(s,[],{id:e.id+'-return',opening:true});emit('这一场热闹结束，街坊分头散开，小镇回到日常。');
 }else if(e.phase==='release'&&s.time>=e.until){if(Object.values(s.eventGuests||{}).some(g=>g.active)&&s.time-e.phaseAt<30){e.until=s.time+1;return;}for(const g of Object.values(s.eventGuests||{}))if(g.active)g.returnRequested=true;s.sceneEvent=null;s.festivalNextAt=s.time+180;s.planRevision++;for(const a of s.actors)if(a.mobile){a.taskRevision=-1;a.reservation=null;a.wait=.2+stableUnit(a.id)*1.5;}stimulateTown(s,[],{id:e.id+'-daily',opening:true});}
}
export function validateSceneEvents(s,nav){ensureSceneEvents(s);const e=s.sceneEvent;if(e&&(!Object.hasOwn(EVENT_TIMING,e.kind)||!['gather','active','closing','release'].includes(e.phase)||![e.phaseAt,e.started,e.until].every(Number.isFinite)||!e.slots||e.next&&!Object.hasOwn(EVENT_TIMING,e.next.kind)))throw Error('Scene event save is invalid');if(e&&Object.entries(e.slots).some(([id,n])=>!s.actors.some(a=>a.id===id)&&!s.eventGuests?.[id]||!Number.isInteger(n)||!nav.nodes[n]))throw Error('Scene event slot is invalid');if(Object.values(s.eventWeather).some(x=>!Number.isFinite(x)||x<0||x>1))throw Error('Weather blend save is invalid');}
