import {interactionStep} from './interaction-sequence.mjs?v=cp50-friendly-fox-d3de906ee97b';
import {handWorldPoint} from './prop-attachment.mjs?v=cp50-friendly-fox-d3de906ee97b';
import * as THREE from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {lanternDisplay,LANTERN_STATIONS} from './lantern-scene.mjs?v=cp50-friendly-fox-d3de906ee97b';

function paperLampGeometry(){
 const pieces=[];
 function add(g,hex){const flat=g.index?g.toNonIndexed():g;const c=new THREE.Color(hex),colors=[];for(let i=0;i<flat.attributes.position.count;i++)colors.push(c.r,c.g,c.b);flat.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));pieces.push(flat);}
 const profile=[[.065,-.37],[.108,-.35],[.137,-.28],[.145,-.19],[.135,-.10],[.092,-.04]].map(([r,y])=>new THREE.Vector2(r,y));
 add(new THREE.LatheGeometry(profile,12),'#edb66d');
 for(const y of [-.37,-.04]){const g=new THREE.CylinderGeometry(.094,.094,.025,12);g.translate(0,y,0);add(g,'#87512d');}
 for(let i=0;i<12;i++){const a=i*Math.PI/6,g=new THREE.BoxGeometry(.006,.26,.006);g.translate(Math.cos(a)*.138,-.20,Math.sin(a)*.138);add(g,'#c78b4c');}
 const ring=new THREE.TorusGeometry(.048,.006,3,12,Math.PI);ring.translate(0,-.045,0);add(ring,'#765332');
 const g=mergeGeometries(pieces,false);for(const p of pieces)p.dispose();return g;
}
export function createLanternView({scene,entities,parts,sockets}){
 const geometry=paperLampGeometry(),material=new THREE.MeshStandardMaterial({vertexColors:true,roughness:1,emissive:0xff9b3d,emissiveIntensity:.50});
 const strands=[],positions=[];
 // These ropes, supports and unlit lamps belong to the town before the wish.
 const wood=new THREE.MeshStandardMaterial({color:0x87613f,roughness:1});
 for(const[a,b]of [[[-5.8,-2.65,2.85],[-2.6,-3.3,2.75]],[[2.15,2.0,3.20],[5.05,.15,2.9]]]){
  const pts=[];for(let j=0;j<=24;j++){const t=j/24,p=a.map((v,k)=>v+(b[k]-v)*t);p[2]-=Math.sin(t*Math.PI)*.23;pts.push(new THREE.Vector3(p[0],p[2],-p[1]));}
  const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),new THREE.LineBasicMaterial({color:0x957344,transparent:true,opacity:.6}));line.userData.runtime_effect_id='effect.lantern_evening_garland_'+strands.length;scene.add(line);strands.push(line);
  for(const p of [a,b]){const pole=new THREE.Mesh(new THREE.CylinderGeometry(.022,.03,p[2]-.64,6),wood);pole.position.set(p[0],(p[2]+.64)/2,-p[1]);scene.add(pole);}
  for(let j=0;j<6;j++){const t=(j+.5)/6,p=a.map((v,k)=>v+(b[k]-v)*t);p[2]-=Math.sin(t*Math.PI)*.23;positions.push(new THREE.Vector3(p[0],p[2],-p[1]));}
 }
 const warmth=new THREE.InstancedBufferAttribute(new Float32Array(positions.length+LANTERN_STATIONS.length),1);geometry.setAttribute('lampWarmth',warmth);
 material.onBeforeCompile=shader=>{shader.vertexShader='attribute float lampWarmth;varying float vLampWarmth;\n'+shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvLampWarmth=lampWarmth;');shader.fragmentShader='varying float vLampWarmth;\n'+shader.fragmentShader.replace('vec3 totalEmissiveRadiance = emissive;','vec3 totalEmissiveRadiance = emissive * vLampWarmth;');};
 material.customProgramCacheKey=()=> 'warm-paper-lanterns-v2';material.emissiveIntensity=1;
 const lamps=new THREE.InstancedMesh(geometry,material,positions.length+LANTERN_STATIONS.length);lamps.frustumCulled=false;lamps.userData.runtime_effect_id='effect.lantern_evening_lamps';scene.add(lamps);
 for(const c of LANTERN_STATIONS){const stand=new THREE.Group();stand.position.set(c.anchor[0],.64,-c.anchor[1]);scene.add(stand);for(const [x,z]of [[-.20,-.12],[.20,-.12],[-.20,.12],[.20,.12]]){const leg=new THREE.Mesh(new THREE.BoxGeometry(.035,.39,.035),wood);leg.position.set(x,.195,z);stand.add(leg);}const top=new THREE.Mesh(new THREE.BoxGeometry(.51,.035,.36),wood);top.position.y=.39;stand.add(top);}
 const poolGeo=new THREE.PlaneGeometry(1,1);poolGeo.rotateX(-Math.PI/2);poolGeo.setAttribute('lampWarmth',warmth);
 const poolMat=new THREE.ShaderMaterial({transparent:true,depthWrite:false,depthTest:true,toneMapped:false,vertexShader:'attribute float lampWarmth;varying vec2 vUv;varying float vWarm;void main(){vUv=uv;vWarm=lampWarmth;gl_Position=projectionMatrix*modelViewMatrix*instanceMatrix*vec4(position,1.);}',fragmentShader:'varying vec2 vUv;varying float vWarm;void main(){float r=length(vUv-.5);float a=exp(-r*r*19.)*.19*vWarm;if(a<.002)discard;gl_FragColor=vec4(1.,.63,.28,a);}'});
 const pools=new THREE.InstancedMesh(poolGeo,poolMat,positions.length+LANTERN_STATIONS.length);pools.frustumCulled=false;pools.renderOrder=1;pools.userData.runtime_effect_id='effect.lantern_ground_warmth';scene.add(pools);
 const dummy=new THREE.Object3D(),point=new THREE.Vector3(),lampColor=new THREE.Color();let visibleCount=0,lastLevels=[];
 function level(s,i){const glow=lanternDisplay(s,i),night=s.dayWeights?.night||0;return .025+night*.28+glow*1.05;}
 function finishLamp(i,s){const glow=level(s,i);lastLevels[i]=glow;warmth.setX(i,glow);lampColor.setRGB(1,1,1).multiplyScalar(.57+.43*Math.min(1,glow));lamps.setColorAt(i,lampColor);dummy.position.y=.674;dummy.rotation.set(0,0,0);dummy.scale.set(2.15,1,1.8);dummy.updateMatrix();pools.setMatrixAt(i,dummy.matrix);}

 const ease=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
 return{ids:[lamps.userData.runtime_effect_id,...strands.map(x=>x.userData.runtime_effect_id)],frame(s){
  lamps.visible=true;visibleCount=positions.length+LANTERN_STATIONS.length;
  for(let i=0;i<positions.length;i++){dummy.position.copy(positions[i]);dummy.rotation.set(Math.sin(s.time*.8+i)*.035,0,Math.sin(s.time*.6+i)*.05);dummy.scale.setScalar(1);dummy.updateMatrix();lamps.setMatrixAt(i,dummy.matrix);finishLamp(i,s);}
  for(const [i,c] of LANTERN_STATIONS.entries()){
   const p=s.neighborhoodWorld?.props.find(p=>p.mode==='lantern'&&p.stockSlot===i),j=p&&s.neighborhoodWorld.jobs.find(j=>j.prop===p.id),step=interactionStep(j),anchor=p?.sourceAnchor||c.anchor;
   dummy.position.set(anchor[0],anchor[2],-anchor[1]);dummy.rotation.set(0,.18,0);dummy.scale.setScalar(1);
   if(p&&j&&(p.location==='hand'||p.location==='supply'&&step?.action==='take')){
    handWorldPoint({entities,parts,sockets},p.owner,'right',point);point.y+=.02;
    const owner=entities.get(p.owner);if(owner)dummy.quaternion.copy(owner.getWorldQuaternion(new THREE.Quaternion()));
    if(step?.action==='take')dummy.position.lerp(point,ease(j.clock/1.2));
    else{dummy.position.copy(point);if(step?.action==='place')dummy.position.lerp(new THREE.Vector3(anchor[0],anchor[2],-anchor[1]),ease(j.clock/2.4));}
   }
   dummy.updateMatrix();lamps.setMatrixAt(positions.length+i,dummy.matrix);finishLamp(positions.length+i,s);
  }
  lamps.instanceMatrix.needsUpdate=true;lamps.instanceColor.needsUpdate=true;warmth.needsUpdate=true;pools.instanceMatrix.needsUpdate=true;
 },snapshot:()=>({visibleLanterns:visibleCount,capacity:lamps.count,physicalStock:LANTERN_STATIONS.length,emissionLevels:lastLevels.slice()})};
}
