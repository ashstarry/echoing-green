import * as THREE from 'three';
const X=new THREE.Vector3(1,0,0),Y=new THREE.Vector3(0,1,0),Z=new THREE.Vector3(0,0,-1);
export function createGroupView({parts}){
 const weights=new Map();const base=new Map([...parts].map(([id,o])=>[id,o.quaternion.clone()]));
 const set=(id,key,x=0,z=0,y=0)=>{const o=parts.get(id+'/'+key),q=base.get(id+'/'+key);if(o&&q){const target=q.clone().multiply(new THREE.Quaternion().setFromAxisAngle(Y,y)).multiply(new THREE.Quaternion().setFromAxisAngle(X,x)).multiply(new THREE.Quaternion().setFromAxisAngle(Z,z));o.quaternion.slerp(target,weights.get(id)?.weight||0);}};
 return{frame(s,dt){const e=s.sceneEvent;if(!e||!['gather','active','closing'].includes(e.phase)){weights.clear();return;}
  for(const a of s.actors){const standing=e.slots?.[a.id]!==undefined&&a.node===e.slots[a.id]&&!a.path.length&&a.mode==='idle'&&(!s.eventGuests?.[a.id]?.active||s.eventGuests[a.id].phase==='hold');const blend=weights.get(a.id)||{weight:Number(standing)};blend.weight+=(Number(standing)-blend.weight)*(1-Math.exp(-Math.max(0,dt||0)*7));weights.set(a.id,blend);if(blend.weight<.005)continue;
   if(e.kind==='festival'){set(a.id,'anim_head',-.64,0,s.residents[a.id]?.lookYaw||0);set(a.id,'anim_torso',-.05);set(a.id,'anim_arm_right',-.54,-.16);set(a.id,'anim_elbow_right',-1.02);}
   else if(e.kind==='lantern'){set(a.id,'anim_head',-.12,0,(s.residents[a.id]?.lookYaw||0)+Math.sin(s.time*.55+a.phase)*.10);set(a.id,'anim_arm_right',-.26,-.10);set(a.id,'anim_elbow_right',-.48);set(a.id,'anim_arm_left',-.08,.08);}
   else if(['market','supper'].includes(e.kind)){set(a.id,'anim_head',0,0,s.residents[a.id]?.lookYaw||0);set(a.id,'anim_arm_right',-.12-.04*Math.sin(s.time*.8+a.phase),-.08);set(a.id,'anim_elbow_right',-.35);}
  }
 }};
}
