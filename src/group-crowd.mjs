import {pathTo,navigationGraph} from './navigation.mjs?v=cp32-events-dea0a76ba5ff';
import {moverBlocks} from './motion.mjs?v=cp32-events-dea0a76ba5ff';
import {FIREWORK_FOCUS} from './event-design.mjs?v=cp32-events-dea0a76ba5ff';
const D=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
function nodeAt(nav,p){const x=Math.round((p[0]-nav.origin[0])/nav.step),y=Math.round((p[1]-nav.origin[1])/nav.step);return nav.grid[x+','+y];}
function targetOf(s,a){const g=s.eventGuests?.[a.id],e=s.sceneEvent;return a.guestReturnNode??a.guestStageNode??(['gather','active','closing'].includes(e?.phase)?e.slots?.[a.id]:undefined)??(g?.active&&g.phase==='hold'?g.goal:undefined);}
function turn(a,target,dt){const want=Math.atan2(target[1]-a.p[1],target[0]-a.p[0])+Math.PI/2;a.yaw+=clamp(Math.atan2(Math.sin(want-a.yaw),Math.cos(want-a.yaw)),-dt*3.8,dt*3.8);}
export function advanceGroupCrowd(s,nav,dt){
 const crowd=s.actors.filter(a=>a.mobile&&targetOf(s,a)!==undefined),graph=navigationGraph(nav);
 const moverClear=p=>Object.entries(s.movers).every(([id,m])=>!['ride','creature_walk'].includes(nav.activities.clips[id].motion)||!moverBlocks(p,m,nav.activities.clips[id],.24));
 // Plan against actual bodies and static terrain. A nearby free point is never substituted for a queue position.
 for(const a of crowd){const goal=targetOf(s,a),target=nav.nodes[goal],g=s.eventGuests?.[a.id],e=s.sceneEvent;const home=a.guestReturnNode!==undefined;a.groupDrivenTick=s.tick;a.segment=0;a.reservation=goal;a.responseDestination=goal;a.localActionUntil=0;a.manualActivity=null;a.wait=0;a.task=home?'stroll':e?.kind==='festival'?'fireworks':e?.kind==='reunion'?'chat':'browse';a.lookTarget=home?target:e?.kind==='festival'?FIREWORK_FOCUS:e?.queue?.[a.id]?nav.activities.spaces.residents[e.queue[a.id].vendor].position:[-.27,-.54,1.3];s.residents[a.id].activity=a.task;s.residents[a.id].lookTarget=a.lookTarget;
  if(e?.queue?.[a.id])a.workstation=e.queue[a.id].vendor;
  if(D(a.p,target)<.035){if(a.crowdArrivedGoal!==goal){s.stats.completed++;a.crowdArrivedGoal=goal;}a.crowdV=[0,0];a.p[0]=target[0];a.p[1]=target[1];a.node=goal;a.path=[];a.target=null;a.mode='idle';a.actualSpeed=0;a.speed=0;a.gaitWeight+=(0-a.gaitWeight)*Math.min(1,dt*10);turn(a,a.lookTarget,dt);continue;}
  a.crowd??={goal:null,route:[],at:0,blocked:0,replan:0};const c=a.crowd;
  if(c.goal!==goal||!c.route.length||(c.blocked>.45||s.time-(c.progressAt||0)>1.2)&&s.time>=c.replan){
   const start=nodeAt(nav,a.p)??a.node,blocked=new Set();for(let i=0;i<nav.nodes.length;i++){const p=nav.nodes[i];if(!moverClear(p)||s.actors.some(b=>b!==a&&Math.abs(b.p[2]-p[2])<1&&D(b.p,p)<.48))blocked.add(i);}blocked.delete(start);blocked.delete(goal);
   let route=pathTo(nav,start,goal,blocked);if(!route.length)route=pathTo(nav,start,goal,new Set(),blocked);c.goal=goal;c.route=route;c.at=route.length>1?1:0;c.replan=s.time+.8;c.blocked=0;c.progressAt=s.time;c.progressDistance=D(a.p,target);
  }
  if(!c.route.length){a.mode='yield';a.path=[];a.actualSpeed=0;continue;}
  while(c.at<c.route.length-1&&D(a.p,nav.nodes[c.route[c.at]])<.18)c.at++;
  const next=nav.nodes[c.route[c.at]],yaw=Math.atan2(next[1]-a.p[1],next[0]-a.p[0]),baseSpeed=Math.min(1.0,Math.max(.22,D(a.p,target)*1.8)),people=s.actors.filter(b=>b!==a&&Math.abs(b.p[2]-a.p[2])<1.0&&D(b.p,a.p)<1.5);let best=null;
  for(const offset of [0,.30,-.30,.60,-.60,.95,-.95,1.3,-1.3,1.7,-1.7,2.2,-2.2,Math.PI])for(const factor of [1,.55]){
   const theta=yaw+offset,velocity=[Math.cos(theta)*baseSpeed*factor,Math.sin(theta)*baseSpeed*factor],p=[a.p[0]+velocity[0]*dt,a.p[1]+velocity[1]*dt,a.p[2]],probe=[a.p[0]+velocity[0]*.22,a.p[1]+velocity[1]*.22,a.p[2]],n=nodeAt(nav,p),nn=nodeAt(nav,probe);if(n===undefined||nn===undefined||graph.components[n]!==graph.components[a.node]||Math.abs(nav.nodes[n][2]-a.p[2])>.17||(!moverClear(p)&&moverClear(a.p)))continue;
   let collision=false,near=0;for(const b of people){const gap=.23*(a.scale+b.scale)+.015,now=D(a.p,b.p),after=D(p,b.p),future=D(probe,[b.p[0]+(b.crowdV?.[0]||0)*.12,b.p[1]+(b.crowdV?.[1]||0)*.12]);if(after<gap&&after<now-.00001){collision=true;break;}near+=Math.max(0,.56-future)*.6;}
   if(collision)continue;const score=D(probe,next)+Math.abs(offset)*.04+(1-factor)*.04+near;if(!best||score<best.score)best={p,n,velocity,score};
  }
  a.path=c.route.slice(c.at);a.target=goal;
  if(!best){c.blocked+=dt;a.crowdV=[0,0];a.actualSpeed=0;a.speed=0;a.mode='yield';a.gaitWeight+=(0-a.gaitWeight)*Math.min(1,dt*8);continue;}
  const moved=D(best.p,a.p);a.p=best.p;a.p[2]=nav.nodes[best.n][2]-.02*a.scale+.006;a.node=best.n;a.walked+=moved;a.actualSpeed=moved/dt;a.speed=a.actualSpeed;a.mode='walk';a.crowdV=best.velocity;a.gaitWeight+=(Math.min(1,a.actualSpeed/.55)-a.gaitWeight)*Math.min(1,dt*8);turn(a,[a.p[0]+best.velocity[0],a.p[1]+best.velocity[1]],dt);c.blocked=0;if(D(a.p,target)<(c.progressDistance??Infinity)-.06){c.progressDistance=D(a.p,target);c.progressAt=s.time;}s.stats.moves++;
 }
}
