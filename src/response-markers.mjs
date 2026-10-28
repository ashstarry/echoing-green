import * as THREE from 'three';
// A brief, faint patch of light at the feet; no text, floating labels or particles.
export function createResponseMarkers({scene,entities}){
 const marks=new Map(),seen=new Set(),p=new THREE.Vector3();
 const geometry=new THREE.PlaneGeometry(.88,.88);
 function start(id,key,time){if(!id?.startsWith('resident.')||!entities.has(id)||seen.has(key))return;seen.add(key);if(seen.size>180)seen.delete(seen.values().next().value);
  let mark=marks.get(id);if(!mark){const group=new THREE.Group();group.name='wish-paper-'+id;group.userData.runtime_effect_id='effect.wish_foot_ring';group.userData.owner_entity=id;
   const material=new THREE.ShaderMaterial({transparent:true,depthWrite:false,depthTest:true,toneMapped:false,side:THREE.DoubleSide,uniforms:{opacity:{value:0}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',fragmentShader:'varying vec2 vUv;uniform float opacity;void main(){float r=length(vUv-0.5);float band=smoothstep(0.29,0.35,r)*(1.0-smoothstep(0.35,0.42,r));gl_FragColor=vec4(0.91,0.79,0.59,band*opacity);}'});
   const ring=new THREE.Mesh(geometry,material);ring.rotation.x=-Math.PI/2;ring.position.y=.075;group.add(ring);scene.add(group);mark={group,material,start:time};marks.set(id,mark);
  }mark.start=time;
 }
 return{frame(s){
  for(const j of s.intentRuntime.jobs)if(j.source!=='day_rhythm'&&j.kind==='resident'&&j.status==='running')start(j.target,'job:'+j.id+':'+j.step,j.updated);
  for(const x of s.townResponse?.pending||[])if(x.dispatched!==undefined&&s.townResponse.theme!=='opening')start(x.id,'pulse:'+s.townResponse.id+':'+x.id,x.dispatched);
  for(const[id,m]of marks){const age=s.time-m.start,alpha=age>=0&&age<3.2?Math.sin(Math.PI*age/3.2):0;m.group.visible=alpha>0&&!['inside','enter'].includes(s.diners?.[id]?.phase);if(!m.group.visible)continue;
   entities.get(id).getWorldPosition(p);m.group.position.copy(p);m.material.uniforms.opacity.value=.18*alpha;m.group.scale.setScalar(1+age*.012);
  }
 },snapshot:()=>[...marks].filter(([,m])=>m.group.visible).map(([id])=>id)};
}
