from pathlib import Path
p=Path('app/runtime-cp47/src/train-journey.mjs');s=p.read_text().replace("import {requestPassengerAction}","import {passengerPose,requestPassengerAction}")
s=s.replace("{location:'hand'});w.delivery={prop:prop.id,phase:'waiting_handoff'", "{location:'vehicle'});w.delivery={prop:prop.id,phase:'expecting',phaseAt:s.time,boardClock:0")
s=s.replace("mode,phase:'greeting',started:s.time,phaseAt:s.time,baselineTrips:p.completedTrips,sequence:j.sequence+1,flags:{parcel:true}", "mode,phase:'expecting',started:s.time,phaseAt:s.time,baselineTrips:p.completedTrips,sequence:j.sequence+1,flags:{parcel:true}")
s=s.replace("电车停在站边，旅客拿起捎来的小包裹，准备交给街坊。", "电车捎来了给街坊的小礼物。旅客望向车门，准备上前接过它。")
key="const w=ensureCraft(s),delivery=w.delivery,parcel=craftProp(s,delivery?.prop);"
s=s.replace(key,key+"""
 if(j.mode==='deliver'&&delivery&&parcel&&['expecting','collecting','receiving','returning_gift'].includes(delivery.phase)){
  const age=s.time-delivery.phaseAt;const phase=value=>{j.phase=delivery.phase=value;j.phaseAt=delivery.phaseAt=s.time;};
  if(delivery.phase==='expecting'){if(!j.flags.notice){gesture(traveler,'check_time');gesture('resident.station_attendant','signal_train');j.flags.notice=true;}if(age>=1.2){phase('collecting');emit('旅客看到车门打开，走到门边接礼物。');}}
  else if(delivery.phase==='collecting'){delivery.boardClock=Math.min(3.7,age*1.6);if(delivery.boardClock>=3.7){phase('receiving');parcel.location='collecting';}}
  else if(delivery.phase==='receiving'){if(age>=1.65){parcel.location='hand';parcel.pickedAt=s.time;phase('returning_gift');emit('旅客双手接住小礼物，准备送给街坊。');}}
  else{delivery.boardClock=Math.max(0,3.7-age*1.6);if(delivery.boardClock<=0){phase('waiting_handoff');j.phase='greeting';}}
  return;
 }
""")
s=s.replace("'greeting','finishing','done'].includes(j.phase)","'greeting','finishing','done','expecting','collecting','receiving','returning_gift'].includes(j.phase)")
s=s.replace("export const JOURNEY_PHASE_LABELS={", """export function giftPickupPose(s,activities){const d=s.craftWorld?.delivery;if(!d||!['collecting','receiving','returning_gift'].includes(d.phase))return null;return passengerPose({...s,passengers:{...s.passengers,[traveler]:{...s.passengers[traveler],phase:'board',clock:d.boardClock}}},activities);}
export const JOURNEY_PHASE_LABELS={expecting:'望向车门，等候捎来的礼物',collecting:'走到车门边接礼物',receiving:'双手接过车里的小礼物',returning_gift:'捧好礼物，带去交给街坊',""")
p.write_text(s)
p=Path('app/runtime-cp47/src/passengers.mjs');s=p.read_text().replace("const open=['prepare_board','board','prepare_exit','alight'].includes(p.phase);", "const open=['prepare_board','board','prepare_exit','alight'].includes(p.phase)||['expecting','collecting','receiving','returning_gift'].includes(s.craftWorld?.delivery?.phase);")
p.write_text(s)
p=Path('app/runtime-cp47/src/passenger-view.mjs');s=p.read_text().replace("import {passengerPose}","import {giftPickupPose} from './train-journey.mjs';\nimport {passengerPose}")
s=s.replace("if(['waiting','prepare_board','close_exit'].includes(p.phase))", "const gift=giftPickupPose(s,activities);if(!gift&&['waiting','prepare_board','close_exit'].includes(p.phase))")
s=s.replace("const pose=passengerPose(s,activities)","const pose=gift||passengerPose(s,activities)")
p.write_text(s)
p=Path('app/runtime-cp47/src/input-session.mjs');s=p.read_text().replace("if(['boarding','onboard','returning'].includes(t.phase))", "if(['expecting','collecting','receiving','returning_gift'].includes(t.phase)){put('gift.pickup',s.time-t.phaseAt);put('gift.walk',s.craftWorld.delivery.boardClock);}if(['boarding','onboard','returning'].includes(t.phase))")
p.write_text(s)
p=Path('app/runtime-cp47/src/craft-view.mjs');s=p.read_text()
s=s.replace("for(const j of jobs)pose(j,s);", """for(const j of jobs)pose(j,s);
  const delivery=w.delivery;if(delivery&&['receiving','returning_gift'].includes(delivery.phase)){
   const u=delivery.phase==='receiving'?ease((s.time-delivery.phaseAt)/1.65):1;
   solve('resident.station_traveler','left',[-.17,.76,.28+.15*(1-u)],1);solve('resident.station_traveler','right',[.17,.76,.28+.15*(1-u)],1);head('resident.station_traveler',.12*u);
  }
""")
s=s.replace("['vehicle','boarding','unloading'].includes(p.location)","['vehicle','boarding','unloading','collecting'].includes(p.location)")
s=s.replace("const rack=car.localToWorld(new THREE.Vector3(.72,.28,-.10))", "const rack=car.localToWorld(new THREE.Vector3(-.56,.80,-.44))")
s=s.replace("const u=p.location==='boarding'?ease((pp.clock-12)/3.6):1-ease(pp.clock/2.2);", "const u=p.location==='collecting'?1-ease((s.time-w.delivery.phaseAt)/1.65):p.location==='boarding'?ease((pp.clock-12)/3.6):1-ease(pp.clock/2.2);")
# A visible but modest ribboned gift instead of a tiny unadorned box.
s=s.replace("const o={root,visual,type:p.type};", "if(p.type==='parcel')visual.scale.setScalar(1.25);const o={root,visual,type:p.type};")
p.write_text(s)
p=Path('app/runtime-cp47/src/small-props.mjs');s=p.read_text().replace("box(g,0,.15,.128,.035,.28,.01,materials.cream);", "box(g,0,.15,.128,.035,.28,.01,materials.cream);for(const side of[-1,1]){const bow=new THREE.Mesh(ring,materials.cream);bow.scale.set(.055,.032,.035);bow.rotation.x=-Math.PI/2;bow.rotation.z=side*.35;bow.position.set(side*.047,.314,0);g.add(bow);}")
p.write_text(s)
