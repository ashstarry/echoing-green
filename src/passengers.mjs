import {ease,legPose,railPose,stationDistance} from './motion.mjs?v=cp30-life-e7bb14ab832f';
const mix=(a,b,t)=>a+(b-a)*t;const angle=(a,b,t)=>a+Math.atan2(Math.sin(b-a),Math.cos(b-a))*t;const lerp=(a,b,t)=>a.map((x,i)=>mix(x,b[i],t));
export function createPassengers(config){if(!config)return{};return{[config.actor]:{phase:'waiting',mode:'auto',clock:0,door:0,ramp:0,vehicle:null,exitArrival:0,nextTripAt:15,completedTrips:0,requested:false}};}
export function requestPassengerAction(s,id,action){const p=s.passengers?.[id];if(!p)throw Error('这个乘车流程还未开放');if(action==='ride_once'){if(p.phase!=='waiting')throw Error('旅客已经在这趟行程中');p.mode='once';p.requested=true;p.nextTripAt=s.time;const hands=s.residentActions[id];if(hands?.action)hands.cancelRemaining=.65;}else if(action==='stay'){p.mode='stay';p.requested=false;if(p.phase==='prepare_board')p.phase='close_exit';else if(p.phase==='board'||p.phase==='secure')p.cancelTrip=true;else if(p.phase==='riding')p.exitArrival=s.train.arrivals+(s.train.mode==='dwell'?0:1);}else if(action==='alight'){if(p.phase==='waiting')throw Error('旅客已经在站台上');if(p.phase==='prepare_board'){p.phase='close_exit';p.mode='stay';return;}if(p.phase==='board'||p.phase==='secure')p.cancelTrip=true;p.mode='once';p.exitArrival=s.train.arrivals+(s.train.mode==='dwell'?0:1);}else throw Error('未开放的乘车动作');s.revision++;}
export function advancePassengers(s,activities,dt){const config=activities?.boarding;if(!config)return;const p=s.passengers[config.actor],tr=s.train;tr.passengerHold=false;
 const waitingForHands=!!s.residentActions[config.actor]?.action;
 if(p.phase==='waiting'&&p.mode!=='stay'&&s.time>=p.nextTripAt&&tr.mode==='dwell'){p.phase='prepare_board';p.clock=0;}
 const open=['prepare_board','board','prepare_exit','alight'].includes(p.phase);p.door+=Math.max(-dt*1.5,Math.min(dt*1.5,Number(open)-p.door));p.ramp+=Math.max(-dt*.8,Math.min(dt*.8,Number(open&&p.door>.98)-p.ramp));
 if(['prepare_board','board','secure','prepare_exit','alight','close_exit'].includes(p.phase))tr.passengerHold=true;
 if(p.phase==='prepare_board'&&p.door>.99&&p.ramp>.99&&!waitingForHands){p.phase='board';p.clock=0;p.vehicle=config.vehicle;}
 else if(p.phase==='board'){p.clock+=dt;if(p.clock>=config.boardDuration){p.phase='secure';p.clock=0;p.exitArrival=p.cancelTrip?tr.arrivals:tr.arrivals+1;p.cancelTrip=false;}}
 else if(p.phase==='secure'&&p.door<.01&&p.ramp<.01){p.phase='riding';p.clock=0;}
 else if(p.phase==='riding'&&tr.mode==='dwell'&&tr.arrivals>=p.exitArrival){p.phase='prepare_exit';p.clock=0;tr.passengerHold=true;}
 else if(p.phase==='prepare_exit'&&p.door>.99&&p.ramp>.99){p.phase='alight';p.clock=0;}
 else if(p.phase==='alight'){p.clock+=dt;if(p.clock>=config.exitDuration){p.phase='close_exit';p.clock=0;p.vehicle=null;p.completedTrips++;p.requested=false;p.nextTripAt=s.time+80+(p.completedTrips%3)*19;if(p.mode==='once')p.mode='stay';}}
 else if(p.phase==='close_exit'&&p.door<.01&&p.ramp<.01){p.phase='waiting';p.clock=0;}
}
export function validatePassengers(s,config){if(!config){if(Object.keys(s.passengers||{}).length)throw Error('未开放的乘车存档');return;}const p=s.passengers?.[config.actor];if(!p||!['waiting','prepare_board','board','secure','riding','prepare_exit','alight','close_exit'].includes(p.phase)||!['auto','once','stay'].includes(p.mode)||!['clock','door','ramp','exitArrival','nextTripAt','completedTrips'].every(k=>Number.isFinite(p[k])))throw Error('乘车存档无效');}
export function passengerPose(s,activities){const c=activities.boarding,p=s.passengers[c.actor],S=c.scale,car=railPose(activities.rail,s.train.distance),cs=Math.cos(car.yaw),sn=Math.sin(car.yaw),sx=c.carScale[0],sy=c.carScale[1];
 const cp=a=>[car.p[0]+cs*a[0]*sx-sn*a[1]*sy,car.p[1]+sn*a[0]*sx+cs*a[1]*sy,car.p[2]+a[2]];
 const local=a=>{const x=a[0]-car.p[0],y=a[1]-car.p[1];return[(cs*x+sn*y)/sx,(-sn*x+cs*y)/sy]};
 const floor=a=>{const[x,y]=local(a);if(x>=-1.25&&x<=1.25&&y>=-.42&&y<=.42)return car.p[2]+.13;if(x>-.90&&x<-.22&&y>.42&&y<.98){const u=Math.max(0,Math.min(1,(y-.42)/.53));return mix(car.p[2]+.13,c.platformFloor+.026,u);}return c.platformFloor;};
 const dock=cp([-.56,1.16,0]);dock[2]=c.platformFloor;const aisle=cp([-.56,.03,.13]),corner=cp([-.20,.03,.13]),seatFront=cp([.48,.03,.13]),seat=cp([.48,-.195,.13]),home=c.home.slice(),pathHeading=Math.atan2(dock[1]-home[1],dock[0]-home[0])+Math.PI/2;
 const turnHome=[home[0]+Math.sin(c.homeYaw)*.12,home[1]-Math.cos(c.homeYaw)*.12,home[2]],returnHeading=Math.atan2(turnHome[1]-dock[1],turnHome[0]-dock[0])+Math.PI/2;
 const boardHeading=Math.atan2(dock[1]-turnHome[1],dock[0]-turnHome[0])+Math.PI/2;
 let ground=home.slice(),yaw=c.homeYaw,crouch=0,walk=0,walked=0,seatBlend=0,feetLocked=false,sideStep=0;const t=p.clock;
 const travel=(a,b,start,duration,heading,low=1,side=0)=>{const raw=(t-start)/duration,u=ease(raw);ground=lerp(a,b,u);yaw=heading;crouch=low;walk=ease(raw/.12)*ease((1-raw)/.12);walked=Math.hypot(b[0]-a[0],b[1]-a[1])*u;sideStep=side;};
 if(['secure','riding','prepare_exit'].includes(p.phase)){ground=seat;ground[2]=car.p[2]+.13;yaw=car.yaw+Math.PI;crouch=1;seatBlend=1;feetLocked=true;}
 if(p.phase==='board'){
  if(t<.6){travel(home,turnHome,0,.6,c.homeYaw,0);walk*=.35;crouch=.5*ease(t/.6);}
  else if(t<1.2){ground=turnHome;crouch=.5;yaw=angle(c.homeYaw,boardHeading,ease((t-.6)/.6));}
  else if(t<3.7)travel(turnHome,dock,1.2,2.5,boardHeading,.5);
  else if(t<4.9){ground=dock;yaw=angle(boardHeading,car.yaw,ease((t-3.7)/1.2));crouch=.5;}
  else if(t<8.4)travel(dock,aisle,4.9,3.5,car.yaw);
  else if(t<9.5){ground=aisle;yaw=angle(car.yaw,car.yaw+Math.PI/2,ease((t-8.4)/1.1));crouch=1;}
  else if(t<10.9)travel(aisle,corner,9.5,1.4,car.yaw+Math.PI/2);
  else if(t<12){ground=corner;yaw=angle(car.yaw+Math.PI/2,car.yaw+Math.PI,ease((t-10.9)/1.1));crouch=1;}
  else if(t<15.6)travel(corner,seatFront,12,3.6,car.yaw+Math.PI,1,1);
  else{const u=ease((t-15.6)/2.2);ground=lerp(seatFront,seat,u);yaw=car.yaw+Math.PI;crouch=1;seatBlend=u;feetLocked=true;}
 }
 if(p.phase==='alight'){
  if(t<2.2){const u=ease(t/2.2);ground=lerp(seat,seatFront,u);yaw=car.yaw+Math.PI;crouch=1;seatBlend=1-u;feetLocked=true;}
  else if(t<5.8)travel(seatFront,corner,2.2,3.6,car.yaw+Math.PI,1,-1);
  else if(t<6.9){ground=corner;yaw=angle(car.yaw+Math.PI,car.yaw-Math.PI/2,ease((t-5.8)/1.1));crouch=1;}
  else if(t<8.3)travel(corner,aisle,6.9,1.4,car.yaw-Math.PI/2);
  else if(t<9.4){ground=aisle;yaw=angle(car.yaw-Math.PI/2,car.yaw+Math.PI,ease((t-8.3)/1.1));crouch=1;}
  else if(t<12.9)travel(aisle,dock,9.4,3.5,car.yaw+Math.PI);
  else if(t<14.1){ground=dock;yaw=angle(car.yaw+Math.PI,returnHeading,ease((t-12.9)/1.2));crouch=.5;}
  else if(t<16.6){travel(dock,turnHome,14.1,2.5,returnHeading);crouch=.5;}
  else if(t<17.8){ground=turnHome;yaw=angle(returnHeading,c.homeYaw,ease((t-16.6)/1.2));crouch=.5*(1-ease((t-16.6)/1.2));}
  else if(t<18.8){travel(turnHome,home,17.8,1,c.homeYaw,0);walk*=.35;walked*=-1;}
  else{ground=home;yaw=c.homeYaw;}
 }
 const onTrip=['board','secure','riding','prepare_exit','alight'].includes(p.phase);if(!onTrip)return{root:[...home,c.homeYaw],legs:null,arms:0,torso:0};
 ground[2]=floor(ground);if(p.phase==='board'&&t>=4.9&&t<8.4||p.phase==='alight'&&t>=9.4&&t<12.9)crouch=Math.max(.5,Math.min(1,(ground[2]-(car.p[2]+.13-.30))/.30));const drop=.30*crouch,root=[ground[0],ground[1],ground[2]-.02*S+.006-drop,yaw];
 if(feetLocked)root[2]=mix(car.p[2]+.13-.02*S+.006-.30,car.p[2]+.13-.31,seatBlend);
 const legs={};for(const side of ['left','right']){const sign=side==='left'?-1:1,base=legPose(walked,S,side,walk),bias=(.045+.105*(sideStep?0:walk))*crouch,lateral=sideStep?base.footY*sideStep:0,fc=[(sign*.10+lateral)*S,(-.01+(sideStep?0:base.footY)-bias)*S],wx=root[0]+Math.cos(yaw)*fc[0]-Math.sin(yaw)*fc[1],wy=root[1]+Math.sin(yaw)*fc[0]+Math.cos(yaw)*fc[1];let footY=(sideStep?0:base.footY)-bias,pitch=0,ankleZ;
  if(feetLocked){const anchor=cp([.48,.087,.13]),dx=anchor[0]-root[0],dy=anchor[1]-root[1];footY=(-Math.sin(yaw)*dx+Math.cos(yaw)*dy)/S+.01;ankleZ=car.p[2]+.13+.09*S+.006;}
  else{const probe=.025,a=[wx-Math.sin(yaw)*probe,wy+Math.cos(yaw)*probe],b=[wx+Math.sin(yaw)*probe,wy-Math.cos(yaw)*probe];pitch=Math.max(-.38,Math.min(.38,Math.atan((floor(a)-floor(b))/(2*probe))));ankleZ=-Infinity;for(const xx of [-.07,0,.07])for(const yy of [-.19,-.15,-.11,-.07,-.03,.01,.06]){const ly=yy*S*Math.cos(pitch)+.09*S*Math.sin(pitch),lz=yy*S*Math.sin(pitch)-.09*S*Math.cos(pitch),point=[wx+Math.cos(yaw)*xx*S-Math.sin(yaw)*ly,wy+Math.sin(yaw)*xx*S+Math.cos(yaw)*ly];ankleZ=Math.max(ankleZ,floor(point)-lz+.006);}ankleZ+=base.lift*S;}
  const dy=footY,dz=(ankleZ-root[2])/S-.49,roll=Math.atan2(lateral,Math.abs(dz))*Math.sign(dz||1),zz=Math.sign(dz||1)*Math.hypot(lateral,dz),knee=Math.acos(Math.max(-1,Math.min(1,(dy*dy+zz*zz-.20*.20-.18*.18)/(2*.20*.18)))),hip=Math.atan2(dy,-zz)-Math.atan2(.18*Math.sin(knee),.20+.18*Math.cos(knee));legs[side]=[hip,knee,-hip-knee+pitch,roll];
 }
 const fold=p.phase==='board'?ease(t/.5):p.phase==='alight'?ease((c.exitDuration-t)/.6):1;return{root,legs,arms:fold,torso:0};
}
