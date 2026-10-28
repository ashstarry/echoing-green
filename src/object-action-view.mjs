import * as THREE from 'three';
const X=new THREE.Vector3(1,0,0),Y=new THREE.Vector3(0,1,0),Z=new THREE.Vector3(0,0,-1);
export function createObjectActionView({entities,parts,registry}){
 const indices=new Map(registry.entities.map((e,i)=>[e.id,i]));
 const roots=new Map([...entities].map(([id,o])=>[id,{p:o.getWorldPosition(new THREE.Vector3()),q:o.quaternion.clone(),s:o.scale.clone()}])),controls=new Map([...parts].map(([id,p])=>[id,{p:p.position.clone(),q:p.quaternion.clone(),s:p.scale.clone()}])),ownedLights=new Map();
 for(const e of registry.entities){if(!['light','star','celestial','water_lantern'].includes(e.kind))continue;const mats=[];entities.get(e.id)?.traverse(o=>{if(o.isMesh)for(const m of Array.isArray(o.material)?o.material:[o.material])if(m.emissiveIntensity>0&&!mats.some(x=>x.m===m))mats.push({m,base:m.emissiveIntensity});});ownedLights.set(e.id,mats);}
 function rotate(id,axis,angle){const p=parts.get(id),b=controls.get(id);if(p&&b)p.quaternion.copy(b.q).multiply(new THREE.Quaternion().setFromAxisAngle(axis,angle));}
 function place(o,p){if(o.parent)o.parent.worldToLocal(p);o.position.copy(p);}
 return {frame(s){for(const[id,c]of Object.entries(s.objectControls||{})){const o=entities.get(id),b=roots.get(id);if(!o||!b)continue;const t=s.time,v=c.value;
  if(c.kind==='windmill')rotate(id+'/rotor',Z,c.phase);
  if(['plant','tree'].includes(c.kind))rotate(id+'/foliage',X,Math.sin(t*1.3+indices.get(id)*.73)*Math.min(.8,s.windSpeed*v)*(c.kind==='tree'?.025:.05));
  if(c.kind==='hanging_ornament'){const e=registry.entities.find(e=>e.id===id);for(const p of e.parts)rotate(id+'/'+p.id,X,Math.sin(t*1.5+indices.get(id))*Math.min(.8,s.windSpeed*v)*.16);}
  if(c.kind==='parked_bicycle')for(const n of [0,1])rotate(id+'/wheel_'+n,Z,c.phase);
  if(c.kind==='bird'){const amount=c.action==='glide'?.10:c.action==='flap'?.56:c.action==='hover'?.25:.48;rotate(id+'/wing_left',X,Math.sin(t*7)*amount);rotate(id+'/wing_right',X,-Math.sin(t*7)*amount);}
  if(c.kind==='animal'){if(c.action==='look')rotate(id+'/head',Y,Math.sin(t*1.5+indices.get(id))*.17);if(c.action==='sniff')rotate(id+'/head',Z,-.12-.12*Math.max(0,Math.sin(t*3)));}
  if(c.kind==='duck'){if(c.action==='nibble')rotate(id+'/head',Z,.12+.16*(.5+.5*Math.sin(t*5)));if(c.action==='look')rotate(id+'/head',Y,Math.sin(t*1.6)*.25);}
  if(c.kind==='door'){const direction=X.clone().applyQuaternion(b.q);place(o,b.p.clone().addScaledVector(direction,.74*v));}
  if(c.kind==='boat'){place(o,b.p.clone().add(new THREE.Vector3(0,Math.sin(t*1.7)*.018*v,0)));o.quaternion.copy(b.q).multiply(new THREE.Quaternion().setFromAxisAngle(X,Math.sin(t*1.1)*.025*v));const blend=Math.min(1,(t-c.started)/.8),row=c.action==='row'?blend:0;rotate(id+'/oar_left',Y,-.07+Math.sin(t*1.2)*.025*v);rotate(id+'/oar_right',Y,Math.sin(t*1.2+1)*.06*v);for(const side of ['left','right'])parts.get(id+'/oar_'+side)?.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(X,(side==='left'?-1:1)*.09*(.5+.5*Math.sin(t*1.2))*row));}
  if(c.kind==='water_lantern')place(o,b.p.clone().add(new THREE.Vector3(0,Math.sin(t*1.4+indices.get(id))*.012*v,0)));
  if(['light','star','celestial'].includes(c.kind)||c.kind==='water_lantern'&&c.action==='shine'){for(const{m,base}of ownedLights.get(id)||[]){const pulse=c.action==='twinkle'?.73+.27*Math.sin(t*1.7+id.length):1;m.emissiveIntensity=base*(c.kind==='water_lantern'?1.28:v)*pulse*({warm:1,soft:.78,bright:1.18}[s.light]);}}
  if(c.kind==='curtain'&&c.action!=='sway'){const amount=v;for(const[index,side]of [[0,-1],[1,1],[4,-1],[5,1]]){const key=id+'/panel_0'+index,p=parts.get(key),base=controls.get(key);if(!p||!base)continue;const existing=Math.abs(p.position.x-base.p.x)/.42,open=Math.max(existing,amount);p.position.x=base.p.x+side*.42*open;p.scale.x=base.s.x*(1-.90*open);}}
 }} };
}
