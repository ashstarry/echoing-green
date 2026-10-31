// Only newly executed intentions create cues. Autonomous daily motion and loading
// an old save are silent. This shared observer covers all current action systems.
export const GLOW_SECONDS=5.2;
export const GLOW_COOLDOWN=7;
export const MAX_GLOWS=24;
const ease=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
export const responseGlowAlpha=age=>age<0||age>=GLOW_SECONDS?0:.17*ease(age/.45)*(1-ease((age-2.0)/3.2));
const alive=j=>['running','done'].includes(j.status);
const macroObjects={music:['resident.musician'],breeze:['windmill.hill_windwheel'],cycling:['bicycle.street_bicycle'],train:['tram.tram_car_front'],dining:['resident.upper_diner_0','resident.upper_diner_1'],animals:['animal.garden_fox','animal.doorstep_cat'],pond:['animal.duck_0','fish.pond_fish_0']};
function macroReady(s,key,action){if(key==='train'&&action==='hold')return s.train?.mode==='dwell';if(key==='cycling'&&action==='rest')return s.movers?.['bicycle.street_bicycle']?.tripState==='parked';if(key==='dining'&&action!=='auto')return Object.values(s.diners||{}).some(d=>['enter','exit'].includes(d.phase));return true;}
export function createResponseSignals(){
 const seen=new Set(),last=new Map(),manual=new Map();let ready=false,previousControls=null;const pendingMacros=new Map();
 function remember(key){seen.add(key);if(seen.size>1600)seen.delete(seen.values().next().value);}
 return{request(id,action,key){manual.set(id,{id,action,key});},collect(s){
  const candidates=[];const cue=(id,key,time=s.time)=>{if(!seen.has(key)){remember(key);candidates.push({id,key,time});}};
  for(const j of s.intentRuntime?.jobs||[]){if(j.source==='day_rhythm'||!alive(j))continue;
   if(j.kind==='resident'||j.kind==='object')cue(j.target,'job:'+j.id+':'+j.step,j.updated);
   else if(j.kind==='macro'&&macroReady(s,j.target,j.action))for(const id of macroObjects[j.target]||[])cue(id,'macro:'+j.id+':'+id,s.time);
  }
  const pulse=s.townResponse;if(pulse&&pulse.theme!=='opening')for(const x of pulse.pending||[])if(x.dispatched!==undefined)cue(x.id,'pulse:'+pulse.id+':'+x.id,x.dispatched);
  const controls={music:s.music,breeze:s.breeze,cycling:s.cycling,train:s.trainPolicy,dining:s.dining,animals:s.animals,pond:s.pond};if(previousControls)for(const [key,value]of Object.entries(controls))if(value!==previousControls[key])pendingMacros.set(key,{action:value,time:s.time,revision:s.revision});previousControls=controls;for(const[key,p]of pendingMacros){if(macroReady(s,key,p.action)){for(const id of macroObjects[key]||[])cue(id,'control:'+key+':'+p.revision+':'+p.time,s.time);pendingMacros.delete(key);}else if(s.time-p.time>90)pendingMacros.delete(key);}
  const e=s.sceneEvent;if(e&&['gather','active'].includes(e.phase)&&!e.kind.startsWith('paper_'))for(const id of Object.keys(e.slots||{})){
   const a=s.actors.find(a=>a.id===id),g=s.eventGuests?.[id];const started=g?.active&&g.phase!=='home'&&g.stand>.1||a&&!a.atHome&&(a.mode==='walk'||a.node===e.slots[id]&&!a.path.length);
   if(started)cue(id,'scene:'+e.id+':'+id,s.time);
  }
  for(const j of s.paperWorld?.jobs||[])if(j.status==='running'){
   const a=s.actors.find(a=>a.id===j.actor);if(a&&(a.mode==='walk'||a.mode==='idle'&&j.clock>.12))cue(j.actor,'paper:'+j.id+':'+j.step,s.time);
  }
  for(const[id,c]of Object.entries(s.objectControls||{}))cue(id,'object:'+id+':'+c.action+':'+c.started,c.started);
  for(const[id,p]of Object.entries(s.passengers||{}))if(p.requested&&['board','alight'].includes(p.phase))cue(id,'passenger:'+id+':'+p.nextTripAt+':'+p.phase,s.time);
  for(const[id,request]of manual){const r=s.residentActions?.[id];if(r?.action===request.action&&r.requested){cue(id,request.key,s.time);manual.delete(id);}else if(!r?.queued&&!r?.requested)manual.delete(id);}
  if(!ready){ready=true;return[];}
  const result=[];for(const c of candidates){if(s.time-c.time>1.5||s.time-(last.get(c.id)??-Infinity)<GLOW_COOLDOWN)continue;last.set(c.id,s.time);result.push({...c,time:s.time});}
  return result;
 }};
}
