import * as THREE from 'three';
const X=new THREE.Vector3(1,0,0),Y=new THREE.Vector3(0,1,0),Z=new THREE.Vector3(0,0,1),q=new THREE.Quaternion(),v=new THREE.Vector3();
export function createLifeView({scene,entities,parts,registry,lights,weatherSupport}){
 const originals=new Map(),partBase=new Map(),emissive=[],stars=[];
 for(const [id,o]of entities){originals.set(id,{p:o.getWorldPosition(new THREE.Vector3()),q:o.quaternion.clone(),s:o.scale.clone()});o.traverse(c=>{if(c.isMesh){const mats=Array.isArray(c.material)?c.material:[c.material];c.material=mats.map(m=>{if(m.emissiveIntensity>0){const n=m.clone();n.emissiveIntensity=Math.min(n.emissiveIntensity,2.4);emissive.push({m:n,base:n.emissiveIntensity});if(id.startsWith('star.'))stars.push({m:n,base:n.emissiveIntensity,index:stars.length});return n;}return m;});if(c.material.length===1)c.material=c.material[0];}});}
 for(const [id,p]of parts)partBase.set(id,{q:p.quaternion.clone(),p:p.position.clone()});
 const cloud=entities.get('weather.cp02_paper_cloud'),rainPart=parts.get('weather.cp02_paper_cloud/rain');if(rainPart)rainPart.visible=false;
 const geo=new THREE.PlaneGeometry(.035,.18),mat=new THREE.MeshBasicMaterial({color:0xbfd3ee,transparent:true,opacity:.44,side:THREE.DoubleSide,depthWrite:false});const rain=new THREE.InstancedMesh(geo,mat,100);rain.frustumCulled=false;scene.add(rain);
 const snow=new THREE.InstancedMesh(new THREE.OctahedronGeometry(.043,0),new THREE.MeshStandardMaterial({color:0xfff1de,roughness:1,transparent:true,opacity:0}),160);snow.frustumCulled=false;scene.add(snow);
 const fireCount=160,fireworks=new THREE.InstancedMesh(new THREE.OctahedronGeometry(.045,0),new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:0,depthWrite:false,blending:THREE.AdditiveBlending}),fireCount);fireworks.frustumCulled=false;scene.add(fireworks);

 const dummy=new THREE.Object3D();let wind=.35,light=1,rainAmount=0,snowAmount=0,birdAmount=1;let first=true;
 function rotate(id,axis,amount){const p=parts.get(id),base=partBase.get(id);if(p&&base)p.quaternion.copy(base.q).multiply(q.setFromAxisAngle(axis,amount));}
 function placeWorld(o,p){v.copy(p);if(o.parent)o.parent.worldToLocal(v);o.position.copy(v);}
 function frame(s,dt){const t=s.time,ease=first?1:Math.min(1,dt*1.8);first=false;wind+=( ({calm:.08,gentle:.35,lively:.8}[s.breeze])-wind)*ease;light+=(({soft:.78,warm:1,bright:1.18}[s.light])-light)*ease;rainAmount+=((s.weather==='rain'?1:0)-rainAmount)*ease;snowAmount+=((s.weather==='snow'?1:0)-snowAmount)*ease;birdAmount+=((s.birds==='fly'?1:0)-birdAmount)*ease;
 for(const a of s.actors){const o=entities.get(a.id),base=originals.get(a.id);if(!o)continue;placeWorld(o,new THREE.Vector3(a.p[0],a.p[2],-a.p[1]));const source=registry.entities.find(e=>e.id===a.id);const delta=a.yaw-(source?.runtime_yaw??0);o.quaternion.copy(base.q); // yaw is applied in world Y relative to authored heading
 const authored=source?.runtime_yaw;if(authored!==undefined)o.quaternion.premultiply(q.setFromAxisAngle(Y,a.yaw-authored));
 const gait=a.mode==='walk'?Math.sin(a.phase*9)*.19:0;
 for(const [side,sign]of [['left',1],['right',-1]]){const id=`${a.id}/anim_leg_${side}`;rotate(id,X,gait*sign);const p=parts.get(id);if(p)p.position.copy(partBase.get(id).p).addScaledVector(Z,Math.abs(gait)*.24);rotate(`${a.id}/anim_arm_${side}`,X,-gait*sign*.5);}
 }
 let i=0;for(const e of registry.entities){const id=e.id,o=entities.get(id);if(!o)continue;
 if(e.kind==='resident'){rotate(`${id}/anim_head`,Z,Math.sin(t*.7+i)*.045);if(id==='resident.musician')rotate(`${id}/anim_arm_left`,X,s.music==='play'?(Math.sin(t*7)-1)*.015:0);else if(id.includes('vendor_')){rotate(`${id}/anim_arm_right`,X,Math.max(0,Math.sin(t*.9+i))*.10);}}
 if(e.kind==='bird'){const b=originals.get(id).p;const p=b.clone();p.x+=Math.sin(t*.6+i)*.22*birdAmount;p.y+=(Math.sin(t*1.1+i)*.09)*birdAmount;p.z+=Math.sin(t*.6+i)*.16*birdAmount;placeWorld(o,p);rotate(`${id}/wing_left`,X,Math.sin(t*5+i)*.24*(.2+birdAmount*.8));rotate(`${id}/wing_right`,X,-Math.sin(t*5+i)*.24*(.2+birdAmount*.8));}
 if(e.kind==='windmill')rotate(`${id}/rotor`,Y,s.windPhase);
 if(e.kind==='curtain'||e.kind==='hanging_ornament')for(const p of e.parts)rotate(`${id}/${p.id}`,X,Math.sin(t*1.2+i)*wind*.06);
 i++;}
 for(const e of emissive)e.m.emissiveIntensity=e.base*light;for(const e of stars)e.m.emissiveIntensity=e.base*light*(.85+.15*Math.sin(t*.8+e.index*1.7));for(const l of lights)l.intensity=l.userData.baseIntensity*light;
 rain.visible=rainAmount>.01;rain.material.opacity=rainAmount*.43;
 for(let j=0;j<100;j++){const a=j*.6180339887%1,b=j*.381966%1;dummy.position.set(8.5+a*2.4,weatherSupport.rain[j]+(1-(t*.65+b)%1)*(5.05-weatherSupport.rain[j]),-.8+(j*.731%1)*2.5);dummy.rotation.set(0,0,-wind*.15);dummy.scale.setScalar(1);dummy.updateMatrix();rain.setMatrixAt(j,dummy.matrix);}rain.instanceMatrix.needsUpdate=true;
 snow.visible=snowAmount>.01;snow.material.opacity=snowAmount*.85;for(let j=0;j<160;j++){dummy.position.set(-11+(j*.618%1)*22+Math.sin(t*.5+j)*.12,weatherSupport.snow[j]+(1-(t*.08+j*.47)%1)*(7.4-weatherSupport.snow[j]),-7+(j*.731%1)*13);dummy.rotation.set(t*.25+j,t*.3,0);const fall=(t*.08+j*.47)%1;dummy.scale.setScalar(Math.min(1,fall*10,(1-fall)*10));dummy.updateMatrix();snow.setMatrixAt(j,dummy.matrix);}snow.instanceMatrix.needsUpdate=true;
 const show=s.festivalUntil>t,phase=t%4;fireworks.visible=show;fireworks.material.opacity=show?Math.sin(Math.PI*phase/4)*.9:0;
 if(show){for(let j=0;j<fireCount;j++){const a=j*2.399963,b=Math.acos(1-2*(j+.5)/fireCount),radius=phase*.42;dummy.position.set(-8+Math.cos(a)*Math.sin(b)*radius,6.4+Math.cos(b)*radius-phase*phase*.018,.2+Math.sin(a)*Math.sin(b)*radius);dummy.rotation.set(a,t*.4,b);dummy.scale.setScalar(.6+Math.sin(j*3.3)*.2);dummy.updateMatrix();fireworks.setMatrixAt(j,dummy.matrix);const c=new THREE.Color().setHSL(.03+(j%3)*.06,.8,.58).multiplyScalar(2);fireworks.setColorAt(j,c);}fireworks.instanceMatrix.needsUpdate=true;fireworks.instanceColor.needsUpdate=true;}

 }
 return {frame};
}
