import * as THREE from 'three';
const ease=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
export function createEventProps(scene){
 const paper=new THREE.MeshStandardMaterial({color:0xf0d6aa,roughness:.95}),wood=new THREE.MeshStandardMaterial({color:0x83532e,roughness:.95}),red=new THREE.MeshStandardMaterial({color:0xa54532,roughness:.92}),gold=new THREE.MeshStandardMaterial({color:0xf4b563,roughness:.9});
 const items=[],groups=[],yaw=37*Math.PI/180;
 function box(g,w,h,d,x,y,z,mat){const o=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;g.add(o);return o;}
 // Small signs unfold beside the counters, outside the public walking corridor.
 for(const[id,p]of [['bread',[-2.11,1.17,3.06]],['tea',[-.62,2.30,3.06]],['supper',[.88,3.42,3.06]]]){
  const g=new THREE.Group();g.name='market_'+id+'_sign';g.userData.runtime_effect_id='event_prop.market_sign_'+id;g.userData.owner_entity='resident.vendor_'+({bread:'bread',tea:'flower',supper:'lamp'}[id]);g.position.set(p[0],p[2],-p[1]);g.rotation.y=yaw;scene.add(g);groups.push(g);
  const hinge=new THREE.Group();g.add(hinge);box(hinge,.82,.44,.045,0,-.25,0,paper);box(hinge,.88,.035,.07,0,-.48,0,wood);box(hinge,.88,.035,.07,0,-.03,0,wood);
  for(const x of [-.44,.44])box(hinge,.035,.47,.07,x,-.25,0,wood);
  // Painted bowl/steam icon uses flat paper geometry, no floating UI label.
  const bowl=new THREE.Mesh(new THREE.CircleGeometry(.125,12,0,Math.PI),red);bowl.rotation.z=Math.PI;bowl.position.set(0,-.24,.026);hinge.add(bowl);for(let i=-1;i<=1;i++)box(hinge,.019,.08,.006,i*.075,-.14,.027,red);
  const ropeGeometry=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-.32,.18,-.45),new THREE.Vector3(-.32,0,0),new THREE.Vector3(.32,0,0),new THREE.Vector3(.32,.18,-.45)]);g.add(new THREE.Line(ropeGeometry,new THREE.LineBasicMaterial({color:0x8b6540})));items.push({hinge,group:g,delay:items.length*.3});
 }
 const pennants=new THREE.Group();pennants.name='market_paper_pennants';pennants.userData.runtime_effect_id='event_prop.market_bunting';pennants.position.set(-.80,3.25,-2.46);pennants.rotation.y=yaw;scene.add(pennants);groups.push(pennants);
 for(let i=0;i<9;i++){const shape=new THREE.Shape();shape.moveTo(-.12,0);shape.lineTo(.12,0);shape.lineTo(0,-.22);shape.closePath();const o=new THREE.Mesh(new THREE.ShapeGeometry(shape),i%2?gold:red);o.material.side=THREE.DoubleSide;o.position.set((i-4)*.36,0,0);pennants.add(o);}
 const petals=new THREE.InstancedMesh(new THREE.OctahedronGeometry(.06,0),new THREE.MeshStandardMaterial({color:0xe5a4b4,roughness:1,transparent:true,opacity:0}),32);petals.name='event_blossom_petals';petals.userData.runtime_effect_id='event_prop.paper_blossom_drift';petals.frustumCulled=false;scene.add(petals);groups.push(petals);const petalPose=new THREE.Object3D();let petalAmount=0;
 let amount=0;
 return{frame(s,dt){const e=s.sceneEvent,active=e&&['market','supper'].includes(e.kind)&&!['closing','release'].includes(e.phase);amount+=(Number(active)-amount)*Math.min(1,dt*1.8);for(const {hinge,group,delay}of items){const open=ease((amount-delay*.12)/.82);hinge.rotation.x=-Math.PI/2*(1-open);group.visible=open>.01;}pennants.scale.y=Math.max(.005,amount);pennants.visible=amount>.01;for(const c of pennants.children)c.rotation.x=Math.sin(s.time*1.2+c.position.x)*.09*amount;const gentle=e&&['reunion','quiet','supper'].includes(e.kind)&&!['closing','release'].includes(e.phase);petalAmount+=(Number(gentle)-petalAmount)*Math.min(1,dt*.8);petals.visible=petalAmount>.01;petals.material.opacity=petalAmount*.75;for(let i=0;i<32;i++){const f=(s.time*.08+i*.618)%1,angle=i*2.399;petalPose.position.set(-.6+Math.cos(angle)*(1.2+f*.4)+Math.sin(s.time*.5+i)*.15,.65+(1-f)*2.2,1+Math.sin(angle)*(1.0+f*.5));petalPose.rotation.set(s.time*.5+i,i*.3,s.time*.4);petalPose.scale.set(.7,.22,1.2).multiplyScalar(Math.min(1,f*9,(1-f)*9));petalPose.updateMatrix();petals.setMatrixAt(i,petalPose.matrix);}petals.instanceMatrix.needsUpdate=true;},ids:groups.map(g=>g.userData.runtime_effect_id),snapshot:()=>({marketDisplay:amount,petalDrift:petalAmount})};
}
