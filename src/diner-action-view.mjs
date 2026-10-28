import * as THREE from 'three';
import {ease} from './motion.mjs?v=cp29-283b7ff62208';
const V=p=>new THREE.Vector3(p[0],p[2],-p[1]);const X=new THREE.Vector3(1,0,0),Y=new THREE.Vector3(0,1,0);
function around(p,q){return new THREE.Matrix4().makeTranslation(p.x,p.y,p.z).multiply(new THREE.Matrix4().makeRotationFromQuaternion(q)).multiply(new THREE.Matrix4().makeTranslation(-p.x,-p.y,-p.z));}
export function createDinerActionView({entities,parts,gestures,diningProps}){
 const anchors=new Map();for(const row of Object.values(diningProps||{}))for(const id of Object.values(row)){const o=entities.get(id);if(o)anchors.set(id,{p:o.getWorldPosition(new THREE.Vector3()),q:o.getWorldQuaternion(new THREE.Quaternion())});}
 function setPart(id,key,m){const o=parts.get(id+'/'+key);if(o){o.matrixAutoUpdate=false;o.matrix.copy(m);o.matrixWorldNeedsUpdate=true;}}
 function poseArm(id,side,target,weight=1){const arm=gestures[id].arms[side],S=V(arm.shoulder),E=V(arm.elbow),H=V(arm.hand),oldL1=S.distanceTo(E),oldL2=E.distanceTo(H),L1=oldL1+((oldL1+oldL2)*.5-oldL1)*weight,L2=oldL2+((oldL1+oldL2)*.5-oldL2)*weight,D=target.clone().sub(S),dist=Math.min(L1+L2-.0002,Math.max(Math.abs(L1-L2)+.001,D.length()));D.normalize();const goal=S.clone().addScaledVector(D,dist),along=(L1*L1-L2*L2+dist*dist)/(2*dist),height=Math.sqrt(Math.max(0,L1*L1-along*along)),pole=new THREE.Vector3(side==='left'?-.8:.8,-.5,.2);pole.addScaledVector(D,-pole.dot(D)).normalize();const restPole=E.clone().sub(S);restPole.addScaledVector(D,-restPole.dot(D)).normalize();pole.copy(restPole.lerp(pole,weight).normalize());const elbow=S.clone().addScaledVector(D,along).addScaledVector(pole,height),q1=new THREE.Quaternion().setFromUnitVectors(E.clone().sub(S).normalize(),elbow.clone().sub(S).normalize()),q2=new THREE.Quaternion().setFromUnitVectors(H.clone().sub(E).normalize(),goal.clone().sub(elbow).normalize());
  const scaleAlong=(dir,f)=>{const a=dir.toArray(),v=[];for(let i=0;i<4;i++)for(let j=0;j<4;j++)v.push(i===3||j===3?(i===j?1:0):(i===j?1:0)+(f-1)*a[i]*a[j]);return new THREE.Matrix4().set(...v);};
  const upper=around(S,q1).multiply(new THREE.Matrix4().makeTranslation(S.x,S.y,S.z)).multiply(scaleAlong(E.clone().sub(S).normalize(),L1/oldL1)).multiply(new THREE.Matrix4().makeTranslation(-S.x,-S.y,-S.z)),lower=new THREE.Matrix4().makeTranslation(elbow.x,elbow.y,elbow.z).multiply(new THREE.Matrix4().makeRotationFromQuaternion(q2)).multiply(scaleAlong(H.clone().sub(E).normalize(),L2/oldL2)).multiply(new THREE.Matrix4().makeTranslation(-E.x,-E.y,-E.z)),hand=new THREE.Matrix4().makeTranslation(goal.x,goal.y,goal.z).multiply(new THREE.Matrix4().makeRotationFromQuaternion(q2)).multiply(new THREE.Matrix4().makeTranslation(-H.x,-H.y,-H.z));setPart(id,arm.parts[2],upper);setPart(id,arm.parts[1],lower);setPart(id,arm.parts[0],hand);return goal;
 }
 function handWorld(id,side){const arm=gestures[id].arms[side],part=parts.get(id+'/'+arm.parts[0]);part.updateWorldMatrix(true,false);return part.localToWorld(V(arm.hand));}
 function place(o,p,q){o.parent.updateWorldMatrix(true,false);o.position.copy(o.parent.worldToLocal(p.clone()));o.quaternion.copy(o.parent.getWorldQuaternion(new THREE.Quaternion()).invert().multiply(q));}
 return {frame(s){for(const[id,meta]of Object.entries(gestures||{})){const r=s.residentActions?.[id],d=s.diners[id],root=entities.get(id),action=d.phase==='dine'?r?.action:null,clock=r?.clock||0,side=meta.workingSide,rest=V(meta.arms[side].hand);let held=null,tilt=0;
   if(['sip_tea','taste_food'].includes(action)){
    const kind=action==='sip_tea'?'cup':'food',propId=diningProps[id][kind],anchor=anchors.get(propId),grip=kind==='cup'?.060:.055,pick=root.worldToLocal(anchor.p.clone().add(new THREE.Vector3(0,grip,0))),mouth=new THREE.Vector3(side==='left'?-.11:.11,1.075,.245);let target;
    if(clock<1.1)target=rest.clone().lerp(pick,ease(clock/1.1));else if(clock<2.7)target=pick.clone().lerp(mouth,ease((clock-1.1)/1.6));else if(clock<4.8)target=mouth.clone();else if(clock<6.5)target=mouth.clone().lerp(pick,ease((clock-4.8)/1.7));else target=pick.clone().lerp(rest,ease((clock-6.5)/1.5));
    poseArm(id,side,target,ease(clock/.9)*ease((8-clock)/1.3));if(clock>=1.1&&clock<=6.5)held={id:propId,side,grip};tilt=kind==='cup'?ease((clock-2.7)/.5)*ease((4.8-clock)/.5)*-.22:0;
   }else if(action==='converse'){
    const free=side==='left'?'right':'left',h=V(meta.arms[free].hand),target=new THREE.Vector3(free==='left'?-.21:.21,.81,.20),w=ease(clock/.8)*ease((8-clock)/.9);poseArm(id,free,h.lerp(target,w*(.8+.2*Math.sin(clock*2.7))),w);
   }else if(action==='watch_sky'){
    const w=ease(clock/.8)*ease((7-clock)/.9),q=new THREE.Quaternion().setFromAxisAngle(X,-.14*w);for(const key of meta.headParts)setPart(id,key,around(new THREE.Vector3(0,.98,0),q));
   }
   root.updateWorldMatrix(true,true);
   for(const propId of Object.values(diningProps[id])){const o=entities.get(propId),anchor=anchors.get(propId);if(!o||!anchor)continue;let p=anchor.p.clone(),q=anchor.q.clone();if(held?.id===propId){p=handWorld(id,held.side).add(new THREE.Vector3(0,-held.grip,0));if(tilt){const axis=X.clone().applyQuaternion(root.getWorldQuaternion(new THREE.Quaternion()));q.premultiply(new THREE.Quaternion().setFromAxisAngle(axis,tilt));}}place(o,p,q);}
  }},handWorld};
}
