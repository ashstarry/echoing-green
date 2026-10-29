// Render between completed simulation states; never extrapolate beyond validated motion.
const mix=(a,b,t)=>a+(b-a)*t;
export const angleMix=(a,b,t)=>a+Math.atan2(Math.sin(b-a),Math.cos(b-a))*t;
const vec=(a,b,t)=>b.map((v,i)=>mix(a[i],v,t));
export function interpolateWorld(previous,current,alpha){
 if(!previous||previous.tick===current.tick)return current;
 const t=Math.max(0,Math.min(1,alpha));
 const p={...current,time:mix(previous.time,current.time,t),windPhase:mix(previous.windPhase,current.windPhase,t)};
 if(previous.eventWeather&&current.eventWeather)p.eventWeather=Object.fromEntries(Object.entries(current.eventWeather).map(([k,v])=>[k,mix(previous.eventWeather[k],v,t)]));
 p.actors=current.actors.map((b,i)=>{const a=previous.actors[i];return !a||a.id!==b.id?b:{...b,p:vec(a.p,b.p,t),yaw:angleMix(a.yaw,b.yaw,t),walked:mix(a.walked,b.walked,t),gaitWeight:mix(a.gaitWeight,b.gaitWeight,t),speed:mix(a.speed,b.speed,t)};});
 p.movers=Object.fromEntries(Object.entries(current.movers).map(([id,b])=>{const a=previous.movers[id];return[id,a?{...b,p:vec(a.p,b.p,t),yaw:angleMix(a.yaw,b.yaw,t),pitch:mix(a.pitch||0,b.pitch||0,t),bank:mix(a.bank||0,b.bank||0,t),distance:mix(a.distance,b.distance,t),footDown:mix(a.footDown||0,b.footDown||0,t),strideWeight:mix(a.strideWeight??1,b.strideWeight??1,t),speed:mix(a.speed,b.speed,t)}:b]}));
 if(current.train&&previous.train)p.train={...current.train,distance:mix(previous.train.distance,current.train.distance,t),speed:mix(previous.train.speed,current.train.speed,t),doorOpen:mix(previous.train.doorOpen||0,current.train.doorOpen||0,t)};
 p.diners=Object.fromEntries(Object.entries(current.diners).map(([id,b])=>{const a=previous.diners[id];if(!a)return[id,b];if(a.phase===b.phase)return[id,{...b,clock:mix(a.clock,b.clock,t)}];if(['exit','enter','turn'].includes(a.phase))return[id,{...a,clock:a.clock+(current.time-previous.time)*t}];return[id,b];}));
 if(current.residents&&previous.residents)p.residents=Object.fromEntries(Object.entries(current.residents).map(([id,b])=>{const a=previous.residents[id];return[id,a?{...b,lookYaw:angleMix(a.lookYaw||0,b.lookYaw||0,t),gesture:mix(a.gesture||0,b.gesture||0,t),umbrellaOpen:mix(a.umbrellaOpen||0,b.umbrellaOpen||0,t),gesturePhase:mix(a.gesturePhase||0,b.gesturePhase||0,t)}:b]}));
 if(current.residentActions&&previous.residentActions)p.residentActions=Object.fromEntries(Object.entries(current.residentActions).map(([id,b])=>{const a=previous.residentActions[id];return[id,a?{...b,clock:a.action===b.action?mix(a.clock,b.clock,t):b.clock,bookOpen:mix(a.bookOpen,b.bookOpen,t),umbrella:mix(a.umbrella,b.umbrella,t)}:b]}));
 if(current.localWalkers)p.localWalkers=Object.fromEntries(Object.entries(current.localWalkers).map(([id,b])=>{const a=previous.localWalkers?.[id];return[id,a?{...b,root:b.root.map((v,i)=>i===3?angleMix(a.root[i],v,t):mix(a.root[i],v,t)),legs:Object.fromEntries(['left','right'].map(side=>[side,b.legs[side].map((v,i)=>mix(a.legs[side][i],v,t))]))}:b]}));
 p.objectControls=Object.fromEntries(Object.entries(current.objectControls||{}).map(([id,b])=>{const a=previous.objectControls?.[id];return[id,a?{...b,value:mix(a.value,b.value,t),phase:mix(a.phase,b.phase,t)}:b]}));
 p.passengers=Object.fromEntries(Object.entries(current.passengers||{}).map(([id,b])=>{const a=previous.passengers?.[id];return[id,a?{...b,clock:a.phase===b.phase?mix(a.clock,b.clock,t):b.clock,door:mix(a.door,b.door,t),ramp:mix(a.ramp,b.ramp,t)}:b]}));
 if(current.eventGuests)p.eventGuests=Object.fromEntries(Object.entries(current.eventGuests).map(([id,b])=>{const a=previous.eventGuests?.[id];return[id,a?{...b,p:vec(a.p,b.p,t),yaw:angleMix(a.yaw,b.yaw,t),walked:mix(a.walked,b.walked,t),gaitWeight:mix(a.gaitWeight,b.gaitWeight,t),stand:mix(a.stand,b.stand,t),authorFeet:a.authorFeet&&b.authorFeet?Object.fromEntries(['left','right'].map(side=>[side,vec(a.authorFeet[side],b.authorFeet[side],t)])):b.authorFeet}:b]}));
 p.music=current.effectiveMusic??current.music;return p;
}
