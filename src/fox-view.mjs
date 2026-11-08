import * as THREE from 'three';
import {createPavingSupport} from './foot-support.mjs?v=cp51-vibe-response-d7c8487e50b4';
import {refineFoxModel} from './fox-model.mjs?v=cp51-vibe-response-d7c8487e50b4';
import {foxPose} from './fox-behavior.mjs?v=cp51-vibe-response-d7c8487e50b4';
const PITCH=new THREE.Vector3(0,0,-1),UP=new THREE.Vector3(0,1,0);
// Four joined, flat-shaded paper folds replace the single rigid triangular tail.
// Each next segment is attached at its predecessor's end, so bends never tear.
export function paperTail(pivot,sourceMaterial){
 if(!pivot)return[];for(const child of pivot.children)child.visible=false;
 const orange=sourceMaterial?.clone()||new THREE.MeshStandardMaterial({color:0xb9672d,roughness:1});orange.vertexColors=false;orange.color.set(0xc47438);orange.flatShading=true;
 const cream=orange.clone();cream.color.set(0xf0d3a0);
 const lengths=[.15,.17,.17,.14],radii=[.043,.085,.105,.067,.012],joints=[];let parent=pivot;
 for(let i=0;i<4;i++){
  const joint=new THREE.Group();joint.name='paper-tail-fold-'+i;parent.add(joint);if(i)joint.position.x=lengths[i-1];
  const g=new THREE.CylinderGeometry(radii[i+1],radii[i],lengths[i],5,1,false);g.rotateZ(-Math.PI/2);g.translate(lengths[i]/2,0,0);g.computeVertexNormals();
  const mesh=new THREE.Mesh(g,i===3?cream:orange);mesh.castShadow=true;mesh.receiveShadow=true;joint.add(mesh);joints.push(joint);parent=joint;
 }
 return joints;
}
export function createFoxView({entities,parts,nav}){
 const id='animal.garden_fox',root=entities.get(id),model=refineFoxModel(root,parts),base=new Map([...parts].filter(([k])=>k.startsWith(id+'/')).map(([k,p])=>[k,{q:p.quaternion.clone(),p:p.position.clone()}]));
 const tail=parts.get(id+'/tail');let sourceMaterial;tail?.traverse(o=>{if(o.isMesh&&!sourceMaterial)sourceMaterial=Array.isArray(o.material)?o.material[0]:o.material;});const folds=paperTail(tail,sourceMaterial);
 function rotate(name,axis,angle){const p=parts.get(id+'/'+name),b=base.get(id+'/'+name);if(p&&b)p.quaternion.copy(b.q).multiply(new THREE.Quaternion().setFromAxisAngle(axis,angle));}
 const paving=createPavingSupport(nav?.activities?.paving),solePoints=new Map(),box=new THREE.Box3(),pieceBox=new THREE.Box3();
 for(let leg=0;leg<4;leg++){
  const node=parts.get(id+'/leg_'+leg);if(!node)continue;node.updateWorldMatrix(true,true);const inverse=node.matrixWorld.clone().invert();box.makeEmpty();
  node.traverse(o=>{if(!o.isMesh)return;if(!o.geometry.boundingBox)o.geometry.computeBoundingBox();pieceBox.copy(o.geometry.boundingBox).applyMatrix4(inverse.clone().multiply(o.matrixWorld));box.union(pieceBox);});
  if(!box.isEmpty())solePoints.set(leg,[new THREE.Vector3(box.min.x,box.min.y,box.min.z),new THREE.Vector3(box.max.x,box.min.y,box.min.z),new THREE.Vector3(box.min.x,box.min.y,box.max.z),new THREE.Vector3(box.max.x,box.min.y,box.max.z)]);
 }
 let gaitWeight=0;let lastLegs=[];let locomoting=false;
 const displayed={headPitch:0,headTurn:0,tail:0,front:0,back:0,lift:0,paw:0,groom:0};
 return{frame(s,dt=1/60){if(!root)return;const target=foxPose(s),alpha=1-Math.exp(-Math.min(.1,Math.max(0,dt))*9);for(const key of Object.keys(displayed))displayed[key]+=((target[key]||0)-displayed[key])*alpha;const p=displayed,m=s.movers?.[id],f=s.foxBehavior;
 // One final owner for the four legs. A fading grooming/paw pose must never
 // replace a travelling fox's gait with its rest transforms.
 locomoting=!!m&&m.speed>.02&&(f?.phase==='walk'||f?.suspended&&s.musicCircle?.phase==='approach');
 const wanted=locomoting?Math.min(1,m.strideWeight??1):0;gaitWeight+=(wanted-gaitWeight)*alpha;if(gaitWeight<.00001)gaitWeight=0;
 const phase=(m?.distance||0)*15.5,amplitude=.34+.07*Math.min(1,(m?.speed||0)*.52/.55),poses=locomoting?[0,0,0,0]:[p.front+p.paw,p.back,p.front+p.paw*.90,p.back];lastLegs=[];
 for(let leg=0;leg<4;leg++){
  const name='leg_'+leg,node=parts.get(id+'/'+name),rest=base.get(id+'/'+name),cycle=phase+(leg===0||leg===3?0:Math.PI),step=Math.sin(cycle)*amplitude*gaitWeight,gesture=poses[leg]*(1-Math.min(1,gaitWeight));
  const knee=model?.knees.get(leg);if(knee)knee.rotation.z=-Math.max(0,Math.sin(cycle))*.26*gaitWeight;rotate(name,PITCH,step+gesture);if(!locomoting&&f?.phase==='greet'&&(leg===0||leg===2)&&node)node.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(UP,p.headTurn*.45));const swing=.045*Math.max(0,Math.sin(cycle))*gaitWeight;let soleY=null,floorY=null;
  if(node&&rest){node.position.copy(rest.p);const sole=solePoints.get(leg);
   if(sole&&(locomoting||gaitWeight>.05)){
    node.updateWorldMatrix(true,false);const pts=sole.map(p=>node.localToWorld(p.clone())),wx=pts.reduce((v,p)=>v+p.x,0)/pts.length,wz=pts.reduce((v,p)=>v+p.z,0)/pts.length;
    const support=paving?.highest([wx-.07,wx+.07,-wz-.07,-wz+.07]);const expected=(m?.p?.[2]??root.getWorldPosition(new THREE.Vector3()).y)+.03;floorY=support!==null&&support!==undefined&&Math.abs(support-expected)<.18?support:expected;soleY=Math.min(...pts.map(p=>p.y));
    const scale=node.parent?.getWorldScale(new THREE.Vector3()).y||1;node.position.y+=(floorY+.008+swing-soleY)/scale;soleY=floorY+.008+swing;
   }else node.position.y+=swing;
  }
  lastLegs.push({angle:step+gesture,lift:swing,soleY,floorY});
 }
 const cuddle=!locomoting&&f?.phase==='greet'?Math.sin(Math.PI*Math.max(0,Math.min(1,(f.clock-.65)/3.9))):0;if(model){model.torso.rotation.z=-cuddle*.27;model.torso.position.y=.445-cuddle*.025;}const headNode=parts.get(id+'/head'),headBase=base.get(id+'/head');if(headNode&&headBase){headNode.position.copy(headBase.p);headNode.position.x-=cuddle*.045;headNode.position.y+=cuddle*.09;}
 if(f?.suspended&&s.musicCircle?.phase!=='listen')return;
 if(cuddle>0&&f?.neighbor){for(const [part,angle]of[['anim_head',.24],['anim_torso',.08],['anim_arm_right',-.34]]){const node=parts.get(f.neighbor+'/'+part);if(node)node.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1,0,0),cuddle*angle));}}
 rotate('head',PITCH,-p.headPitch);parts.get(id+'/head')?.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(UP,p.headTurn));rotate('tail',UP,p.tail*.55);
 for(const[i,joint]of folds.entries()){joint.rotation.set(0,p.tail*(.30+i*.10)+Math.sin(s.time*4.2-i*.65)*Math.abs(p.tail)*.15,([.12,.16,-.12,-.19][i])+Math.sin(s.time*2.4-i*.5)*.035);}
 // Only the stationary play bounce may lift the root; walking and the
 // one-paw greeting keep the body supported by the other feet.
 if(!locomoting&&f?.phase==='play'&&p.lift){const v=root.getWorldPosition(new THREE.Vector3());v.y+=p.lift;if(root.parent)root.parent.worldToLocal(v);root.position.copy(v);}
 },snapshot:()=>({legModel:model?{length:model.legLength,knees:model.knees.size}:null,tailFolds:folds.length,foldAngles:folds.map(j=>j.rotation.y),pose:{...displayed},walking:locomoting,gaitWeight,legs:lastLegs.map(x=>({...x})),renderedJoints:Array.from({length:4},(_,i)=>{const node=parts.get(id+'/leg_'+i);if(!node)return null;node.updateWorldMatrix(true,false);const ys=solePoints.get(i)?.map(p=>node.localToWorld(p.clone()).y);return {quaternion:node.quaternion.toArray(),position:node.position.toArray(),soleY:ys?Math.min(...ys):null};})})};
}
