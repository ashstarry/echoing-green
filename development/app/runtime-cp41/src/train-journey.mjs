import {requestPassengerAction} from './passengers.mjs';
const traveler='resident.station_traveler';
export function ensureJourney(s){return s.trainJourney??={mode:'rest',phase:'idle',started:0,phaseAt:0,baselineTrips:0,sequence:0,flags:{}};}
export function requestJourney(s,mode,emit=()=>{}){const j=ensureJourney(s),p=s.passengers[traveler];if(!p)return;
 if(mode==='rest'){j.deferredDeparture=false;const rev=s.revision;requestPassengerAction(s,traveler,'stay');s.revision=rev;j.mode='rest';j.phase=p.phase==='waiting'?'idle':'finishing';j.phaseAt=s.time;emit('这趟行程先收住，已经上车的人会到站后再下来。');return;}
 const sequence=j.sequence+1;Object.assign(j,{mode,phase:'waiting',started:s.time,phaseAt:s.time,baselineTrips:p.completedTrips-(mode==='welcome'&&p.phase==='close_exit'?1:0),sequence,flags:{},deferredDeparture:mode==='depart'&&['prepare_exit','alight','close_exit'].includes(p.phase)});
 const rev=s.revision;if(p.phase==='waiting')requestPassengerAction(s,traveler,'ride_once');else if(mode==='welcome')requestPassengerAction(s,traveler,'alight');else if(!j.deferredDeparture){p.mode='once';p.requested=true;}s.revision=rev;
 s.trainPolicy='auto';s.train.hold=false;if(s.sceneEvent){s.sceneEvent.protectedIds??=[];if(!s.sceneEvent.protectedIds.includes(traveler))s.sceneEvent.protectedIds.push(traveler);delete s.sceneEvent.slots[traveler];}if(s.eventGuests?.[traveler]?.active)s.eventGuests[traveler].returnRequested=true;
 emit(mode==='welcome'?'车站留意归来的电车，准备迎接这位旅客。':'旅客准备乘电车绕镇一程，站边的邻居来送行。');
}
export function advanceJourney(s,dt,gesture,emit=()=>{}){const j=ensureJourney(s),p=s.passengers?.[traveler],tr=s.train;if(!p||['idle','done'].includes(j.phase))return;
 const once=(key,fn)=>{if(j.flags[key])return;j.flags[key]=true;fn();};const phase=value=>{if(j.phase!==value){j.phase=value;j.phaseAt=s.time;}};
 if(j.deferredDeparture){if(p.phase==='waiting'){const rev=s.revision;j.baselineTrips=p.completedTrips;j.deferredDeparture=false;j.flags={};requestPassengerAction(s,traveler,'ride_once');s.revision=rev;phase('waiting');}else{return;}}
 if(j.phase==='finishing'){if(p.phase==='waiting')phase('idle');return;}
 if(p.phase==='waiting'&&p.completedTrips<=j.baselineTrips){once('notice',()=>{gesture(traveler,'check_time');gesture('resident.station_attendant','signal_train');});if(s.eventGuests?.[traveler]?.active)s.eventGuests[traveler].returnRequested=true;}
 if(['prepare_board','board'].includes(p.phase)){phase('boarding');once('sendoff',()=>{gesture('resident.waiting_passenger','greet');gesture('resident.waiting_passenger_2','greet');emit('邻居抬手送行，旅客等踏板放稳，再一步步上车。');});}
 if(p.phase==='riding'){phase('onboard');once('aboard',()=>emit('旅客在车窗边挥挥手，电车载着他绕过小镇。'));}
 if(['prepare_exit','alight','close_exit'].includes(p.phase)){phase('returning');once('welcome',()=>{gesture('resident.station_attendant','greet');gesture('resident.waiting_passenger','greet');gesture('resident.waiting_passenger_2','greet');emit('电车回到站台，熟悉的邻居正等着招手。');});}
 if(p.phase==='waiting'&&p.completedTrips>j.baselineTrips){if(j.phase!=='greeting')phase('greeting');once('returned',()=>gesture(traveler,'greet'));if(s.time-j.phaseAt>6){phase('done');j.completedAt=s.time;emit('这一程结束，旅客回到站台，和邻居打过招呼。');}}
}
export function validateJourney(s){const j=ensureJourney(s);if(!['rest','depart','welcome'].includes(j.mode)||!['idle','waiting','boarding','onboard','returning','greeting','finishing','done'].includes(j.phase)||![j.started,j.phaseAt,j.baselineTrips,j.sequence].every(Number.isFinite)||!j.flags||typeof j.flags!=='object')throw Error('Invalid train journey');}
export const JOURNEY_PHASE_LABELS={waiting:'旅客先等电车进站',boarding:'邻居送行，旅客正在上车',onboard:'旅客在车窗边挥手，绕镇看看',returning:'电车回站，旅客准备下来',greeting:'回到站台，和邻居打招呼',finishing:'先完成当前这段安全上下车',done:'这一程已经完成',idle:'暂时没有新的旅程'};
