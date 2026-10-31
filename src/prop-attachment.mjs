import * as THREE from 'three';
// Shared by cups/snacks, hand lanterns and paper notes. The actual modeled hand
// socket is used; carried props do not invent an independent floating path.
export function handWorldPoint({entities,parts,sockets},id,side='right',out=new THREE.Vector3()){
 const entry=sockets[id]?.hands?.[side],root=entities.get(id);if(!entry||!root)return root?root.getWorldPosition(out).add(new THREE.Vector3(0,.7,0)):out.set(0,0,0);
 const node=parts.get(id+'/'+(entry.part||'anim_arm_'+side));if(!node)return root.getWorldPosition(out);
 node.updateWorldMatrix(true,false);const p=entry.part_local;return node.localToWorld(out.set(p[0],p[2],-p[1]));
}
