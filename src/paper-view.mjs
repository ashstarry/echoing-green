import * as THREE from 'three';
import {makeArmSolver} from './arm-ik.mjs?v=cp37-paper-c8fccf30daca';
import {handWorldPoint} from './prop-attachment.mjs?v=cp37-paper-c8fccf30daca';
import {interactionStep,INTERACTION_PRIMITIVES} from './interaction-sequence.mjs?v=cp37-paper-c8fccf30daca';
const ease=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
const palette=['#e1ba78','#99b8ad','#d5a1a5','#8faec5','#d6c6a0','#ad9dbd'];
export function createPaperView({scene,entities,parts,sockets}){
 const group=new THREE.Group();group.name='Reusable paper notes';group.userData.runtime_effect_id='effect.paper_notes';scene.add(group);
 const base=new Map([...parts].map(([id,o])=>[id,{p:o.position.clone(),q:o.quaternion.clone(),s:o.scale.clone()}])),solve=makeArmSolver({entities,parts,sockets,base}),objects=new Map(),pens=new Map();
 const paperGeo=new THREE.BoxGeometry(.25,.66,.009),flapGeo=new THREE.BoxGeometry(.25,.105,.009),ink=new THREE.MeshStandardMaterial({color:0x695947,roughness:1}),ropeMat=new THREE.LineBasicMaterial({color:0xb4a182}),penMat=new THREE.MeshStandardMaterial({color:0x73533c,roughness:1});
 let paperMap=null;scene.traverse(o=>{if(o.isMesh&&o.material?.name==='WEB paper'&&!paperMap)paperMap=o.material.map;});
 const materials=palette.map(color=>new THREE.MeshStandardMaterial({color,roughness:1,map:paperMap,side:THREE.DoubleSide}));
 const glyphMaterials={};for(const[key,glyph]of [['wish','願'],['heart','心']]){const canvas=document.createElement('canvas');canvas.width=128;canvas.height=256;const ctx=canvas.getContext('2d');ctx.fillStyle='#5f5143';ctx.textAlign='center';ctx.textBaseline='middle';ctx.font='90px "Yu Mincho", "Songti SC", "Noto Serif CJK JP", serif';ctx.fillText(glyph,64,100);ctx.globalAlpha=.65;ctx.fillRect(61,180,2,27);ctx.fillRect(72,187,2,17);const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;glyphMaterials[key]=new THREE.MeshBasicMaterial({map:texture,transparent:true,opacity:.76,depthWrite:false,side:THREE.DoubleSide});}
 const bamboo=[];const stemMaterial=new THREE.MeshStandardMaterial({color:0x72856f,roughness:1,map:paperMap}),leafMaterial=new THREE.MeshStandardMaterial({color:0x879981,roughness:1,side:THREE.DoubleSide});
 function support(station,anchor){if(bamboo[station])return bamboo[station];const groupStem=new THREE.Group();groupStem.name='paper-note-support-'+station;group.add(groupStem);const tree=new THREE.Vector3(-.2347,.78,.6956),tip=new THREE.Vector3(anchor[0],anchor[2]+.53,-anchor[1]),outward=new THREE.Vector3(tip.x-tree.x,0,tip.z-tree.z).normalize();const foot=tree.clone().addScaledVector(outward,1.05),bend=tree.clone().addScaledVector(outward,1.4);bend.y=2.32;tip.addScaledVector(outward,-.18);const curve=new THREE.CatmullRomCurve3([foot,bend,tip]);groupStem.add(new THREE.Mesh(new THREE.TubeGeometry(curve,6,.018,5,false),stemMaterial));
  for(let i=0;i<4;i++){const p=curve.getPoint(.55+i*.13),leaf=new THREE.BufferGeometry();const side=i%2?1:-1;leaf.setAttribute('position',new THREE.Float32BufferAttribute([0,0,0,side*.28,.03,.07,side*.12,.035,0,0,0,0,side*.12,.035,0,side*.28,-.02,-.03],3));leaf.computeVertexNormals();const m=new THREE.Mesh(leaf,leafMaterial);m.position.copy(p);m.rotation.y=i*.8;groupStem.add(m);}return bamboo[station]={group:groupStem,tip};}
 const tmp=new THREE.Vector3(),q=new THREE.Quaternion(),rotx=new THREE.Quaternion(),axis=new THREE.Vector3(1,0,0);
 function make(note){
  const root=new THREE.Group();root.userData.entity_id='paper.note.'+note.id;root.userData.paper_note_id=note.id;root.name=root.userData.entity_id;entities.set(root.userData.entity_id,root);group.add(root);
  const face=new THREE.Mesh(paperGeo,materials[note.color%palette.length]);face.position.y=-.3825;face.castShadow=true;root.add(face);
  const flap=new THREE.Group();flap.position.y=-.0525;const fold=new THREE.Mesh(flapGeo,materials[note.color%palette.length]);fold.position.y=.0525;fold.castShadow=true;flap.add(fold);root.add(flap);
  const knot=new THREE.Mesh(new THREE.SphereGeometry(.014,6,4),ink);knot.position.set(0,.012,0);root.add(knot);
  const strokes=new THREE.Group();root.add(strokes);
  const inkPlane=new THREE.Mesh(new THREE.PlaneGeometry(.18,.35),glyphMaterials[note.purpose==='paper_share'?'heart':'wish']);inkPlane.position.set(0,-.31,.006);strokes.add(inkPlane);

  const stringGeo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3()]);const string=new THREE.Line(stringGeo,ropeMat);group.add(string);const record={root,face,flap,strokes,string};objects.set(note.id,record);return record;
 }
 function pen(id){if(!pens.has(id)){const m=new THREE.Mesh(new THREE.CylinderGeometry(.007,.011,.14,6),penMat);m.castShadow=true;group.add(m);pens.set(id,m);}return pens.get(id);}
 function rootTarget(id,p){return entities.get(id).localToWorld(new THREE.Vector3(...p));}
 function head(id,pitch){const node=parts.get(id+'/anim_head'),b=base.get(id+'/anim_head');if(node&&b)node.quaternion.copy(b.q).multiply(new THREE.Quaternion().setFromAxisAngle(axis,pitch));}
 function pose(job,s){
  const step=interactionStep(job),action=job.cancelledPose||step?.action,clock=job.cancelledPose?job.cancelClock:job.clock,duration=INTERACTION_PRIMITIVES[action]?.seconds||1,weight=['approach','receive'].includes(action)?1:ease(clock/.4),actor=s.actors.find(a=>a.id===job.actor),note=s.paperWorld.notes.find(n=>n.id===job.prop),id=job.actor;
  if(!entities.has(id)||!actor)return;let left=null,right=null;
  if(note?.location==='hand'&&note.owner===id)left=[-.14,.73,.24];
  if(action==='take'){left=[-.15,.62+.16*ease(clock/.9),.23];right=[.10,.65,.18];}
  if(action==='write'){left=[-.13,.79,.27];right=[.07+Math.sin(clock*7)*.035,.815,.30+Math.cos(clock*4)*.025];head(id,.24);}
  if(action==='fold'){const u=ease(clock/duration);left=[-.13+.05*u,.80,.27];right=[.13-.07*u,.80+.03*Math.sin(clock*3),.30];head(id,.18);}
  if(action==='read'||action==='receive'){left=[-.12,.86,.28];right=[.12,.86,.27];head(id,.14);}
  if(action==='hang'||action==='collect'){
   const p=job.context.anchor,world=new THREE.Vector3(p[0],p[2],-p[1]),local=entities.get(id).worldToLocal(world);const lift=ease(clock/1.25);if(action==='collect'){left=[-.14,.73,.24];right=new THREE.Vector3(.14,.73,.24).lerp(local,lift).toArray();}else{left=new THREE.Vector3(-.14,.73,.24).lerp(local,lift).toArray();right=[local.x+.05,local.y-.035,local.z];}head(id,-.08);
  }
  if(action==='offer'){left=[-.10,.82,.35];right=[.15,.79,.29];head(id,.10);}
  if(action==='stow'){left=[-.14,.78-.25*ease(clock/1.4),.22];right=[.12,.62-.13*ease(clock/1.4),.20];head(id,.10);}
  if(left)solve(id,'left',left,weight);if(right)solve(id,'right',right,weight);
  const brush=pen(id);brush.visible=action==='write';if(brush.visible){handWorldPoint({entities,parts,sockets},id,'right',brush.position);brush.position.y-=.035;brush.quaternion.copy(entities.get(id).getWorldQuaternion(q)).multiply(new THREE.Quaternion().setFromAxisAngle(axis,.35));}
 }
 return{group,ids:['effect.paper_notes'],frame(s){
  const world=s.paperWorld;if(!world){group.visible=false;return;}group.visible=true;for(const p of pens.values())p.visible=false;
  const jobs=world.jobs.filter(j=>j.status==='running');for(const j of jobs)pose(j,s);
  for(const note of world.notes){const o=objects.get(note.id)||make(note),job=jobs.find(j=>(j.prop===note.id||j.context.oldNote===note.id)&&j.actor===note.owner),step=interactionStep(job),rawAction=job?.cancelledPose||step?.action,action=['collect','stow'].includes(rawAction)&&!job?.cancelledPose&&!['receive_note','collect_note'].includes(job?.recipe)&&job?.context.oldNote!==note.id?'carry':rawAction,clock=job?.cancelledPose?job.cancelClock:job?.clock||0;
   o.root.visible=note.location!=='archived'&&(note.location!=='supply'||action==='take');o.string.visible=note.location==='anchor';o.root.userData.owner_entity=note.owner;o.root.userData.paper_location=note.location;if(!o.root.visible)continue;
   let fold=note.stage==='folded'?1:0;if(action==='fold')fold=ease(clock/2.1);if(action==='write')fold=0;if(action==='read'||action==='receive')fold=1-ease(clock/.6);
   o.flap.rotation.x=-fold*1.2;o.strokes.visible=note.stage!=='blank'||action==='write'&&clock>.3;o.strokes.scale.y=action==='write'?Math.max(.05,ease(clock/4.5)):1;
   const owner=entities.get(note.owner);o.root.scale.setScalar(1);
   if(note.location==='anchor'){
    const p=note.anchor;o.root.position.set(p[0],p[2],-p[1]);o.root.rotation.set(Math.sin(s.time*1.25+note.color)*.065*s.windSpeed/.35,.18+Math.sin(s.time*.65+note.color)*.06,Math.sin(s.time*.8+note.color)*.035);
    o.flap.rotation.x=-.12;const direction=new THREE.Vector3(-.2347-p[0],0,-(-.6956)-(-p[1])).normalize();const top=support(note.station,p).tip;const a=o.string.geometry.attributes.position;a.setXYZ(0,top.x,top.y,top.z);a.setXYZ(1,p[0],p[2]+.025,-p[1]);a.needsUpdate=true;o.string.geometry.computeBoundingSphere();
   }else if(owner){
    owner.updateWorldMatrix(true,true);let pos=handWorldPoint({entities,parts,sockets},note.owner,note.side||'left',tmp).clone();q.copy(owner.getWorldQuaternion(new THREE.Quaternion()));
    if(note.location==='pocket'){pos=rootTarget(note.owner,[-.12,.64,.19]);o.root.scale.set(.44,.34,.7);o.root.quaternion.copy(q);}
    else{
     const writing=['take','write','fold','read','receive','offer'].includes(action);o.root.quaternion.copy(q).multiply(rotx.setFromAxisAngle(axis,writing?-1.14:-.15));
     if(action==='take'){const u=ease((clock-.2)/.85);pos=rootTarget(note.owner,[-.12,.54,.18]).lerp(pos,u);o.root.scale.setScalar(.30+.70*u);}
     if(action==='stow'){o.root.quaternion.copy(q).multiply(rotx.setFromAxisAngle(axis,-1.14*(1-ease(clock/1.6))));pos.lerp(rootTarget(note.owner,[-.12,.64,.19]),ease(clock/1.6));o.root.scale.set(1-.56*ease(clock/1.6),1-.66*ease(clock/1.6),1);}
     if(action==='hang'){const p=job.context.anchor,u=ease((clock-1.65)/1.05);pos.lerp(new THREE.Vector3(p[0],p[2],-p[1]),u);o.root.quaternion.slerp(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),.18),u);}
     if(action==='offer'&&job.context.recipient){const other=handWorldPoint({entities,parts,sockets},job.context.recipient,'left',new THREE.Vector3());const u=ease((clock-.8)/1.5);pos.lerp(other,u);o.root.quaternion.slerp(entities.get(job.context.recipient).getWorldQuaternion(new THREE.Quaternion()).multiply(new THREE.Quaternion().setFromAxisAngle(axis,-1.14)),u);}
    }
    o.root.position.copy(pos);
   }
  }
  const keep=new Set(world.notes.map(n=>n.id));for(const[id,o]of objects)if(!keep.has(id)){group.remove(o.root,o.string);entities.delete(o.root.userData.entity_id);objects.delete(id);o.string.geometry.dispose();}
 },snapshot:()=>({notes:objects.size,sharedHandBinding:true,bindings:[...objects.values()].map(o=>({id:o.root.userData.entity_id,owner:o.root.userData.owner_entity,location:o.root.userData.paper_location}))})};
}
