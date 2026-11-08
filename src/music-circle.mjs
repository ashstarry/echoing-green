import {navigationGraph,pathTo} from './navigation.mjs?v=cp51-vibe-response-67b273e60e03';
import {makeRoom} from './event-travel.mjs?v=cp51-vibe-response-67b273e60e03';

export const MUSIC_CHILDREN=['resident.child_runner','resident.garden_child'];
export const MUSIC_FOCUS=[-2.4684,-1.4537,1.1];
const FOX='animal.garden_fox';
const distance=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
const extended=new WeakMap();
export function prepareMusicSpace(s,nav,e){
 if(e.musicSpacePrepared)return;e.musicSpacePrepared=true;e.musicErrands=[];
 const spots=[[2.08,3.76],[3.36,2.64],[4.16,.88],[2.72,.56],[3.52,-.72],[2.56,-2.32]],used=[];
 const eligible=s.actors.filter(a=>a.mobile&&!a.eventOnly&&!a.id.includes('child')&&!e.protectedIds?.includes(a.id)&&!a.interactionLock&&a.p[0]<2.7&&a.p[1]>-.8);
 for(const a of eligible){const options=spots.map(p=>nearest(nav,p)).filter(n=>!used.includes(n));const n=options.sort((x,y)=>distance(a.p,nav.nodes[x])-distance(a.p,nav.nodes[y]))[0];if(n===undefined)break;used.push(n);a.musicErrandNode=n;a.path=[];a.wait=.1;a.taskRevision=-1;delete a.courtesyDestination;delete a.courtesyExpires;a.crowd=null;e.musicErrands.push(a.id);}
}
export function musicRoaming(nav,original){
 if(extended.has(nav))return extended.get(nav);
 const connected=navigationGraph(nav),main=connected.components[nav.actors[0].entry.at(-1)];
 const selected=nav.nodes.map((p,i)=>({p,i})).filter(({p,i})=>connected.components[i]===main&&p[2]<.85),index=new Map(selected.map((v,i)=>[v.i,i]));
 const data={...original,origin:nav.origin,nodes:selected.map(({p})=>[p[0],p[1],p[2]-.03]),adjacency:selected.map(({i})=>connected.edges[i].filter(j=>index.has(j)).map(j=>index.get(j)))};
 extended.set(nav,data);return data;
}
function nearest(nav,p){const graph=navigationGraph(nav),main=graph.components[nav.actors[0].entry.at(-1)];return nav.nodes.map((q,i)=>({i,d:distance(q,p)})).filter(x=>graph.components[x.i]===main).sort((a,b)=>a.d-b.d)[0].i;}
function route(s,nav,m,destination){
 const start=nearest(nav,m.p),goal=nearest(nav,destination),approach=nearest(nav,[destination[0]-.16,destination[1]+.48]),blocked=new Set(nav.nodes.flatMap((p,i)=>s.actors.some(a=>Math.abs(a.p[2]-p[2])<1&&distance(a.p,p)<.72)?[i]:[]));
 blocked.delete(start);blocked.delete(goal);blocked.delete(approach);
 let first=pathTo(nav,start,approach,blocked),last=pathTo(nav,approach,goal,blocked);let nodes=first.length&&last.length?[...first,...last.slice(1)]:pathTo(nav,start,goal,blocked);if(!nodes.length)nodes=pathTo(nav,start,goal);
 // Drop collinear grid points, retaining actual corners and continuous ground contact.
 const points=[m.p.slice()];for(let i=1;i<nodes.length;i++){const p=nav.nodes[nodes[i]],a=nav.nodes[nodes[i-1]],b=nav.nodes[nodes[i+1]];if(!b||Math.abs((p[0]-a[0])*(b[1]-p[1])-(p[1]-a[1])*(b[0]-p[0]))>.001)points.push([p[0],p[1],p[2]-.03]);}
 return points;
}
export function advanceMusicFox(s,nav,dt,gesture){
 const e=s.sceneEvent,m=s.movers[FOX];if(!m)return false;const control=s.objectControls?.[FOX];if(e?.kind==='music'&&control&&control.started>=e.started){if(s.musicCircle?.eventId===e.id)s.musicCircle.phase='done';return false;}
 if(e?.kind==='music'&&['gather','active'].includes(e.phase)&&s.musicCircle?.eventId!==e.id){
  s.musicCircle={eventId:e.id,phase:'approach',started:s.time,path:route(s,nav,m,[-3.04,.24]),at:1,blocked:0,speed:0,children:{},home:m.p.slice(),distance:0};
  const r=s.residentActions['resident.musician'];if(r?.action)r.cancelRemaining=.35;gesture('resident.musician','play_music');
 }
 const w=s.musicCircle;if(!w||w.eventId!==e?.id||e.kind!=='music'||!['gather','active'].includes(e.phase)){if(w&&w.phase!=='done'){w.phase='done';s.foxBehavior.suspended=false;s.foxBehavior.phase='look';s.foxBehavior.clock=0;s.foxBehavior.duration=9;s.foxBehavior.route=null;}return false;}
 for(const id of [...MUSIC_CHILDREN,'resident.child_listener']){const a=s.actors.find(a=>a.id===id);if(!a)continue;const at=id==='resident.child_listener'||e.slots[id]!==undefined&&(!!e.musicStanding?.[id]||distance(a.p,nav.nodes[e.slots[id]])<.20);if(at&&s.time-(w.children[id]??-100)>6){gesture(id,w.children[id]===undefined?'applaud':id==='resident.child_listener'?'tap_music':'applaud');w.children[id]=s.time;}}
 s.foxBehavior.suspended=true;m.intent=w.phase==='listen'?'listen_to_music':'walk_to_music';
 if(w.phase==='listen'){m.speed=0;m.strideWeight+=(0-m.strideWeight)*Math.min(1,dt*8);return true;}
 const target=w.path[w.at];if(!target){w.phase='listen';w.arrived=s.time;m.speed=0;return true;}
 const d=distance(m.p,target),yaw=Math.atan2(target[1]-m.p[1],target[0]-m.p[0])+Math.PI,error=Math.atan2(Math.sin(yaw-m.yaw),Math.cos(yaw-m.yaw));
 w.speed+=clamp(.78-w.speed,-dt*.9,dt*.6);const move=Math.min(d,w.speed*dt*Math.max(.25,Math.cos(error))),p=m.p.map((v,k)=>v+(target[k]-v)*move/Math.max(d,.001));
 const obstruct=s.actors.find(a=>Math.abs(a.p[2]-p[2])<1&&distance(a.p,p)<.48&&distance(a.p,p)<distance(a.p,m.p)-.0001);
 if(obstruct){w.blocked+=dt;m.speed=0;m.strideWeight*=Math.max(0,1-dt*8);if(w.blocked>.7&&s.time>(w.yieldAt||0)){makeRoom(s,nav,{id:FOX,p:m.p},obstruct.p);w.yieldAt=s.time+1;}if(w.blocked>1.6){w.path=route(s,nav,m,[-3.04,.24]);w.at=1;w.blocked=0;}return true;}
 w.blocked=0;m.p=p;m.yaw+=clamp(error,-dt*1.8,dt*1.8);m.distance+=move;w.distance+=move;m.speed=Math.min(1,move/(dt*.52));m.strideWeight+=(Math.min(1,move/dt/.25)-m.strideWeight)*Math.min(1,dt*7);
 if(d<.06||move>=d)w.at++;return true;
}
