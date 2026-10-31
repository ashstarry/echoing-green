import {needsClearPromenade} from './event-design.mjs?v=cp37-paper-c8fccf30daca';
import {makeRoom} from './event-travel.mjs?v=cp37-paper-c8fccf30daca';
import {CADENCE,varied} from './cadence.mjs?v=cp37-paper-c8fccf30daca';
export const TAU=Math.PI*2;
export const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
export const ease=x=>{x=clamp(x,0,1);return x*x*(3-2*x)};
export function legPose(distance,scale,side,weight,groundOffset=0){
 const phase=((distance/(.56*scale)*TAU+(side==='right'?Math.PI:0))%TAU+TAU)%TAU;
 const swing=phase>=Math.PI,u=swing?(phase-Math.PI)/Math.PI:phase/Math.PI;
 const footY=(swing?.14-.28*ease(u):-.14+.28*u)*weight;
 const drop=.026*weight,lift=(swing?Math.sin(Math.PI*u)*.105:0)*weight;
 const dy=footY,dz=.11+drop+lift+groundOffset-.49,L1=.20,L2=.18,d2=dy*dy+dz*dz;
 const knee=Math.acos(clamp((d2-L1*L1-L2*L2)/(2*L1*L2),-1,1));
 const hip=Math.atan2(dy,-dz)-Math.atan2(L2*Math.sin(knee),L1+L2*Math.cos(knee));
 return {hip,knee,ankle:-hip-knee,drop,phase,lift,footY};
}
export function sampleRail(path,distance){
 const d=((distance%path.length)+path.length)%path.length,ls=path.lengths,ps=path.points;let lo=0,hi=ps.length-1;while(lo<hi){const m=(lo+hi)>>1;if(ls[m+1]<d)lo=m+1;else hi=m;}const i=lo,j=(i+1)%ps.length,u=(d-ls[i])/(ls[i+1]-ls[i]);return ps[i].map((v,k)=>v+(ps[j][k]-v)*u);
}
export function railPose(path,d){const p=sampleRail(path,d),a=sampleRail(path,d-1.166),b=sampleRail(path,d+1.166);return {p:[p[0],p[1],p[2]+path.root_height_above_rail],yaw:Math.atan2(b[1]-a[1],b[0]-a[0])};}
export function stationDistance(path){let best=0,score=Infinity;for(let i=0;i<path.points.length;i++){const p=path.points[i],d=(p[0]+.6)**2+(p[1]+6.9)**2;if(d<score){score=d;best=i;}}return path.lengths[best];}
export function createTrain(path){if(!path)return null;const stop=stationDistance(path);return {distance:stop-4.3,nextStop:stop,speed:.5,mode:'cruise',remaining:0,arrivals:0,departures:0,laps:0,hold:false,doorOpen:0,dwellDuration:16,arrivedAt:-1};}
export function stepTrain(s,path,dt,emit){const tr=s.train;if(!tr||!path)return;
 if(tr.mode==='dwell'){tr.speed=0;tr.doorOpen+=clamp((tr.hold||tr.passengerHold||tr.remaining>2?1:0)-tr.doorOpen,-dt*.75,dt*.75);tr.remaining=Math.max(0,tr.remaining-dt);if(tr.remaining===0&&!tr.hold&&!tr.passengerHold){tr.mode='depart';tr.nextStop+=path.length;tr.departures++;emit('电车关上车门，继续绕镇行驶。');}return;}
 tr.doorOpen=Math.max(0,tr.doorOpen-dt*.75);
 const left=Math.max(0,tr.nextStop-tr.distance),target=Math.min(.62,Math.max(0,Math.sqrt(2*.20*left)-.20*dt));tr.speed+=clamp(target-tr.speed,-.26*dt,.18*dt);const move=Math.min(left,tr.speed*dt);tr.distance+=move;
 if(left<2.1&&tr.mode!=='arrive'){tr.mode='arrive';emit('电车正在减速进站。');}
 if(left<=.0004||move>=left){tr.distance=tr.nextStop;tr.speed=0;tr.mode='dwell';tr.dwellDuration=varied(CADENCE.trainDwell,'train',tr.arrivals);tr.remaining=tr.dwellDuration;tr.arrivedAt=s.time;tr.arrivals++;emit('电车到站，停下来等候。');}else if(tr.mode==='depart'&&tr.speed>.32)tr.mode='cruise';
 tr.laps=Math.floor(Math.max(0,tr.distance-stationDistance(path))/path.length);
}
export function sampleClip(clip,clock){const n=clip.samples.length-1,at=clamp(clock/clip.duration*n,0,n),i=Math.floor(at),j=Math.min(n,i+1),u=at-i,a=clip.samples[i],b=clip.samples[j],da=Math.atan2(Math.sin(b[3]-a[3]),Math.cos(b[3]-a[3]));return {p:a.slice(0,3).map((v,k)=>v+(b[k]-v)*u),yaw:a[3]+da*u,pitch:(a[4]||0)+((b[4]||0)-(a[4]||0))*u,bank:(a[5]||0)+((b[5]||0)-(a[5]||0))*u};}
export function createMovers(activities){return Object.fromEntries(Object.entries(activities?.clips||{}).map(([id,c])=>[id,{clock:0,distance:0,footDown:0,stopWait:0,stopIndex:0,completedStops:0,tripState:'ride',blocked:false,wait:0,speed:1,strideWeight:1,clearTime:0,restUntil:0,nextPause:varied([3,7],id),pauses:0,intent:c.motion==='creature_walk'?'explore':c.motion,...sampleClip(c,0)}]));}
export function advanceMovers(s,activities,dt,nav=null){for(const[id,m]of Object.entries(s.movers||{})){
 const clip=activities.clips[id];if(id==='animal.garden_fox'&&advanceEventFox(s,m,clip,dt))continue;const ground=['creature_walk','ride'].includes(clip.motion),policy=clip.motion==='fly'?s.birds:clip.motion==='ride'?s.cycling:clip.motion==='swim'?s.pond:s.animals;
 if(clip.motion==='creature_walk'&&s.time>=m.nextPause&&s.time>=m.restUntil){m.pauses++;m.restUntil=s.time+varied([2.5,6],id,m.pauses);m.nextPause=m.restUntil+varied([3,7],id,m.pauses);}
 const eventRest=clip.motion==='creature_walk'&&needsClearPromenade(s.sceneEvent?.kind);
 const wantsRest=eventRest||policy==='rest'||s.time<m.restUntil||(clip.motion==='ride'&&(s.weather==='rain'||s.worldEvent?.kind==='festival'));
 if(clip.motion==='ride'&&advanceCycle(s,id,m,clip,dt,nav))continue;
 const radius=clip.radius||.5,look=sampleClip(clip,(m.clock+.65*Math.max(.25,m.speed))%clip.duration);
 const nearActor=(p,extra=0)=>Object.values(s.eventGuests||{}).some(g=>g.active&&Math.hypot(g.p[0]-p[0],g.p[1]-p[1])<radius+.5+extra)||s.actors.some(a=>(!a.eventOnly||a.mobile||s.eventGuests?.[a.id]?.active)&&Math.hypot(a.p[0]-p[0],a.p[1]-p[1])<(a.mobile?(clip.dynamic_clearance||radius):radius)+.47+extra);
 const aheadBlocked=ground&&nearActor(look.p,.10);m.clearTime=aheadBlocked?0:m.clearTime+dt;
 const feeding=s.pondFeeding&&s.time>=s.pondFeeding.started&&s.time<s.pondFeeding.until&&['fish.','animal.duck_'].some(prefix=>id.startsWith(prefix))&&Math.hypot(m.p[0]-s.pondFeeding.target[0],m.p[1]-s.pondFeeding.target[1])<.78;m.feeding=!!feeding;
 const override=s.objectControls?.[id];const desired=wantsRest&& !override||aheadBlocked||(m.blocked&&m.clearTime<.7)?0:override?override.value:feeding?.12:1;m.speed=clamp(m.speed+clamp(desired-m.speed,-.9*dt,.55*dt),0,1);
 const clock=(m.clock+dt*m.speed)%clip.duration,candidate=sampleClip(clip,clock);const blocked=ground&&(nearActor(candidate.p)||Object.entries(s.movers).some(([other,b])=>other!==id&&['creature_walk','ride'].includes(activities.clips[other].motion)&&Math.hypot(candidate.p[0]-b.p[0],candidate.p[1]-b.p[1])<radius+(activities.clips[other].radius||.5)+.04));
 m.strideWeight+=((blocked?0:Math.min(1,m.speed/.55))-m.strideWeight)*Math.min(1,dt*7);m.blocked=blocked||aheadBlocked;m.wait=m.blocked?m.wait+dt:0;m.intent=feeding?'nibble':blocked||aheadBlocked?'yield':wantsRest?(clip.motion==='creature_walk'?'sniff':'rest'):clip.motion;
 if(!blocked){m.distance+=Math.hypot(m.p[0]-candidate.p[0],m.p[1]-candidate.p[1]);m.clock=clock;Object.assign(m,candidate);}else m.speed=Math.max(0,m.speed-.9*dt);
}}
export function createDiners(config){return Object.fromEntries(Object.keys(config||{}).map((id,i)=>[id,{phase:'dine',clock:0,wait:varied([25,55],id),policy:'auto',effectivePolicy:'auto',cycles:0}]));}
export function advanceDiners(s,config,dt,emit){for(const[id,d]of Object.entries(s.diners||{})){const c=config[id];if(d.phase==='dine'&&s.residentActions?.[id]?.action){d.wait=Math.max(0,d.wait-dt);continue;}if(d.phase==='dine'||d.phase==='inside'){d.wait=Math.max(0,d.wait-dt);if(d.wait===0&&((d.phase==='dine'&&d.policy!=='dine')||(d.phase==='inside'&&d.policy!=='inside'))){d.phase=d.phase==='dine'?'exit':'turn';d.clock=0;emit(d.phase==='exit'?'二楼的客人推开椅子，走进门帘。':'二楼的客人准备回来用餐。');}}else{d.clock=Math.min(c.clips[d.phase].duration,d.clock+dt);if(d.clock>=c.clips[d.phase].duration){if(d.phase==='exit'){d.phase='inside';d.clock=0;d.wait=varied(d.policy==='dine'?CADENCE.reaction:CADENCE.inside,id,d.cycles);}else if(d.phase==='turn'){d.phase='enter';d.clock=0;}else{d.phase='dine';d.clock=0;d.wait=varied(d.policy==='inside'?CADENCE.reaction:CADENCE.meal,id,d.cycles);d.cycles++;emit('客人回到自己的座位，继续用餐。');}}}}}

export function moverBlocks(p,m,clip,actorRadius=.43){if(clip.motion==='ride'){const dx=p[0]-m.p[0],dy=p[1]-m.p[1],c=Math.cos(m.yaw),n=Math.sin(m.yaw),u=dx*c+dy*n,v=-dx*n+dy*c;return Math.hypot(u-clamp(u,-.75,.75),v)<actorRadius+(m.footDown>.1&&actorRadius>.35?.52:.29)+.025;}return Math.hypot(p[0]-m.p[0],p[1]-m.p[1])<actorRadius+(clip.dynamic_clearance||clip.radius||.5)+.02;}
function advanceCycle(s,id,m,clip,dt,nav){
 const eventParking=needsClearPromenade(s.sceneEvent?.kind)||Object.values(s.eventGuests||{}).some(g=>g.active);
 const held=s.cycling==='rest'||s.weather==='rain'||eventParking&&m.stopIndex===0;m.stopIndex??=0;m.stopWait??=0;m.footDown??=0;m.completedStops??=0;const stops=clip.stops||[];
 if(!stops.length)return false;
 if(m.stopWait>0||m.tripState==='parked'){
  if(eventParking&&m.stopIndex===1)m.stopWait=Math.min(m.stopWait,1.2);m.stopWait=Math.max(0,m.stopWait-dt);m.speed=0;m.intent=stops[(m.stopIndex+stops.length-1)%stops.length].label;m.tripState='parked';m.footDown+=Math.min(1,dt*3)*(1-m.footDown);
  if(m.stopWait<=0&&(!held||eventParking&&m.stopIndex===1)){m.tripState='depart';m.intent='准备去下一处';}return true;
 }
 if(m.tripState==='depart'){m.footDown=Math.max(0,m.footDown-dt*1.5);if(m.footDown>.01)return true;m.tripState='ride';}
 const target=stops[m.stopIndex].clock,left=(target-m.clock+clip.duration)%clip.duration;
 const look=sampleClip(clip,(m.clock+.6*Math.max(.25,m.speed))%clip.duration),ahead=Object.values(s.eventGuests||{}).some(g=>g.active&&moverBlocks(g.p,{...m,...look},clip))||s.actors.some(a=>(!a.eventOnly||a.mobile||s.eventGuests?.[a.id]?.active)&&moverBlocks(a.p,{...m,...look},clip));
 const desired=ahead?0:Math.min(1,Math.sqrt(Math.max(0,left))*.85);m.speed=clamp(m.speed+clamp(desired-m.speed,-dt*1.3,dt*.55),0,1);
 const move=Math.min(left,dt*m.speed),clock=(m.clock+move)%clip.duration,candidate=sampleClip(clip,clock),blocked=Object.values(s.eventGuests||{}).some(g=>g.active&&moverBlocks(g.p,{...m,...candidate},clip))||s.actors.some(a=>(!a.eventOnly||a.mobile||s.eventGuests?.[a.id]?.active)&&moverBlocks(a.p,{...m,...candidate},clip));m.blocked=blocked||ahead;m.wait=m.blocked?(m.wait||0)+dt:0;if(m.wait>.7&&nav)makeRoom(s,nav,{id:'resident.cyclist',p:m.p},look.p);m.intent=m.blocked?'让行人先走':m.stopIndex===0?'去车站旁看看':'去池塘边歇脚';
 if(!blocked){m.distance+=Math.hypot(m.p[0]-candidate.p[0],m.p[1]-candidate.p[1]);m.clock=clock;Object.assign(m,candidate);}else m.speed=Math.max(0,m.speed-dt*1.3);
 if(s.cycling==='rest'&&!eventParking&&m.blocked&&m.wait>2){m.tripState='parked';m.stopWait=0;m.speed=0;return true;}
 if(left<.004||move>=left-.00001){m.clock=target;Object.assign(m,sampleClip(clip,target));m.stopIndex=(m.stopIndex+1)%stops.length;m.stopWait=varied([11,19],id,m.completedStops++);m.tripState='parked';m.speed=0;}
 return true;
}

function advanceEventFox(s,m,clip,dt){
 const active=needsClearPromenade(s.sceneEvent?.kind)&&['gather','active','closing'].includes(s.sceneEvent.phase);
 if(s.objectControls?.['animal.garden_fox']?.target===0){m.speed=0;m.strideWeight+=(0-m.strideWeight)*Math.min(1,dt*8);m.intent='rest';return true;}
 if(active&&!m.eventHome)m.eventHome={p:m.p.slice(),yaw:m.yaw};
 if(!m.eventHome)return false;const target=active?[5.15,1.7,.624]:m.eventHome.p,dx=target[0]-m.p[0],dy=target[1]-m.p[1],d=Math.hypot(dx,dy),move=Math.min(d,.72*dt),candidate=m.p.map((x,k)=>x+(target[k]-x)*move/(d||1));if(s.actors.some(a=>Math.abs(a.p[2]-candidate[2])<1&&Math.hypot(a.p[0]-candidate[0],a.p[1]-candidate[1])<.78&&Math.hypot(a.p[0]-candidate[0],a.p[1]-candidate[1])<Math.hypot(a.p[0]-m.p[0],a.p[1]-m.p[1])-1e-6)){m.speed=0;m.strideWeight+=(0-m.strideWeight)*Math.min(1,dt*8);m.intent='yield';return true;}m.speed=d>.05?1:0;m.strideWeight+=(Number(d>.05)-m.strideWeight)*Math.min(1,dt*8);m.intent=active?'head_for_garden':'return_to_garden';if(d>.005){m.p=m.p.map((x,k)=>x+(target[k]-x)*move/d);m.distance+=move;const yaw=Math.atan2(dy,dx);m.yaw+=clamp(Math.atan2(Math.sin(yaw-m.yaw),Math.cos(yaw-m.yaw)),-dt*3,dt*3);}else if(!active){m.p=m.eventHome.p;m.yaw=m.eventHome.yaw;delete m.eventHome;}return true;
}
