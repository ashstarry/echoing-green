import {rainingAt} from './local-cloud.mjs';
import {varied} from './cadence.mjs';
const ID='animal.garden_fox';const D=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const modes=new Set(['explore','sniff','look','rest','play','greet','stretch']);
export function ensureFoxBehavior(s){return s.foxBehavior??={phase:'look',clock:0,duration:2.5,cycle:0,path:[],at:0,velocity:0,blocked:0,neighbor:null,command:null,seenControl:null,completedControl:null,completed:0,suspended:false,reacted:false};}
function people(s){return s.actors.map(a=>({id:a.id,p:s.eventGuests?.[a.id]?.active?s.eventGuests[a.id].p:a.p,actor:a}));}
function separation(p,yaw,q){const dx=q[0]-p[0],dy=q[1]-p[1],c=Math.cos(yaw),n=Math.sin(yaw),u=dx*c+dy*n,v=-dx*n+dy*c;return Math.hypot(u-clamp(u,-.70,.72),v);}
function nearest(nodes,p){let best=0,d=Infinity;for(let i=0;i<nodes.length;i++){const x=D(nodes[i],p);if(x<d){d=x;best=i;}}return best;}
function route(data,start,end,blocked){const queue=[start],prev=new Map([[start,null]]);for(let i=0;i<queue.length;i++){const n=queue[i];if(n===end){const path=[];for(let k=n;k!==null;k=prev.get(k))path.unshift(k);return path;}for(const k of data.edges[n])if(!prev.has(k)&&(!blocked.has(k)||k===end)){prev.set(k,n);queue.push(k);}}return[];}
function beginWalk(s,data,m,f,goalMode){
 const ps=people(s),start=nearest(data.nodes,m.p),blocked=new Set(data.nodes.flatMap((p,i)=>ps.some(a=>D(p,a.p)<.87)?[i]:[]));blocked.delete(start);
 let neighbor=null;if(goalMode==='greet')neighbor=ps.filter(a=>D(m.p,a.p)<5&&!a.actor.interactionLock&&s.sceneEvent?.slots?.[a.id]===undefined&&!s.residentActions?.[a.id]?.requested&&!a.id.includes('vendor')).sort((a,b)=>(a.id.includes('child')?-.7:0)+D(m.p,a.p)-((b.id.includes('child')?-.7:0)+D(m.p,b.p)))[0];
 if(goalMode==='greet'&&!neighbor){f.phase='look';f.goalMode=goalMode;f.clock=0;f.duration=2.5;f.neighbor=null;f.path=[];return false;}
 const leaf=goalMode==='leaf'?s.craftWorld?.leaves.find(p=>!p.collected&&D(p.center,m.p)<3.5):null;
 const options=data.nodes.map((p,i)=>({p,i,d:D(p,m.p)})).filter(x=>!blocked.has(x.i)&&x.d>.75&&x.d<3.4&&(goalMode!=='shelter'||!rainingAt(s,x.p))&&(!neighbor||D(x.p,neighbor.p)>1.0&&D(x.p,neighbor.p)<1.9)).sort((a,b)=>neighbor?D(a.p,neighbor.p)-D(b.p,neighbor.p):leaf?Math.abs(D(a.p,leaf.center)-.85)-Math.abs(D(b.p,leaf.center)-.85):Math.abs(a.d-1.4)-Math.abs(b.d-1.4)||((a.i+f.cycle*17)%23)-((b.i+f.cycle*17)%23));
 for(const x of options){let path=route(data,start,x.i,blocked);if(!path.length)continue;f.path=path.filter((n,i)=>i===0||i===path.length-1||Math.abs(Math.atan2(data.nodes[n][1]-data.nodes[path[i-1]][1],data.nodes[n][0]-data.nodes[path[i-1]][0])-Math.atan2(data.nodes[path[i+1]][1]-data.nodes[n][1],data.nodes[path[i+1]][0]-data.nodes[n][0]))>.01);f.at=0;f.goalMode=goalMode;f.neighbor=neighbor?.id||null;f.phase='walk';f.clock=0;f.blocked=0;f.reacted=false;return true;}
 f.phase=goalMode==='greet'&&neighbor?'greet':'look';f.neighbor=neighbor?.id||null;f.clock=0;f.duration=goalMode==='greet'?6:3;return false;
}
export function suspendFox(s){const f=ensureFoxBehavior(s);f.suspended=true;f.velocity=0;}
export function advanceFox(s,data,dt,requestGesture=()=>{}){
 const m=s.movers?.[ID];if(!m||!data?.nodes?.length)return false;const f=ensureFoxBehavior(s),c=s.objectControls?.[ID],key=c?c.action+':'+c.started:null;
 if(f.suspended){f.suspended=false;if(f.command&&f.completedControl!==key)f.seenControl=null;f.path=[];f.phase='look';f.clock=0;f.duration=.6;}
 if(key!==f.seenControl){f.seenControl=key;f.completedControl=null;f.command=c?.action||null;f.path=[];f.velocity=0;f.reacted=false;f.clock=0;f.neighbor=null;
  if(c?.action==='play'){f.phase='bow';f.duration=2.2;}else if(c?.action==='greet')beginWalk(s,data,m,f,'greet');else if(c?.action==='stretch'){f.phase='stretch';f.duration=5.5;}else if(c?.action==='explore'){beginWalk(s,data,m,f,'explore');}else{f.phase=c?.action||'look';f.duration=3;}
 }
 const held=['sniff','look','rest'].includes(c?.action)?c.action:!c&&s.animals==='rest'?'rest':null;
 if(held){f.phase=held;f.path=[];f.velocity=0;f.clock+=dt;m.speed=0;m.strideWeight+=(0-m.strideWeight)*Math.min(1,dt*8);m.intent=held;return true;}
 if(!held&&(!c||f.completedControl===key)){const wet=rainingAt(s,m.p);if(wet&&!f.rainReacted){f.rainReacted=true;beginWalk(s,data,m,f,'shelter');}if(!wet)f.rainReacted=false;const leaf=s.craftWorld?.leaves.find(p=>!p.collected&&D(p.center,m.p)<3.5&&f.lastLeaf!==p.id);if(!wet&&leaf&&f.phase!=='walk'){f.lastLeaf=leaf.id;beginWalk(s,data,m,f,'leaf');}}
 f.clock+=dt;
 if(f.phase==='walk'){
  const n=f.path[f.at],p=data.nodes[n];if(!p){f.phase=f.goalMode==='greet'?'greet':f.goalMode==='play'?'play':'sniff';f.duration=f.phase==='greet'?6.5:f.phase==='play'?3.2:varied([3,5],ID,f.cycle);f.clock=0;f.velocity=0;f.path=[];return true;}
  const d=D(m.p,p);if(d<.045){f.at++;if(f.at>=f.path.length)f.path=[];return true;}
  const yaw=Math.atan2(p[1]-m.p[1],p[0]-m.p[0])+Math.PI,turn=Math.atan2(Math.sin(yaw-m.yaw),Math.cos(yaw-m.yaw));m.yaw+=clamp(turn,-dt*2.6,dt*2.6);
  const max=f.goalMode==='play'?.72:.48;f.velocity=Math.min(max,f.velocity+dt*.8);const step=Math.min(d,f.velocity*dt*Math.max(0,Math.cos(turn))),candidate=m.p.map((x,k)=>x+(p[k]-x)*step/(d||1));
  const obstruction=people(s).some(a=>Math.abs(a.p[2]-candidate[2])<1&&separation(candidate,m.yaw,a.p)<.54&&separation(candidate,m.yaw,a.p)<separation(m.p,m.yaw,a.p)-1e-6)||Object.entries(s.movers).some(([id,b])=>id!==ID&&id==='bicycle.street_bicycle'&&D(candidate,b.p)<1.25&&D(candidate,b.p)<D(m.p,b.p));
  if(obstruction){f.blocked+=dt;f.velocity=0;m.speed=0;m.intent='yield';m.strideWeight+=(0-m.strideWeight)*Math.min(1,dt*8);if(f.blocked>1.7){if(f.goalMode==='greet'&&f.neighbor&&D(m.p,people(s).find(a=>a.id===f.neighbor)?.p||m.p)<2.2){f.phase='greet';f.duration=6.5;f.clock=0;f.path=[];}else beginWalk(s,data,m,f,f.goalMode);}return true;}
  f.blocked=0;m.p=candidate;m.distance+=step;m.clock=(m.clock+step)%5;m.speed=f.velocity/.72;m.intent=f.goalMode==='play'?'trot':'explore';m.strideWeight+=(Math.min(1,step/dt/.35)-m.strideWeight)*Math.min(1,dt*8);return true;
 }
 m.speed=0;m.strideWeight+=(0-m.strideWeight)*Math.min(1,dt*8);m.intent=f.phase;
 if(f.phase==='greet'&&f.neighbor){const a=s.actors.find(a=>a.id===f.neighbor);if(a){const yaw=Math.atan2(a.p[1]-m.p[1],a.p[0]-m.p[0])+Math.PI;m.yaw+=clamp(Math.atan2(Math.sin(yaw-m.yaw),Math.cos(yaw-m.yaw)),-dt*2,dt*2);if(!f.reacted&&!c?.preserveOthers&&D(m.p,a.p)<2.4&&!a.interactionLock&&!s.residentActions[a.id]?.requested){requestGesture(a.id,'greet');if(a.mobile&&a.path.length){a.path=a.path.slice(0,a.segment+1);a.target=a.path.at(-1);}f.reacted=true;}}}
 if(f.clock>=f.duration){
  if(f.phase==='bow'){beginWalk(s,data,m,f,'play');return true;}
  if(f.command==='play'&&f.phase!=='play'){beginWalk(s,data,m,f,'play');return true;}if(f.command==='greet'&&(f.phase!=='greet'||!f.neighbor||D(m.p,people(s).find(a=>a.id===f.neighbor)?.p||[999,999])>2.4)){beginWalk(s,data,m,f,'greet');return true;}
  if(f.command&&['play','greet','stretch'].includes(f.command)&&f.completedControl!==f.seenControl){f.completedControl=f.seenControl;f.completed++;f.command=null;}
  f.cycle++;const autonomous=!c||['play','greet','stretch'].includes(c.action)&&f.completedControl===key;if(f.cycle%7===0&&autonomous){f.phase='bow';f.clock=0;f.duration=1.6;}else if(f.cycle%5===0&&autonomous){f.phase='stretch';f.clock=0;f.duration=5;}else beginWalk(s,data,m,f,'explore');
 }
 return true;
}
export function foxPose(s){const f=s.foxBehavior;if(!f||f.suspended)return{headPitch:0,headTurn:0,tail:0,front:0,back:0,lift:0};const t=f.clock,held=['look','sniff','rest'].includes(s.objectControls?.[ID]?.action)||s.animals==='rest',soft=Math.max(0,Math.min(1,t/.45,['walk'].includes(f.phase)||held?1:(f.duration-t)/.65));const active=['greet','play','bow'].includes(f.phase);return{headPitch:(f.phase==='sniff'?.30+.10*Math.sin(t*3):['stretch','bow'].includes(f.phase)?.32:active?-.10:-.03)*soft,headTurn:(f.phase==='look'?Math.sin(t*1.25)*.28:active?Math.sin(t*2.5)*.12:0)*soft,tail:(active?Math.sin(t*6)*.44:Math.sin(s.time*2)*.12)*soft,front:f.phase==='play'?Math.max(0,Math.sin(t*5))*.16*soft:['stretch','bow'].includes(f.phase)?.27*Math.sin(Math.PI*Math.min(1,t/f.duration)):0,back:f.phase==='play'?-Math.max(0,Math.sin(t*5))*.10*soft:['stretch','bow'].includes(f.phase)?-.10*Math.sin(Math.PI*Math.min(1,t/f.duration)):0,lift:f.phase==='play'?Math.max(0,Math.sin(t*5))*.065*soft:0};}
export function validateFox(s,data){if(!s.foxBehavior)return;const f=s.foxBehavior;if(!['walk','look','sniff','rest','stretch','greet','play','bow'].includes(f.phase)||![f.clock,f.duration,f.velocity,f.cycle,f.completed].every(Number.isFinite)||!Array.isArray(f.path)||f.path.some(i=>!Number.isInteger(i)||!data?.nodes[i])||f.command&&!modes.has(f.command))throw Error('Invalid fox behavior');}
export const FOX_PHASE_LABELS={walk:'沿花园空地走走',look:'抬头看看周围',sniff:'停下来认真闻一闻',rest:'安静歇一会',stretch:'伸展前爪，舒展身体',greet:'朝附近居民摇尾打招呼',play:'轻轻跳两下，摇摇尾巴',bow:'压低前身，邀请一起玩'};
