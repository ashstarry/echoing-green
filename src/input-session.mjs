import {lanternDisplay} from './lantern-scene.mjs?v=cp50-friendly-fox-e903b4ae61c3';
import {actionAvailability} from './action-availability.mjs?v=cp50-friendly-fox-e903b4ae61c3';
import {requestSceneEvent,eventKind} from './scene-events.mjs?v=cp50-friendly-fox-e903b4ae61c3';
import {requestCloud} from './local-cloud.mjs?v=cp50-friendly-fox-e903b4ae61c3';
import {interactionStep} from './interaction-sequence.mjs?v=cp50-friendly-fox-e903b4ae61c3';
import {RESIDENT_ACTIONS} from './resident-actions.mjs?v=cp50-friendly-fox-e903b4ae61c3';
import {PROFILES} from './community.mjs?v=cp50-friendly-fox-e903b4ae61c3';
import {FIREWORK_BURSTS,FIREWORK_FLIGHT} from './firework-score.mjs?v=cp50-friendly-fox-e903b4ae61c3';
const terminal=j=>['done','cancelled','failed'].includes(j.status);
export const INPUT_IDLE_SECONDS=2.8;
export const inputBusy=s=>['listening','running','closing'].includes(s.inputSession?.phase);
export function beginInput(s,items=[],{source='menu',listening=false}={}){if(inputBusy(s))return{accepted:false,reason:'busy'};for(const item of items){const a=actionAvailability(s,item);if(!a.available)throw Error(a.reason);}for(const item of items)if(item.kind==='resident'&&RESIDENT_ACTIONS[item.action]?.pose){const a=s.actors.find(a=>a.id===item.target),r=s.residentActions[item.target];if(a?.mobile&&!s.eventGuests?.[item.target]?.active){a.path=[];a.speed=0;a.actualSpeed=0;a.wait=.2;a.mode='idle';a.reservation=a.node;a.localActionUntil=0;a.manualActivity=null;}if(r?.action&&!RESIDENT_ACTIONS[r.action]?.route&&!RESIDENT_ACTIONS[r.action]?.navTask)r.cancelRemaining=.45;}const id='input-'+s.tick+'-'+s.revision;s.inputSession={id,source,phase:listening?'listening':'running',started:s.time,activeAt:s.time,lastProgress:s.time,lastSample:s.time-.25,items:structuredClone(items),observed:{},tracked:{},progressSamples:0,requestIds:[],baseStops:s.movers?.['bicycle.street_bicycle']?.completedStops||0};return{accepted:true,id};}
export function activateInput(s,items,requestId){const q=s.inputSession;if(!q)return;q.phase='running';q.activeAt=s.time;q.lastProgress=s.time;q.items=structuredClone(items);const kind=eventKind(Object.fromEntries(items.filter(i=>i.kind==='macro').map(i=>[i.target,i.action])));q.expectedSceneKind=kind;if(kind&&s.sceneEvent?.kind===kind)q.sceneId=s.sceneEvent.id;else if(kind&&s.sceneEvent?.next?.kind===kind){q.sceneId=s.sceneEvent.next.id;q.transitionId=s.sceneEvent.id;}if(requestId)q.requestIds.push(requestId);}
export function abortInput(s,reason='not_applied'){if(s.inputSession){s.inputSession.phase='done';s.inputSession.ended=s.time;s.inputSession.outcome=reason;}}
export function runInput(s,items,run,options={}){const opened=beginInput(s,items,options);if(!opened.accepted)throw Error('小镇还在回应上一句话，请等这一段结束。');try{const result=run();if(result?.accepted===false){abortInput(s,result.reason);return result;}activateInput(s,items,result?.receipt?.id);return result;}catch(error){abortInput(s,'not_applied');throw error;}}
function stopOwned(s,q){
 if(q.items.some(i=>['cloud','weather'].includes(i.target))&&s.craftWorld.background?.started>=q.started-.1)s.craftWorld.background.phase='closing';
 if(q.sceneId&&s.sceneEvent?.next?.id===q.sceneId)s.sceneEvent.next=null;
 for(const j of s.intentRuntime.jobs)if(q.requestIds.includes(j.requestId)&&!terminal(j)){j.status='cancelled';j.reason='这一段互动已经收束';j.updated=s.time;}
 for(const item of q.items){if(item.kind==='resident'){const r=s.residentActions[item.target];if(r){r.queued=null;r.queuedByUser=false;if(r.action)r.cancelRemaining=.45;r.requested=false;}const a=s.actors.find(a=>a.id===item.target);if(a){a.manualActivity=null;a.activityUntil=s.time;a.localActionUntil=s.time;a.wait=Math.min(a.wait,.4);}}}
 if(q.sceneId&&s.sceneEvent?.id===q.sceneId){const e=s.sceneEvent;delete e.paperRepeat;delete e.craftRepeat;delete e.neighborhoodNext;e.next=null;requestSceneEvent(s,{occasion:'ordinary',weather:'clear',festival:'quiet',craft:'rest',paper:'rest',neighborhood:'rest'},()=>{});e.until=Math.min(e.until,s.time+1.5);s.festivalAuto=false;}
 for(const [name,w] of [['paper',s.paperWorld],['neighborhood',s.neighborhoodWorld],['craft',s.craftWorld]])if(w&&(w.eventId===q.sceneId||q.items.some(i=>i.kind==='macro'&&i.target===name)||name==='craft'&&q.items.some(i=>['weather','cloud'].includes(i.target))&&w.background?.started>=q.started-.1)){w.pending=null;for(const j of w.jobs||[])if(j.status==='running')j.cancelClock??=0;}
 if(q.items.some(i=>i.target==='cloud'))requestCloud(s,'rest');
 if(q.items.some(i=>i.target==='boat.pond_boat')&&s.boatJourney.phase!=='moored'&&s.objectControls['boat.pond_boat'])s.objectControls['boat.pond_boat']={...s.objectControls['boat.pond_boat'],action:'rest',target:0,started:s.time};
 if(q.items.some(i=>i.target==='animal.garden_fox')){const f=s.foxBehavior;if(f){f.command=null;f.completedControl=f.seenControl;if(f.phase==='walk'){f.route=null;f.phase='look';f.clock=0;f.duration=3;}}}
 if(q.items.some(i=>i.target==='journey')){s.trainJourney.stationHold=false;const d=s.craftWorld.delivery;if(d&&!['delivered','cancelled'].includes(d.phase))d.cancel=true;}
}
function close(s,q,outcome){if(q.phase==='closing')return;q.phase='closing';q.closingAt=s.time;q.outcome=outcome;stopOwned(s,q);}
function sample(s,q){const values={},ids=new Set(q.items.filter(i=>i.kind==='resident').map(i=>i.target)),macro=new Set(q.items.filter(i=>i.kind==='macro').map(i=>i.target));
 const put=(key,value)=>{if(Number.isFinite(value))values[key]=value;},point=(key,p)=>p?.slice(0,3).forEach((v,k)=>put(key+k,v));
 const e=s.sceneEvent;if(e&&e.started>=q.started-.1&&!q.sceneId)q.sceneId=e.id;
 const ownScene=!!e&&e.id===q.sceneId,transition=!!e&&e.id===q.transitionId;if(ownScene||transition){if(transition&&s.time-e.phaseAt<2.6)put('transition.props',s.time-e.phaseAt);for(const id of Object.keys({...e.slots,...e.returnSlots}))ids.add(id);for(const[id,g]of Object.entries(s.eventGuests||{}))if(g.active)ids.add(id);
  if(e.kind==='festival'&&s.festivalUntil>s.time){const age=s.time-s.festivalStarted,stop=s.festivalStop===null?Infinity:s.festivalStop-s.festivalStarted;if(FIREWORK_BURSTS.some(at=>at-FIREWORK_FLIGHT<=stop&&age>=at-FIREWORK_FLIGHT&&age<at+5.8))put('firework',Math.floor(age*4));}
  for(const kind of['rain','snow','cover'])put('weather.'+kind,s.eventWeather[kind]);
 }
 if(ownScene&&e.kind==='lantern')for(let lamp=0;lamp<14;lamp++)put('lantern.'+lamp,lanternDisplay(s,lamp));
 if(ownScene)for(const a of s.actors)if((a.eventYieldUntil||0)-5>=q.started-.1&&(a.courtesyDestination!==undefined||a.detouring))ids.add(a.id);
 const pulse=s.townResponse;if(pulse&&pulse.id!=='opening'&&pulse.theme!=='opening')for(const p of pulse.pending||[])if(p.dispatched!==undefined&&p.dispatched>=q.started-.1)ids.add(p.id);
 for(const [name,w]of [['paper',s.paperWorld],['neighbor',s.neighborhoodWorld],['craft',s.craftWorld]]){
  if(!w||!(ownScene||macro.has(name==='neighbor'?'neighborhood':name)||name==='craft'&&(macro.has('weather')||macro.has('cloud'))&&w.background?.started>=q.started-.1))continue;
  for(const j of w.jobs||[]){if(j.status==='running'){ids.add(j.actor);const action=interactionStep(j)?.action;if(action&&!['approach','carry','pair_walk','wait_for','dry','admire'].includes(action)&&!(action==='read'&&j.clock>.8))put(name+'.pose.'+j.id,j.step*100+Math.min(j.clock,20));}}
  for(const p of w.props||w.notes||[]){if(p.created<q.started-.1)continue;put(name+'.prop.'+p.id,JSON.stringify([p.location,p.owner,p.open,p.placedAt]).split('').reduce((n,c)=>n+c.charCodeAt(0),0));}
  for(const k of['door','window','bloom','steamer'])put(name+'.'+k,w[k]);
 }
 if(macro.has('cloud')){const c=s.localCloud;point('cloud',c.center);put('rain',c.rain);for(const id of Object.keys(c.exposures||{}))ids.add(id);}
 if(macro.has('journey')){const t=s.trainJourney;for(const id of['resident.station_traveler','resident.waiting_passenger','resident.waiting_passenger_2','resident.station_attendant'])ids.add(id);if(['expecting','collecting','receiving','returning_gift'].includes(t.phase)){put('gift.pickup',s.time-t.phaseAt);put('gift.walk',s.craftWorld.delivery.boardClock);}if(['boarding','onboard','returning'].includes(t.phase)){put('train',s.train.distance);put('passenger',s.passengers['resident.station_traveler'].clock);put('door',s.passengers['resident.station_traveler'].door);}}
 for(const i of q.items){if(i.target==='boat.pond_boat'){point('boat',s.boatJourney.p);put('rope',s.boatJourney.tether);put('oar',s.boatJourney.fold);}else if(i.target==='animal.garden_fox'){point('fox',s.movers[i.target].p);const f=s.foxBehavior;if(['greet','bow','play','stretch'].includes(f.phase))put('fox.pose',f.clock);if(f.neighbor)ids.add(f.neighbor);}else if(i.kind==='object'){const m=s.movers[i.target];if(m)point(i.target,m.p);put(i.target+'.value',s.objectControls[i.target]?.value);const owner=s.objectControls[i.target]?.owner;if(owner)ids.add(owner);}}
 if(macro.has('day_phase'))for(const[k,v]of Object.entries(s.dayWeights))put('day'+k,v);
 if(macro.has('light'))put('light',s.dayWeights.night||0);
 if(macro.has('dining'))for(const[id,d]of Object.entries(s.diners)){if(['enter','exit','turn'].includes(d.phase))put(id,d.clock);}
 if(s.sceneEvent?.kind==='music'&&q.sceneId===s.sceneEvent.id){point('music.fox',s.movers['animal.garden_fox'].p);for(const id of ['resident.child_runner','resident.garden_child','resident.child_listener','resident.musician'])ids.add(id);if(Number.isFinite(s.musicCircle?.arrived)&&s.time-s.musicCircle.arrived<8)put('music.listen',s.time);}
 if(macro.has('music')&&s.effectiveMusic==='play'&&s.time-q.activeAt<4)put('music',Math.floor(s.time*5));
 if(macro.has('cycling'))point('cycle',s.movers['bicycle.street_bicycle'].p);
 for(const id of ids){const a=s.actors.find(a=>a.id===id),g=s.eventGuests?.[id],w=s.localWalkers?.[id],r=s.residentActions[id];
  const track=q.tracked[id]??={started:s.time,baseCycle:r?.cycle,settled:false};
  const explicit=q.items.some(i=>i.kind==='resident'&&i.target===id),inScene=ownScene&&e.phase!=='release';
  if(!inScene&&!explicit&&!(macro.has('cloud')||macro.has('journey'))&&a?.mode==='idle'&&!a.path.length&&s.time-track.started>1.5)track.settled=true;
  if(!track.settled||inScene||explicit){point('actor.'+id,g?.active?g.p:w?.clip?w.root:a?.p);put(id+'.umbrella',s.residents[id]?.umbrellaOpen);put(id+'.propUmbrella',r?.umbrella);if(r?.action&&!RESIDENT_ACTIONS[r.action]?.route&&!RESIDENT_ACTIONS[r.action]?.navTask&&(r.requested||macro.has('journey')||id===s.foxBehavior?.neighbor||inScene&&PROFILES[id]?.role==='vendor'&&r.cycle<=(track.baseCycle??r.cycle)+1))put(id+'.pose',r.clock);const diner=s.diners[id];if(diner&&['enter','exit','turn'].includes(diner.phase))put(id+'.diner',diner.clock);}
 }
 return values;
}
function hasWork(s,q){const macro=new Set(q.items.filter(i=>i.kind==='macro').map(i=>i.target));
 if(macro.has('day_phase')&&Object.entries(s.dayWeights).some(([k,v])=>Math.abs(v-Number(k===s.day_phase))>.025))return true;
 if(macro.has('cloud')&&(s.localCloud.phase!=='home'||s.localCloud.rain>.03))return true;if((macro.has('cloud')||macro.has('weather'))&&s.craftWorld.background?.started>=q.started-.1&&s.craftWorld.eventId===s.craftWorld.background.id&&s.craftWorld.jobs.some(j=>j.status==='running'))return true;
 if(macro.has('journey')&&(!['idle','done'].includes(s.trainJourney.phase)||s.eventGuests?.['resident.station_traveler']?.active))return true;
 if(q.items.some(i=>i.target==='boat.pond_boat'&&['cruise','dock'].includes(i.action))&&!['moored','resting'].includes(s.boatJourney.phase))return true;
 if(q.items.some(i=>i.target==='animal.garden_fox'&&i.action==='explore')&&s.foxBehavior.phase==='walk')return true;
 for(const i of q.items)if(i.kind==='resident'&&i.action==='trial'){const r=s.residentActions[i.target],a=s.actors.find(a=>a.id===i.target);if(r?.requested||r?.queuedByUser)return true;if(a?.manualActivity&&s.time-q.activeAt<8)return true;}
 if(q.requestIds.some(id=>s.intentRuntime.jobs.some(j=>j.requestId===id&&!terminal(j))))return true;
 for(const w of[s.paperWorld,s.neighborhoodWorld,s.craftWorld])if(w&&q.sceneId===w.eventId&&(w.jobs.some(j=>j.status==='running')||w.pending))return true;
 const e=s.sceneEvent;if(e&&q.transitionId&&e.id===q.transitionId&&e.next?.id===q.sceneId)return true;if(e&&e.id===q.sceneId){if(['paper_','memory_','laundry_','tea_','umbrella_','leaf_','parcel_'].some(p=>e.kind.startsWith(p))){return[s.paperWorld,s.craftWorld].some(w=>w?.eventId===e.id&&w.jobs.some(j=>j.status==='running'));}return !['release'].includes(e.phase);}
 if(macro.has('dining')&&Object.values(s.diners).some(d=>['enter','exit','turn'].includes(d.phase)||d.policy==='inside'&&d.phase!=='inside'||d.policy==='dine'&&d.phase!=='dine'))return true;
 if(macro.has('cycling')&&s.movers['bicycle.street_bicycle'].tripState!=='parked'&&s.movers['bicycle.street_bicycle'].completedStops<=q.baseStops)return true;
 return false;
}
export function advanceInput(s,nav){const q=s.inputSession;if(!inputBusy(s)||q.phase==='listening')return;
 if(q.phase==='running'&&!q.sceneId){const e=s.sceneEvent,kind=q.expectedSceneKind??eventKind(Object.fromEntries(q.items.filter(i=>i.kind==='macro').map(i=>[i.target,i.action])));if(kind&&e?.kind===kind)q.sceneId=e.id;else if(kind&&e?.next?.kind===kind){q.sceneId=e.next.id;q.transitionId=e.id;}else if(e?.phase==='closing'&&q.items.some(i=>i.kind==='macro'&&['weather','festival','occasion'].includes(i.target)&&['clear','quiet','ordinary'].includes(i.action)))q.sceneId=e.id;}

 if(q.phase==='closing'){const packing=[s.paperWorld,s.neighborhoodWorld,s.craftWorld].some(w=>w?.jobs.some(j=>j.status==='running'&&j.cancelClock<2.5));const cloud=q.items.some(i=>i.target==='cloud')&&s.localCloud.phase!=='home',sky=q.sceneId&&s.festivalUntil>s.time,weather=q.sceneId&&Math.max(s.eventWeather.rain,s.eventWeather.snow)>.04,lantern=q.sceneId===s.sceneEvent?.id&&s.sceneEvent?.kind==='lantern'&&s.sceneEvent.phase==='closing';if(s.time-q.closingAt>2.6&&!packing&&!cloud&&!sky&&!weather&&!lantern){q.phase='done';q.ended=s.time;for(const a of s.actors)if(a.interactionLock&&!s.craftWorld.jobs.some(j=>j.id===a.interactionLock&&j.status==='running')){delete a.interactionLock;delete a.interactionDestination;}}return;}
 if(s.time-q.lastSample<.2)return;q.lastSample=s.time;const values=sample(s,q);let changed=false;for(const[k,v]of Object.entries(values)){if(q.observed[k]!==undefined&&Math.abs(v-q.observed[k])>(k.includes('actor.')||['boat0','boat1','fox0','fox1'].includes(k)?.025:.015))changed=true;}q.observed=values;if(changed){q.lastProgress=s.time;q.progressSamples++;}
 const jobs=q.requestIds.flatMap(id=>s.intentRuntime.jobs.filter(j=>j.requestId===id));if(jobs.some(j=>j.status==='failed')){close(s,q,'stalled');return;}
 if(q.items.some(i=>i.target==='boat.pond_boat')&&s.boatJourney.blocked>1.8){close(s,q,'stalled');return;}
 if(!hasWork(s,q)&&s.time-q.activeAt>2.0){close(s,q,q.progressSamples?'completed':'unchanged');return;}
 if(s.time-q.lastProgress>INPUT_IDLE_SECONDS){close(s,q,q.progressSamples?'settled':'no_response');}
}

export function recoverInput(s){if(s.inputSession?.phase==='listening'){abortInput(s,'not_applied');return;}if(Object.hasOwn(s,'inputSession'))return;s.inputSession=null;const receipt=s.intentRuntime?.lastReceipt,items=receipt?s.intentRuntime.jobs.filter(j=>j.requestId===receipt.id).map(j=>({kind:j.kind,target:j.target,action:j.action})):[];if(receipt&&(s.sceneEvent||items.some(i=>i.target==='cloud'&&s.localCloud?.phase!=='home'||i.target==='boat.pond_boat'&&!['moored','resting'].includes(s.boatJourney?.phase)))){s.inputSession={id:'resume-'+s.tick,source:'resume',phase:'running',started:receipt.started,activeAt:s.time,lastProgress:s.time,lastSample:s.time-.25,items,observed:{},tracked:{},progressSamples:0,requestIds:[receipt.id],sceneId:s.sceneEvent?.id,baseStops:s.movers?.['bicycle.street_bicycle']?.completedStops||0};}}
