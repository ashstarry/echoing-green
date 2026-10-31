import * as THREE from 'three';
import {createResponseSignals,responseGlowAlpha,GLOW_SECONDS,MAX_GLOWS} from './response-signals.mjs?v=cp38-response-b8cecd6027c5';
const supported=new Set(['animal','duck','fish','boat','bicycle','parked_bicycle','tram','windmill','door','plant','tree','water_lantern']);
export function createResponseMarkers({scene,entities,parts=new Map(),registry={entities:[]},nav}){
 const signals=createResponseSignals(),marks=new Map(),rows=new Map(registry.entities.map(e=>[e.id,e])),anchors=new Map();
 const geo=new THREE.PlaneGeometry(1,1);geo.rotateX(-Math.PI/2);
 const alphas=new THREE.InstancedBufferAttribute(new Float32Array(MAX_GLOWS),1),seeds=new THREE.InstancedBufferAttribute(Float32Array.from({length:MAX_GLOWS},(_,i)=>i*2.399),1);geo.setAttribute('markAlpha',alphas);geo.setAttribute('markSeed',seeds);
 const material=new THREE.ShaderMaterial({transparent:true,depthWrite:false,depthTest:true,toneMapped:false,side:THREE.DoubleSide,vertexShader:'attribute float markAlpha;attribute float markSeed;varying vec2 vUv;varying float vAlpha;varying float vSeed;void main(){vUv=uv;vAlpha=markAlpha;vSeed=markSeed;gl_Position=projectionMatrix*modelViewMatrix*instanceMatrix*vec4(position,1.0);}',fragmentShader:'varying vec2 vUv;varying float vAlpha;varying float vSeed;void main(){vec2 p=vUv-.5;float a=atan(p.y,p.x);float r=length(p);float rim=.345+.005*sin(a*3.+vSeed)+.003*sin(a*7.-vSeed);float band=exp(-pow((r-rim)/.024,2.));float wash=exp(-r*r*23.)*.10;float opacity=(band*.9+wash)*vAlpha;if(opacity<.001)discard;gl_FragColor=vec4(.84,.57,.28,opacity);}'});
 const mesh=new THREE.InstancedMesh(geo,material,MAX_GLOWS);mesh.name='Soft washi response at ground contact';mesh.userData.runtime_effect_id='effect.wish_foot_ring';mesh.frustumCulled=false;mesh.renderOrder=2;mesh.visible=false;scene.add(mesh);
 const point=new THREE.Vector3(),size=new THREE.Vector3(),dummy=new THREE.Object3D(),box=new THREE.Box3(),partBox=new THREE.Box3();
 function resolve(id,s){if(id?.startsWith('resident.'))return entities.has(id)?id:null;const row=rows.get(id);const owner=row?.state?.owner;if(owner?.startsWith('resident.')&&entities.has(owner))return owner;if(supported.has(row?.kind)&&entities.has(id))return id;return null;}
 function feetFloor(id,root,s){
  const a=s.actors.find(a=>a.id===id);if(a?.task==='hop'&&nav?.nodes[a.node])return nav.nodes[a.node][2]+.009;
  let lowest=Infinity;for(const side of['left','right']){const foot=parts.get(id+'/anim_ankle_'+side)||parts.get(id+'/event_ankle_'+side)||parts.get(id+'/tap_foot_'+side);if(!foot)continue;foot.updateWorldMatrix(true,true);foot.traverse(o=>{if(!o.isMesh)return;if(!o.geometry.boundingBox)o.geometry.computeBoundingBox();partBox.copy(o.geometry.boundingBox).applyMatrix4(o.matrixWorld);lowest=Math.min(lowest,partBox.min.y);});}
  if(Number.isFinite(lowest))return lowest+.008;
  // Seated variants without ankle controls still share the actual support floor.
  return (a?.p?.[2]??root.getWorldPosition(point).y)+.025;
 }
 function support(id,root,s){
  root.getWorldPosition(point);if(id.startsWith('resident.')){point.y=feetFloor(id,root,s);const a=s.actors.find(a=>a.id===id);return{width:1.16*(a?.scale||1),depth:1.04*(a?.scale||1)};}
  let base=anchors.get(id);if(!base){root.updateWorldMatrix(true,true);box.setFromObject(root);box.getSize(size);base={offset:box.min.y-point.y,width:Math.max(.55,Math.min(2.6,size.x+.22)),depth:Math.max(.5,Math.min(1.65,size.z+.22))};anchors.set(id,base);}
  point.y+=base.offset+.012;const kind=id.startsWith('animal.duck_')?'duck':rows.get(id)?.kind;if(['fish','duck','water_lantern'].includes(kind))point.y=Math.max(point.y,.64);return base;
 }
 function visible(id,s){if(['inside','enter'].includes(s.diners?.[id]?.phase))return false;if(s.passengers?.[id]?.phase==='riding')return false;let root=entities.get(id);for(let o=root;o;o=o.parent)if(!o.visible)return false;return !!root;}
 return{request(id,action,key){signals.request(id,action,key);},frame(s){
  for(const signal of signals.collect(s)){const id=resolve(signal.id,s);if(id&&!marks.has(id)&&marks.size<MAX_GLOWS)marks.set(id,{start:signal.time});}
  let i=0;for(const[id,m]of marks){const age=s.time-m.start;if(age>=GLOW_SECONDS||!entities.has(id)){marks.delete(id);continue;}const alpha=responseGlowAlpha(age);if(alpha<=0||!visible(id,s))continue;const root=entities.get(id),bounds=support(id,root,s);dummy.position.copy(point);dummy.rotation.set(0,0,0);dummy.scale.set(bounds.width,1,bounds.depth);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);alphas.setX(i,alpha);i++;}
  mesh.count=i;mesh.visible=i>0;mesh.instanceMatrix.needsUpdate=true;alphas.needsUpdate=true;
 },snapshot:()=>[...marks.keys()],resources:()=>({geometry:1,material:1,maxInstances:MAX_GLOWS})};
}
