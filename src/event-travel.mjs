import {moverBlocks} from './motion.mjs?v=cp31-sound-dea918b266ec';
import {pathTo,navigationGraph} from './navigation.mjs?v=cp31-sound-dea918b266ec';
import {FIREWORK_FOCUS} from './event-design.mjs?v=cp31-sound-dea918b266ec';
const dist=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
const turn=(a,b,n)=>a+Math.max(-n,Math.min(n,Math.atan2(Math.sin(b-a),Math.cos(b-a))));
const live=j=>!['done','cancelled','failed'].includes(j.status);
const kinds=new Set(['festival','market','supper','reunion']);
export function ensureEventTravel(s,nav){
 s.eventGuests??={};for(const[id,c]of Object.entries(nav.activities?.eventTrips||{}))if(!s.eventGuests[id])s.eventGuests[id]={id,phase:'home',active:false,p:c.home.slice(0,3),yaw:c.home[3],stand:0,walked:0,gaitWeight:0,progress:0,path:[],segment:0,blocked:0,returnRequested:false,readyAt:0,goal:null,eventId:null,bookBefore:1,umbrellaBefore:1};
}
export function eventGuestPositions(s){return [];}
export function eventGuestCandidates(s,nav,e){ensureEventTravel(s,nav);return Object.values(s.eventGuests).filter(g=>(!nav.activities.eventTrips[g.id].events||nav.activities.eventTrips[g.id].events.includes(e.kind))&&!e.protectedIds?.includes(g.id)&&!s.intentRuntime.jobs.some(j=>j.target===g.id&&live(j))).map(g=>({id:g.id,p:g.p,node:nav.activities.eventTrips[g.id].portal}));}
function obstacle(s,g,p){
 const separation=['resident.listener','resident.child_listener'].includes(g.id)?.64:.74;
 return s.actors.some(a=>a.id!==g.id&&Math.abs(a.p[2]-p[2])<1.4&&dist(a.p,p)<separation&&dist(a.p,p)<dist(a.p,g.p)-1e-7)||Object.values(s.eventGuests).some(o=>o!==g&&o.active&&Math.abs(o.p[2]-p[2])<1.4&&dist(o.p,p)<separation&&dist(o.p,p)<dist(o.p,g.p)-1e-7)||Object.entries(s.localWalkers||{}).some(([id,w])=>id!==g.id&&!s.eventGuests?.[id]?.active&&Math.abs(w.root[2]-p[2])<1.4&&dist(w.root,p)<.74&&dist(w.root,p)<dist(w.root,g.p)-1e-7);
}
export function makeRoom(s,nav,g,target){
 const blocks=s.actors.filter(a=>a.id!==g.id&&a.mobile).map(a=>({id:a.id,p:a.p,actor:a}));
 const b=blocks.find(b=>Math.abs(b.p[2]-target[2])<1.4&&dist(b.p,target)<(g.id==='resident.cyclist'?1.9:.97));if(!b||s.time<(b.actor?.eventYieldUntil||b.guest?.yieldUntil||0)||s.sceneEvent?.protectedIds?.includes(b.id)||s.intentRuntime.jobs.some(j=>j.target===b.id&&live(j)))return;
 const start=nearest(nav,b.p),people=[...s.actors.filter(a=>a.id!==b.id).map(a=>a.p),...Object.values(s.eventGuests).filter(o=>o.id!==b.id&&o.active).map(o=>o.p)],blocked=new Set(nav.nodes.flatMap((p,i)=>people.some(q=>Math.abs(q[2]-p[2])<1.4&&dist(p,q)<.97)?[i]:[]));blocked.delete(start);
 const candidates=nav.nodes.map((p,i)=>({p,i})).filter(({p,i})=>!blocked.has(i)&&Object.entries(nav.activities.eventTrips||{}).filter(([id])=>s.eventGuests?.[id]?.active).every(([,c])=>c.entry.every(q=>Math.abs(p[2]-q[2])>1.4||dist(p,q)>1.0))&&(g.id!=='resident.cyclist'||!nav.noStopping.has(i))&&Object.entries(s.movers).every(([id,m])=>!['creature_walk','ride'].includes(nav.activities.clips[id].motion)||!moverBlocks(p,m,nav.activities.clips[id],nav.radius))&&dist(p,b.p)>.55&&dist(p,b.p)<2.3&&dist(p,g.p)>1.15&&navigationGraph(nav).components[i]===navigationGraph(nav).components[start]&&(!b.actor||b.id!=='resident.kite_child'||p[0]>2.3&&p[0]<3.8&&p[1]>-1.7&&p[1]<.65)).sort((a,c)=>dist(a.p,b.p)-dist(c.p,b.p));
 for(const c of candidates){let path=pathTo(nav,start,c.i,blocked);if(path.length<2)path=pathTo(nav,start,c.i,new Set(),blocked);if(path.length<2)continue;if(b.actor){const a=b.actor;a.path=path;a.segment=0;a.target=c.i;a.detouring=true;a.reservation=s.sceneEvent?.slots[a.id]??a.reservation;a.responseDestination=a.reservation;a.wait=0;a.localActionUntil=0;a.mode='walk';a.taskRevision=s.planRevision;a.responseReplan=false;a.eventYieldUntil=s.time+5;s.residentActions[a.id].cancelRemaining=.65;s.residents[a.id].reason='侧身让远处赶来的邻居先过去';}else{const o=b.guest;o.phase='make_room';o.path=path;o.segment=0;o.yieldUntil=s.time+5;}return;}
}
function nearest(nav,p){let best=-1,score=Infinity;const graph=navigationGraph(nav),main=graph.components[nav.actors[0].entry.at(-1)];for(let i=0;i<nav.nodes.length;i++)if(graph.components[i]===main){const d=dist(nav.nodes[i],p);if(d<score){score=d;best=i;}}return best;}
function routeGround(s,nav,g,destination){
 const start=nearest(nav,g.p),blocked=new Set(nav.nodes.flatMap((p,i)=>s.actors.some(a=>a.id!==g.id&&Math.abs(a.p[2]-p[2])<1.4&&dist(a.p,p)<.98)||Object.values(s.eventGuests).some(o=>o!==g&&o.active&&Math.abs(o.p[2]-p[2])<1.4&&dist(o.p,p)<1.02)?[i]:[]));blocked.delete(start);blocked.delete(destination);
 let path=pathTo(nav,start,destination,blocked);if(!path.length)path=pathTo(nav,start,destination,new Set(),blocked);
 if(!path.length)return false;
 g.path=path;g.segment=0;g.goal=destination;g.blocked=0;return true;
}
function toward(s,g,target,dt,speed=.76,nav=null){
 const d=dist(g.p,target);if(d<.014){g.p[0]=target[0];g.p[1]=target[1];g.p[2]+=Math.max(-dt*.35,Math.min(dt*.35,target[2]-g.p[2]));return Math.abs(g.p[2]-target[2])<.008;}
 const yaw=Math.atan2(target[1]-g.p[1],target[0]-g.p[0])+Math.PI/2;g.yaw=turn(g.yaw,yaw,dt*2.6);const delta=Math.atan2(Math.sin(yaw-g.yaw),Math.cos(yaw-g.yaw)),amount=Math.min(d,speed*dt*Math.max(0,Math.cos(delta))),p=g.p.map((x,k)=>x+(target[k]-x)*amount/d);
 if(obstacle(s,g,p)){g.blocked+=dt;if(nav&&g.blocked>.6)makeRoom(s,nav,g,p);g.gaitWeight*=Math.max(0,1-dt*9);return false;}
 g.blocked=0;g.p=p;g.walked+=amount;g.gaitWeight+=(Number(amount>.001)-g.gaitWeight)*Math.min(1,dt*8);return d<=amount+.014;
}
function departureReady(s,c){const other=c.departAfter?s.eventGuests[c.departAfter]:null;return !other||(c.departAfterAt!==undefined&&other.phase==='entry_out'&&(other.entryClock||0)>=c.departAfterAt)||(c.departWhen==='hold'?['hold']:['ground_out','hold']).includes(other.phase);}
function followEntry(s,g,c,dt,direction,nav){
 const frames=direction>0?c.outFrames:c.backFrames;if(!frames?.length)throw Error('活动脚步轨迹尚未准备好');
 if(g.motionDirection!==direction){g.motionDirection=direction;g.entryClock=null;g.authorFeet=null;}
 if(g.entryClock===null){const first=frames[0].root;if(dist(g.p,first)>.014||Math.abs(g.p[2]-first[2])>.015){toward(s,g,first,dt,.65,nav);return false;}g.yaw=turn(g.yaw,first[3],dt*2.6);if(Math.abs(Math.atan2(Math.sin(g.yaw-first[3]),Math.cos(g.yaw-first[3])))>.03)return false;g.entryClock=0;}
 const time=Math.min(frames.at(-1).time,direction>0&&c.departGateTime!==undefined&&!departureReady(s,c)?Math.min(c.departGateTime,g.entryClock+dt):g.entryClock+dt);let lo=0,hi=frames.length-1;while(lo<hi){const mid=(lo+hi)>>1;if(frames[mid].time<time)lo=mid+1;else hi=mid;}const b=frames[lo],a=frames[Math.max(0,lo-1)],u=b.time===a.time?0:(time-a.time)/(b.time-a.time),p=a.root.slice(0,3).map((x,k)=>x+(b.root[k]-x)*u);
 if(obstacle(s,g,p)){g.blocked+=dt;if(g.blocked>.6)makeRoom(s,nav,g,p);g.gaitWeight*=Math.max(0,1-dt*8);return false;}
 const travel=dist(g.p,p);g.blocked=0;g.walked+=travel;g.gaitWeight+=(Number(travel>.001)-g.gaitWeight)*Math.min(1,dt*8);g.p=p;g.yaw=a.root[3]+Math.atan2(Math.sin(b.root[3]-a.root[3]),Math.cos(b.root[3]-a.root[3]))*u;g.authorFeet=Object.fromEntries(['left','right'].map(side=>[side,a.feet[side].map((x,k)=>x+(b.feet[side][k]-x)*u)]));g.entryClock=time;g.progress=Math.round((direction>0?time/frames.at(-1).time:1-time/frames.at(-1).time)*(c.entry.length-1));return time>=frames.at(-1).time;
}
export function advanceEventTravel(s,nav,dt){
 ensureEventTravel(s,nav);const e=s.sceneEvent;let order=0;
 for(const g of Object.values(s.eventGuests)){
  const actor=s.actors.find(a=>a.id===g.id);
  const original=nav.activities.eventTrips[g.id],c=original.paths&&g.startAnchor?{...original,entry:original.paths[g.startAnchor],outFrames:original.outFramePaths[g.startAnchor],backFrames:original.backFramePaths[g.startAnchor]}:original,r=s.residentActions[g.id],personal=s.intentRuntime.jobs.some(j=>j.target===g.id&&live(j));
  if(g.active&&g.id==='resident.water_companion'&&s.weather==='rain'){const n=nearest(nav,g.p);r.umbrellaTarget=['hold','aside'].includes(g.phase)&&nav.activities.spaces.nodes[n]?.umbrellaClear?1:0;}
  if(e?.slots?.[g.id]!==undefined)g.destination=e.slots[g.id];
  const desired=e&&kinds.has(e.kind)&&(!c.events||c.events.includes(e.kind))&&['gather','active'].includes(e.phase)&&!e.protectedIds?.includes(g.id)&&!personal&&!g.returnRequested;
  if(g.phase==='home'){
   if(!desired)continue;
   const walker=s.localWalkers?.[g.id];if(walker?.clip)continue;if(walker){g.startAnchor=walker.anchor;g.home=walker.root.slice();g.p=walker.root.slice(0,3);g.yaw=walker.root[3];}
   if(r.action){if(!['sip_tea','feed_pond','look_pond'].includes(r.action))r.cancelRemaining=r.cancelRemaining||.65;continue;}
   g.active=true;g.motionDirection=null;g.authorFeet=null;g.phase='prepare';g.eventId=e.id;g.readyAt=s.time+1.8+order++*.75;g.bookBefore=r.bookTarget;g.umbrellaBefore=r.umbrellaTarget;g.progress=0;g.returnRequested=false;g.path=[];g.blocked=0;r.bookTarget=0;r.umbrellaTarget=0;r.queued=null;r.nextAt=s.time+1;
  }
  if(g.phase==='prepare'){
   if(!desired){g.phase='sit';continue;}
   if(s.time<g.readyAt)continue;if(c.departGateTime===undefined&&!departureReady(s,c))continue;
   g.stand=Math.min(1,g.stand+dt/1.6);if(!c.seated)g.stand=1;else{const u=g.stand*g.stand*(3-2*g.stand);g.p=c.home.slice(0,3).map((x,k)=>x+(c.entry[0][k]-x)*u);}
   if(g.stand>=1){g.phase=desired?'entry_out':'entry_home';g.p=c.entry[0].slice();g.progress=0;}
   continue;
  }
  if(!desired&&['entry_out','ground_out','hold'].includes(g.phase)){
   if(g.phase!=='entry_out'&&c.returnAfter&&s.eventGuests[c.returnAfter]?.active){if(g.phase==='hold'){if(!actor.path.length){actor.wait=Math.max(actor.wait,.4);actor.reservation=actor.node;g.gaitWeight=0;}continue;}actor.guestStageNode=g.destination;}else 
   if(g.phase==='entry_out'){g.finishThenReturn=true;}else{g.phase='ground_home';actor.guestReturnNode=c.portal;actor.taskRevision=-1;actor.reservation=null;actor.path=[];actor.wait=.1;}
  }else if(desired&&['entry_home','ground_home'].includes(g.phase)){
   if(g.phase==='entry_home'){g.finishThenReturn=false;}else{g.phase='ground_out';g.path=[];delete actor.guestReturnNode;actor.taskRevision=-1;actor.path=[];actor.wait=.1;}
  }
  if(g.phase==='make_room'){const node=nav.nodes[g.path[g.segment]],p=[node[0],node[1],node[2]-.02*c.scale+.006];if(toward(s,g,p,dt,.72)){g.segment++;if(g.segment>=g.path.length){g.phase='aside';g.path=[];g.yieldUntil=s.time+3.5;g.gaitWeight=0;}}continue;}
  if(g.phase==='aside'){g.gaitWeight=0;if(s.time>=g.yieldUntil){g.phase=desired?'ground_out':'ground_home';g.path=[];}continue;}
  if(g.phase==='entry_out'){if(followEntry(s,g,c,dt,1,nav)){g.phase='ground_out';g.authorFeet=null;g.motionDirection=null;g.path=[];actor.p=g.p.slice();actor.yaw=g.yaw;actor.node=c.portal;actor.atHome=false;actor.mobile=true;actor.wait=.1;actor.taskRevision=-1;actor.path=[];actor.reservation=null;actor.localActionUntil=0;delete actor.guestReturnNode;}}
  else if(g.phase==='entry_home'){
   if(followEntry(s,g,c,dt,-1,nav)){g.phase='sit';g.authorFeet=null;g.motionDirection=null;g.readyAt=s.time+.2;g.gaitWeight=0;}
  }else if(['ground_out','ground_home'].includes(g.phase)){
   if(g.id==='resident.water_companion'&&r.umbrella>.08){r.umbrellaTarget=0;actor.wait=Math.max(actor.wait,.2);}
   const target=g.phase==='ground_home'?c.portal:(e?.slots[g.id]??g.destination);if(target===undefined)continue;
   if(g.phase==='ground_home'){actor.guestReturnNode=target;delete actor.guestStageNode;}else{delete actor.guestReturnNode;if(!desired)actor.guestStageNode=target;else delete actor.guestStageNode;}
   g.p=actor.p.slice();g.yaw=actor.yaw;g.walked=actor.walked;g.gaitWeight=actor.gaitWeight;
   if(actor.node===target&&!actor.path.length&&(g.phase==='ground_home'||actor.reservation===target)){g.gaitWeight=0;g.phase=g.phase==='ground_home'?'entry_home':'hold';g.goal=target;g.progress=c.entry.length-1;if(g.phase==='entry_home'){actor.mobile=false;delete actor.guestReturnNode;}}
  }else if(g.phase==='hold'){
   const target=e?.kind==='festival'?FIREWORK_FOCUS:c.look||[-1,3,1.5],yaw=Math.atan2(target[1]-g.p[1],target[0]-g.p[0])+Math.PI/2;g.yaw=turn(g.yaw,yaw,dt*1.4);g.gaitWeight*=Math.max(0,1-dt*8);
   if(desired&&e&&g.goal!==e.slots[g.id]){g.phase='ground_out';g.path=[];delete actor.guestReturnNode;actor.taskRevision=-1;actor.path=[];actor.wait=.1;}
  }else if(g.phase==='sit'){
   g.yaw=turn(g.yaw,(g.home||c.home)[3],dt*2);if(Math.abs(Math.atan2(Math.sin(g.yaw-(g.home||c.home)[3]),Math.cos(g.yaw-(g.home||c.home)[3])))>.03)continue;
   g.stand=Math.max(0,g.stand-dt/1.8);if(!c.seated)g.stand=0;else{const u=g.stand*g.stand*(3-2*g.stand);g.p=c.home.slice(0,3).map((x,k)=>x+(c.entry[0][k]-x)*u);}
   if(g.stand<=0){g.phase='home';g.active=false;g.returnRequested=false;actor.mobile=false;actor.path=[];actor.reservation=null;delete actor.guestReturnNode;delete actor.guestStageNode;g.p=(g.home||c.home).slice(0,3);g.yaw=(g.home||c.home)[3];r.bookTarget=g.bookBefore;r.umbrellaTarget=g.umbrellaBefore;r.nextAt=s.time+1.5;r.action=null;r.clock=0;r.queued=null;r.requested=false;}
  }
  if(g.active&&!['ground_out','ground_home','hold'].includes(g.phase)){actor.mobile=false;actor.p=g.p.slice();actor.yaw=g.yaw;}
  if(g.active){const resident=s.residents[g.id];resident.activity=g.phase==='hold'?(e?.kind==='festival'?'fireworks':'browse'):'stroll';resident.lookTarget=e?.kind==='festival'?FIREWORK_FOCUS.slice():[-1,3,1.5];resident.reason=['ground_home','entry_home','sit'].includes(g.phase)?'活动结束，走回原来的位置':'收好手边的东西，走去参加小镇的活动';}
 }
}

export function syncGuestActors(s){for(const g of Object.values(s.eventGuests||{})){const a=s.actors.find(a=>a.id===g.id);if(a&&['ground_out','ground_home','hold'].includes(g.phase)){g.p=a.p.slice();g.yaw=a.yaw;g.walked=a.walked;g.gaitWeight=a.gaitWeight;}else if(a&&g.phase==='home'){const w=s.localWalkers?.[g.id];a.mobile=false;if(w){g.p=w.root.slice(0,3);g.yaw=w.root[3];}a.p=g.p.slice();a.yaw=g.yaw;}}}

export function validateEventTravel(s,nav){ensureEventTravel(s,nav);const phases=['home','prepare','entry_out','ground_out','hold','ground_home','entry_home','sit','make_room','aside'];for(const[id,g]of Object.entries(s.eventGuests)){const c=nav.activities.eventTrips?.[id];if(!c||!phases.includes(g.phase)||typeof g.active!=='boolean'||!g.p?.every(Number.isFinite)||!Number.isFinite(g.yaw)||!Number.isFinite(g.stand)||g.stand<0||g.stand>1||!Number.isInteger(g.progress)||g.progress<0||!Array.isArray(g.path)||g.path.some(n=>!Number.isInteger(n)||!nav.nodes[n]))throw Error('居民往返活动存档无效');}}
