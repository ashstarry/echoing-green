// A small cast for the current local wish, derived from the same live ownership
// and job state as the action. Daily life and town-wide events stay unmarked.
export function actionSubjects(s){
 const q=s.inputSession;if(q?.phase!=='running')return[];
 const items=q.items||[],e=s.sceneEvent;if(e&&q.sceneId===e.id&&['festival','market','supper','reunion','rain','snow','quiet'].includes(e.kind))return[];
 const ids=[];const add=id=>{if(id&&!ids.includes(id))ids.push(id);};
 if(items.some(i=>i.target==='animal.garden_fox')){add('animal.garden_fox');if(s.foxBehavior?.invitedNeighbor)add(s.foxBehavior.invitedNeighbor);if(s.foxBehavior?.phase==='greet')add(s.foxBehavior.neighbor);}
 if(items.some(i=>i.target==='journey')){
  const d=s.craftWorld?.delivery,p=s.craftWorld?.props?.find(p=>p.id===d?.prop);
  if(!d||!['delivered','cancelled'].includes(d.phase))add(p?.owner||'resident.station_traveler');
  if(d?.phase==='handoff')for(const j of s.craftWorld.jobs||[])if(j.status==='running')add(j.actor);
 }
 for(const w of[s.paperWorld,s.neighborhoodWorld,s.craftWorld]){
  if(!w||!q.sceneId||w.eventId!==q.sceneId)continue;
  for(const j of w.jobs||[])if(j.status==='running'&&!j.context?.fixed)add(j.actor);
 }
 for(const i of items)if(i.kind==='resident'&&(s.residentActions?.[i.target]?.requested||s.residentActions?.[i.target]?.queuedByUser))add(i.target);
 return ids.slice(0,3);
}
export function subjectAlpha(age,time){const fade=Math.min(1,Math.max(0,age/.55));return fade*(.44+.025*Math.sin(time*1.5));}
