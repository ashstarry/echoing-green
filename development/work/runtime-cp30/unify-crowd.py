from pathlib import Path
p=Path('app/runtime-cp30/src/event-travel.mjs');s=p.read_text().replace('return Object.values(s.eventGuests||{}).map(g=>g.p);','return [];')
s=s.replace('s.actors.some(a=>Math.abs', 's.actors.some(a=>a.id!==g.id&&Math.abs').replace('s.actors.map(a=>({id:a.id', 's.actors.filter(a=>a.id!==g.id).map(a=>({id:a.id')
s=s.replace("const original=nav.activities.eventTrips[g.id],c=", "const actor=s.actors.find(a=>a.id===g.id);\n  const original=nav.activities.eventTrips[g.id],c=")
s=s.replace("g.phase='ground_home';routeGround(s,nav,g,c.portal);", "g.phase='ground_home';actor.guestReturnNode=c.portal;actor.taskRevision=-1;actor.reservation=null;actor.path=[];actor.wait=.1;")
s=s.replace("g.phase='ground_out';g.path=[];", "g.phase='ground_out';g.path=[];delete actor.guestReturnNode;actor.taskRevision=-1;actor.path=[];actor.wait=.1;")
s=s.replace("if(g.phase==='entry_out'){if(followEntry(s,g,c,dt,1)){g.phase='ground_out';g.path=[];delete actor.guestReturnNode;actor.taskRevision=-1;actor.path=[];actor.wait=.1;}}", "if(g.phase==='entry_out'){if(followEntry(s,g,c,dt,1)){g.phase='ground_out';g.path=[];actor.p=g.p.slice();actor.yaw=g.yaw;actor.node=c.portal;actor.atHome=false;actor.mobile=true;actor.wait=.1;actor.taskRevision=-1;actor.path=[];actor.reservation=null;delete actor.guestReturnNode;}}")
start=s.index("  }else if(['ground_out','ground_home'].includes(g.phase)){");end=s.index("  }else if(g.phase==='hold'){",start)
s=s[:start]+'''  }else if(['ground_out','ground_home'].includes(g.phase)){
   const target=g.phase==='ground_home'?c.portal:e?.slots[g.id];if(target===undefined)continue;
   if(g.phase==='ground_home')actor.guestReturnNode=target;else delete actor.guestReturnNode;
   g.p=actor.p.slice();g.yaw=actor.yaw;g.walked=actor.walked;g.gaitWeight=actor.gaitWeight;
   if(actor.node===target&&!actor.path.length&&actor.reservation===target){g.gaitWeight=0;g.phase=g.phase==='ground_home'?'entry_home':'hold';g.goal=target;g.progress=c.entry.length-1;if(g.phase==='entry_home'){actor.mobile=false;delete actor.guestReturnNode;}}
'''+s[end:]
s=s.replace("g.phase='home';g.active=false;g.returnRequested=false;", "g.phase='home';g.active=false;g.returnRequested=false;actor.mobile=false;actor.path=[];actor.reservation=null;delete actor.guestReturnNode;")
s=s.replace("if(g.active){const resident=", "if(g.active&&!['ground_out','ground_home','hold'].includes(g.phase)){actor.mobile=false;actor.p=g.p.slice();actor.yaw=g.yaw;}\n  if(g.active){const resident=")
s+='''
export function syncGuestActors(s){for(const g of Object.values(s.eventGuests||{})){const a=s.actors.find(a=>a.id===g.id);if(a&&['ground_out','ground_home','hold'].includes(g.phase)){g.p=a.p.slice();g.yaw=a.yaw;g.walked=a.walked;g.gaitWeight=a.gaitWeight;}else if(a&&g.phase==='home'){a.mobile=false;a.p=g.p.slice();a.yaw=g.yaw;}}}
'''
p.write_text(s)
p=Path('app/runtime-cp30/src/simulation.mjs');s=p.read_text().replace('ensureEventTravel,advanceEventTravel,eventGuestPositions','ensureEventTravel,advanceEventTravel,eventGuestPositions,syncGuestActors').replace('mobile:!!a.entry?.length','mobile:!a.eventOnly&&!!a.entry?.length')
s=s.replace("const assigned=s.sceneEvent?.slots?.[a.id];", "const assigned=a.guestReturnNode??s.sceneEvent?.slots?.[a.id],assignmentActive=a.guestReturnNode!==undefined||['gather','active'].includes(s.sceneEvent?.phase);")
s=s.replace("assigned!==undefined&&['gather','active'].includes(s.sceneEvent.phase)","assigned!==undefined&&assignmentActive")
s=s.replace("}else if(a.responseReplan||desired!==a.task||a.reservation===null)","}else if(a.guestReturnNode!==undefined||a.responseReplan||desired!==a.task||a.reservation===null)")
s=s.replace("}\nexport function serialize(s)","}\nexport function serialize(s)")
needle='\n }\n}\nexport function serialize';assert needle in s;s=s.replace(needle,'\n }\n syncGuestActors(s);\n}\nexport function serialize')
s=s.replace("s.actors.some(b=>b!==a&&distance(candidate,b.p)","s.actors.some(b=>b!==a&&Math.abs(candidate[2]-b.p[2])<1.4&&distance(candidate,b.p)")
p.write_text(s)
p=Path('app/runtime-cp30/src/scene-events.mjs');s=p.read_text().replace("const actors=[...s.actors.filter(a=>a.mobile&&!e.protectedIds?.includes(a.id)),...eventGuestCandidates(s,nav,e)]", "const candidates=eventGuestCandidates(s,nav,e),candidateIds=new Set(candidates.map(a=>a.id));const actors=[...s.actors.filter(a=>a.mobile&&!candidateIds.has(a.id)&&!e.protectedIds?.includes(a.id)),...candidates]")
s=s.replace("export function holdsEventPlace(s,a){const e=s.sceneEvent;", "export function holdsEventPlace(s,a){if(a.guestReturnNode!==undefined&&a.node===a.guestReturnNode&&!a.path.length)return true;const e=s.sceneEvent;")
p.write_text(s)
