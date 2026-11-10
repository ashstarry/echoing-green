import {inviteFoxNeighbor,settleFoxMeeting} from './fox-rendezvous.mjs';
import {rainingAt} from './local-cloud.mjs';
import {foxGroundGreeting,foxBicycleGap} from './fox-ground-path.mjs';
import {makeRoom} from './event-travel.mjs';
import {varied} from './cadence.mjs';
import {foxCurve,foxBackstep,foxPathPose,foxFloor,foxTurnArc} from './fox-path.mjs';
const ID='animal.garden_fox',D=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]),clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
// Fox half-width plus a resident's body radius, with a small margin.
const PERSON_CLEARANCE=.38;
const modes=new Set(['explore','sniff','look','rest','play','greet','stretch']);
const delta=(a,b)=>Math.atan2(Math.sin(b-a),Math.cos(b-a));
export function ensureFoxBehavior(s){return s.foxBehavior??={phase:'look',clock:0,duration:2.5,cycle:0,path:[],at:0,velocity:0,blocked:0,neighbor:null,command:null,seenControl:null,completedControl:null,completed:0,suspended:false,reacted:false};}
const people=s=>s.actors.filter(a=>s.passengers?.[a.id]?.phase!=='riding'&&s.diners?.[a.id]?.phase!=='inside').map(a=>({id:a.id,p:s.eventGuests?.[a.id]?.active?s.eventGuests[a.id].p:s.localWalkers?.[a.id]?.root?.slice(0,3)||a.p,actor:a}));
function separation(p,yaw,q){const dx=q[0]-p[0],dy=q[1]-p[1],c=Math.cos(yaw),n=Math.sin(yaw),u=dx*c+dy*n,v=-dx*n+dy*c;return Math.hypot(u-clamp(u,-.70,.72),v);}
function settled(m,f,dt){f.velocity=0;m.speed=0;m.strideWeight+=(0-m.strideWeight)*Math.min(1,dt*7);m.intent=f.phase;}
function pause(f,phase,seconds){f.phase=phase;f.clock=0;f.duration=seconds;f.path=[];f.route=null;f.velocity=0;}
function bikeRouteBlocked(s,m,route){const bike=s.movers['bicycle.street_bicycle'];return !!bike&&route.poses.some((p,i)=>i%3===0&&foxBicycleGap(p.p,bike)<.56&&foxBicycleGap(p.p,bike)<foxBicycleGap(m.p,bike)-.01);}
function beginWalk(s,data,m,f,goalMode,nav=null){
 f.obstruction=null;const ps=people(s),neighbors=goalMode==='greet'?ps.map(a=>a.id===f.invitedNeighbor&&f.meetingPoint?{...a,p:f.meetingPoint}:a).filter(a=>D(m.p,a.p)<(a.id===f.invitedNeighbor?15:8)&&((f.greetingTravel||0)>1.7||D(m.p,a.p)>1.7||a.id===f.invitedNeighbor)&&!a.actor.interactionLock&&Math.abs(a.p[2]-m.p[2])<.5&&!a.id.includes('vendor')).sort((a,b)=>(Math.abs(D(m.p,a.p)-3.0)-(a.id===f.invitedNeighbor?4:0)-(a.id.includes('child')?.3:0)+(s.residentActions?.[a.id]?.requested?2:0))-(Math.abs(D(m.p,b.p)-3.0)-(b.id===f.invitedNeighbor?4:0)-(b.id.includes('child')?.3:0)+(s.residentActions?.[b.id]?.requested?2:0))).slice(0,9):[null];
 if(goalMode==='greet'&&(f.greetingTravel||0)>=1.7&&D(m.p,f.greetingOrigin||m.p)>=1.2){const close=ps.filter(a=>D(m.p,a.p)>.50&&D(m.p,a.p)<=1.16&&Math.abs(a.p[2]-m.p[2])<.5&&!a.id.includes('vendor')&&!a.actor.interactionLock&&Math.abs(delta(m.yaw,Math.atan2(a.p[1]-m.p[1],a.p[0]-m.p[0])+Math.PI))<1.85).sort((a,b)=>D(a.p,m.p)-D(b.p,m.p))[0];if(close){pause(f,'greet',5.2);f.neighbor=close.id;f.reacted=false;f.greeted=false;return true;}}
 const leaf=goalMode==='leaf'?s.craftWorld?.leaves.find(p=>!p.collected&&D(p.center,m.p)<3.5):null,goals=goalMode==='aside'?[[5.15,1.7,.624],...data.nodes]:data.nodes;
 let chosen=null,neighbor=null;
 for(const near of(f.pavingNeeded&&goalMode==='greet'?[]:neighbors)){
  const options=goals.map(p=>({p,d:D(p,m.p),turn:Math.abs(delta(m.yaw,Math.atan2(p[1]-m.p[1],p[0]-m.p[0])+Math.PI))})).filter(x=>x.d>(near?Math.max(.10,1.75-(f.greetingTravel||0)):.44)&&x.d<(near?3.5:2.5)&&(!near||D(x.p,near.p)>.78&&D(x.p,near.p)<1.1)&&(goalMode!=='shelter'||!rainingAt(s,x.p))).sort((a,b)=>{const score=x=>Math.abs(x.d-(near?2.25:1.25))+x.turn*.22+(near?Math.abs(D(x.p,near.p)-.88)*1.4:0)+(leaf?Math.abs(D(x.p,leaf.center)-.85):0)+(goalMode==='aside'?-x.p[0]*.45:0);if(goalMode==='aside'&&(a.p[0]>5||b.p[0]>5))return b.p[0]-a.p[0];return score(a)-score(b);});
  for(const x of options.slice(0,70)){
   const endYaw=goalMode==='aside'&&x.p[0]>5?Math.PI:near?Math.atan2(near.p[1]-x.p[1],near.p[0]-x.p[0])+Math.PI:Math.atan2(x.p[1]-m.p[1],x.p[0]-m.p[0])+Math.PI;
   search:for(const offset of(near?[0,.4,-.4,.85,-.85]:[0,.6,-.6,1.2,-1.2,1.8,-1.8,Math.PI]))for(const handle of[.27,.38,.62,.90]){
    const heading=endYaw+offset;if(!(goalMode==='aside'&&x.p[0]>5)&&foxFloor(data,[x.p[0]-Math.cos(heading)*.26,x.p[1]-Math.sin(heading)*.26])===null)continue;
    const route=foxCurve(data,m.p,m.yaw,x.p,heading,handle);if(!route||bikeRouteBlocked(s,m,route))continue;
    if(route.poses.some((p,i)=>i%4===0&&ps.some(a=>Math.abs(a.p[2]-p.p[2])<1&&separation(p.p,p.yaw,a.p)<PERSON_CLEARANCE&&separation(p.p,p.yaw,a.p)<separation(m.p,m.yaw,a.p)-.02)))continue;
    chosen=route;neighbor=near;break search;
   }
   if(chosen)break;
  }
  if(chosen)break;
 }
 if(!chosen&&goalMode==='greet'){const fallback=foxGroundGreeting(data,m,neighbors,[...ps,...Object.entries(s.movers).filter(([id])=>id==='bicycle.street_bicycle').map(([id,m])=>({id,p:m.p,bike:m}))],Math.max(.10,1.75-(f.greetingTravel||0)));if(fallback){chosen=fallback.route;neighbor=fallback.neighbor;}}
 // When furniture/people split the promenade, first travel toward an open
 // intermediate patch. A staging walk cannot be mistaken for the greeting.
 if(!chosen&&goalMode==='greet'){
  const near=neighbors.find(Boolean),stages=data.nodes.map(p=>({p,d:D(p,m.p)})).filter(x=>x.d>.75&&x.d<1.65&&(!near||D(x.p,near.p)<D(m.p,near.p)-.18)).sort((a,b)=>(near?D(a.p,near.p)-D(b.p,near.p):b.d-a.d));
  outer:for(const x of stages.slice(0,60))for(const off of[0,.5,-.5,1,-1])for(const h of[.27,.42,.7]){
   const heading=Math.atan2(x.p[1]-m.p[1],x.p[0]-m.p[0])+Math.PI+off,route=foxCurve(data,m.p,m.yaw,x.p,heading,h);if(!route||bikeRouteBlocked(s,m,route))continue;
   if(route.poses.some((p,i)=>i%3===0&&ps.some(a=>Math.abs(a.p[2]-p.p[2])<1&&separation(p.p,p.yaw,a.p)<PERSON_CLEARANCE&&separation(p.p,p.yaw,a.p)<separation(m.p,m.yaw,a.p)-.01)))continue;
   chosen={...route,maneuver:'stage'};neighbor=near;break outer;
  }
 }
 // Try a walking arc before backing up again. A single end-to-end cubic
 // cannot describe every safe U-turn in this narrow, irregular garden.
 if(!chosen&&s.time-(f.lastTurnAt??-100)>(goalMode==='greet'?.5:12)&&(goalMode!=='greet'||(f.greetingTurns||0)<2)){
  const turns=[];for(const side of[-1,1])for(const radius of(goalMode==='greet'?[.22,.27,.34,.42,.16,.12,.08]:[.27,.34,.42]))for(const angle of[Math.PI,Math.PI/2]){
   const arc=foxTurnArc(data,m.p,m.yaw,side,radius,angle);if(!arc||bikeRouteBlocked(s,m,arc))continue;
   if(arc.poses.some((p,i)=>i%3===0&&ps.some(a=>Math.abs(a.p[2]-p.p[2])<1&&separation(p.p,p.yaw,a.p)<PERSON_CLEARANCE&&separation(p.p,p.yaw,a.p)<separation(m.p,m.yaw,a.p)-.01)))continue;
   const end=arc.poses.at(-1),target=neighbors.find(Boolean),desired=target?Math.atan2(target.p[1]-end.p[1],target.p[0]-end.p[0])+Math.PI:Math.atan2(1.15-end.p[1],3.1-end.p[0])+Math.PI;
   turns.push({arc,score:Math.abs(delta(end.yaw,desired))+arc.length*.15});
  }
  if(turns.length){chosen=turns.sort((a,b)=>a.score-b.score)[0].arc;f.lastTurnAt=s.time;if(goalMode==='greet')f.greetingTurns=(f.greetingTurns||0)+1;}
 }
 // Back up with actual footsteps if the nose is against the edge; do not spin.
 if(!chosen&&((f.failedPlans||0)>=1||goalMode==='greet')&&(goalMode==='greet'?(f.greetingBacksteps||0)<3&&s.time-(f.lastBackAt??-100)>.9:s.time-(f.lastBackAt??-100)>25)){const back=foxBackstep(data,m.p,m.yaw,goalMode==='greet'&&m.p[0]>4.05?Math.min(1.5,m.p[0]-3.7):.27);if(back){const safe=[];for(const pose of back.poses){const bike=s.movers['bicycle.street_bicycle'];if(bike&&foxBicycleGap(pose.p,bike)<.56&&foxBicycleGap(pose.p,bike)<foxBicycleGap(m.p,bike)-.01)break;const obstacle=ps.find(a=>separation(pose.p,pose.yaw,a.p)<PERSON_CLEARANCE&&separation(pose.p,pose.yaw,a.p)<separation(m.p,m.yaw,a.p)-.01);if(obstacle){f.obstruction=obstacle.id;break;}safe.push(pose);}if(safe.length>=5)chosen={...back,poses:safe,length:safe.at(-1).d};}}
 // A curved backward step can leave the retreat strip when a straight
 // backstep or forward turn has no room. It ends on an open piece of paving.
 if(!chosen&&goalMode==='greet'&&!f.reverseCurveUsed){
  const pads=data.nodes.filter(p=>D(p,m.p)>.7&&D(p,m.p)<2.2&&[[.28,0],[-.28,0],[0,.28],[0,-.28]].every(([x,y])=>foxFloor(data,[p[0]+x,p[1]+y])!==null)).sort((a,b)=>D(a,m.p)-D(b,m.p));
  outer:for(const end of pads.slice(0,70))for(const offset of[0,.6,-.6,1.2,-1.2,Math.PI])for(const handle of[.18,.27,.38,.62]){
   const heading=Math.atan2(end[1]-m.p[1],end[0]-m.p[0])+Math.PI+offset,arc=foxCurve(data,m.p,m.yaw+Math.PI,end,heading,handle);if(!arc)continue;
   const route={...arc,reverse:true,maneuver:'reverse_curve',poses:arc.poses.map(p=>({...p,yaw:p.yaw-Math.PI}))};if(bikeRouteBlocked(s,m,route))continue;
   if(route.poses.some((p,i)=>i%3===0&&ps.some(a=>Math.abs(a.p[2]-p.p[2])<1&&separation(p.p,p.yaw,a.p)<PERSON_CLEARANCE&&separation(p.p,p.yaw,a.p)<separation(m.p,m.yaw,a.p)-.01)))continue;
   chosen=route;f.reverseCurveUsed=true;f.greetingTurns=0;break outer;
  }
 }
 if(!chosen){if(goalMode==='greet'&&nav&&!s.objectControls?.[ID]?.preserveOthers&&s.time>(f.roomAt||0)){makeRoom(s,nav,{id:ID,p:m.p,interactionLock:true},m.p);f.roomAt=s.time+1;}f.failedPlans=(f.failedPlans||0)+1;pause(f,'look',goalMode==='greet'?.35:varied([2,4],ID,f.cycle));f.goalMode=goalMode;return false;}
 f.failedPlans=0;if(chosen.reverse){f.lastBackAt=s.time;if(goalMode==='greet')f.greetingBacksteps=(f.greetingBacksteps||0)+1;}f.route=chosen;f.routeDistance=0;f.path=[];f.at=0;f.goalMode=goalMode;f.neighbor=neighbor?.id||f.invitedNeighbor||null;f.phase='walk';f.clock=0;f.velocity=0;f.blocked=0;f.reacted=false;f.greeted=false;return true;
}
export function suspendFox(s){const f=ensureFoxBehavior(s);f.suspended=true;f.velocity=0;}
export function advanceFox(s,data,dt,requestGesture=()=>{},{clearing=false,nav=null}={}){
 const m=s.movers?.[ID];if(!m||!data?.nodes?.length)return false;const f=ensureFoxBehavior(s),c=s.objectControls?.[ID],key=c?c.action+':'+c.started:null;
 if(f.motionVersion!==2){f.motionVersion=2;f.route=null;f.path=[];if(f.phase==='walk')pause(f,'look',1.5);delete m.eventHome;}f.suspended=false;
 if(key!==f.seenControl){f.seenControl=key;f.completedControl=null;f.command=c?.action||null;f.reacted=false;f.greeted=false;f.neighbor=null;f.immediateGreeting=false;f.wasClearing=false;f.greetingBacksteps=0;f.greetingTurns=0;f.reverseCurveUsed=false;f.invitedNeighbor=null;f.meetingPoint=null;f.pavingNeeded=false;f.greetingTravel=0;f.greetingOrigin=m.p.slice();if(c?.action==='play')pause(f,'bow',1.8);else if(c?.action==='greet'){inviteFoxNeighbor(s,nav);beginWalk(s,data,m,f,'greet',nav);}else if(c?.action==='stretch')pause(f,'stretch',5.5);else if(c?.action==='explore')beginWalk(s,data,m,f,'explore',nav);else pause(f,c?.action||'look',3);}
 if(f.command==='greet'&&(f.failedPlans||f.obstruction))inviteFoxNeighbor(s,nav,f.obstruction);
 const held=['sniff','look','rest'].includes(c?.action)?c.action:!c&&s.animals==='rest'?'rest':null;
 if(held){if(f.phase!==held)pause(f,held,20);f.clock+=dt;settled(m,f,dt);return true;}
 if(!c||f.completedControl===key){const wet=rainingAt(s,m.p);if(wet&&!f.rainReacted){f.rainReacted=true;beginWalk(s,data,m,f,'shelter',nav);}if(!wet)f.rainReacted=false;const leaf=s.craftWorld?.leaves.find(p=>!p.collected&&D(p.center,m.p)<3.5&&f.lastLeaf!==p.id);if(!wet&&leaf&&f.phase!=='walk'){f.lastLeaf=leaf.id;beginWalk(s,data,m,f,'leaf',nav);}}
 // A fresh local wish owns the fox over an older ambient gathering.
 clearing=clearing&&!(c&&c.started>=(s.sceneEvent?.started??Infinity)&&f.completedControl!==key);
 if(clearing&&D(m.p,[5.15,1.7])<.08){if(f.phase!=='look'||f.route)pause(f,'look',999);f.clock+=dt;settled(m,f,dt);f.wasClearing=true;return true;}if(!clearing&&f.wasClearing)pause(f,'look',2);if(clearing&&!f.wasClearing)beginWalk(s,data,m,f,'aside',nav);f.wasClearing=clearing;f.clock+=dt;
 if(f.phase==='walk'&&f.route){const route=f.route,left=route.length-f.routeDistance,pose=foxPathPose(route,f.routeDistance),top=route.reverse?(f.command==='greet'?.32:.18):f.goalMode==='greet'?.64:f.goalMode==='play'?.55:.40;const wanted=Math.min(route.maneuver==='paving'&&Math.abs(delta(m.yaw,pose.yaw))>1.0?Math.min(.30,top):top,Math.sqrt(Math.max(0,left)*.32),(f.command==='greet'?1.15:.85)/Math.max(.01,route.maneuver==='paving'?0:pose.curvature));f.velocity+=clamp(wanted-f.velocity,-dt*.65,dt*.65);const move=Math.min(left,f.velocity*dt),next=foxPathPose(route,f.routeDistance+move),ps=people(s);if(route.maneuver==='paving')next.yaw=m.yaw+clamp(delta(m.yaw,next.yaw),-dt*1.15*Math.min(1,move/dt/.06),dt*1.15*Math.min(1,move/dt/.06));
  const blocked=ps.some(a=>Math.abs(a.p[2]-next.p[2])<1&&(route.maneuver==='paving'?D(next.p,a.p)<.53&&D(next.p,a.p)<D(m.p,a.p)-1e-6:separation(next.p,next.yaw,a.p)<PERSON_CLEARANCE&&separation(next.p,next.yaw,a.p)<separation(m.p,m.yaw,a.p)-1e-6))||Object.entries(s.movers).some(([id,b])=>id==='bicycle.street_bicycle'&&foxBicycleGap(next.p,b)<.56&&foxBicycleGap(next.p,b)<foxBicycleGap(m.p,b));
  if(blocked){f.blocked+=dt;if(f.command==='greet'&&f.blocked>.4)f.pavingNeeded=true;if(f.command==='greet'&&nav&&!c?.preserveOthers&&f.blocked>.25&&s.time>(f.roomAt||0)){makeRoom(s,nav,{id:ID,p:m.p,interactionLock:true},next.p);f.roomAt=s.time+1;}if(f.command==='greet'&&f.blocked>.4){const obstruction=ps.find(a=>separation(next.p,next.yaw,a.p)<.55);inviteFoxNeighbor(s,nav,obstruction?.id);} settled(m,f,dt);m.intent='yield';const neighbor=ps.filter(a=>D(m.p,a.p)<1.18&&Math.abs(delta(m.yaw,Math.atan2(a.p[1]-m.p[1],a.p[0]-m.p[0])+Math.PI))<1.1&&!a.id.includes('vendor')&&!a.actor.interactionLock).sort((a,b)=>D(m.p,a.p)-D(m.p,b.p))[0];if(f.command==='greet'&&!route.reverse&&neighbor&&(f.greetingTravel||0)>1.7&&D(m.p,f.greetingOrigin||m.p)>1.2){f.neighbor=neighbor.id;pause(f,'greet',5.2);return true;}if(f.blocked>(f.command==='greet'?.65:3.5))pause(f,'look',f.command==='greet'?.35:varied([2,4],ID,f.cycle++));return true;}
  f.blocked=0;f.routeDistance+=move;const reverseFeet=route.reverse||route.maneuver==='paving'&&((next.p[0]-m.p[0])*-Math.cos(m.yaw)+(next.p[1]-m.p[1])*-Math.sin(m.yaw))<0,footTravel=move+(['turn','paving'].includes(route.maneuver)?Math.abs(delta(m.yaw,next.yaw))*.24:0);m.p=next.p;m.yaw=next.yaw;m.distance+=footTravel*(reverseFeet?-1:1);if(f.command==='greet')f.greetingTravel=(f.greetingTravel||0)+move;m.speed=Math.min(1,footTravel/(dt*.52));m.intent=route.reverse?'step_back':['play','greet'].includes(f.goalMode)?'trot':'explore';m.strideWeight+=(Math.min(1,footTravel/dt/.25)-m.strideWeight)*Math.min(1,dt*6);
  if(f.command==='greet'&&(f.greetingTravel||0)>=1.7&&D(m.p,f.greetingOrigin||m.p)>=1.2){const met=ps.filter(a=>D(m.p,a.p)>.50&&D(m.p,a.p)<1.08&&Math.abs(a.p[2]-m.p[2])<.5&&!a.id.includes('vendor')&&!a.actor.interactionLock&&Math.abs(delta(m.yaw,Math.atan2(a.p[1]-m.p[1],a.p[0]-m.p[0])+Math.PI))<1.5).sort((a,b)=>D(m.p,a.p)-D(m.p,b.p))[0];if(met){f.neighbor=met.id;pause(f,'greet',5.2);f.reacted=false;f.greeted=false;return true;}}
  if(left<.003||move>=left){const goal=f.goalMode,reverse=route.reverse,turning=route.maneuver==='turn';if(goal==='greet'&&!reverse&&!turning&&((f.greetingTravel||0)<1.7||D(m.p,f.greetingOrigin||m.p)<1.2)){pause(f,'look',.2);return true;}if(turning||route.maneuver==='stage'){pause(f,'look',.15);return true;}pause(f,reverse?'look':goal==='greet'?'greet':goal==='play'?'play':'sniff',reverse?(f.command==='greet'?.3:1.5):goal==='greet'?5.2:goal==='play'?4:varied([3,6],ID,f.cycle));}return true;}
 settled(m,f,dt);
 if(f.phase==='greet'&&f.neighbor){const a=people(s).find(a=>a.id===f.neighbor);if(a&&D(m.p,a.p)>1.18&&!f.greeted){beginWalk(s,data,m,f,'greet',nav);return true;}if(a&&D(m.p,a.p)<=1.18){f.greeted=true;if(!f.reacted&&!c?.preserveOthers&&!a.actor.interactionLock&&!s.residentActions[a.id]?.requested){const r=s.residentActions[a.id];if(r?.action&&r.action!=='greet')r.cancelRemaining=.25;a.actor.path=[];a.actor.target=null;a.actor.reservation=null;a.actor.wait=5.8;a.actor.mode='idle';a.actor.actualSpeed=0;a.actor.speed=0;settleFoxMeeting(s,a);requestGesture(a.id,'greet');f.reacted=true;}}}
 if(f.clock>=f.duration){if(f.phase==='bow'){beginWalk(s,data,m,f,'play',nav);return true;}if(f.command==='play'&&f.phase!=='play'){beginWalk(s,data,m,f,'play',nav);return true;}if(f.command==='greet'&&!f.greeted&&!f.immediateGreeting){beginWalk(s,data,m,f,'greet',nav);return true;}
  if(f.command&&['play','greet','stretch'].includes(f.command)&&f.completedControl!==f.seenControl){f.completedControl=f.seenControl;f.completed++;f.command=null;pause(f,'look',varied([2,4],ID,f.cycle));return true;}
  f.cycle++;if(f.cycle%5===1)pause(f,'groom',3.4);else if(f.cycle%5===3)pause(f,'stretch',2.8);else beginWalk(s,data,m,f,clearing?'aside':'explore',nav);}return true;
}
export function foxPose(s){
 const f=s.foxBehavior,m=s.movers?.[ID],zero={headPitch:0,headTurn:0,tail:0,front:0,back:0,lift:0,paw:0,groom:0};
 if(s.musicCircle?.phase==='listen'&&s.sceneEvent?.kind==='music')return {...zero,headPitch:-.12,headTurn:clamp(delta(m.yaw,Math.atan2(-1.4537-m.p[1],-2.4684-m.p[0])+Math.PI),-1.45,1.45),tail:Math.sin(s.time*3.8)*.24};
 if(!f||f.suspended)return zero;
 const t=f.clock,held=['look','sniff','rest'].includes(s.objectControls?.[ID]?.action)||s.animals==='rest',soft=clamp(Math.min(t/.45,f.phase==='walk'||held?1:(f.duration-t)/.5),0,1),friendly=['greet','play'].includes(f.phase),stretch=['stretch','bow'].includes(f.phase),groom=f.phase==='groom';
 const neighbor=people(s).find(a=>a.id===f.neighbor),look=neighbor&&f.phase==='greet'?clamp(delta(m.yaw,Math.atan2(neighbor.p[1]-m.p[1],neighbor.p[0]-m.p[0])+Math.PI),-1.05,1.05):f.phase==='look'?Math.sin(t*.9)*.16:0;
 // The body keeps its foot-driven heading. Greeting and grooming use the neck,
 // individual front paws and articulated tail, never a spin about the root.
 return {headPitch:(f.phase==='sniff'?.24+.05*Math.sin(t*2.2):groom?.42+.10*Math.sin(t*6):stretch?.24:friendly?-.24:0)*soft,headTurn:(groom?-.25:look)*soft,
 tail:(friendly?Math.sin(t*6.8)*.48:f.phase==='walk'?Math.sin(s.time*4)*.12:f.phase==='rest'?.025*Math.sin(t):Math.sin(s.time*2.4)*.16)*soft,
 front:stretch?.28*Math.sin(Math.PI*clamp(t/f.duration,0,1)):0,back:stretch?-.07*Math.sin(Math.PI*clamp(t/f.duration,0,1)):0,
 paw:(f.phase==='greet'?(1.06+.08*Math.sin(t*4.8))*Math.sin(Math.PI*clamp((t-.65)/3.9,0,1)):friendly?1.12*Math.pow(Math.max(0,Math.sin(t*3.4)),2):groom?.9:0)*soft,groom:Number(groom)*soft,lift:friendly?.025*Math.max(0,Math.sin(t*3.4))*soft:0};
}
export function validateFox(s,data){if(!s.foxBehavior)return;const f=s.foxBehavior;if(!['walk','look','sniff','rest','stretch','greet','play','bow','groom'].includes(f.phase)||![f.clock,f.duration,f.velocity,f.cycle,f.completed].every(Number.isFinite)||!Array.isArray(f.path)||f.path.some(i=>!Number.isInteger(i)||!data?.nodes[i])||f.command&&!modes.has(f.command))throw Error('Invalid fox behavior');if(f.route&&(!Number.isFinite(f.routeDistance)||!Number.isFinite(f.route.length)||f.route.poses.length>256||f.route.poses.length<2||f.route.poses.some(p=>!p.p.every(Number.isFinite)||!Number.isFinite(p.yaw)||!Number.isFinite(p.d))))throw Error('Invalid fox route');}
export const FOX_PHASE_LABELS={walk:'沿花园空地走走',look:'抬头看看周围',sniff:'停下来认真闻一闻',rest:'安静歇一会',groom:'抬起前爪，低头舔一舔',stretch:'伸展前爪，舒展身体',greet:'朝附近居民摇尾打招呼',play:'停下摇尾，等邻居回应',bow:'压低前身，邀请一起玩'};
