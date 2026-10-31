import {createInteraction,advanceInteraction,interactionStep,INTERACTION_RECIPES} from './interaction-sequence.mjs?v=cp37-paper-1dbadc3fdf78';
import {navigationGraph} from './navigation.mjs?v=cp37-paper-1dbadc3fdf78';
export const PAPER_MODES=new Set(['paper_hang','paper_share','paper_read','paper_collect']);
export const PAPER_LIMIT=6;
const STATIONS=[{write:[-2.88,-.56],hang:[-2.72,.24],receive:[-2.4,.88]},{write:[1.92,2],hang:[2.24,.24],receive:[2.88,.72]},{write:[3.04,-.08],hang:[1.44,-1.68],receive:[2.08,-1.68]}];
const ELIGIBLE=['resident.customer_one','resident.customer_two','resident.customer_three','resident.market_browser','resident.strolling_parent','resident.courier'];
const D=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
export function ensurePaperWorld(s){s.paperWorld??={next:1,notes:[],jobs:[],eventId:null,pending:null};return s.paperWorld;}
function nearest(nav,p){const graph=navigationGraph(nav),main=graph.components[nav.actors[0].entry.at(-1)];return nav.nodes.map((q,i)=>({i,d:D(q,p)})).filter(x=>graph.components[x.i]===main).sort((a,b)=>a.d-b.d)[0].i;}
export function paperAnchor(nav,station,slot,scale=1.08){const p=nav.nodes[nearest(nav,STATIONS[station].hang)],dx=-.2347-p[0],dy=-.6956-p[1],d=Math.hypot(dx,dy),side=slot%2?1:-1;return[p[0]+dx/d*.23-dy/d*.14*side,p[1]+dy/d*.23+dx/d*.14*side,p[2]+1.06*scale];}
function unlock(s,job,e){const a=s.actors.find(a=>a.id===job.actor);if(!a)return;delete a.interactionLock;delete a.interactionLook;delete a.interactionTask;if(e?.slots)delete e.slots[a.id];a.path=[];a.reservation=null;a.target=null;a.taskRevision=-1;a.wait=.4;if(s.residentActions[a.id])s.residentActions[a.id].nextAt=s.time+1;}
function lock(s,job,e,targetName){const a=s.actors.find(a=>a.id===job.actor),node=job.context[targetName+'Node'];if(!a||node===undefined)return;a.interactionLock=job.id;a.interactionLook=(targetName==='destination'?job.context.look:job.context.writeLook).slice();a.interactionTask=interactionStep(job)?.action==='approach'?'stroll':'inspect';e.slots[a.id]=node;a.reservation=node;a.localActionUntil=0;a.manualActivity=null;}
function startPaper(s,nav,e){
 const w=ensurePaperWorld(s);w.eventId=e.id;w.jobs=[];e.slotsAssigned=true;e.slots={};e.paperStarted=true;e.openRideLane=true;
 const used=new Set(),candidates=s.actors.filter(a=>ELIGIBLE.includes(a.id)&&a.mobile&&!a.manual&&!e.protectedIds?.includes(a.id)&&!s.residentActions[a.id]?.requested);
 if(['paper_read','paper_collect'].includes(e.kind)){
  const note=w.notes.filter(n=>n.location==='anchor').sort((a,b)=>b.created-a.created)[0];
  if(note&&candidates.length){const destinationNode=nearest(nav,STATIONS[note.station].hang),actor=candidates.sort((a,b)=>D(a.p,nav.nodes[destinationNode])-D(b.p,nav.nodes[destinationNode]))[0],context={eventId:e.id,writingNode:destinationNode,destinationNode,station:note.station,slot:note.slot,anchor:note.anchor.slice(),oldNote:note.id,occupied:true,writeLook:note.anchor.slice(),look:note.anchor.slice()};
   const job=createInteraction({id:e.id+':'+actor.id,recipe:e.kind==='paper_read'?'read_note':'collect_note',actor:actor.id,prop:note.id,context});w.jobs.push(job);actor.path=[];actor.wait=.1;actor.reservation=null;actor.taskRevision=-1;const r=s.residentActions[actor.id];r.action=null;r.queued=null;lock(s,job,e,'destination');
  }return;
 }
 const count=e.kind==='paper_share'?Math.min(2,Math.floor(candidates.length/2)):Math.min(3,candidates.length);
 for(let station=0;station<count;station++){
  const config=STATIONS[station],writingNode=nearest(nav,config.write),destinationNode=nearest(nav,config.hang);
  const actor=candidates.filter(a=>!used.has(a.id)).sort((a,b)=>D(a.p,nav.nodes[writingNode])-D(b.p,nav.nodes[writingNode]))[0];if(!actor)continue;used.add(actor.id);
  const ids=w.notes.filter(n=>n.location==='anchor').map(n=>n.slot),options=[station*2,station*2+1],slot=options.find(x=>!ids.includes(x))??options.sort((a,b)=>(w.notes.find(n=>n.location==='anchor'&&n.slot===a)?.placedAt||0)-(w.notes.find(n=>n.location==='anchor'&&n.slot===b)?.placedAt||0))[0];
  const old=w.notes.find(n=>n.location==='anchor'&&n.slot===slot),id='paper-note-'+w.next++,anchor=paperAnchor(nav,station,slot,actor.scale),note={id,purpose:e.kind,author:actor.id,owner:actor.id,side:'left',location:'supply',stage:'blank',color:(w.next-2)%6,message:String(e.sourceText||'').slice(0,160),created:s.time,slot:null,anchor:null,station};
  w.notes.push(note);let recipient=null,recipientNode=null;
  if(e.kind==='paper_share'){recipient=candidates.filter(a=>!used.has(a.id)).sort((a,b)=>D(a.p,nav.nodes[destinationNode])-D(b.p,nav.nodes[destinationNode]))[0];if(!recipient)continue;used.add(recipient.id);const p=nav.nodes[destinationNode];recipientNode=nearest(nav,config.receive);}
  const context={eventId:e.id,writingNode,destinationNode,station,slot,anchor,oldNote:old?.id||null,occupied:!!old,recipient:recipient?.id||null,writeLook:[nav.nodes[writingNode][0],nav.nodes[writingNode][1]-1,.9],look:recipient?nav.nodes[recipientNode].slice(0,3):anchor};
  w.jobs.push(createInteraction({id:e.id+':'+actor.id,recipe:recipient?'share_note':'hang_note',actor:actor.id,prop:id,context}));
  if(recipient){w.jobs.push(createInteraction({id:e.id+':'+recipient.id,recipe:'receive_note',actor:recipient.id,prop:id,context:{...context,writingNode:recipientNode,destinationNode:recipientNode,look:nav.nodes[destinationNode].slice(0,3),sender:actor.id,occupied:false}}));}
 }
 for(const j of w.jobs){const a=s.actors.find(a=>a.id===j.actor),r=s.residentActions[j.actor];a.path=[];a.wait=.1;a.reservation=null;a.taskRevision=-1;delete a.courtesyDestination;delete a.courtesyExpires;delete a.courtesyArrivedAt;if(r&&!r.requested){r.action=null;r.queued=null;r.cancelRemaining=0;}lock(s,j,e,j.recipe==='receive_note'?'destination':'writing');}
}
export function advancePaperWorld(s,nav,dt,startDeferred){
 const w=ensurePaperWorld(s);if(!s.sceneEvent&&w.pending&&startDeferred){const pending=w.pending;w.pending=null;startDeferred(pending);}const e=s.sceneEvent;
 if(e&&PAPER_MODES.has(e.kind)&&['gather','active'].includes(e.phase)&&!e.paperStarted)startPaper(s,nav,e);
 for(const job of w.jobs){
  if(job.status==='done'||job.status==='cancelled')continue;const note=w.notes.find(n=>n.id===job.prop),a=s.actors.find(a=>a.id===job.actor);
  const active=e?.id===job.context.eventId&&['gather','active'].includes(e.phase)&&!e.protectedIds?.includes(job.actor);
  if(!active){job.cancelClock=(job.cancelClock||0)+dt;job.cancelledPose='stow';if(job.cancelClock>=1.6){for(const n of w.notes)if(n.owner===job.actor&&['supply','hand'].includes(n.location)){n.location=n.location==='supply'?'archived':'pocket';n.stage='folded';n.placedAt=s.time;}job.status='cancelled';unlock(s,job,e);}continue;}
  advanceInteraction(job,dt,{
   condition(key){if(key==='occupied')return job.context.occupied;if(key==='received')return note.owner===job.actor&&note.location==='hand';if(key==='recipient'){const r=w.jobs.find(j=>j.actor===job.context.recipient);const b=s.actors.find(x=>x.id===job.context.recipient);return r&&b&&b.node===r.context.destinationNode&&!b.path.length&&D(a.p,b.p)<1.2;}return false;},
   enter(step){lock(s,job,e,step.target||((job.step<4&&job.recipe!=='receive_note')?'writing':'destination'));},
   move(target){lock(s,job,e,target);},
   arrived(target){return a.node===job.context[target+'Node']&&!a.path.length&&a.mode==='idle'&&D(a.p,nav.nodes[job.context[target+'Node']])<.08;},
   commit(step){
    if(step.action==='take'){note.location='hand';note.owner=job.actor;}
    if(step.action==='write')note.stage='written';
    if(step.action==='fold')note.stage='folded';
    if(step.action==='collect'){const old=w.notes.find(n=>n.id===job.context.oldNote);if(old){old.location='hand';old.owner=job.actor;old.side='right';old.slot=null;old.anchor=null;}}
    if(step.action==='stow'){const n=['receive_note','collect_note'].includes(job.recipe)?note:w.notes.find(n=>n.id===job.context.oldNote);if(n){n.location=['receive_note','collect_note'].includes(job.recipe)?'pocket':'archived';n.stage='folded';n.placedAt=s.time;}}
    if(step.action==='hang'){note.location='anchor';note.slot=job.context.slot;note.anchor=job.context.anchor.slice();note.stage='written';note.placedAt=s.time;}
    if(step.action==='offer'){note.owner=job.context.recipient;note.side='left';note.location='hand';note.placedAt=s.time;}
   },
   finish(){unlock(s,job,e);}
  });
 }
 if(e&&PAPER_MODES.has(e.kind)&&e.paperStarted&&w.jobs.every(j=>j.status!=='running')){if(e.phase==='gather'){e.phase='active';e.phaseAt=s.time;}if(e.phase==='active')e.until=Math.min(e.until,s.time+2.5);}
 // Keep a bounded physical display plus a small local history. Never remove an active prop.
 const active=new Set(w.jobs.filter(j=>j.status==='running').map(j=>j.prop));
 for(const owner of new Set(w.notes.filter(n=>n.location==='pocket').map(n=>n.owner))){const held=w.notes.filter(n=>n.owner===owner&&n.location==='pocket').sort((a,b)=>(b.placedAt||b.created)-(a.placedAt||a.created));for(const n of held.slice(1))if(!active.has(n.id))n.location='archived';}
 const history=w.notes.filter(n=>n.location==='archived').sort((a,b)=>b.created-a.created).slice(0,12);w.notes=w.notes.filter(n=>n.location!=='archived'||history.includes(n));
}
export function validatePaperWorld(s,nav){const w=ensurePaperWorld(s);if(!Number.isInteger(w.next)||w.next<1||!Array.isArray(w.notes)||w.notes.length>30||!Array.isArray(w.jobs)||w.jobs.length>8)throw Error('Invalid paper state');if(w.pending&&(!['hang','share','read','collect'].includes(w.pending.mode)||typeof w.pending.text!=='string'||w.pending.text.length>160))throw Error('Invalid deferred paper activity');const ids=new Set();for(const n of w.notes){if(ids.has(n.id)||typeof n.id!=='string'||typeof n.message!=='string'||n.message.length>160||!s.residents[n.owner]||!Number.isInteger(n.color)||n.color<0||n.color>5||n.location==='anchor'&&(!Number.isInteger(n.slot)||n.slot<0||n.slot>=PAPER_LIMIT||!n.anchor)||!['supply','hand','anchor','pocket','archived'].includes(n.location)||!Number.isFinite(n.created)||n.anchor&&(!Array.isArray(n.anchor)||n.anchor.length!==3||!n.anchor.every(Number.isFinite)))throw Error('Invalid paper note');ids.add(n.id);}if(w.notes.filter(n=>n.location==='anchor').length>PAPER_LIMIT||new Set(w.notes.filter(n=>n.location==='anchor').map(n=>n.slot)).size!==w.notes.filter(n=>n.location==='anchor').length)throw Error('Paper display occupancy is invalid');for(const j of w.jobs)if(!INTERACTION_RECIPES[j.recipe]||!Number.isInteger(j.step)||j.step<0||j.step>INTERACTION_RECIPES[j.recipe].length||!['running','done','cancelled'].includes(j.status)||!s.actors.some(a=>a.id===j.actor)||!Number.isInteger(j.context.destinationNode)||!Number.isInteger(j.context.writingNode)||!nav.nodes[j.context.destinationNode]||!nav.nodes[j.context.writingNode]||!Number.isFinite(j.clock))throw Error('Invalid paper interaction');}
