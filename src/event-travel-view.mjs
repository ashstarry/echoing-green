import * as THREE from 'three';
import {legPose,ease} from './motion.mjs?v=cp32-events-e037ba401068';
import {makeArmSolver} from './arm-ik.mjs?v=cp32-events-e037ba401068';
import {FIREWORK_FOCUS,EVENT_GAZE_PITCH} from './event-design.mjs?v=cp32-events-e037ba401068';
const X=new THREE.Vector3(1,0,0),Y=new THREE.Vector3(0,1,0),Z=new THREE.Vector3(0,0,-1),clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
export function createEventTravelView({entities,parts,sockets,seated={},support}){
 const bases=new Map([...parts].map(([id,o])=>[id,o.quaternion.clone()])),armBase=new Map([...parts].map(([id,o])=>[id,{q:o.quaternion.clone(),p:o.position.clone(),s:o.scale.clone()}])),origins=new Map([...entities].map(([id,o])=>[id,{p:o.position.clone(),q:o.quaternion.clone()}]));
 const solveArm=makeArmSolver({entities,parts,sockets,base:armBase}),umbrella=entities.get('umbrella.carried_umbrella'),book=entities.get('book.terrace_reader_book');
 function handWorld(id,side){const h=sockets[id].hands[side],o=parts.get(id+'/'+h.part);o.updateWorldMatrix(true,false);return o.localToWorld(new THREE.Vector3(h.part_local[0],h.part_local[2],-h.part_local[1]));}
 const umbrellaRest=umbrella?{p:umbrella.position.clone(),s:umbrella.scale.clone(),grip:umbrella.worldToLocal(handWorld('resident.water_companion','right'))}:null;
 const bookRel=book?entities.get('resident.quiet_reader').getWorldQuaternion(new THREE.Quaternion()).invert().multiply(book.getWorldQuaternion(new THREE.Quaternion())):null;
 const triangles=support?.triangles||[],bins=new Map();for(let i=0;i<triangles.length;i++){const t=triangles[i];for(let x=Math.floor(Math.min(...t.map(p=>p[0]))*2);x<=Math.floor(Math.max(...t.map(p=>p[0]))*2);x++)for(let y=Math.floor(Math.min(...t.map(p=>p[1]))*2);y<=Math.floor(Math.max(...t.map(p=>p[1]))*2);y++){const k=x+','+y;if(!bins.has(k))bins.set(k,[]);bins.get(k).push(i);}}
 function floorAt(x,y,expected){let best=-Infinity;for(const i of bins.get(Math.floor(x*2)+','+Math.floor(y*2))||[]){const[a,b,c]=triangles[i],det=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1]);if(Math.abs(det)<1e-9)continue;const u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/det,v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/det,w=1-u-v;if(Math.min(u,v,w)<-.0001)continue;const h=u*a[2]+v*b[2]+w*c[2];if(h<expected+.20&&h>expected-.24)best=Math.max(best,h);}return Number.isFinite(best)?best:expected;}
 function rotate(id,key,angle,axis=X){const o=parts.get(id+'/'+key),b=bases.get(id+'/'+key);if(o&&b)o.quaternion.copy(b).multiply(new THREE.Quaternion().setFromAxisAngle(axis,angle));}
 function solveFoot(id,side,root,target,rig){const local=root.worldToLocal(target.clone()),sx=side==='left'?-.1:.1,dx=local.x-sx,dy=-local.z+(rig?0:.01),dz=local.y-(rig?.hip||.49),roll=-Math.atan2(dx,-dz),zz=-Math.hypot(dx,dz),L1=rig?.upper||.20,L2=rig?.lower||.18,knee=Math.acos(clamp((dy*dy+zz*zz-L1*L1-L2*L2)/(2*L1*L2),-1,1)),hip=Math.atan2(dy,-zz)-Math.atan2(L2*Math.sin(knee),L1+L2*Math.cos(knee)),prefix=rig?'event_':'anim_';
  rotate(id,prefix+(rig?'hip':'leg')+'_'+side,roll,Z);parts.get(id+'/'+prefix+(rig?'hip':'leg')+'_'+side)?.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(X,hip+(rig?Math.PI/2:0)));rotate(id,prefix+'knee_'+side,knee-(rig?Math.PI/2:0));rotate(id,prefix+'ankle_'+side,-hip-knee);parts.get(id+'/'+prefix+'ankle_'+side)?.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(Z,-roll));if(rig)rotate(id,'tap_foot_'+side,0);
 }
 return{frame(s){
  if(umbrellaRest){umbrella.position.copy(umbrellaRest.p);umbrella.scale.copy(umbrellaRest.s);}
  for(const[id,g]of Object.entries(s.eventGuests||{})){
   const root=entities.get(id),sock=sockets[id],rig=seated[id];if(!root||!sock)continue;
   if(!g.active){if(rig)for(const side of ['left','right'])for(const key of ['hip','knee','ankle'])rotate(id,'event_'+key+'_'+side,0);continue;}
   const scale=sock.scale[2],stand=rig?ease(g.stand):1,home=sock.origin,homeYaw=sock.yaw,transition=['prepare','sit'].includes(g.phase),ground=['ground_out','ground_home','hold'].includes(g.phase),p=g.p.slice(),weight=transition?0:g.gaitWeight||0;
   if(transition&&rig){p[0]=home[0]+Math.sin(homeYaw)*.235*scale*stand;p[1]=home[1]-Math.cos(homeYaw)*.235*scale*stand;p[2]=home[2];}
   if(rig||!ground){const rise=(rig?.standingRise||0)*scale*stand,drop=g.authorFeet?0:.026*scale*weight,world=new THREE.Vector3(p[0],p[2]+rise-drop,-p[1]);root.parent?.updateWorldMatrix(true,false);if(root.parent)root.parent.worldToLocal(world);root.position.copy(world);root.quaternion.copy(origins.get(id).q).premultiply(new THREE.Quaternion().setFromAxisAngle(Y,g.yaw-sock.yaw));root.updateWorldMatrix(true,true);
    for(const side of ['left','right']){
     if(!rig&&transition&&!g.authorFeet){for(const key of ['leg','knee','ankle'])rotate(id,'anim_'+key+'_'+side,0);continue;}
     let target;if(g.authorFeet){const f=g.authorFeet[side].slice();if(g.blocked>.2)f[2]+=(floorAt(f[0],f[1],p[2]+.02*scale)+.02*scale-f[2])*Math.min(1,(g.blocked-.2)*5);target=new THREE.Vector3(f[0],f[2]+(rig?.ankle?rig.ankle-.02:.09)*scale,-f[1]);}
     else{const gait=legPose(g.walked,scale,side,weight),sx=side==='left'?-.1:.1,localY=transition&&rig?-.235*(1-stand):-.01+gait.footY,cs=Math.cos(g.yaw),sn=Math.sin(g.yaw),wx=p[0]+(cs*sx-sn*localY)*scale,wy=p[1]+(sn*sx+cs*localY)*scale,expected=p[2]+.02*scale;let floor=expected;for(const dx of[-.065,.065])for(const dy of[-.14,.075])floor=Math.max(floor,floorAt(wx+(cs*dx-sn*dy)*scale,wy+(sn*dx+cs*dy)*scale,expected));target=new THREE.Vector3(wx,floor+(rig?.ankle?rig.ankle-.02:.09)*scale+.014+gait.lift*scale,-wy);}
     solveFoot(id,side,root,target,rig);
    }
   }
   if(g.authorFeet&&id!=='resident.quiet_reader')for(const side of ['left','right'])if(!(id==='resident.water_companion'&&side==='right')){rotate(id,'anim_arm_'+side,-.08-Math.sin((g.walked||0)/(.56*scale)*Math.PI*2+(side==='left'?0:Math.PI))*.18*(g.gaitWeight||0));const arm=parts.get(id+'/anim_arm_'+side);arm?.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(Z,side==='left'?-.18:.18));rotate(id,'anim_elbow_'+side,-.35);}
   // Compact the closed parasol around the real hand grip while it is carried.
   if(id==='resident.water_companion'&&umbrellaRest){rotate(id,'anim_arm_right',0);rotate(id,'anim_elbow_right',0);root.updateWorldMatrix(true,true);const grip=handWorld(id,'right'),factor=.55+.45*(s.residentActions[id].umbrella||0);umbrella.scale.y=umbrellaRest.s.y*factor;umbrella.updateWorldMatrix(true,true);const shifted=umbrella.localToWorld(umbrellaRest.grip.clone()),world=umbrella.getWorldPosition(new THREE.Vector3()).add(grip.sub(shifted));umbrella.parent.worldToLocal(world);umbrella.position.copy(world);}
   if(id==='resident.quiet_reader'&&book){const w=transition?stand:1;solveArm(id,'left',[-.08,.64,.30],w);root.updateWorldMatrix(true,true);const target=root.localToWorld(new THREE.Vector3(-.10,.69,.38));book.parent.updateWorldMatrix(true,false);book.position.lerp(book.parent.worldToLocal(target),w);const orientation=root.getWorldQuaternion(new THREE.Quaternion()).multiply(bookRel);book.quaternion.copy(book.parent.getWorldQuaternion(new THREE.Quaternion()).invert().multiply(orientation));}
   const watching=g.phase==='hold'&&s.sceneEvent?.kind==='festival',head=parts.get(id+'/anim_head'),b=bases.get(id+'/anim_head');if(head&&b){const target=watching?FIREWORK_FOCUS:[-1,3,1.6],desired=Math.atan2(target[1]-p[1],target[0]-p[0])+Math.PI/2-g.yaw;head.quaternion.copy(b).multiply(new THREE.Quaternion().setFromAxisAngle(Y,clamp(Math.atan2(Math.sin(desired),Math.cos(desired)),-.3,.3))).multiply(new THREE.Quaternion().setFromAxisAngle(X,watching?EVENT_GAZE_PITCH:0));}
   root.updateWorldMatrix(true,true);
  }
 },floorAt};
}
