import {navigationGraph,pathTo} from './navigation.mjs';
const FOX='animal.garden_fox',D=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
export function foxMeetingActive(s,a){return !!a.foxGreetingFor&&s.foxBehavior?.command==='greet'&&s.foxBehavior.invitedNeighbor===a.id&&s.time<a.foxGreetingUntil;}
// One neighbor may step out of an old crowd to a free, existing piece of paving.
// The same crowd walker handles the trip; no actor position is reassigned.
export function inviteFoxNeighbor(s,nav,preferredId=null){
 const f=s.foxBehavior,c=s.objectControls?.[FOX],m=s.movers?.[FOX];if(!nav||!f||f.invitedNeighbor||c?.preserveOthers||f.command!=='greet')return false;
 const candidates=s.actors.filter(a=>a.mobile&&!a.eventOnly&&!a.interactionLock&&!a.manual&&!a.id.includes('kite')&&!s.eventGuests?.[a.id]?.active&&!s.residentActions?.[a.id]?.requested&&!s.sceneEvent?.protectedIds?.includes(a.id)&&D(a.p,m.p)<5.5);
 const graph=navigationGraph(nav),main=graph.components[nav.actors[0].entry.at(-1)],anchors=[[2.56,.72],[1.60,-.40],[-1.28,-.40],[-3.20,-1.60]].sort((a,b)=>D(a,m.p)-D(b,m.p));
 for(const anchor of anchors.slice(0,2)){
  const nodes=nav.nodes.map((p,i)=>({p,i})).filter(({p,i})=>graph.components[i]===main&&!nav.noStopping.has(i)&&D(p,anchor)<.65&&D(p,m.p)>.95&&s.actors.every(a=>D(a.p,p)>.5)&&D(p,s.movers['bicycle.street_bicycle'].p)>1.05).sort((a,b)=>D(a.p,anchor)-D(b.p,anchor)).slice(0,8);
  for(const a of candidates.sort((a,b)=>Number(b.id===preferredId)-Number(a.id===preferredId)||D(a.p,anchor)-D(b.p,anchor)))for(const n of nodes){
   if(!pathTo(nav,a.node,n.i).length)continue;
   a.courtesyDestination=n.i;a.courtesyExpires=s.time+25;a.courtesyArrivedAt=null;a.foxGreetingFor=c.action+':'+c.started;a.foxGreetingUntil=s.time+25;a.path=[];a.target=null;a.reservation=null;a.wait=0;a.taskRevision=-1;a.crowd=null;a.localActionUntil=0;
   const r=s.residentActions[a.id];if(r?.action)r.cancelRemaining=.3;s.residents[a.id].reason='停一步，看看来打招呼的小狐狸';f.invitedNeighbor=f.neighbor=a.id;return true;
  }
 }
 return false;
}
