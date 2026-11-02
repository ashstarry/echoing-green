from pathlib import Path
A=Path('app/runtime-cp26')
def edit(f,a,b):
 p=A/f;s=p.read_text();assert a in s,(f,a[:80]);p.write_text(s.replace(a,b))
edit('src/simulation.mjs',"import {stimulateTown", "import {eventCenter,eventScore} from './event-space.mjs';\nimport {stimulateTown")
edit('src/simulation.mjs',"if(zone==='chat'){", "center=eventCenter(a.id,task,center);\n if(zone==='chat'){")
edit('src/simulation.mjs',"(zone==='home'&&nav.activities.spaces.nodes[c.i].covered?-2:0)","eventScore(task,c,nav.activities.spaces.nodes[c.i],a.id)")
edit('src/simulation.mjs',"varied(CADENCE.reaction,a.id,s.planRevision)","varied(s.weather==='rain'?[.1,1.1]:CADENCE.reaction,a.id,s.planRevision)")
edit('src/simulation.mjs',"speed=a.task==='hop'?.85:a.id.includes('child')?.72:.58", "speed=a.task==='shelter'?.80:a.task==='hop'?.85:a.id.includes('child')?.72:.58")
edit('src/town-response.mjs',"const role=PROFILES[a.id],cycle=s.residents[a.id].cycle;", """const role=PROFILES[a.id],cycle=s.residents[a.id].cycle;
+  // A new town-wide event supersedes earlier mobile errands, not same-request
+  // explicit exceptions or fixed-role residents. Carried gestures finish safely.
+  if(!opening&&['rain','festival'].includes(theme)){
+   for(const j of s.intentRuntime.jobs)if(j.target===a.id&&live(j)){j.status='cancelled';j.updated=s.time;j.reason='跟随最新的全镇活动';}
+   const r=s.residentActions[a.id];r.requested=false;r.queuedByUser=false;r.queued=null;
+   if(RESIDENT_ACTIONS[r.action]?.navTask){r.action=null;r.clock=0;}
+   a.manual=false;a.manualActivity=null;a.activityUntil=0;
+  }
""".replace('\n+','\n'))
edit('src/town-response.mjs',"at:s.time+.15+n++*.22", "at:s.time+.10+n++*(['rain','festival'].includes(theme)?.12:.20)")
edit('src/town-response.mjs',"a.responseMinTravel=['shelter','kite','follow','hop'].includes(a.responseTask)?.8:1.45;", "a.responseMinTravel=['kite','follow','hop'].includes(a.responseTask)?.9:pulse.theme==='rain'?1.4:pulse.theme==='festival'?2.25:2.4;")
edit('src/town-response.mjs',"until:s.time+(opening?16:30)", "until:s.time+(opening?16:48)")
edit('src/community.mjs',"if(s.worldEvent?.phase==='show')return;", "if(s.worldEvent?.phase==='show'){s.worldEvent.until=Math.max(s.worldEvent.until,s.time+18);s.festivalUntil=s.worldEvent.until;s.planRevision++;return;}")
# Repeated fireworks can renew the communal response instead of being discarded.
edit('decision-api.mjs',"['train','festival'].includes(key)&&!(key==='festival'&&action==='quiet'&&state.festival_auto)","['train','festival'].includes(key)&&!(key==='festival'&&(action==='fireworks'||action==='quiet'&&state.festival_auto))")
edit('src/main.mjs',"import {QUICK_WISHES", "import {createResponseMarkers} from './response-markers.mjs';\nimport {QUICK_WISHES")
edit('src/main.mjs',"const environment=createEnvironmentView({scene,art,entities,camera});", "const environment=createEnvironmentView({scene,art,entities,camera});\nconst responseMarkers=createResponseMarkers({scene,entities});")
edit('src/main.mjs',"environment.frame(presented);camera.updateMatrixWorld", "environment.frame(presented);responseMarkers.frame(presented);camera.updateMatrixWorld")
edit('src/main.mjs',"window.__town={ready:true", "window.__town={ready:true,responseMarkers")
print('Longer group travel and paper response marks wired.')
