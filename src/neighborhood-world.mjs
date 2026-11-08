import {LANTERN_STATIONS} from './lantern-scene.mjs?v=cp51-vibe-response-acb055878926';
import {createInteraction,advanceInteraction,interactionStep} from './interaction-sequence.mjs?v=cp51-vibe-response-acb055878926';
import {navigationGraph,pathTo} from './navigation.mjs?v=cp51-vibe-response-acb055878926';
export const NEIGHBORHOOD_KINDS=new Set(['homecoming','prepare','reopen','spring','lantern']);
export const HOME={door:[-5.947,-1.723,.77],yaw:25*Math.PI/180,host:[-5.76,-2.48,.628],guest:[-4.96,-2.48,.628]};
const ADULTS=['resident.customer_one','resident.customer_two','resident.customer_three','resident.market_browser','resident.strolling_parent','resident.courier'];
const D=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
export function ensureNeighborhood(s){return s.neighborhoodWorld??={eventId:null,jobs:[],props:[],history:[],next:1,door:0,window:0,bloom:0,phase:'idle',pending:null,accent:0};}
function nearest(nav,p,used=[]){const graph=navigationGraph(nav),main=graph.components[nav.actors[0].entry.at(-1)];return nav.nodes.map((q,i)=>({i,d:D(q,p)})).filter(x=>graph.components[x.i]===main&&!nav.noStopping.has(x.i)&&used.every(n=>D(nav.nodes[n],nav.nodes[x.i])>.65)).sort((a,b)=>a.d-b.d)[0]?.i;}
function release(s,j,e){const a=s.actors.find(a=>a.id===j.actor);if(!a||a.interactionLock!==j.id)return;delete a.interactionLock;delete a.interactionLook;delete a.interactionTask;if(e?.id===j.context.eventId)delete e.slots[a.id];a.path=[];a.target=null;a.reservation=null;a.taskRevision=-1;a.wait=.5;const r=s.residentActions[a.id];if(r)r.nextAt=s.time+1.4;}
function lock(s,j,e,key){const a=s.actors.find(a=>a.id===j.actor),n=j.context[key+'Node'];if(!a||n===undefined)return;a.interactionLock=j.id;a.interactionLook=(key==='supply'?j.context.supplyLook:j.context.look).slice();a.interactionTask=['approach','carry'].includes(interactionStep(j)?.action)?'stroll':'inspect';e.slots[a.id]=n;a.reservation=n;a.localActionUntil=0;a.manualActivity=null;}
function start(s,nav,e,requestGesture){
 const w=ensureNeighborhood(s);w.eventId=e.id;w.jobs=[];w.phase='working';w.kind=e.kind;w.completedAt=null;w.doorTarget=0;w.windowTarget=0;w.bloomTarget=0;w.accent++;w.started=s.time;w.before={cycling:s.cycling,animals:s.animals};e.slotsAssigned=true;e.slots={};e.neighborhoodStarted=true;e.openRideLane=true;
 // Replacing a display is finite and soft; the same physical IDs are not duplicated.
 for(const p of w.props)p.retireAt=s.time;
 const used=new Set(),nodes=[],candidates=s.actors.filter(a=>nav.grid[`${Math.round((a.p[0]-nav.origin[0])/nav.step)},${Math.round((a.p[1]-nav.origin[1])/nav.step)}`]!==undefined&&a.mobile&&!a.eventOnly&&!a.manual&&!e.protectedIds?.includes(a.id)&&!s.residentActions[a.id]?.requested);
 const pick=(p,child=false,home=false)=>{const goal=home?nearest(nav,p):null;const cost=a=>{if(!home)return D(a.p,p);const path=pathTo(nav,a.node,goal);if(!path.length)return Infinity;return path.reduce((n,id,i)=>n+(i?D(nav.nodes[path[i-1]],nav.nodes[id]):0),0);};const options=candidates.filter(a=>!used.has(a.id)&&(child?['resident.child_runner','resident.garden_child'].includes(a.id):ADULTS.includes(a.id)||home&&a.id==='resident.postman')).sort((a,b)=>cost(a)-cost(b));const a=options[0];if(a)used.add(a.id);return a;};
 function job(recipe,type,supply,destination,opts={}){
  const a=pick(supply,opts.child,recipe.startsWith('home'));if(!a)return null;const supplyNode=nearest(nav,supply,nodes),destinationNode=nearest(nav,destination,nodes);if(supplyNode===undefined||destinationNode===undefined)return null;nodes.push(destinationNode);
  const pos=nav.nodes[destinationNode],look=opts.look||[pos[0],pos[1]+1,pos[2]+.7],anchor=opts.anchor||[pos[0]+(look[0]-pos[0])*.58,pos[1]+(look[1]-pos[1])*.58,pos[2]+.02];
  const prop=type?{id:'neighborhood-prop-'+w.next++,type,owner:a.id,location:recipe==='home_arrive'?'hand':['wipe_place','wipe_surface'].includes(recipe)&&type==='bench'?'placed':'supply',anchor,supply:nav.nodes[supplyNode].slice(0,3),created:s.time,unfold:0,mode:e.kind}:null;if(prop)w.props.push(prop);
  const j=createInteraction({id:e.id+':'+a.id,recipe,actor:a.id,prop:prop?.id||null,context:{eventId:e.id,pace:s.inputSession?.phase==='running'?1.18:1,supplyNode,destinationNode,look,supplyLook:[nav.nodes[supplyNode][0],nav.nodes[supplyNode][1]+1,1.2],anchor,...opts}});w.jobs.push(j);
  a.path=[];a.wait=.1;a.reservation=null;a.taskRevision=-1;delete a.courtesyDestination;delete a.courtesyExpires;delete a.courtesyArrivedAt;const r=s.residentActions[a.id];r.action=null;r.queued=null;r.cancelRemaining=0;lock(s,j,e,recipe==='home_host'||['wipe_place','wipe_surface'].includes(recipe)?'destination':'supply');return j;
 }
 if(e.kind==='lantern'){
  for(const [slot,c] of LANTERN_STATIONS.entries()){const j=job('carry_lantern','lantern',c.stand,c.destination,{anchor:c.anchor,slot,supplyAnchor:c.anchor});if(j){const p=w.props.find(p=>p.id===j.prop);p.stockSlot=slot;p.sourceAnchor=c.anchor.slice();p.location='supply';}}
 }else if(e.kind==='homecoming'){
  job('home_return',null,HOME.host,HOME.host,{look:HOME.door});
  w.windowTarget=1;requestGesture('resident.porch_resident','greet');requestGesture('resident.elder','greet');
 }else if(e.kind==='prepare'){
  job('carry_place','tray',[-2.8,1.4],[-2.88,-.56]);job('carry_place','stool',[1.4,3.2],[1.92,2]);
  const child=job('carry_give','lantern',[3.52,-1.04],[3.52,-1.68],{child:true}),receiver=job('receive_prop',null,[2.88,-1.68],[2.88,-1.68]);
  if(child&&receiver){child.context.partner=receiver.actor;receiver.context.partner=child.actor;receiver.prop=child.prop;receiver.context.anchor=[3.2,-1.68,.64];}else if(child)child.recipe='carry_place';
  for(const id of['resident.vendor_bread','resident.vendor_flower','resident.vendor_lamp'])requestGesture(id,'offer_food');
 }else if(e.kind==='reopen'){
  job('wipe_place','bench',[-2.88,-.56],[-2.88,-.56]);job('carry_place','crate',[-2.8,1.4],[-.7,1.5]);
  for(const id of['resident.vendor_bread','resident.vendor_flower','resident.vendor_lamp'])requestGesture(id,'wipe_counter');
  s.cycling='rest';s.animals='rest';w.reopenReleased=false;
 }else if(e.kind==='spring'){
  job('plant_flower','flowerpot',[4.96,2.2],[2.88,.72]);job('plant_flower','flowerpot',[-2.88,-.56],[-4.0,-.4]);job('plant_flower','flowerpot',[1.92,2],[1.44,-1.68]);
  requestGesture('resident.gardener','water_plants');requestGesture('resident.assistant_gardener','inspect_leaf');
  for(const id of ['resident.child_runner','resident.child_parent'])requestGesture(id,'shade_eyes');
  const kite=s.actors.find(a=>a.id==='resident.kite_child');if(kite){kite.manualActivity='kite';kite.activityUntil=s.time+52;kite.taskRevision=-1;kite.wait=.2;}w.bloomTarget=1;
 }
 for(const j of w.jobs)if(j.recipe==='receive_prop'){const other=w.jobs.find(x=>x.actor===j.context.partner);j.context.look=nav.nodes[other?.context.destinationNode??j.context.destinationNode].slice(0,3);lock(s,j,e,'destination');}
}
export function advanceNeighborhood(s,nav,dt,request,emit,requestGesture=()=>{}){
 const w=ensureNeighborhood(s);if(!s.sceneEvent&&w.pending){const p=w.pending;w.pending=null;request({neighborhood:p});}const e=s.sceneEvent;
 if(e&&NEIGHBORHOOD_KINDS.has(e.kind)&&['gather','active'].includes(e.phase)&&!e.neighborhoodStarted)start(s,nav,e,(id,action)=>{if(!e.protectedIds?.includes(id))requestGesture(id,action);});
 const live=e?.id===w.eventId&&['gather','active'].includes(e.phase);
 w.door+=(Number(live&&w.doorTarget)-w.door)*Math.min(1,dt*1.8);w.window+=((live?w.windowTarget||0:.3)-w.window)*Math.min(1,dt*.55);w.bloom+=((live?w.bloomTarget||0:0)-w.bloom)*Math.min(1,dt*.65);
 for(const j of w.jobs){if(j.status!=='running'){if(!live)release(s,j,e);continue;}const a=s.actors.find(a=>a.id===j.actor),p=w.props.find(p=>p.id===j.prop);if(!a)continue;
  if((!live||e.protectedIds?.includes(j.actor))&&p?.mode==='lantern'&&p.location==='hand'&&!j.context.returningLantern){j.context.returningLantern=true;j.recipe='return_lantern';j.step=0;j.clock=0;j.entered=false;j.cancelClock=0;}
  if((!live||e?.protectedIds?.includes(j.actor))&&!j.context.returningLantern){j.cancelClock=(j.cancelClock||0)+dt;j.cancelledPose='pack';if(j.cancelClock>=2.5){if(p&&p.owner===j.actor&&p.location==='hand'){p.location='stored';p.retireAt=s.time;}j.status='cancelled';release(s,j,e);if(w.kind==='reopen'&&!w.reopenReleased){if(s.cycling==='rest')s.cycling=w.before?.cycling||'ride';if(s.animals==='rest')s.animals=w.before?.animals||'wander';w.reopenReleased=true;}}continue;}
  advanceInteraction(j,dt,{
   condition(key){if(key==='door')return w.door>.85;const other=w.jobs.find(x=>x.actor===j.context.partner),b=s.actors.find(a=>a.id===j.context.partner);if(key==='partner'||key==='recipient')return !other||b&&b.node===other.context.destinationNode&&!b.path.length;if(key==='received')return p?.owner===j.actor&&p.location==='hand';return true;},
   enter(step){if(step.target)j.context.station=step.target;if(j.recipe.startsWith('home')&&['welcome','offer','receive','admire'].includes(step.action)){const partner=s.actors.find(a=>a.id===j.context.partner);if(partner)j.context.look=partner.p.slice();}lock(s,j,e,step.target||j.context.station||'destination');},
   move(target){lock(s,j,e,target);},
   arrived(target){return a.node===j.context[target+'Node']&&!a.path.length&&a.mode==='idle'&&D(a.p,nav.nodes[j.context[target+'Node']])<.08;},
   commit(step){if(step.action==='open'){if(p?.mode==='lantern')p.lit=true;else w.doorTarget=1;};if(step.action==='take'&&p&&p.type!=='bench'){p.location='hand';p.owner=j.actor;}if(step.action==='offer'&&j.recipe==='carry_give'&&p){p.owner=j.context.partner;p.location='hand';}if(step.action==='place'&&p){p.location='placed';p.anchor=(p.mode==='lantern'?j.context.supplyAnchor:j.context.anchor).slice();p.placedAt=s.time;}if(step.action==='unfold'&&p){p.unfold=1;p.location='placed';p.anchor=j.context.anchor.slice();p.placedAt=s.time;}if(step.action==='stow'&&p?.type==='cloth'){p.location='stored';p.retireAt=s.time;}if(step.action==='receive'&&j.recipe==='home_arrive'&&p){p.location='stored';p.retireAt=s.time;}},
   finish(){j.completedAt=s.time;if(!j.recipe.startsWith('home'))release(s,j,e);}
  });
 }
 if(live&&e.neighborhoodStarted){
  if(e.kind==='reopen'&&!w.reopenReleased&&w.jobs.some(j=>j.history.includes('wipe')||j.history.includes('place'))){w.reopenReleased=true;s.cycling=w.before?.cycling||'ride';s.animals=w.before?.animals||'wander';emit('椅子擦干，点心重新摆好，自行车和小动物又回到街上。');}
  if(w.jobs.length&&w.jobs.every(j=>j.status!=='running')&&!w.completedAt){w.completedAt=s.time;for(const job of w.jobs)release(s,job,e);w.phase='enjoy';w.accent++;w.history.push({kind:e.kind,at:s.time,completed:w.jobs.filter(j=>j.status==='done').length});w.history=w.history.slice(-12);if(e.phase==='gather'){e.phase='active';e.phaseAt=s.time;}e.until=Math.min(e.until,s.time+6);emit({lantern:'街坊把纸灯送到街边，照过一段路，再轻轻放回灯架。',homecoming:'晚归的街坊打开家门，暖窗亮着，邻居从窗边打招呼。',prepare:'点心、小凳和纸灯都准备好了，大家可以一起过一个开心的晚上。',reopen:'雨后的街巷重新开张，日常又热闹起来。',spring:'折纸花在街角展开，新的春风从这里传开。'}[e.kind]);if(e.kind==='prepare')e.neighborhoodNext={kind:'reunion',id:e.id+'-celebrate',protectedIds:[],automatic:true,explicitDay:true};}
 }
 for(const p of w.props)if(!live&&!p.retireAt)p.retireAt=s.time+45;w.props=w.props.filter(p=>!p.retireAt||s.time-p.retireAt<4);if(!live&&w.jobs.every(j=>j.status!=='running'))w.phase='idle';
}
export function validateNeighborhood(s,nav){const w=ensureNeighborhood(s);if(!Array.isArray(w.jobs)||w.jobs.length>10||!Array.isArray(w.props)||w.props.length>20||!Array.isArray(w.history)||w.history.length>12||![w.door,w.window,w.bloom].every(x=>Number.isFinite(x)&&x>=0&&x<=1)||w.pending&&!NEIGHBORHOOD_KINDS.has(w.pending))throw Error('Invalid neighborhood state');for(const j of w.jobs)if(!s.actors.some(a=>a.id===j.actor)||!nav.nodes[j.context.supplyNode]||!nav.nodes[j.context.destinationNode]||!['running','done','cancelled'].includes(j.status)||!Number.isFinite(j.clock))throw Error('Invalid neighborhood job');for(const p of w.props)if(!['tray','stool','lantern','crate','bench','cloth','flowerpot','parcel'].includes(p.type)||!['supply','hand','placed','stored'].includes(p.location)||!p.anchor?.every(Number.isFinite)||!s.residents[p.owner])throw Error('Invalid neighborhood prop');}
