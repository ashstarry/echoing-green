import {FIREWORK_FOCUS} from './event-design.mjs?v=cp30-life-e7bb14ab832f';
import * as THREE from 'three';
// One GPU draw for all rockets, glowing red/gold heads and curved trailing sparks.
export function createFireworks(scene,camera,renderer){
 const effects=new THREE.Scene();
 const right=new THREE.Vector3(1,0,0).applyQuaternion(camera.quaternion),up=new THREE.Vector3(0,1,0).applyQuaternion(camera.quaternion),forward=camera.getWorldDirection(new THREE.Vector3());
 const center=(x,y)=>camera.position.clone().addScaledVector(forward,42).addScaledVector(right,x*(camera.right-camera.left)/2).addScaledVector(up,(y+1)*(camera.top-camera.bottom)/2+camera.bottom);
 const centers=[new THREE.Vector3(FIREWORK_FOCUS[0],FIREWORK_FOCUS[2],-FIREWORK_FOCUS[1])];const times=[1.2,2.9,5.3,6.8,9.2,11.0,13.0,15.4,17.0,17.4,18.1];
 const arrays={position:[],ray:[],center:[],color:[],timing:[],size:[]};let seed=180026;const rnd=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};
 function add(c,r,col,delay,trail,kind,speed,size){arrays.position.push(0,0,0);arrays.center.push(...c.toArray());arrays.ray.push(...r.toArray());arrays.color.push(...col);arrays.timing.push(delay,trail,kind,speed);arrays.size.push(size);}
 for(let burst=0;burst<times.length;burst++){
  const c=centers[0],count=burst%3===2?180:280,delay=times[burst],gold=burst%4===1,scale=burst%3===2?.8:1;
  for(let j=0;j<count;j++){const theta=j*2.3999632297,z=1-2*(j+.5)/count,ring=Math.sqrt(Math.max(0,1-z*z));const r=right.clone().multiplyScalar(Math.cos(theta)*ring).addScaledVector(up,Math.sin(theta)*ring).addScaledVector(forward,z*.30);const speed=(1.65+rnd()*.35)*scale;const col=gold?[1,.30,.012]:(j%9===0?[1,.45,.018]:[1,.008+rnd()*.008,.004]);
   for(let k=0;k<18;k++)add(c,r,col,delay,k*.07,0,speed,k===0?6.5:4.5-k*.14);
  }
  for(let j=0;j<28;j++)add(c,up,[1,.35,.012],delay-.95,j*.019,1,5.3,4.3);
 }
 const geometry=new THREE.BufferGeometry();for(const [name,size]of [['position',3],['ray',3],['center',3],['color',3],['timing',4],['size',1]])geometry.setAttribute(name,new THREE.Float32BufferAttribute(arrays[name],size));
 const material=new THREE.ShaderMaterial({transparent:true,depthWrite:false,depthTest:true,blending:THREE.NormalBlending,toneMapped:false,uniforms:{uTime:{value:0},uStop:{value:100},uPixel:{value:renderer.getPixelRatio()}},vertexShader:`
 attribute vec3 ray,center,color;attribute vec4 timing;attribute float size;uniform float uTime,uStop,uPixel;varying vec3 vColor;varying float vAlpha;
 void main(){float age=uTime-timing.x-timing.y;float sparkOn=step(0.,age)*step(timing.x-(timing.z<.5?.95:0.),uStop);vec3 p=center;float alpha=0.;
 if(timing.z<.5){float radius=timing.w*(1.-exp(-max(0.,age)*.74));p+=ray*radius;p.y-=.025*age*age;alpha=sparkOn*pow(max(0.,1.-age/4.8),1.05)*exp(-timing.y*1.35);}
 else{float progress=clamp(age/.95,0.,1.);p-=ray*(1.-progress)*timing.w;alpha=sparkOn*step(age,.95)*(1.-timing.y);}
 vColor=color;vAlpha=alpha;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);gl_PointSize=max(1.,size*uPixel)*(alpha>.001?1.:0.);
 }`,fragmentShader:`varying vec3 vColor;varying float vAlpha;void main(){vec2 p=gl_PointCoord*2.-1.;float diamond=abs(p.x)+abs(p.y);float craft=1.-smoothstep(.15,.78,diamond);float halo=exp(-3.8*dot(p,p))*.42;float alpha=(craft+halo)*vAlpha;if(alpha<.002)discard;gl_FragColor=vec4(vColor,min(.98,alpha*2.0));
#include <colorspace_fragment>
}`});
 const sparks=new THREE.Points(geometry,material);sparks.frustumCulled=false;sparks.userData.entity_id='effect.festival_fireworks';effects.add(sparks);
 const haloMaterial=material.clone();haloMaterial.uniforms=material.uniforms;haloMaterial.blending=THREE.AdditiveBlending;haloMaterial.vertexShader=material.vertexShader.replace('size*uPixel','size*uPixel*3.2');haloMaterial.fragmentShader=`varying vec3 vColor;varying float vAlpha;void main(){vec2 p=gl_PointCoord*2.-1.;float alpha=exp(-5.*dot(p,p))*vAlpha*.15;if(alpha<.002)discard;gl_FragColor=vec4(vColor,alpha);
#include <colorspace_fragment>
}`;const glow=new THREE.Points(geometry,haloMaterial);glow.frustumCulled=false;effects.add(glow);sparks.renderOrder=2;glow.renderOrder=1;
 const reflected=new THREE.PointLight(0xff3910,0,18,2);reflected.position.set(FIREWORK_FOCUS[0],4,-FIREWORK_FOCUS[1]);scene.add(reflected);
 return {render(){const clear=renderer.autoClear;renderer.autoClear=false;renderer.clearDepth();renderer.render(effects,camera);renderer.autoClear=clear;},update(s){const active=s.festivalUntil>s.time;const elapsed=s.time-(s.festivalStarted||0);sparks.visible=active;glow.visible=active;material.uniforms.uTime.value=elapsed;material.uniforms.uStop.value=s.festivalStop===null?100:(s.festivalStop-s.festivalStarted);let pulse=0;for(const at of times)if(at<=material.uniforms.uStop.value)pulse+=Math.exp(-Math.pow((elapsed-at-.12)/.22,2));reflected.intensity=active?Math.min(14,pulse*10):0;},particleCount:arrays.size.length};
}
