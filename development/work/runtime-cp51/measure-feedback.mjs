import {readFileSync,writeFileSync} from 'node:fs';
import {setup,step,runInput,inputBusy,queueIntent} from '../runtime-cp50/audit-utils.mjs';
const out='outputs/runtime-checkpoint-51/';
const name=process.argv[2]||'final';
const rows=JSON.parse(readFileSync(out+name+'.json'));
const output=[];
for(const row of rows){
 const {s,nav}=setup(62417,10),control=setup(62417,10),start=s.time;
 const initial=Object.fromEntries(s.actors.map(a=>[a.id,a.p.slice()]));
 const affected=new Set(),changed=new Set(),trips={},deviations={},jobs=new Map(),scenes=new Set();let first=null,maxSnow=0,maxRain=0,foxDistance=0,props=0;
 if(!row.plan?.items.length){output.push({id:row.id,items:[],noChange:true});continue;}
 try{runInput(s,row.plan.items,()=>queueIntent(s,row.plan.items,{source:'words',sourceText:row.text},nav.activities.objectCatalog));}catch(e){output.push({id:row.id,error:e.message});continue;}
 for(let i=0;i<3200&&inputBusy(s);i++){
  step(s,nav);step(control.s,control.nav);
  const age=s.time-start,e=s.sceneEvent,q=s.inputSession;
  if(e&&e.id===q.sceneId){scenes.add(e.kind);for(const id of Object.keys({...e.slots,...e.returnSlots}))affected.add(id);}
  for(const item of row.plan.items)if(item.kind==='resident')affected.add(item.target);
  for(const [group,w]of [['paper',s.paperWorld],['craft',s.craftWorld],['neighborhood',s.neighborhoodWorld]])for(const j of w.jobs||[]){
   if(j.actor&&(w.eventId===q.sceneId||q.items.some(x=>x.target===group))){affected.add(j.actor);jobs.set(j.id||j.actor+j.recipe,{actor:j.actor,recipe:j.recipe,status:j.status,step:j.step,history:j.history.slice()});}
  }
  for(const a of s.actors)if(affected.has(a.id)){
   const b=control.s.actors.find(x=>x.id===a.id),travel=Math.hypot(a.p[0]-initial[a.id][0],a.p[1]-initial[a.id][1]),delta=Math.hypot(a.p[0]-b.p[0],a.p[1]-b.p[1]);
   trips[a.id]=Math.max(trips[a.id]||0,travel);deviations[a.id]=Math.max(deviations[a.id]||0,delta);
   if(delta>.6){changed.add(a.id);first??=age;}
  }
  const df=s.movers['animal.garden_fox'],bf=control.s.movers['animal.garden_fox'];
  if(row.plan.items.some(x=>x.target==='animal.garden_fox')){foxDistance=Math.max(foxDistance,Math.hypot(df.p[0]-bf.p[0],df.p[1]-bf.p[1]));if(foxDistance>.6)first??=age;}
  maxRain=Math.max(maxRain,s.eventWeather.rain);maxSnow=Math.max(maxSnow,s.eventWeather.snow);
  if(maxRain>.2||maxSnow>.2)first??=age;
  props=Math.max(props,[...jobs.values()].filter(j=>j.history.some(h=>!['approach','carry','admire'].includes(h))).length);
  if(props)first??=age;
 }
 output.push({id:row.id,scene:[...scenes],seconds:+(s.time-start).toFixed(2),outcome:s.inputSession.outcome,firstPhysicalDifference:first===null?null:+first.toFixed(2),participants:affected.size,actorsDifferentFromUnprompted:changed.size,travel:Object.fromEntries(Object.entries(trips).map(([k,v])=>[k,+v.toFixed(2)])),counterfactualDifference:Object.fromEntries(Object.entries(deviations).map(([k,v])=>[k,+v.toFixed(2)])),jobs:[...jobs.values()],maxRain,maxSnow,foxDifference:+foxDistance.toFixed(2),note:'Position differences are against a same-seed unprompted simulation; they are not a perceptual visibility score. Only actors assigned to the requested episode or jobs are counted.'});
 writeFileSync(out+name+'-feedback-measurements.json',JSON.stringify(output,null,2));
 console.log(JSON.stringify(output.at(-1),(k,v)=>['travel','counterfactualDifference','note','jobs'].includes(k)?undefined:v));
}
