from pathlib import Path
p=Path('app/runtime-cp19/src/simulation.mjs');s=p.read_text();s="import {createCommunity,updateDirector,updateResidents,wantedTask,routineTask,setResidentTask,ACTIVITIES,PROFILES,requestFestival} from './community.mjs';\nimport {CADENCE,varied,stableUnit} from './cadence.mjs';\n"+s;s=s.replace('VERSION=4','VERSION=5').replace('festivalNextAt:10','festivalNextAt:38')
s=s.replace("const s={version", "const s={occasion:'ordinary',lastOccasion:'ordinary',lastWeather:'clear',weatherChangedAt:0,afterRainUntil:0,musicManual:false,effectiveMusic:'play',musicGatherUntil:0,occasionUntil:0,planRevision:0,worldEvent:{kind:'ordinary',phase:'ongoing',started:0,until:0,revision:0},residents:createCommunity(nav),version")
s=s.replace("walked:0,speed:0", "manual:false,task:'stroll',taskRevision:0,reservation:null,lookTarget:null,walked:0,speed:0")
s=s.replace("s.festivalStarted=s.time;s.festivalUntil=s.time+24;s.festivalStop=null;", "requestFestival(s);")
s=s.replace("s.festivalAuto=false;s.festivalStop=s.time;", "s.festivalAuto=false;s.worldEvent={kind:'ordinary',phase:'ongoing',started:s.time,until:0,revision:s.worldEvent.revision+1};s.planRevision++;s.festivalStop=s.time;")
s=s.replace("s.festivalNextAt=s.time+110", "s.festivalNextAt=s.time+varied(CADENCE.ambientFestivalGap,'festival',s.revision)")
s=s.replace("if(d.street!=='keep')for", "if(d.music!=='keep'){s.musicManual=true;if(d.music==='play')s.musicGatherUntil=s.time+24;s.planRevision++;}\n if(d.street!=='keep')s.planRevision++;\n if(d.street!=='keep')for")
s=s.replace("a.intent=d.street;", "a.manual=false;a.intent=d.street;")
s=s.replace("a.intent=d[k];a.wait=0;", "a.manual=true;a.intent=d[k];a.taskRevision=-1;a.wait=0;")
a=s.index('function chooseGoal(');b=s.index('export function step(',a)
s=s[:a]+'''function chooseGoal(s,nav,a){
 const forced=wantedTask(s,a),task=forced||routineTask(s,a);a.task=task;
 if(a.manual&&a.intent==='quiet'||s.street==='quiet'&&!forced){setResidentTask(s,a.id,'rest','想在这里停下来看看');a.wait=varied(CADENCE.rest,a.id,s.residents[a.id].cycle);a.mode='idle';return;}
 const zone=ACTIVITIES[task]?.zone||'street',home=nav.actors.find(x=>x.id===a.id).position,centers={market:[-.5,2.2],music:[-1,-.6],pond:[3.4,.4],chat:[-.8,.2],post:[-4.8,.2],view:[.2,-1.5],home:home,street:a.p},center=centers[zone];
 const occupied=s.actors.filter(b=>b!==a).map(b=>b.reservation!==null?nav.nodes[b.reservation]:b.p);
 const candidates=nav.nodes.map((p,i)=>({i,p})).filter(({i,p})=>distance(p,a.p)>.55&&occupied.every(b=>distance(p,b)>.97)&&(zone!=='home'||nav.activities.spaces.nodes[i].covered||nav.activities.spaces.nodes[i].umbrellaClear));
 candidates.sort((x,y)=>{
  const score=({i,p})=>distance(p,center)+(zone==='home'&&nav.activities.spaces.nodes[i].covered?-2:0)+stableUnit(a.id+':'+i,s.residents[a.id].cycle)*.6;
  return score(x)-score(y);
 });
 const blocked=new Set(nav.nodes.map((p,i)=>s.actors.some(b=>b!==a&&distance(p,b.p)<nav.radius*2+.12)?i:-1).filter(i=>i>=0));
 for(const {i:dest}of candidates.slice(0,24)){const path=findPath(nav,a.node,dest,blocked);if(path.length<2)continue;
  a.path=[a.node,...smoothPath(nav,path,blocked).slice(1)];if(a.atHome)a.path=[...a.entry,...a.path.slice(1)];a.atHome=false;a.segment=0;a.target=dest;a.reservation=dest;a.mode='walk';a.lookTarget=null;
  const reason=task==='shelter'?(nav.activities.spaces.nodes[dest].covered?'走向有屋檐的空位':'回到门前，准备撑伞等雨停'):task==='fireworks'?'给别人留出通路，找个看得清的位置':task==='browse'?'想看看晚市，顺便和店家打招呼':task==='mail'?'沿着门牌走一段，留意收信的人':task==='chat'?'找个不挡路的地方和邻居聊一会':'按自己的兴趣走到下一处';
  setResidentTask(s,a.id,task,reason);return;
 }
 a.reservation=null;a.wait=varied([2,5],a.id,s.tick);setResidentTask(s,a.id,task,'前面的地方暂时不方便，先等一等');
}
''' +s[b:]
# Replace the old immediate festival timer with the event director.
a=s.index("stepTrain(s,nav.activities?.rail");b=s.index('\n for(const a of s.actors)',a)
s=s[:a]+"updateDirector(s,dt,text=>event(s,text));stepTrain(s,nav.activities?.rail,dt,text=>event(s,text));if(nav.activities){advanceMovers(s,nav.activities,dt);advanceDiners(s,nav.activities.diners||{},dt,text=>event(s,text));}updateResidents(s,nav,dt);let planned=0;"+s[b:]
s=s.replace("for(const a of s.actors){a.phase+=dt;", "for(const a of s.actors){a.phase+=dt;if(a.mobile&&a.taskRevision!==s.planRevision){a.taskRevision=s.planRevision;a.path=[];a.reservation=null;a.target=null;a.wait=varied(CADENCE.reaction,a.id,s.planRevision);a.mode='idle';}")
s=s.replace("if(a.wait>0){a.wait-=dt;a.speed=Math.max(0,a.speed-dt*2);continue;}", "if(a.wait>0){a.wait-=dt;a.speed=Math.max(0,a.speed-dt*2);if(a.lookTarget){const want=Math.atan2(a.lookTarget[1]-a.p[1],a.lookTarget[0]-a.p[0])+Math.PI/2;const delta=Math.atan2(Math.sin(want-a.yaw),Math.cos(want-a.yaw));a.yaw+=clamp(delta,-dt*.9,dt*.9);}continue;}")
a=s.index("if(!a.path.length){a.mode='idle';");b=s.index('\n const n=a.path',a)
s=s[:a]+"if(!a.path.length){a.mode='idle';if(planned>=1)continue;planned++;a.reservation=null;chooseGoal(s,nav,a);if(!a.path.length)continue;}if((s.residents[a.id]?.umbrellaOpen||0)>.06){a.mode='fold_umbrella';continue;}"+s[b:]
s=s.replace("if(a.blocked>4&&a.segment>0)","if(a.blocked>3&&a.segment>=0)")
s=s.replace("a.wait=1.8+random(s)*3.2;s.stats.completed++;", "a.wait=varied(ACTIVITIES[a.task]?.range||CADENCE.rest,a.id,s.residents[a.id].cycle);const r=s.residents[a.id];r.started=s.time;r.until=s.time+a.wait;r.reason=a.task==='shelter'?(nav.activities.spaces.nodes[a.node].covered?'在屋檐下等雨小些':'在门前撑伞，等雨小些'):'已经到了，'+(ACTIVITIES[a.task]?.label||'休息一会');a.lookTarget=a.task==='fireworks'?[0,7,9]:a.task==='lotus'?[8,-1.5,.7]:a.task==='listen'?[-2.47,-1.45,1.2]:a.task==='browse'?[-1,3,1.2]:null;if(a.task==='chat'){const other=s.actors.filter(b=>b!==a).sort((b,c)=>distance(a.p,b.p)-distance(a.p,c.p))[0];a.lookTarget=other?.p?.slice()||null;}r.needs[a.task==='chat'?'social':a.task==='rest'?'rest':'curiosity']=.1;s.stats.completed++;")
s=s.replace("['weather','breeze','light','music','street','birds','dining','pond','animals','cycling']", "['weather','breeze','light','music','street','birds','dining','pond','animals','cycling','occasion']")
s=s.replace(" return s;}\n", " if(!s.residents||Object.keys(s.residents).length!==32||!s.worldEvent||!Number.isFinite(s.planRevision))throw Error('居民意图存档无效');\n return s;}\n")
p.write_text(s)
