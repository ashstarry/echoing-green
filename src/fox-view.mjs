import * as THREE from 'three';
import {foxPose} from './fox-behavior.mjs?v=cp47-expressive-life-7673d851eb71';
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
export function createFoxView({entities,parts}){
 const id='animal.garden_fox',root=entities.get(id),base=new Map([...parts].filter(([k])=>k.startsWith(id+'/')).map(([k,p])=>[k,p.quaternion.clone()]));
 const tail=parts.get(id+'/tail');let sourceMaterial;tail?.traverse(o=>{if(o.isMesh&&!sourceMaterial)sourceMaterial=Array.isArray(o.material)?o.material[0]:o.material;});const folds=paperTail(tail,sourceMaterial);
 function rotate(name,axis,angle){const p=parts.get(id+'/'+name),b=base.get(id+'/'+name);if(p&&b)p.quaternion.copy(b).multiply(new THREE.Quaternion().setFromAxisAngle(axis,angle));}
 const displayed={headPitch:0,headTurn:0,tail:0,front:0,back:0,lift:0,paw:0,groom:0};
 return{frame(s,dt=1/60){if(!root)return;const target=foxPose(s),alpha=1-Math.exp(-Math.min(.1,Math.max(0,dt))*9);for(const key of Object.keys(displayed))displayed[key]+=((target[key]||0)-displayed[key])*alpha;const p=displayed;if(s.foxBehavior?.suspended&&s.musicCircle?.phase!=='listen')return;
 rotate('head',PITCH,-p.headPitch);parts.get(id+'/head')?.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(UP,p.headTurn));rotate('tail',UP,p.tail*.55);
 for(const[i,joint]of folds.entries()){joint.rotation.set(0,p.tail*(.30+i*.10)+Math.sin(s.time*4.2-i*.65)*Math.abs(p.tail)*.15,([.12,.16,-.12,-.19][i])+Math.sin(s.time*2.4-i*.5)*.035);}
 // A clear one-paw greeting; the other three feet remain planted.
 if(p.front||p.paw||p.groom){rotate('leg_0',PITCH,p.front+p.paw);rotate('leg_2',PITCH,p.front);for(const i of[1,3])rotate('leg_'+i,PITCH,p.back);}
 if(p.lift){const v=root.getWorldPosition(new THREE.Vector3());v.y+=p.lift;if(root.parent)root.parent.worldToLocal(v);root.position.copy(v);}
 },snapshot:()=>({tailFolds:folds.length,foldAngles:folds.map(j=>j.rotation.y),pose:{...displayed}})};
}
