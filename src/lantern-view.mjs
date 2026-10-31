import {handWorldPoint} from './prop-attachment.mjs?v=cp38-response-b8cecd6027c5';
import * as THREE from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {lanternDisplay,LANTERN_CARRIERS} from './lantern-scene.mjs?v=cp38-response-b8cecd6027c5';

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
 const hanging=[],strands=[],positions=[];
 // Keep the paper garlands over the promenade, never on the walking surface.
 for(const[a,b]of [[[ -5.8,-2.65,2.85],[-2.6,-3.3,2.75]],[[2.15,2.0,3.20],[5.05,.15,2.9]]]){
  const pts=[];for(let j=0;j<=24;j++){const t=j/24,p=a.map((v,k)=>v+(b[k]-v)*t);p[2]-=Math.sin(t*Math.PI)*.23;pts.push(new THREE.Vector3(p[0],p[2],-p[1]));}
  const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),new THREE.LineBasicMaterial({color:0xaa8a5b,transparent:true,opacity:0}));line.userData.runtime_effect_id='effect.lantern_evening_garland_'+strands.length;scene.add(line);strands.push(line);
  for(let j=0;j<6;j++){const t=(j+.5)/6,p=a.map((v,k)=>v+(b[k]-v)*t);p[2]-=Math.sin(t*Math.PI)*.23;positions.push(new THREE.Vector3(p[0],p[2],-p[1]));}
 }
 const lamps=new THREE.InstancedMesh(geometry,material,positions.length+LANTERN_CARRIERS.length);lamps.frustumCulled=false;lamps.userData.runtime_effect_id='effect.lantern_evening_lamps';scene.add(lamps);
 const dummy=new THREE.Object3D(),point=new THREE.Vector3();let visibleCount=0;
 const bindings=LANTERN_CARRIERS.map(id=>({id,part:sockets[id]?.hands?.right?.part||'anim_arm_right',local:sockets[id]?.hands?.right?.part_local})).filter(x=>x.local&&parts.has(x.id+'/'+x.part));
 return{ids:[lamps.userData.runtime_effect_id,...strands.map(x=>x.userData.runtime_effect_id)],frame(s){
  const amount=lanternDisplay(s);lamps.visible=amount>.001;visibleCount=0;
  for(const line of strands){line.visible=amount>.001;line.material.opacity=amount*.75;}
  for(let i=0;i<positions.length;i++){const a=lanternDisplay(s,i);dummy.position.copy(positions[i]);dummy.rotation.set(Math.sin(s.time*.8+i)*.035,0,Math.sin(s.time*.6+i)*.05);dummy.scale.set(a,a,a);dummy.updateMatrix();lamps.setMatrixAt(i,dummy.matrix);if(a>.05)visibleCount++;}
  for(let i=0;i<LANTERN_CARRIERS.length;i++){
   const id=LANTERN_CARRIERS[i],binding=bindings.find(x=>x.id===id),actor=s.actors.find(x=>x.id===id),guest=s.eventGuests?.[id],e=s.sceneEvent;
   const chosen=e?.kind==='lantern'&&(e.slots?.[id]!==undefined||e.phase==='closing')&&!e.protectedIds?.includes(id);
   const ready=chosen&&(!guest||!guest.active||!['prepare','sit'].includes(guest.phase));
   const a=ready&&binding?lanternDisplay(s,i+3):0;
   if(a>.001){handWorldPoint({entities,parts,sockets},id,'right',point);dummy.position.copy(point);dummy.rotation.set(Math.sin(s.time*2.1+i)*.06,actor?.yaw||0,Math.sin(s.time*1.6+i)*.05);const scale=(actor?.scale||1)*.76*a;dummy.scale.setScalar(scale);visibleCount++;}
   else dummy.scale.setScalar(0);
   dummy.updateMatrix();lamps.setMatrixAt(positions.length+i,dummy.matrix);
  }
  lamps.instanceMatrix.needsUpdate=true;
 },snapshot:()=>({visibleLanterns:visibleCount,capacity:lamps.count})};
}
