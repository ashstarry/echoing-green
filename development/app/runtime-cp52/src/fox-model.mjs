import * as THREE from 'three';
// Presentation-only refinement. The existing entity, head, tail and four leg
// control IDs remain the owners used by the simulation and saved towns.
export function refineFoxModel(root,parts){
 if(!root||root.userData.koyoiFox)return null;
 const id='animal.garden_fox',body=root.children.find(o=>!o.userData.part_id&&o.name.endsWith('body'));
 if(!body)return null;root.userData.koyoiFox=true;body.visible=false;
 const paper=color=>new THREE.MeshStandardMaterial({color,roughness:.94,flatShading:true});
 const orange=paper(0xc97539),chest=paper(0xf0d5ad),sock=paper(0x4b3733),paw=paper(0x403332),knees=new Map();
 const torso=new THREE.Group();torso.name='fox-folded-torso';torso.position.set(.015,.445,0);root.add(torso);
 const add=(parent,geo,mat,x,y,z)=>{const o=new THREE.Mesh(geo,mat);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o;};
 const hull=new THREE.SphereGeometry(1,7,4);hull.scale(.355,.155,.145);add(torso,hull,orange,0,0,0);
 const bib=new THREE.ConeGeometry(.112,.235,5);bib.rotateZ(Math.PI/2);bib.scale(1,.85,.85);add(torso,bib,chest,-.24,-.005,0);
 for(let i=0;i<4;i++){
  const leg=parts.get(id+'/leg_'+i);if(!leg)continue;for(const o of leg.children)o.visible=false;
  const front=i===0||i===2;leg.position.set(front?-.195:.225,.398,i<2?.111:-.111);
  add(leg,new THREE.CylinderGeometry(.044,.031,.18,5),orange,front?.008:-.014,-.087,0);
  const knee=new THREE.Group();knee.name='fox-paper-knee-'+i;knee.position.set(front?.008:-.014,-.177,0);leg.add(knee);knees.set(i,knee);
  add(knee,new THREE.CylinderGeometry(.029,.026,.151,5),sock,0,-.073,0);
  const foot=new THREE.BoxGeometry(.100,.052,.068);add(knee,foot,paw,-.020,-.164,0);
 }
 const head=parts.get(id+'/head');if(head){head.position.y+=.054;head.scale.multiplyScalar(.94);}
 const tail=parts.get(id+'/tail');if(tail)tail.position.y+=.075;
 return {torso,knees,legLength:.367,materials:[orange,chest,sock,paw]};
}
