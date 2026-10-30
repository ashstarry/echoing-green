import {createDinerActionView} from './diner-action-view.mjs?v=cp34-art-a447e84106f5';
import {makeArmSolver} from './arm-ik.mjs?v=cp34-art-a447e84106f5';
import * as THREE from 'three';
import {RESIDENT_ACTIONS,RESIDENT_CAPABILITIES} from './resident-actions.mjs?v=cp34-art-a447e84106f5';
import {PROFILES} from './community.mjs?v=cp34-art-a447e84106f5';
import {ease,legPose} from './motion.mjs?v=cp34-art-a447e84106f5';
const X=new THREE.Vector3(1,0,0),Y=new THREE.Vector3(0,1,0),Z=new THREE.Vector3(0,0,-1);
const mix=(a,b,t)=>a+(b-a)*t;
export function createResidentActionView({scene,entities,parts,sockets,localRoutes,support,dinerGestures,diningProps}){
 const base=new Map([...parts].map(([id,p])=>[id,{q:p.quaternion.clone(),p:p.position.clone(),s:p.scale.clone()}])),roots=new Map([...entities].map(([id,o])=>[id,{p:o.position.clone(),q:o.quaternion.clone()}])), props=new Map(),observed=new Map();
 const dinerView=createDinerActionView({entities,parts,gestures:dinerGestures,diningProps});
 const book=entities.get('book.terrace_reader_book'),reader=entities.get('resident.quiet_reader');const bookRest=book?{q:book.getWorldQuaternion(new THREE.Quaternion()),ownerQ:reader.getWorldQuaternion(new THREE.Quaternion()),offset:new THREE.Vector3(.18,.08,.11)}:null;
 const solveArm=makeArmSolver({entities,parts,sockets,base});
 const ivory=new THREE.MeshStandardMaterial({color:0xe6cba1,roughness:.92}),tea=new THREE.MeshStandardMaterial({color:0x68523c,roughness:.85}),blue=new THREE.MeshStandardMaterial({color:0x547b87,roughness:.94}),bread=new THREE.MeshStandardMaterial({color:0xbf8148,roughness:1}),cloth=new THREE.MeshStandardMaterial({color:0x9caa96,roughness:1,side:THREE.DoubleSide});
 function register(id,key,obj){obj.name='CP22_'+key+'_'+id.slice(9);obj.userData.runtime_effect_id='prop.'+id+'.'+key;obj.userData.owner_entity=id;obj.traverse(m=>{if(m.isMesh){m.name=obj.name+'_mesh_'+props.size;m.castShadow=true;m.receiveShadow=true;}});entities.get(id).add(obj);props.set(id+'/'+key,obj);return obj;}
 function cup(){const g=new THREE.Group();g.add(new THREE.Mesh(new THREE.CylinderGeometry(.055,.042,.09,8),blue));const liquid=new THREE.Mesh(new THREE.CircleGeometry(.043,8),tea);liquid.rotation.x=-Math.PI/2;liquid.position.y=.046;g.add(liquid);return g;}
 for(const[id,cap]of Object.entries(RESIDENT_CAPABILITIES)){if(PROFILES[id].role==='diner')continue;
  if(cap.includes('sip_tea'))register(id,'cup',cup());
  if(cap.includes('taste_food')||cap.includes('offer_food')){const g=new THREE.Group(),plate=new THREE.Mesh(new THREE.CylinderGeometry(.09,.09,.012,10),ivory),bun=new THREE.Mesh(new THREE.SphereGeometry(.055,8,5),bread);bun.scale.y=.65;bun.position.y=.04;g.add(plate,bun);register(id,'snack',g);}
  if(cap.includes('wipe_counter')){const g=new THREE.Mesh(new THREE.BoxGeometry(.15,.008,.11),cloth);register(id,'cloth',g);}
  if(cap.includes('feed_pond')){const g=new THREE.Mesh(new THREE.CylinderGeometry(.07,.065,.12,5),ivory);register(id,'feed_bag',g);}
 }
 const crumb=new THREE.InstancedMesh(new THREE.IcosahedronGeometry(.021,0),ivory,8);crumb.name='CP22_paper_pond_food';crumb.userData.runtime_effect_id='effect.pond_food';crumb.userData.owner_entity='resident.water_visitor';crumb.frustumCulled=false;scene.add(crumb);const dummy=new THREE.Object3D(),point=new THREE.Vector3();
 function rot(id,key,axis,a){const p=parts.get(id+'/'+key),b=base.get(id+'/'+key);if(p&&b&&!p.matrixAutoUpdate)return;if(p&&b)p.quaternion.copy(b.q).multiply(new THREE.Quaternion().setFromAxisAngle(axis,a));}
 function arm(id,side,pitch=0,roll=0,elbow=0){rot(id,'anim_arm_'+side,X,pitch);const p=parts.get(id+'/anim_arm_'+side);if(p)p.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(Z,roll));rot(id,'anim_elbow_'+side,X,elbow);}
 function handWorld(id,side){const entry=sockets[id]?.hands?.[side];if(!entry)return entities.get(id).getWorldPosition(new THREE.Vector3()).add(new THREE.Vector3(0,.7,0));const node=parts.get(id+'/'+(entry.part||'anim_arm_'+side));const p=entry.part_local;node.updateWorldMatrix(true,false);return node.localToWorld(new THREE.Vector3(p[0],p[2],-p[1]));}
 function toRoot(id,world){return entities.get(id).worldToLocal(world.clone());}
 function resetElbows(id){for(const side of ['left','right'])rot(id,'anim_elbow_'+side,X,0);}
 function fitBridgeFeet(id,root,weight){
  const field=support?.bridge;if(!field)return;const targets={};let sum=0;root.updateWorldMatrix(true,true);
  // Bound the entire projected shoe, including plank ridges between shoe vertices.
  function highestUnder(bounds){let highest=-Infinity;for(const tri of field.triangles||[]){let poly=tri;for(const[axis,edge,sign]of [[0,bounds[0],1],[0,bounds[1],-1],[1,bounds[2],1],[1,bounds[3],-1]]){const out=[];for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length],da=(a[axis]-edge)*sign,db=(b[axis]-edge)*sign;if(da>=-1e-8)out.push(a);if((da>=0)!==(db>=0)){const t=da/(da-db);out.push(a.map((v,k)=>v+(b[k]-v)*t));}}poly=out;if(!poly.length)break;}for(const v of poly)highest=Math.max(highest,v[2]);}return highest;}
  for(const side of ['left','right']){for(const k of ['leg','knee','ankle'])rot(id,'anim_'+k+'_'+side,X,0);root.updateWorldMatrix(true,true);const foot=parts.get(id+'/anim_ankle_'+side);if(!foot)continue;const bounds=[Infinity,-Infinity,Infinity,-Infinity];let low=Infinity;
   foot.traverse(m=>{if(!m.isMesh)return;const a=m.geometry.attributes.position;for(let i=0;i<a.count;i++){const p=new THREE.Vector3().fromBufferAttribute(a,i).applyMatrix4(m.matrixWorld);bounds[0]=Math.min(bounds[0],p.x);bounds[1]=Math.max(bounds[1],p.x);bounds[2]=Math.min(bounds[2],-p.z);bounds[3]=Math.max(bounds[3],-p.z);low=Math.min(low,p.y);}});
   let shift=highestUnder(bounds)+.014-low;if(!Number.isFinite(shift))shift=0;shift=Math.max(-.10,Math.min(.20,shift));targets[side]=foot.getWorldPosition(new THREE.Vector3()).add(new THREE.Vector3(0,shift,0));sum+=shift;
  }
  root.position.y+=sum/2-.045*weight;root.updateWorldMatrix(true,true);
  for(const[side,target]of Object.entries(targets)){const p=root.worldToLocal(target.clone()),dx=p.x-(side==='left'?-.1:.1),dy=-p.z+.01,dz=p.y-.49,roll=-Math.atan2(dx,-dz),zz=-Math.hypot(dx,dz),knee=Math.acos(Math.max(-1,Math.min(1,(dy*dy+zz*zz-.20*.20-.18*.18)/(2*.20*.18)))),hip=Math.atan2(dy,-zz)-Math.atan2(.18*Math.sin(knee),.20+.18*Math.cos(knee));rot(id,'anim_leg_'+side,Z,roll);parts.get(id+'/anim_leg_'+side).quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(X,hip));rot(id,'anim_knee_'+side,X,knee);rot(id,'anim_ankle_'+side,X,-hip-knee);parts.get(id+'/anim_ankle_'+side).quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(Z,-roll));}
 }
 function frame(s,dt){const active=[];for(const[id,r]of Object.entries(s.residentActions||{})){
  const root=entities.get(id),profile=PROFILES[id],a=s.actors.find(a=>a.id===id);if(!root)continue;resetElbows(id);
  const valid=r.action&&!s.eventGuests?.[id]?.active&&!(s.sceneEvent?.slots?.[id]!==undefined&&['gather','active'].includes(s.sceneEvent.phase))&&!['walk','yield','fold_umbrella'].includes(a?.mode)&&!(s.residents[id]?.umbrellaOpen>.08)&&(profile.role!=='diner'||s.diners[id].phase==='dine')&&(profile.role!=='cycle'||s.movers['bicycle.street_bicycle'].tripState==='parked');
  const def=RESIDENT_ACTIONS[r.action],clock=r.clock||0,duration=def?.duration||1,w=valid?ease(clock/.75)*ease((duration-clock)/.9)*(r.cancelRemaining>0?r.cancelRemaining/.65:1):0,beat=Math.sin(clock*3.7),slow=.5-.5*Math.cos(clock*2.3),pose=valid?def.pose:null;
  if(w>.02){active.push(id+'/'+r.action);observed.set(id+'/'+r.action,(observed.get(id+'/'+r.action)||0)+dt);}
  let readerCupHeld=false,readerCupTilt=0;
  const constrained=profile.role==='vendor'||id.startsWith('resident.water_'),amp=id==='resident.quiet_reader'?.45:constrained?.65:1;
  if(pose){
   if(pose==='wave'){arm(id,'right',-.22*w,-.64*w*amp,-(.55+.16*beat)*w);}
   if(pose==='talk'){arm(id,'right',-.16*w,-(.17+.10*slow)*w*amp,-(.4+.2*slow)*w);}
   if(pose==='stretch'){arm(id,'left',-.16*w,-.38*w,-.34*w);arm(id,'right',-.16*w,.38*w,-.34*w);}
   if(pose==='warm'||pose==='clap'){const k=pose==='clap'?.08*Math.sin(clock*8):.025*Math.sin(clock*11);arm(id,'left',-.18*w,-(.08+k)*w,-1.0*w);arm(id,'right',-.18*w,(.08+k)*w,-1.0*w);}
   if(pose==='sky'||pose==='shade'){arm(id,'right',-.30*w,-.20*w*amp,-1.3*w);rot(id,'anim_head',X,(id==='resident.station_traveler'&&s.passengers?.[id]?.phase!=='waiting'?0:['resident.porch_resident','resident.station_traveler'].includes(id)?-.12:-.46)*w);}
   if(pose==='sip'){arm(id,'right',-.24*w,-.03*w,-1.35*w);}
   if(pose==='eat'){arm(id,'right',-.20*w,.08*w,-1.1*w);}
   if(pose==='offer'){arm(id,'left',-.18*w,-.18*w,-.70*w);arm(id,'right',-.08*w,-.18*w,-.30*w);}
   if(pose==='wipe'){arm(id,'right',-.16*w,(-.15+.16*Math.sin(clock*3))*w,-.52*w);}
   if(pose==='cover'){arm(id,'right',-.16*w,-.12*w,-.7*w);arm(id,'left',-.16*w,.12*w,-.7*w);}
   if(pose==='inspect'){arm(id,'left',-.17*w,-.15*w,-.58*w);rot(id,'anim_head',X,.19*w);}
   if(pose==='read'){arm(id,'left',-.10*w,0,-.15*w);arm(id,'right',-.10*w,.08*w,-.68*w);rot(id,'anim_head',X,.16*w);}
   if(pose==='close'){arm(id,'left',.13*w,0,.10*w);arm(id,'right',.10*w,0,-.25*w);}
   if(pose==='letter'){const side='right';arm(id,side,-.10*w,0,-.95*w);rot(id,'anim_head',X,.12*w);}
   if(pose==='feed'){arm(id,'left',0,0,-.45*w);const toss=Math.max(0,Math.sin((clock-2.5)*Math.PI*1.3));arm(id,'right',-.10*toss*w,-.04*w,-(1.7-.20*toss)*w);}
   if(pose==='brush'){arm(id,'right',-.14*w,.10*w,-(.8+.17*beat)*w);}
   if(pose==='time'){arm(id,'left',-.12*w,-.08*w,-1.0*w);rot(id,'anim_head',X,.22*w);}
   if(pose==='signal'){arm(id,'right',-.18*w,-.7*w*amp,-.45*w);}
   if(pose==='tap'){for(const side of ['left','right']){const pulse=Math.max(0,Math.sin(clock*5+(side==='left'?0:Math.PI)))*w;if(parts.has(id+'/tap_foot_'+side))rot(id,'tap_foot_'+side,X,-pulse*.16);else{const v=legPose(0,sockets[id].scale[2],side,0,.018*pulse);rot(id,'anim_leg_'+side,X,v.hip);rot(id,'anim_knee_'+side,X,v.knee);rot(id,'anim_ankle_'+side,X,v.ankle);}}}
  }
  if(profile.role==='vendor'&&pose){const reach=pose==='wipe'?1.25:pose==='offer'?1.72:pose==='cover'?1.4:pose==='wave'?1.5:.65;arm(id,'right',0,-(.34+(pose==='wipe'?.035*Math.sin(clock*3):0))*w,-reach*w);if(['offer','cover'].includes(pose))arm(id,'left',0,.34*w,-1.72*w);}
  if(id==='resident.water_companion'&&pose){arm(id,'right',0,0,0);arm(id,'left',0,.10*w,-(['sky','shade'].includes(pose)?1.15:.55)*w);}
  if(pose&&profile.role!=='diner'&&profile.role!=='cycle'){
   let left=null,right=null;
   if(pose==='wave')right=[.34,1.01+.025*beat,.10];
   if(pose==='talk')right=[.30,.74+.035*slow,.24];
   if(pose==='stretch'){left=[-.36,.85,.04];right=[.36,.85,.04];}
   if(pose==='warm'||pose==='clap'){const spread=pose==='clap'?.075+.02*beat:.07;left=[-spread,.71,.27];right=[spread,.71,.27];}
   if(pose==='sky'||pose==='shade')right=[.24,1.04,.20];
   if(pose==='sip')right=[.10,.96,.24];
   if(pose==='eat')left=[-.09,.94,.25];
   if(pose==='offer')left=[-.46,.84,.27];
   if(pose==='wipe')right=[.45+.018*beat,.685,.265];
   if(pose==='cover'){left=[-.44,.81,.24];right=[.44,.81,.24];}
   if(pose==='inspect')left=[-.28,.73,.29];
   if(pose==='read'){left=[-.18,.55,.22];right=[.04,.65,.27];}
   if(pose==='close'){left=[-.18,.49,.22];right=[.10,.59,.24];}
   if(pose==='letter')right=[.20,.86,.24];
   if(pose==='feed'||pose==='pond'){left=[-.26,.73,.17];right=[.27,.91,.28+.025*beat];}
   if(pose==='brush')right=[.08,.78+.025*beat,.26];
   if(pose==='time')left=[-.09,.77,.26];
   if(pose==='signal')right=[.35,1.02,.10];
   if(profile.role==='vendor'){if(right&&!['wipe','cover'].includes(pose))right=[.45,.84+.015*beat,.20];if(left)left=[-.46,.84,.22];}
   if(id==='resident.waiting_passenger'&&pose==='signal'){left=right?[-right[0],right[1],right[2]]:left;right=null;arm(id,'right',0,0,0);}
   if(id==='resident.quiet_reader'&&pose==='sip'){
    const storage=new THREE.Vector3(...(sockets[id].cupStorage||[.30,.402,.02])),pickup=storage.clone().add(new THREE.Vector3(0,.03,0)),rest=new THREE.Vector3(.18,.53,.22),outside=new THREE.Vector3(.34,.53,.22),lifted=new THREE.Vector3(.34,.65,.24),mouth=new THREE.Vector3(.10,1.00,.245);let target;
    if(clock<.4)target=rest.clone().lerp(outside,ease(clock/.4));else if(clock<1.2)target=outside.clone().lerp(pickup,ease((clock-.4)/.8));else if(clock<2)target=pickup.clone().lerp(lifted,ease((clock-1.2)/.8));else if(clock<2.8)target=lifted.clone().lerp(mouth,ease((clock-2)/.8));else if(clock<4.5)target=mouth;else if(clock<5.3)target=mouth.clone().lerp(lifted,ease((clock-4.5)/.8));else if(clock<6.1)target=lifted.clone().lerp(pickup,ease((clock-5.3)/.8));else if(clock<6.7)target=pickup.clone().lerp(outside,ease((clock-6.1)/.6));else target=outside.clone().lerp(rest,ease((clock-6.7)/1.3));
    right=target.toArray();readerCupHeld=clock>=1.2&&clock<=6.1;readerCupTilt=-.18*ease((clock-2.8)/.4)*ease((4.5-clock)/.4);
   }
   if(id==='resident.quiet_reader'&&['wave','sky','shade'].includes(pose))right=[.22,.97,.20];
   if(id==='resident.gardener'&&pose!=='water'){left=right?[-.26,.88,.22]:left;right=null;arm(id,'right',0,0,0);}
   if(id==='resident.water_companion'){left=right?[-.25,.88,.22]:left;right=null;arm(id,'right',0,0,0);}
   if(id==='resident.kite_child')left=null;
   if(left)solveArm(id,'left',left,w);if(right)solveArm(id,'right',right,w);
  }
  if(!a&&!['cycle','diner'].includes(profile.role)){root.position.copy(roots.get(id).p);root.quaternion.copy(roots.get(id).q);}
  if(id==='resident.water_visitor'&&['feed','pond'].includes(pose)){const turn=ease((clock-.8)/1.3)*ease((duration-clock-1)/1.2);root.quaternion.copy(roots.get(id).q).premultiply(new THREE.Quaternion().setFromAxisAngle(Y,-3.03*turn));fitBridgeFeet(id,root,w);}
  if(!s.eventGuests?.[id]?.active&&(localRoutes?.[id]||id==='resident.water_visitor'&&!['feed','pond'].includes(pose)))for(const side of ['left','right'])for(const k of ['leg','knee','ankle']){const key=id+'/anim_'+k+'_'+side,p=parts.get(key),b=base.get(key);if(p&&b)p.quaternion.copy(b.q);}
  for(const side of ['left','right'])if(pose!=='tap')rot(id,'tap_foot_'+side,X,0);
  if(s.localWalkers?.[id]&&!s.eventGuests?.[id]?.active){const walker=s.localWalkers[id],p=walker.root,yaw=p[3];point.set(p[0],p[2],-p[1]);if(root.parent)root.parent.worldToLocal(point);root.position.copy(point);root.quaternion.copy(roots.get(id).q).premultiply(new THREE.Quaternion().setFromAxisAngle(Y,yaw-sockets[id].yaw));
   for(const side of ['left','right']){const[hip,knee,ankle,roll]=walker.legs[side];rot(id,'anim_leg_'+side,Z,roll);parts.get(id+'/anim_leg_'+side)?.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(X,hip));rot(id,'anim_knee_'+side,X,knee);rot(id,'anim_ankle_'+side,X,ankle);parts.get(id+'/anim_ankle_'+side)?.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(Z,-roll));if(walker.clip)arm(id,side,-.08-Math.sin(walker.clock*4+(side==='left'?0:Math.PI))*.025,side==='left'?-.18:.18,-.35);}
  }

  if(id==='resident.quiet_reader'&&book&&bookRest){const ownerQ=root.getWorldQuaternion(new THREE.Quaternion()),deltaQ=ownerQ.clone().multiply(bookRest.ownerQ.clone().invert()),offset=bookRest.offset.clone().multiply(root.getWorldScale(new THREE.Vector3())).applyQuaternion(ownerQ),position=handWorld(id,'left').add(offset);book.parent.updateWorldMatrix(true,false);book.position.copy(book.parent.worldToLocal(position));book.quaternion.copy(book.parent.getWorldQuaternion(new THREE.Quaternion()).invert().multiply(deltaQ.multiply(bookRest.q.clone())));}
  const page=parts.get('book.terrace_reader_book/turn_page');if(id==='resident.quiet_reader'&&page){const b=base.get('book.terrace_reader_book/turn_page');const turn=Math.min(3.02,3.02*(1-r.bookOpen)+(pose==='read'?Math.sin(Math.PI*ease((clock%3.5)/3.5))*2.8*w*r.bookOpen:0));page.quaternion.copy(b.q).multiply(new THREE.Quaternion().setFromAxisAngle(Z,-turn));const cover=parts.get('book.terrace_reader_book/close_cover'),cb=base.get('book.terrace_reader_book/close_cover');if(cover&&cb)cover.quaternion.copy(cb.q).multiply(new THREE.Quaternion().setFromAxisAngle(Z,-3.02*(1-r.bookOpen)));}
  if(id==='resident.water_companion'){const fold=parts.get('umbrella.carried_umbrella/fold_canopy'),b=base.get('umbrella.carried_umbrella/fold_canopy');if(fold&&b){fold.scale.copy(b.s);fold.scale.x*=.13+.87*r.umbrella;fold.scale.z*=.13+.87*r.umbrella;fold.scale.y*=1+.5*(1-r.umbrella);}}
  root.updateWorldMatrix(true,true);
  for(const key of ['cup','snack','cloth','feed_bag']){const obj=props.get(id+'/'+key);if(!obj)continue;const side=key==='feed_bag'||key==='snack'?'left':'right',hp=handWorld(id,side);obj.position.copy(toRoot(id,hp));obj.position.y+=key==='cloth'?.02:.055;if(key==='feed_bag')obj.position.x-=.045;if(key==='cup')obj.position.z+=.03;if(key==='snack')obj.position.x-=.13;if(key==='cloth')obj.position.x+=.055;obj.quaternion.identity();if(key==='cup')obj.rotation.x=pose==='sip'?-.18*w:0;
   // Reader's cup has a stable place on the bench; it travels continuously to and from the hand.
   if(id==='resident.quiet_reader'&&key==='cup'){const storage=new THREE.Vector3(...(sockets[id].cupStorage||[.30,.402,.02]));obj.position.copy(readerCupHeld?toRoot(id,handWorld(id,'right')).add(new THREE.Vector3(0,-.03,0)):storage);obj.rotation.x=readerCupTilt;}
  }
 }
 dinerView.frame(s);
 const feeder=s.residentActions?.['resident.water_visitor'];crumb.visible=s.weather!=='rain'&&feeder?.action==='feed_pond'&&feeder.clock>1&&feeder.clock<7.5;if(crumb.visible){const start=handWorld('resident.water_visitor','right'),target=s.pondFeeding?.target||[8.7,-1.6,.62];for(let i=0;i<8;i++){const f=((feeder.clock-1)*.52+i*.08)%1,end=new THREE.Vector3(target[0]+Math.sin(i*2.4)*.20,target[2],-target[1]+Math.cos(i*1.8)*.13);dummy.position.copy(start).lerp(end,f);dummy.position.y+=Math.sin(f*Math.PI)*.36;dummy.scale.setScalar(f>.92?(1-f)/.08:1);dummy.updateMatrix();crumb.setMatrixAt(i,dummy.matrix);}crumb.instanceMatrix.needsUpdate=true;}
 return active;
 }
 return{frame,props,observed:()=>Object.fromEntries(observed),handWorld};
}
