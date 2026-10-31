import * as THREE from 'three';
import {makeArmSolver} from './arm-ik.mjs?v=cp39-neighborhood-18b2d8344ad8';
import {handWorldPoint} from './prop-attachment.mjs?v=cp39-neighborhood-18b2d8344ad8';
import {interactionStep,INTERACTION_PRIMITIVES} from './interaction-sequence.mjs?v=cp39-neighborhood-18b2d8344ad8';
import {HOME} from './neighborhood-world.mjs?v=cp39-neighborhood-18b2d8344ad8';
const ease=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
export function createNeighborhoodView({scene,entities,parts,sockets}){
 const group=new THREE.Group();group.name='Neighborhood reusable props';group.userData.runtime_effect_id='effect.neighborhood_work';scene.add(group);
 const base=new Map([...parts].map(([id,o])=>[id,{p:o.position.clone(),q:o.quaternion.clone(),s:o.scale.clone()}])),solve=makeArmSolver({entities,parts,sockets,base}),objects=new Map(),cloths=new Map();
 let texture=null;scene.traverse(o=>{if(o.isMesh&&o.material?.name==='WEB paper'&&!texture)texture=o.material.map;});
 const material=(color,extra={})=>new THREE.MeshStandardMaterial({color,roughness:.96,map:texture,...extra});
 const mats={wood:material('#95673c'),ink:material('#5e5345'),cream:material('#e8d7ae'),red:material('#b05a4e'),sage:material('#9daa82'),pink:material('#dda2a4',{side:THREE.DoubleSide}),blue:material('#95aab8'),amber:material('#f1ba67',{emissive:'#de8e35',emissiveIntensity:.25}),leaf:material('#809b78')};
 const handleGeo=new THREE.TorusGeometry(.115,.008,4,12,Math.PI);
 const cube=new THREE.BoxGeometry(1,1,1),disc=new THREE.CylinderGeometry(1,1,1,10),ball=new THREE.IcosahedronGeometry(1,0);
 function box(g,x,y,z,w,h,d,mat){const m=new THREE.Mesh(cube,mat);m.position.set(x,y,z);m.scale.set(w,h,d);m.castShadow=true;m.receiveShadow=true;g.add(m);return m;}
 function round(g,x,y,z,r,h,mat){const m=new THREE.Mesh(disc,mat);m.position.set(x,y,z);m.scale.set(r,h,r);m.castShadow=true;g.add(m);return m;}
 function flower(parent,x,y,z,index=0){const f=new THREE.Group();f.position.set(x,y,z);parent.add(f);box(f,0,.16,0,.025,.32,.025,mats.leaf);const petals=[];for(let j=0;j<5;j++){const pivot=new THREE.Group();pivot.position.y=.33;pivot.rotation.y=j*Math.PI*2/5;f.add(pivot);const petal=new THREE.Mesh(ball,index%2?mats.cream:mats.pink);petal.position.set(0,.035,.14);petal.scale.set(.115,.025,.19);pivot.add(petal);petals.push(pivot);}round(f,0,.35,0,.055,.04,mats.amber);return petals;}
 function createProp(p){const root=new THREE.Group();root.name='prop.'+p.id;root.userData.entity_id='prop.'+p.id;root.userData.owner_entity=p.owner;root.userData.runtime_effect_id='prop.'+p.id;group.add(root);entities.set(root.userData.entity_id,root);let petals=[];
  if(p.type==='tray'||p.type==='crate'){
   box(root,0,.055,0,.66,.07,.42,mats.wood);for(const z of[-.22,.22])box(root,0,.11,z,.69,.07,.025,mats.wood);
   for(let j=0;j<6;j++){const x=(j%3-1)*.18,z=j<3?-.1:.1;round(root,x,.105,z,.077,.018,mats.cream);const bun=new THREE.Mesh(ball,j%3===0?mats.pink:mats.cream);bun.scale.set(.055,.043,.052);bun.position.set(x,.15,z);root.add(bun);}
   if(p.type==='crate')for(const x of[-.35,.35])box(root,x,.14,0,.035,.20,.44,mats.wood);
  }else if(p.type==='stool'||p.type==='bench'){
   const width=p.type==='bench'?.92:.52;box(root,0,.35,0,width,.08,.40,mats.wood);for(const x of[-width*.38,width*.38])for(const z of[-.13,.13])box(root,x,.17,z,.06,.34,.06,mats.wood);if(p.type==='bench')for(let j=0;j<2;j++)box(root,0,.53+j*.11,-.17,width,.065,.035,mats.wood);
  }else if(p.type==='lantern'){
   round(root,0,.25,0,.18,.38,mats.amber);for(const y of[.055,.445])round(root,0,y,0,.16,.025,mats.wood);for(let j=0;j<8;j++){const a=j*Math.PI/4;box(root,Math.sin(a)*.175,.25,Math.cos(a)*.175,.008,.37,.008,mats.cream);}const h=new THREE.Mesh(handleGeo,mats.wood);h.position.y=.445;root.add(h);
  }else if(p.type==='flowerpot'){
   round(root,0,.13,0,.19,.24,mats.red);round(root,0,.26,0,.205,.045,mats.wood);for(let j=0;j<3;j++)petals.push(...flower(root,(j-1)*.13,.22,(j%2)*.1,j));
  }else if(p.type==='parcel'){box(root,0,.15,0,.32,.28,.25,mats.blue);box(root,0,.294,0,.035,.012,.26,mats.cream);box(root,0,.15,.128,.035,.28,.01,mats.cream);}else box(root,0,.01,0,.27,.012,.24,mats.blue);
  const o={root,petals};objects.set(p.id,o);return o;
 }
 // A small double sliding door fits the existing postal-home facade gap.
 const doorway=new THREE.Group();doorway.name='postal_home_welcome_door';doorway.userData.runtime_effect_id='component.home_welcome_door';doorway.userData.entity_id='component.home_welcome_door';entities.set('component.home_welcome_door',doorway);doorway.position.set(HOME.door[0],HOME.door[2],-HOME.door[1]);doorway.rotation.y=HOME.yaw;scene.add(doorway);
 const recess=material('#473b31',{emissive:'#b56d2e',emissiveIntensity:.04});box(doorway,0,.59,-.015,.54,1.20,.045,recess);const leaves=[];
 for(const side of[-1,1]){const leaf=new THREE.Group();leaf.position.x=side*.135;doorway.add(leaf);box(leaf,0,.60,.018,.258,1.18,.035,mats.wood);box(leaf,0,.75,.040,.19,.70,.008,mats.cream);for(const y of[.46,.66,.86,1.06])box(leaf,0,y,.049,.21,.018,.012,mats.wood);box(leaf,0,.75,.05,.018,.70,.013,mats.wood);leaves.push({leaf,side});}for(const x of[-.285,.285])box(doorway,x,.60,.035,.035,1.26,.065,mats.wood);box(doorway,0,1.23,.035,.61,.04,.08,mats.wood);
 const windowMaterial=material('#d39d5a',{emissive:'#f2a142',emissiveIntensity:.1,transparent:true,opacity:.22,depthWrite:false});const window=new THREE.Mesh(new THREE.PlaneGeometry(.67,.85),windowMaterial);window.position.set(-5.415,1.465,1.435);window.rotation.y=25*Math.PI/180;scene.add(window);
 const porchLamp=new THREE.Group();porchLamp.position.set(HOME.door[0]+.35,HOME.door[2]+1.12,-HOME.door[1]+.14);scene.add(porchLamp);round(porchLamp,0,0,0,.09,.21,mats.amber);round(porchLamp,0,.115,0,.105,.018,mats.wood);
 const borders=[];for(const [i,p]of [[-7.0,-2.75],[5.8,1.25],[6.6,2.7],[3.5,6.8]].entries())for(let j=0;j<3;j++)borders.push(...flower(group,p[0]+j*.16,.67,-p[1],i+j));
 const axis=new THREE.Vector3(1,0,0),temp=new THREE.Vector3(),q=new THREE.Quaternion();
 function head(id,pitch){const n=parts.get(id+'/anim_head'),b=base.get(id+'/anim_head');if(n&&b)n.quaternion.copy(b.q).multiply(q.setFromAxisAngle(axis,pitch));}
 function pose(j,s){const a=s.actors.find(a=>a.id===j.actor);if(!a)return;const step=interactionStep(j),action=j.cancelledPose||step?.action,c=j.cancelledPose?j.cancelClock:j.clock,p=s.neighborhoodWorld.props.find(p=>p.id===j.prop),id=j.actor;const duration=INTERACTION_PRIMITIVES[action]?.seconds||1,weight=['approach','carry','wait_for'].includes(action)?1:ease(c/.35);let left=null,right=null;
  if(p?.location==='hand'&&p.owner===id){left=[-.19,.72,.28];right=[.19,.72,.28];}
  if(['take','place','pack','stow','unfold'].includes(action)){const u=action==='take'?1-ease(c/duration):ease(c/duration);left=[-.18,.74-u*.25,.30+u*.12];right=[.18,.74-u*.25,.30+u*.12];head(id,.18*u);}
  if(action==='wipe'){left=[-.18,.54,.35];right=[.10+Math.sin(c*5)*.16,.55,.42];head(id,.2);}
  if(action==='open'){right=[.24,.79,.43];head(id,.10);}
  if(action==='welcome'){left=[-.20,.74,.25];right=[.27,.95+Math.sin(c*4)*.05,.22];head(id,.10*Math.sin(c*1.3));}
  if(action==='offer'||action==='receive'){left=[-.17,.79,.40];right=[.17,.79,.40];head(id,.12);}
  if(action==='admire'){left=[-.17,.65,.25];right=[.20,.78,.25];head(id,-.1);}
  if(left)solve(id,'left',left,weight);if(right)solve(id,'right',right,weight);
  let cloth=cloths.get(id);if(!cloth){cloth=new THREE.Mesh(cube,mats.blue);cloth.scale.set(.22,.01,.18);group.add(cloth);cloths.set(id,cloth);}cloth.visible=action==='wipe';if(cloth.visible){handWorldPoint({entities,parts,sockets},id,'right',cloth.position);cloth.quaternion.copy(entities.get(id).getWorldQuaternion(q));}
 }
 return{group,ids:['effect.neighborhood_work','component.home_welcome_door'],frame(s){const w=s.neighborhoodWorld;if(!w)return;for(const c of cloths.values())c.visible=false;for(const j of w.jobs.filter(j=>j.status==='running'))pose(j,s);
  for(const p of w.props){const o=objects.get(p.id)||createProp(p),job=w.jobs.find(j=>j.prop===p.id&&j.actor===p.owner&&j.status==='running'),action=job?.cancelledPose||interactionStep(job)?.action,clock=job?.cancelledPose?job.cancelClock:job?.clock||0;const root=o.root;root.userData.owner_entity=p.owner;root.visible=p.location!=='stored'&&(p.location!=='supply'||action==='take');if(!root.visible)continue;const fade=p.retireAt?1-ease((s.time-p.retireAt)/4):1;root.visible=fade>.005;root.scale.setScalar(fade);root.quaternion.identity();
   if(p.location==='placed'){root.position.set(p.anchor[0],p.anchor[2],-p.anchor[1]);root.rotation.y=.18;}
   else{const owner=entities.get(p.owner);if(!owner)continue;handWorldPoint({entities,parts,sockets},p.owner,p.type==='lantern'?'right':'left',temp);const other=handWorldPoint({entities,parts,sockets},p.owner,'right',new THREE.Vector3());if(p.type!=='lantern')temp.add(other).multiplyScalar(.5);temp.y-=p.type==='lantern'?.50:p.type==='stool'?.28:.08;root.position.copy(temp);root.quaternion.copy(owner.getWorldQuaternion(q));if(action==='take')root.scale.multiplyScalar(.4+.6*ease(clock/1.2));if(action==='place'){const dest=new THREE.Vector3(...[job.context.anchor[0],job.context.anchor[2],-job.context.anchor[1]]);root.position.lerp(dest,ease(clock/2.4));}if(action==='offer'&&job.context.partner){const target=handWorldPoint({entities,parts,sockets},job.context.partner,'right',new THREE.Vector3());target.y-=.5;root.position.lerp(target,ease((clock-.8)/2.2));}if(['pack','stow'].includes(action))root.scale.multiplyScalar(1-ease(clock/(INTERACTION_PRIMITIVES[action]?.seconds||2.5)));}
   const open=action==='unfold'?ease(clock/3.2):p.unfold?1:.05;for(const petal of o.petals)petal.rotation.x=-1.22*(1-open)+Math.sin(s.time*1.2+petal.rotation.y)*.04*open;
  }
  for(const [id,o]of objects)if(!w.props.some(p=>p.id===id)){group.remove(o.root);entities.delete(o.root.userData.entity_id);objects.delete(id);}
  for(const {leaf,side}of leaves)leaf.position.x=side*(.135+w.door*.23);recess.emissiveIntensity=.04+w.window*.32;windowMaterial.opacity=.10+w.window*.24;windowMaterial.emissiveIntensity=.10+w.window*.38;porchLamp.scale.setScalar(.85+w.window*.15);
  for(const petal of borders){petal.parent.visible=w.bloom>.015;petal.rotation.x=-1.22*(1-w.bloom)+Math.sin(s.time*1.25+petal.rotation.y)*.06*w.bloom;}
 },snapshot:()=>({props:objects.size,doorway:true})};
}
