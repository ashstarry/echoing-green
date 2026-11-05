import {setup,station,step,runInput,queueIntent,inputBusy} from './audit-utils.mjs';
import {foxPose} from '../../app/runtime-cp47/src/fox-behavior.mjs';
import {giftPickupPose} from '../../app/runtime-cp47/src/train-journey.mjs';
import {actionSubjects} from '../../app/runtime-cp47/src/action-subjects.mjs';
import {WISH_SUGGESTIONS} from '../../app/runtime-cp47/src/wish-suggestions.mjs';
import {writeFileSync} from 'node:fs';
const out=[];
for(const[seed,warm]of[[62417,10],[90210,120],[12345,2]])for(const id of['fox','parcel','night','paper','spring','leaves']){
 const{s,nav}=setup(seed,warm);if(id==='parcel')station(s,nav);const c=WISH_SUGGESTIONS.find(x=>x.id===id),started=s.time,origin=s.movers['animal.garden_fox'].p.slice(),phases=[],subjects=new Set(),owners=new Set(),places=new Set();let span=0,paw=0,tail=0,firstMove=null,firstCue=null,maxMarker=0,old=s.movers['animal.garden_fox'].p.slice(),trace=[];
 runInput(s,c.items,()=>queueIntent(s,c.items,{source:'words',sourceText:c.zh},nav.activities.objectCatalog));
 for(let i=0;i<3200&&inputBusy(s);i++){
  step(s,nav);const p=foxPose(s),f=s.foxBehavior,d=s.craftWorld.delivery,g=giftPickupPose(s,nav.activities),ids=actionSubjects(s);maxMarker=Math.max(maxMarker,ids.length);ids.forEach(x=>subjects.add(x));if(ids.length&&firstCue===null)firstCue=s.time-started;
  span=Math.max(span,Math.hypot(s.movers['animal.garden_fox'].p[0]-origin[0],s.movers['animal.garden_fox'].p[1]-origin[1]));paw=Math.max(paw,p.paw||0);tail=Math.max(tail,Math.abs(p.tail));if(firstMove===null&&Math.hypot(...s.movers['animal.garden_fox'].p.map((v,k)=>v-old[k]))>.001)firstMove=s.time-started;old=s.movers['animal.garden_fox'].p.slice();
  const phase=id==='fox'?f.phase:id==='parcel'?d?.phase:s.sceneEvent?.phase;if(phases.at(-1)!==phase)phases.push(phase);
  if(d){const box=s.craftWorld.props.find(p=>p.id===d.prop);if(box){owners.add(box.owner);places.add(box.location);}}
  if(i%20===0)trace.push({t:+(s.time-started).toFixed(1),phase,fox:s.movers['animal.garden_fox'].p,neighbor:f.neighbor,greeted:f.greeted,subject:ids,giftRoot:g?.root});
 }
 out.push({seed,warm,id,seconds:+(s.time-started).toFixed(2),outcome:s.inputSession.outcome,busy:inputBusy(s),firstMove,firstCue,span,paw,tail,phases,subjects:[...subjects],owners:[...owners],places:[...places],maxMarker,jobs:[...s.paperWorld.jobs,...s.neighborhoodWorld.jobs,...s.craftWorld.jobs].map(j=>({recipe:j.recipe,status:j.status})),trace});
}
writeFileSync('outputs/runtime-checkpoint-47/targeted-audit.json',JSON.stringify(out,null,2));console.log(JSON.stringify(out.map(({trace,...x})=>x),null,2));
