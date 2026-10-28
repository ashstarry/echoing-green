import * as THREE from 'three';
import {celestialVisibility} from './celestial-phase.mjs?v=cp29-283b7ff62208';
export function createEnvironmentView({scene,art,entities,camera}){
 const themes={dawn:['#39313e','#756061','#49414c'],day:['#49434a','#938577','#625a5a'],dusk:art.preset.background,night:['#201f2a','#403a4c','#2c2937']};
 const textures=Object.fromEntries(Object.entries(themes).map(([key,colors])=>[key,key==='dusk'?scene.background:art.backgroundFactory(colors)]));
 const uniforms=Object.fromEntries(Object.entries(textures).map(([key,value])=>['t_'+key,{value}]));
 for(const key of Object.keys(themes))uniforms['w_'+key]={value:key==='dusk'?1:0};
 const material=new THREE.ShaderMaterial({uniforms,depthTest:false,depthWrite:false,vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=vec4(position.xy,1.0,1.0);}',fragmentShader:'varying vec2 vUv;uniform sampler2D t_dawn,t_day,t_dusk,t_night;uniform float w_dawn,w_day,w_dusk,w_night;void main(){vec3 c=texture2D(t_dawn,vUv).rgb*w_dawn+texture2D(t_day,vUv).rgb*w_day+texture2D(t_dusk,vUv).rgb*w_dusk+texture2D(t_night,vUv).rgb*w_night;gl_FragColor=vec4(c,1.0);}',toneMapped:false});
 const quad=new THREE.Mesh(new THREE.PlaneGeometry(2,2),material);quad.name='CP24 paper room atmosphere';quad.frustumCulled=false;quad.renderOrder=-1000;scene.add(quad);
 const p=art.preset,profiles={dusk:{hemi:p.hemi,key:p.key,fill:p.fill,bounce:p.bounce,ambient:p.ambient,local:1,keyColor:0xffd4a1,sky:0xb8c6df,stars:1},dawn:{hemi:1.0,key:2.45,fill:.65,bounce:.4,ambient:.09,local:.86,keyColor:0xffd1ab,sky:0xe7c3c4,stars:.65},day:{hemi:1.08,key:2.65,fill:.62,bounce:.35,ambient:.09,local:.65,keyColor:0xffe5bf,sky:0xd7dce2,stars:.3},night:{hemi:.88,key:2.05,fill:.66,bounce:.38,ambient:.09,local:1.06,keyColor:0xffc78f,sky:0xaebcdb,stars:1.2}};
 const skyMaterials=[],skyOpacity=[];for(const[id,o]of entities)if(id.startsWith('star.')||id==='moon.paper_crescent')o.traverse(m=>{if(m.isMesh)for(const x of Array.isArray(m.material)?m.material:[m.material]){if(x.emissiveIntensity>0)skyMaterials.push(x);skyOpacity.push({material:x,moon:id==='moon.paper_crescent'});x.transparent=true;x.depthWrite=false;}});
 const sun=new THREE.Group();sun.name='CP24 folded daylight sun';sun.userData.entity_id='effect.daylight_sun';sun.userData.runtime_effect_id='effect.daylight_sun';const moon=entities.get('moon.paper_crescent');if(moon)sun.position.copy(new THREE.Box3().setFromObject(moon).getCenter(new THREE.Vector3()));sun.quaternion.copy(camera.getWorldQuaternion(new THREE.Quaternion()));scene.add(sun);
 const vertices=[],colors=[],a=new THREE.Color('#f0c37b'),b=new THREE.Color('#ffdfa1');
 for(let i=0;i<12;i++){const t=i*Math.PI/6,u=(i+1)*Math.PI/6;vertices.push(0,0,.07,Math.cos(t)*.50,Math.sin(t)*.50,0,Math.cos(u)*.50,Math.sin(u)*.50,0);for(let j=0;j<3;j++){const c=i%2?a:b;colors.push(c.r,c.g,c.b);}}
 const sunGeometry=new THREE.BufferGeometry();sunGeometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));sunGeometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));sunGeometry.computeVertexNormals();
 const sunMaterial=new THREE.MeshStandardMaterial({vertexColors:true,roughness:1,emissive:0xffb35c,emissiveIntensity:.28,transparent:true,depthWrite:false,side:THREE.DoubleSide});sun.add(new THREE.Mesh(sunGeometry,sunMaterial));
 const edge=new THREE.Mesh(new THREE.CylinderGeometry(.50,.50,.055,12),new THREE.MeshStandardMaterial({color:0xc7944f,roughness:1,transparent:true,depthWrite:false}));edge.rotation.x=Math.PI/2;sun.add(edge);sun.visible=false;
 const color=new THREE.Color(),tmp=new THREE.Color();
 return {textures,sun,frame(s){const weights=s.dayWeights||{dusk:1},sum=(prop)=>Object.entries(profiles).reduce((n,[key,v])=>n+(weights[key]||0)*v[prop],0);for(const key of Object.keys(themes))uniforms['w_'+key].value=weights[key]||0;
  for(const [lamp,prop]of [['hemi','hemi'],['sun','key'],['fill','fill'],['bounce','bounce'],['ambient','ambient']])art.globalLights[lamp].intensity=sum(prop);
  for(const[prop,lamp]of [['keyColor','sun'],['sky','hemi']]){color.setRGB(0,0,0);for(const[key,profile]of Object.entries(profiles))color.add(tmp.setHex(profile[prop]).multiplyScalar(weights[key]||0));art.globalLights[lamp].color.copy(color);}
  for(const l of art.lights)l.intensity*=sum('local');for(const m of new Set(skyMaterials))m.emissiveIntensity*=sum('stars');const visible=celestialVisibility(weights);for(const{material,moon:isMoon}of skyOpacity)material.opacity=isMoon?visible.moon:visible.stars;if(moon)moon.visible=visible.moon>.001;sun.visible=visible.sun>.001;sunMaterial.opacity=visible.sun;edge.material.opacity=visible.sun;
 },snapshot:()=>Object.fromEntries(Object.keys(themes).map(k=>[k,uniforms['w_'+k].value]))};
}
