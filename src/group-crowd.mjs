import {makeRoom} from './event-travel.mjs?v=cp37-paper-c8fccf30daca';
import {groupPlaces} from './group-layout.mjs?v=cp37-paper-c8fccf30daca';
import {pathTo,navigationGraph} from './navigation.mjs?v=cp37-paper-c8fccf30daca';
import {moverBlocks} from './motion.mjs?v=cp37-paper-c8fccf30daca';
import {FIREWORK_FOCUS} from './event-design.mjs?v=cp37-paper-c8fccf30daca';
const D=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const angle=(a,b)=>Math.atan2(Math.sin(b-a),Math.cos(b-a));
const patience=id=>.45+[...id].reduce((n,c)=>n+c.charCodeAt(0),0)%5*.07;
function nodeAt(nav,p){const x=Math.round((p[0]-nav.origin[0])/nav.step),y=Math.round((p[1]-nav.origin[1])/nav.step);return nav.grid[x+','+y];}
function targetOf(s,a){const g=s.eventGuests?.[a.id],e=s.sceneEvent;return (a.courtesyDestination!==undefined&&s.time<a.courtesyExpires?a.courtesyDestination:undefined)??a.guestReturnNode??a.guestStageNode??(['gather','active','closing'].includes(e?.phase)?e.slots?.[a.id]:undefined)??(g?.active&&g.phase==='hold'?g.goal:undefined);}
function turn(a,target,dt){const want=Math.atan2(target[1]-a.p[1],target[0]-a.p[0])+Math.PI/2,error=angle(a.yaw,want);a.yaw+=clamp(error*(1-Math.exp(-dt*7)),-dt*3.2,dt*3.2);a.turnVelocity=0;}
function clearSegment(nav,from,to,blocked){const a=nav.nodes[from],b=nav.nodes[to],n=Math.ceil(D(a,b)/(.5*nav.step)),graph=navigationGraph(nav);let prior=from;for(let j=1;j<=n;j++){const p=[a[0]+(b[0]-a[0])*j/n,a[1]+(b[1]-a[1])*j/n],id=nodeAt(nav,p);if(id===undefined||blocked.has(id)||id!==prior&&!graph.edges[prior].includes(id))return false;prior=id;}return true;}
function smoothRoute(nav,path,blocked){if(path.length<3)return path;const route=[path[0]];let i=0;while(i<path.length-1){let j=Math.min(path.length-1,i+14);while(j>i+1&&!clearSegment(nav,path[i],path[j],blocked))j--;route.push(path[j]);i=j;}return route;}
export function advanceGroupCrowd(s,nav,dt){
 for(const a of s.actors)if(a.courtesyDestination!==undefined&&((['festival','market','supper','reunion','lantern','music','quiet'].includes(s.sceneEvent?.kind)&&['gather','active'].includes(s.sceneEvent.phase))||s.time>=a.courtesyExpires||a.courtesyArrivedAt!==null&&s.time-a.courtesyArrivedAt>.65)){delete a.courtesyDestination;delete a.courtesyExpires;delete a.courtesyArrivedAt;a.detouring=false;a.reservation=null;a.path=[];a.target=null;a.taskRevision=-1;a.wait=.3;}
 const crowd=s.actors.filter(a=>a.mobile&&targetOf(s,a)!==undefined),graph=navigationGraph(nav);
 const moverClear=p=>Object.entries(s.movers).every(([id,m])=>!['ride','creature_walk'].includes(nav.activities.clips[id].motion)||!moverBlocks(p,m,nav.activities.clips[id],.24));
 // Plan against actual bodies and static terrain. A nearby free point is never substituted for a queue position.
 for(const a of crowd){const goal=targetOf(s,a),target=nav.nodes[goal],g=s.eventGuests?.[a.id],e=s.sceneEvent;const home=a.guestReturnNode!==undefined;a.groupDrivenTick=s.tick;a.segment=0;a.reservation=goal;a.responseDestination=goal;a.localActionUntil=0;a.manualActivity=null;a.wait=0;a.task=a.interactionLock?(a.interactionTask||'inspect'):home?'stroll':e?.kind==='music'?'listen':e?.kind==='quiet'?'rest':e?.kind==='festival'?'fireworks':['reunion','lantern'].includes(e?.kind)?'chat':'browse';a.lookTarget=a.interactionLock?a.interactionLook:home?target:e?.kind==='music'?[-2.47,-1.45,1.25]:e?.kind==='quiet'?(a.p[0]>1.8?[7.7,-1.2,.7]:[-.3,-.5,1.4]):e?.kind==='festival'?FIREWORK_FOCUS:e?.queue?.[a.id]?nav.activities.spaces.residents[e.queue[a.id].vendor].position:[-.27,-.54,1.3];s.residents[a.id].activity=a.task;s.residents[a.id].lookTarget=a.lookTarget;
  if(e?.queue?.[a.id])a.workstation=e.queue[a.id].vendor;
  if(D(a.p,target)<.035){if(a.courtesyDestination!==undefined&&a.courtesyArrivedAt===null)a.courtesyArrivedAt=s.time;if(a.crowdArrivedGoal!==goal){s.stats.completed++;a.crowdArrivedGoal=goal;}a.crowdV=[0,0];a.p[0]=target[0];a.p[1]=target[1];a.node=goal;a.path=[];a.target=null;a.mode='idle';a.actualSpeed=0;a.speed=0;a.gaitWeight+=(0-a.gaitWeight)*Math.min(1,dt*10);turn(a,a.lookTarget,dt);continue;}
  a.crowd??={goal:null,route:[],at:0,blocked:0,replan:0};const c=a.crowd;
  if(c.motionRevision!==2){Object.assign(c,{motionRevision:2,route:[],yieldUntil:0,passUntil:0,passSide:0,direction:null,watchAt:s.time,watchP:a.p.slice(),watchDistance:a.walked});}
  if(c.intentKey!==(e?.id||'')+':'+home){c.intentKey=(e?.id||'')+':'+home;c.relocations=0;c.bestRemaining=D(a.p,target);c.goalProgressAt=s.time;c.direction=null;c.passUntil=0;c.watchAt=s.time;c.watchP=a.p.slice();c.watchDistance=a.walked;c.waitFor=[];}
  if(c.goal!==goal){c.bestRemaining=D(a.p,target);c.goalProgressAt=s.time;c.waitFor=[];c.direction=null;c.passUntil=0;c.watchAt=s.time;c.watchP=a.p.slice();c.watchDistance=a.walked;}
  if(D(a.p,target)<(c.bestRemaining??Infinity)-.08){c.bestRemaining=D(a.p,target);c.goalProgressAt=s.time;}
  const settle=()=>{a.actualSpeed=0;a.speed=0;a.crowdV=[0,0];a.mode='yield';a.path=[goal];a.gaitWeight+=(0-a.gaitWeight)*Math.min(1,dt*10);a.turnVelocity=0;};
  if(!a.interactionLock&&a.courtesyDestination===undefined&&!home&&e&&['gather','active'].includes(e.phase)&&s.time-(c.goalProgressAt||0)>2.5&&(c.relocations||0)<1&&s.time>=(c.relocationCheckAt||0)){
   c.relocationCheckAt=s.time+1.2;
   e.placePool??=groupPlaces(nav,e.kind,s).map(({node,lane,index})=>({node,index,...(lane===undefined?{}:{lane})}));
   const start=nodeAt(nav,a.p)??a.node,blocked=new Set(nav.nodes.flatMap((p,i)=>!moverClear(p)||s.actors.some(b=>b!==a&&Math.abs(b.p[2]-p[2])<1&&D(b.p,p)<.48)?[i]:[]));blocked.delete(start);
   const available=e.placePool.filter(p=>p.node!==goal&&!blocked.has(p.node)&&Object.entries(e.slots).every(([id,n])=>id===a.id||D(nav.nodes[p.node],nav.nodes[n])>.60)).sort((x,y)=>D(a.p,nav.nodes[x.node])-D(a.p,nav.nodes[y.node]));
   for(const place of available){const path=pathTo(nav,start,place.node,blocked);if(!path.length)continue;e.slots[a.id]=place.node;if(place.lane!==undefined)e.queue[a.id]={lane:place.lane,index:place.index,vendor:['resident.vendor_bread','resident.vendor_flower','resident.vendor_lamp'][place.lane]};c.relocations++;c.goalProgressAt=s.time;c.bestRemaining=D(a.p,nav.nodes[place.node]);c.yieldUntil=s.time+.25;c.direction=null;c.passUntil=0;c.route=[];a.reservation=place.node;a.responseDestination=place.node;settle();break;}
   if(e.slots[a.id]!==goal)continue;
  }
  if(c.waitFor?.length){const same=c.waitGoal===goal&&c.waitFor.every(w=>{const b=s.actors.find(b=>b.id===w.id);return b&&D(b.p,w.p)<.10;});if(same){if((home||a.interactionLock)&&s.time>=(c.courtesyAt||0)){makeRoom(s,nav,a,target);c.courtesyAt=s.time+1;}settle();turn(a,a.lookTarget,dt);continue;}c.waitFor=[];c.route=[];c.direction=null;c.passUntil=0;c.watchAt=s.time;c.watchP=a.p.slice();c.watchDistance=a.walked;c.goalProgressAt=s.time;c.bestRemaining=D(a.p,target);}
  if(s.time-(c.goalProgressAt||0)>2){const blockers=s.actors.filter(b=>b!==a&&Math.abs(b.p[2]-a.p[2])<1&&D(b.p,a.p)<.86&&(!b.mobile||!b.path.length||a.id>b.id));if(blockers.length){c.waitFor=blockers.map(b=>({id:b.id,p:b.p.slice()}));c.waitGoal=goal;settle();continue;}}
  if(s.time<c.yieldUntil){settle();continue;}
  if(s.time-c.watchAt>=.85){const progress=D(c.watchP,a.p),travel=a.walked-c.watchDistance;c.watchAt=s.time;c.watchP=a.p.slice();c.watchDistance=a.walked;if(progress<.08&&travel>.10){c.yieldUntil=s.time+patience(a.id);c.route=[];c.replan=c.yieldUntil;c.passUntil=0;c.direction=null;settle();continue;}}

  if(c.goal!==goal||!c.route.length||(c.blocked>.45||s.time-(c.progressAt||0)>1.2)&&s.time>=c.replan){
   const start=nodeAt(nav,a.p)??a.node,blocked=new Set();for(let i=0;i<nav.nodes.length;i++){const p=nav.nodes[i];if(!moverClear(p)||s.actors.some(b=>b!==a&&Math.abs(b.p[2]-p[2])<1&&D(b.p,p)<.48))blocked.add(i);}blocked.delete(start);blocked.delete(goal);
   let route=pathTo(nav,start,goal,blocked);if(!route.length)route=pathTo(nav,start,goal,new Set(),blocked);c.goal=goal;c.route=smoothRoute(nav,route,blocked);c.at=route.length>1?1:0;c.replan=s.time+.8;c.blocked=0;c.progressAt=s.time;c.progressDistance=D(a.p,target);
  }
  if(!c.route.length){a.mode='yield';a.path=[];a.actualSpeed=0;continue;}
  while(c.at<c.route.length-1&&D(a.p,nav.nodes[c.route[c.at]])<.18)c.at++;
  const next=nav.nodes[c.route[c.at]],yaw=Math.atan2(next[1]-a.p[1],next[0]-a.p[0]),baseSpeed=Math.min(a.courtesyDestination!==undefined?.78:e?.kind==='quiet'?.68:e?.kind==='music'?.83:1.0,Math.max(.08,D(a.p,target)*2.4)),people=s.actors.filter(b=>b!==a&&Math.abs(b.p[2]-a.p[2])<1.0&&D(b.p,a.p)<1.5);let best=null;
  for(const offset of [0,.30,-.30,.60,-.60,.95,-.95,1.3,-1.3,Math.PI/2,-Math.PI/2])for(const factor of [1,.55]){
   if(c.passUntil>s.time&&Math.abs(offset)>.2&&Math.sign(offset)!==c.passSide)continue;
   const theta=yaw+offset,alignment=Math.max(.08,Math.cos(theta+Math.PI/2-a.yaw)),velocity=[Math.cos(theta)*baseSpeed*factor*alignment,Math.sin(theta)*baseSpeed*factor*alignment],p=[a.p[0]+velocity[0]*dt,a.p[1]+velocity[1]*dt,a.p[2]],probeTime=Math.min(.22,D(a.p,next)/baseSpeed),probe=[a.p[0]+velocity[0]*probeTime,a.p[1]+velocity[1]*probeTime,a.p[2]],n=nodeAt(nav,p),nn=nodeAt(nav,probe);if(n===undefined||nn===undefined||graph.components[n]!==graph.components[a.node]||Math.abs(nav.nodes[n][2]-a.p[2])>.17||(!moverClear(p)&&moverClear(a.p)))continue;
   let collision=false,near=0;for(const b of people){const gap=.23*(a.scale+b.scale)+.015,now=D(a.p,b.p),after=D(p,b.p),future=D(probe,[b.p[0]+(b.crowdV?.[0]||0)*.12,b.p[1]+(b.crowdV?.[1]||0)*.12]);if(after<gap&&after<now-.00001){collision=true;break;}near+=Math.max(0,.56-future)*.6;}
   if(collision)continue;const continuity=c.direction===null?0:Math.abs(angle(c.direction,theta))*.035;const score=D(probe,next)+Math.abs(offset)*.04+(1-factor)*.04+near+continuity;if(!best||score<best.score)best={p,n,velocity,score,theta,offset};
  }
  a.path=c.route.slice(c.at);a.target=goal;
  if(!best){c.blocked+=dt;if((home||a.interactionLock)&&c.blocked>.65&&s.time>=(c.courtesyAt||0)){makeRoom(s,nav,a,next);c.courtesyAt=s.time+1;}a.crowdV=[0,0];a.actualSpeed=0;a.speed=0;a.mode='yield';a.gaitWeight+=(0-a.gaitWeight)*Math.min(1,dt*8);continue;}
  if(Math.abs(best.offset)>.2&&people.some(b=>D(b.p,a.p)<.9)&&s.time>=c.passUntil){c.passSide=Math.sign(best.offset);c.passUntil=s.time+.9;}c.direction=best.theta;
  const moved=D(best.p,a.p);a.p=best.p;a.p[2]=nav.nodes[best.n][2]-.02*a.scale+.006;a.node=best.n;a.walked+=moved;a.actualSpeed=moved/dt;a.speed=a.actualSpeed;a.mode='walk';a.crowdV=best.velocity;a.gaitWeight+=(Math.min(1,a.actualSpeed/.55)-a.gaitWeight)*Math.min(1,dt*8);turn(a,[a.p[0]+best.velocity[0],a.p[1]+best.velocity[1]],dt);c.blocked=0;if(D(a.p,target)<(c.progressDistance??Infinity)-.06){c.progressDistance=D(a.p,target);c.progressAt=s.time;}s.stats.moves++;
 }
}
