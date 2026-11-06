import * as THREE from 'three';
import {createPavingSupport} from './foot-support.mjs?v=cp50-friendly-fox-e903b4ae61c3';
import {actionSubjects,subjectAlpha} from './action-subjects.mjs?v=cp50-friendly-fox-e903b4ae61c3';
import {createResponseSignals,responseGlowAlpha,GLOW_SECONDS,MAX_GLOWS} from './response-signals.mjs?v=cp50-friendly-fox-e903b4ae61c3';
const supported=new Set(['animal','duck','fish','boat','bicycle','parked_bicycle','tram','windmill','door','plant','tree','water_lantern']);
export function createResponseMarkers({scene,entities,parts=new Map(),registry={entities:[]},nav}){
 const paving=createPavingSupport(nav?.activities?.paving);let lastTime=-1;const signals=createResponseSignals(),marks=new Map(),rows=new Map(registry.entities.map(e=>[e.id,e])),anchors=new Map();
 // Six folded paper petals share a single geometry/instance batch. The
 // breeze travels across the actor's feet; it never draws an enclosing ring.
 const positions=[],petalIds=[],shades=[];
 const outline=[[-.025,0,-.17],[-.085,0,-.07],[-.10,0,.025],[-.065,0,.12],[-.025,0,.16],[0,0,.115],[.04,0,.15],[.09,0,.065],[.09,0,-.035],[.025,0,-.14]],shape=[...outline,[0,.032,0]];
 for(let k=0;k<6;k++)for(let edge=0;edge<outline.length;edge++)for(const j of[edge,(edge+1)%outline.length,outline.length]){positions.push(...shape[j]);petalIds.push(k);shades.push(j===outline.length?1:0);}
 const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geo.setAttribute('petalIndex',new THREE.Float32BufferAttribute(petalIds,1));geo.setAttribute('paperFold',new THREE.Float32BufferAttribute(shades,1));
 const alphas=new THREE.InstancedBufferAttribute(new Float32Array(MAX_GLOWS),1),seeds=new THREE.InstancedBufferAttribute(Float32Array.from({length:MAX_GLOWS},(_,i)=>i*2.399),1);geo.setAttribute('markAlpha',alphas);geo.setAttribute('markSeed',seeds);
 const material=new THREE.ShaderMaterial({
  uniforms:{time:{value:0}},transparent:true,blending:THREE.NormalBlending,depthWrite:false,depthTest:true,toneMapped:false,side:THREE.DoubleSide,
  vertexShader:`uniform float time;attribute float markAlpha;attribute float markSeed;attribute float petalIndex;attribute float paperFold;varying float vAlpha;varying float vFold;varying float vPetal;
   void main(){float k=petalIndex;float cycle=fract(time*.24+k*.167+markSeed*.13);float theta=k*2.399+time*.65;
    vec3 p=position;float co=cos(theta),si=sin(theta);p.xz=mat2(co,-si,si,co)*p.xz;
    p.x+=-.75+cycle*1.35+sin(k*3.3+markSeed)*.20;p.z+=sin(k*2.1+markSeed)*.48+cycle*.18;
    p.y+=.07+sin(cycle*3.141593)*(.44+.055*mod(k,3.));
    vAlpha=min(.95,markAlpha*2.05)*smoothstep(0.,.12,cycle)*(1.-smoothstep(.80,1.,cycle));vFold=paperFold;vPetal=k;
    gl_Position=projectionMatrix*modelViewMatrix*instanceMatrix*vec4(p,1.0);}`,
  fragmentShader:`varying float vAlpha;varying float vFold;varying float vPetal;
   void main(){if(vAlpha<.01)discard;vec3 rose=vec3(.24,.024,.055);vec3 coral=vec3(.72,.145,.095);vec3 cream=vec3(.95,.61,.35);
    vec3 paper=mod(vPetal,3.)<1.?rose:mod(vPetal,3.)<2.?coral:mix(cream,coral,.35);paper=mix(paper,vec3(1.,.78,.57),vFold*.32);gl_FragColor=vec4(paper,vAlpha);}`
 });
 const mesh=new THREE.InstancedMesh(geo,material,MAX_GLOWS);mesh.name='Petals carried by a local wish';mesh.userData.runtime_effect_id='effect.wish_foot_ring';mesh.frustumCulled=false;mesh.renderOrder=2;mesh.visible=false;scene.add(mesh);
 let enabled=true;
 const spots=Array.from({length:2},()=>{const l=new THREE.PointLight(0xffbd68,0,2.6,2);l.castShadow=false;l.name='Gentle local action fill';scene.add(l);return l;});
 const point=new THREE.Vector3(),size=new THREE.Vector3(),dummy=new THREE.Object3D(),box=new THREE.Box3(),partBox=new THREE.Box3();
 function resolve(id,s){if(id?.startsWith('resident.'))return entities.has(id)?id:null;const row=rows.get(id);const owner=row?.state?.owner;if(owner?.startsWith('resident.')&&entities.has(owner))return owner;if(supported.has(row?.kind)&&entities.has(id))return id;return null;}
 function feetFloor(id,root,s){
  root.getWorldPosition(point);const floor=paving?.highest([point.x-.14,point.x+.14,-point.z-.14,-point.z+.14]);if(floor!==null&&floor!==undefined&&Math.abs(point.y-floor)<.09)return floor+.018;
  const a=s.actors.find(a=>a.id===id);if(a?.task==='hop'&&nav?.nodes[a.node])return nav.nodes[a.node][2]+.009;
  let lowest=Infinity;for(const side of['left','right']){const foot=(s.eventGuests?.[id]?.active?parts.get(id+'/event_ankle_'+side):null)||parts.get(id+'/anim_ankle_'+side)||parts.get(id+'/tap_foot_'+side);if(!foot)continue;foot.updateWorldMatrix(true,true);foot.traverse(o=>{if(!o.isMesh)return;if(!o.geometry.boundingBox)o.geometry.computeBoundingBox();partBox.copy(o.geometry.boundingBox).applyMatrix4(o.matrixWorld);lowest=Math.min(lowest,partBox.min.y);});}
  if(Number.isFinite(lowest))return lowest+.008;
  // Seated variants without ankle controls still share the actual support floor.
  return (a?.p?.[2]??root.getWorldPosition(point).y)+.025;
 }
 function support(id,root,s){
  root.getWorldPosition(point);if(id.startsWith('resident.')){point.y=feetFloor(id,root,s);const a=s.actors.find(a=>a.id===id);return{width:1.16*(a?.scale||1),depth:1.04*(a?.scale||1)};}
  let base=anchors.get(id);if(!base){root.updateWorldMatrix(true,true);box.setFromObject(root);box.getSize(size);base={offset:box.min.y-point.y,width:Math.max(.55,Math.min(2.6,size.x+.22)),depth:Math.max(.5,Math.min(1.65,size.z+.22))};anchors.set(id,base);}
  point.y+=base.offset+.012;if(id==='animal.garden_fox'&&s.movers?.[id]){const floor=paving?.highest([point.x-.12,point.x+.12,-point.z-.12,-point.z+.12]);point.y=floor===null||floor===undefined?s.movers[id].p[2]+.042:floor+.012;}const kind=id.startsWith('animal.duck_')?'duck':rows.get(id)?.kind;if(['fish','duck','water_lantern'].includes(kind))point.y=Math.max(point.y,.64);return base;
 }
 function visible(id,s){if(['inside','enter'].includes(s.diners?.[id]?.phase))return false;if(s.passengers?.[id]?.phase==='riding')return false;let root=entities.get(id);for(let o=root;o;o=o.parent)if(!o.visible)return false;return !!root;}
 return{setEnabled(value){enabled=!!value;},request(id,action,key){signals.request(id,action,key);},frame(s){
  material.uniforms.time.value=s.time;
  if(s.time<lastTime)marks.clear();lastTime=s.time;const subjects=actionSubjects(s),busy=['running','closing'].includes(s.inputSession?.phase);
  for(const signal of signals.collect(s)){const id=resolve(signal.id,s);if(!busy&&id&&!marks.has(id)&&marks.size<MAX_GLOWS)marks.set(id,{start:signal.time});}
  for(const raw of subjects){const id=resolve(raw,s);if(!id)continue;let m=marks.get(id);if(!m)marks.set(id,m={start:s.time});m.activeAt=s.time;m.subject=true;}
  if(busy)for(const[id,m]of marks)if(!m.subject)marks.delete(id);
  for(const l of spots)l.intensity=0;let spot=0;
  let i=0;for(const[id,m]of marks){const age=s.time-m.start,after=s.time-(m.activeAt??m.start);if((m.subject?after>1.4:age>=GLOW_SECONDS)||!entities.has(id)){marks.delete(id);continue;}const alpha=m.subject?subjectAlpha(age,s.time)*Math.max(0,1-after/1.4):responseGlowAlpha(age);if(alpha<=0||!visible(id,s))continue;const root=entities.get(id),bounds=support(id,root,s);if(m.subject&&spot<spots.length){spots[spot].position.copy(point).add(new THREE.Vector3(-.28,1.15,.35));spots[spot].intensity=Math.min(.62,alpha*1.8);spot++;}dummy.position.copy(point);dummy.rotation.set(0,0,0);dummy.scale.set(bounds.width,1,bounds.depth);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);alphas.setX(i,alpha);i++;}
  mesh.count=i;mesh.visible=enabled&&i>0;mesh.instanceMatrix.needsUpdate=true;alphas.needsUpdate=true;
 },snapshot:()=>[...marks.keys()],diagnostics:()=>({appearance:'paper-petals',enabled,subjects:[...marks].map(([id,m])=>({id,...m})),count:mesh.count,alpha:Array.from(alphas.array).slice(0,mesh.count),points:Array.from({length:mesh.count},(_,i)=>{const m=new THREE.Matrix4();mesh.getMatrixAt(i,m);return new THREE.Vector3().setFromMatrixPosition(m).toArray();})}),resources:()=>({geometry:1,material:1,maxInstances:MAX_GLOWS,unshadowedLights:2})};
}
