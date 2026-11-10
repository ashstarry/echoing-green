import {pathTo} from './navigation.mjs';
import {EXPERIENCES,EXPERIENCE_THEMES} from './experience-choices.mjs';
const actorExists=(s,id)=>s.actors?.some(a=>a.id===id);
export function ensureWishMemory(s){
 if(s.wishMemory?.version!==1)s.wishMemory={version:1,recent:[],care:[],pending:null};
 return s.wishMemory;
}
export function beginExperience(s,items,receipt){
 const x=items.find(i=>i.experience)?.experience;if(!x||!Object.hasOwn(EXPERIENCES,x.variant)||!EXPERIENCE_THEMES.includes(x.theme))return;
 const w=ensureWishMemory(s);w.pending={id:receipt.id,variant:x.variant,theme:x.theme,at:s.time,actors:[],sceneId:null};
}
export function advanceWishMemory(s){
 const w=ensureWishMemory(s),q=s.inputSession,p=w.pending;
 if(p&&q?.requestIds?.includes(p.id)){
  if(q.sceneId)p.sceneId=q.sceneId;
  const ids=new Set(p.actors);
  if(s.sceneEvent?.id===p.sceneId)for(const id of Object.keys(s.sceneEvent.slots||{}))ids.add(id);
  for(const world of [s.paperWorld,s.craftWorld,s.neighborhoodWorld])if(world?.eventId===p.sceneId)for(const j of world.jobs||[])if(j.actor)ids.add(j.actor);
  p.actors=[...ids].filter(id=>actorExists(s,id)).slice(0,24);
  if(q.phase==='done'){
   const work=[s.paperWorld,s.craftWorld,s.neighborhoodWorld].filter(x=>x?.eventId===p.sceneId).flatMap(x=>x.jobs||[]);
   if(q.progressSamples>0)w.recent.push({variant:p.variant,theme:p.theme,at:s.time,actors:p.actors,scene:EXPERIENCES[p.variant].scene,outcome:work.some(j=>j.status==='cancelled'||j.status==='failed')?'interrupted':q.outcome,completed:!work.some(j=>j.status!=='done')});
   w.recent=w.recent.slice(-8);w.pending=null;
  }
 }
 for(const j of s.paperWorld?.jobs||[])if(j.recipe==='receive_note'&&j.status==='done'){
  const n=s.paperWorld.notes.find(n=>n.id===j.prop);if(n&&n.owner!==n.author&&!w.care.some(c=>c.note===n.id))w.care.push({note:n.id,from:n.author,to:n.owner,at:n.placedAt||n.created||s.time});
 }
 w.care=w.care.slice(-8);
}
export function validateWishMemory(s){
 const w=ensureWishMemory(s);
 w.recent=(Array.isArray(w.recent)?w.recent:[]).slice(-8).filter(x=>x&&Object.hasOwn(EXPERIENCES,x.variant)&&EXPERIENCE_THEMES.includes(x.theme)&&Number.isFinite(x.at)&&Array.isArray(x.actors)).map(x=>({...x,actors:x.actors.filter(id=>actorExists(s,id)).slice(0,24)}));
 w.care=(Array.isArray(w.care)?w.care:[]).slice(-8).filter(x=>x&&typeof x.note==='string'&&x.note.length<80&&actorExists(s,x.from)&&actorExists(s,x.to)&&x.from!==x.to&&Number.isFinite(x.at));
 if(w.pending&&(!Object.hasOwn(EXPERIENCES,w.pending.variant)||!EXPERIENCE_THEMES.includes(w.pending.theme)||!Number.isFinite(w.pending.at)||!Array.isArray(w.pending.actors)))w.pending=null;
 return w;
}
export function recentParticipationPenalty(s,id){const w=s.wishMemory;if(!w?.pending)return 0;return (w.recent||[]).slice(-2).reverse().reduce((n,r,i)=>n+(r.actors.includes(id)?.8/(i+1):0),0);}
export function returnKindness(s,candidates){
 if(s.wishMemory?.pending?.variant!=='comfort_note')return null;
 const ids=new Set(candidates.map(a=>a.id));return (s.wishMemory.care||[]).slice().reverse().find(c=>ids.has(c.from)&&ids.has(c.to))||null;
}
export function experienceContext(s,nav=null){
 const w=ensureWishMemory(s),free=s.actors.filter(a=>a.mobile&&!a.eventOnly&&!a.manual&&!a.interactionLock&&!s.residentActions[a.id]?.requested),adults=free.filter(a=>!a.id.includes('child')&&!a.id.includes('gardener'));
 const history=[...(s.craftWorld?.history||[]),...(s.neighborhoodWorld?.history||[]),...w.recent.map(r=>({kind:r.scene,at:r.at}))].sort((a,b)=>b.at-a.at);
 const dry=s.weather==='clear';
 const homeGoal=nav?nav.nodes.reduce((best,p,i)=>Math.hypot(p[0]+5.76,p[1]+2.48)<Math.hypot(nav.nodes[best][0]+5.76,nav.nodes[best][1]+2.48)?i:best,0):null;
 const homeNear=adults.some(a=>{if(!nav)return a.p[0]<-2&&a.p[1]<-1.8;const path=pathTo(nav,a.node,homeGoal);return path.length&&path.reduce((n,id,i)=>n+(i?Math.hypot(nav.nodes[id][0]-nav.nodes[path[i-1]][0],nav.nodes[id][1]-nav.nodes[path[i-1]][1]):0),0)<=6;});
 return{version:1,recent:w.recent.map(r=>r.variant),lastScene:history[0]?.kind||null,hasCare:w.care.length>0,available:{gather:free.length>=4,company:dry&&adults.length>=2,tea:adults.length>=1&&!s.residentActions['resident.vendor_bread']?.requested,home:homeNear,paper:adults.length>=2,prepare:dry&&adults.length>=3&&free.some(a=>a.id==='resident.child_runner'||a.id==='resident.garden_child'),music:dry&&free.some(a=>a.id==='resident.child_runner'||a.id==='resident.garden_child')}};
}
