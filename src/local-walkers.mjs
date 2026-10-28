const lerp=(a,b,t)=>a+(b-a)*t;const angle=(a,b,t)=>a+Math.atan2(Math.sin(b-a),Math.cos(b-a))*t;
const standing=root=>({root:root.slice(),legs:{left:[0,0,0,0],right:[0,0,0,0]}});
export function createLocalWalkers(routes){return Object.fromEntries(Object.entries(routes||{}).map(([id,r])=>[id,{anchor:r.initial,goal:r.initial,clip:null,clock:0,completed:0,waiting:false,...standing(r.anchors[r.initial].root)}]));}
export function requestLocalDestination(s,id,goal,routes){const r=routes[id],w=s.localWalkers[id];if(!w||!r.anchors[goal])throw Error('这个目的地尚未开放');w.goal=goal;w.waiting=false;}
function nextHop(config,from,to){if(from===to)return null;if(config.clips[from+'_'+to])return from+'_'+to;return config.clips[from+'_landing']?from+'_landing':null;}
export function advanceLocalWalkers(s,routes,dt){for(const[id,w]of Object.entries(s.localWalkers||{})){const config=routes[id];if(!config)continue;
 if(!w.clip){if(w.anchor===w.goal){w.waiting=false;continue;}const key=nextHop(config,w.anchor,w.goal);if(!key){w.goal=w.anchor;continue;}const target=config.anchors[config.clips[key].to].root;
  const occupied=s.actors.some(a=>Math.abs(a.p[2]-target[2])<1.4&&Math.hypot(a.p[0]-target[0],a.p[1]-target[1])<.9);w.waiting=occupied;if(occupied)continue;w.clip=key;w.clock=0;}
 const clip=config.clips[w.clip];w.clock=Math.min(clip.duration,w.clock+dt);const rows=clip.frames;let lo=0,hi=rows.length-1;while(lo<hi){const m=(lo+hi)>>1;if(rows[m].time<w.clock)lo=m+1;else hi=m;}const j=lo,i=Math.max(0,j-1),a=rows[i],b=rows[j],f=b.time===a.time?0:(w.clock-a.time)/(b.time-a.time);w.root=a.root.map((x,k)=>k===3?angle(x,b.root[k],f):lerp(x,b.root[k],f));w.legs=Object.fromEntries(['left','right'].map(side=>[side,a.legs[side].map((x,k)=>lerp(x,b.legs[side][k],f))]));
 if(w.clock>=clip.duration){w.anchor=clip.to;w.clip=null;w.clock=0;w.completed++;Object.assign(w,standing(config.anchors[w.anchor].root));}
 }}
export function validateLocalWalkers(s,routes){if(Object.keys(s.localWalkers||{}).length!==Object.keys(routes||{}).length)throw Error('局部行走存档不完整');for(const[id,w]of Object.entries(s.localWalkers)){const r=routes[id];if(!r?.anchors[w.anchor]||!r.anchors[w.goal]||w.clip&&!r.clips[w.clip]||!w.root?.every(Number.isFinite)||!Number.isFinite(w.clock)||w.clock<0)throw Error('局部行走状态无效');}}
