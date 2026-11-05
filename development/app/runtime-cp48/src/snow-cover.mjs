import * as THREE from 'three';
// A one-time top depth map keeps the thin paper-snow tint off sheltered floors.
// Existing geometry and lighting remain intact; the runtime adds no draw calls.
export function createSnowCover({scene,asset,renderer}){
 const exposure=new THREE.Scene(),depthMaterial=new THREE.MeshDepthMaterial();
 const eligible=[],skip=/^(resident\.|animal\.|fish\.|bird\.|tram\.|bicycle\.|boat\.|weather\.|moon\.|star\.|kite\.|letter\.|book\.|umbrella\.)/;
 asset.updateWorldMatrix(true,true);
 asset.traverse(o=>{if(!o.isMesh)return;let p=o,excluded=false;while(p){if(!p.visible||skip.test(p.userData.entity_id||''))excluded=true;p=p.parent;}if(excluded)return;
  const copy=new THREE.Mesh(o.geometry,depthMaterial);copy.matrixAutoUpdate=false;copy.matrix.copy(o.matrixWorld);exposure.add(copy);eligible.push(o);
 });
 const camera=new THREE.OrthographicCamera(-13,13,13,-13,.1,24);camera.position.set(0,20,0);camera.up.set(0,0,-1);camera.lookAt(0,0,0);camera.updateMatrixWorld(true);
 const target=new THREE.WebGLRenderTarget(768,768,{minFilter:THREE.NearestFilter,magFilter:THREE.NearestFilter});target.depthTexture=new THREE.DepthTexture(768,768,THREE.UnsignedIntType);
 const previous=renderer.getRenderTarget(),auto=renderer.autoClear;renderer.setRenderTarget(target);renderer.autoClear=true;renderer.clear();renderer.render(exposure,camera);renderer.setRenderTarget(previous);renderer.autoClear=auto;
 const amount={value:0},clones=new Map();
 for(const object of eligible){const materials=(Array.isArray(object.material)?object.material:[object.material]).map(original=>{
  if(!['WEB paper','WEB wood'].includes(original.name))return original;
  if(clones.has(original))return clones.get(original);const material=original.clone();
  material.onBeforeCompile=shader=>{shader.uniforms.uPaperSnow=amount;shader.uniforms.uSnowDepth={value:target.depthTexture};
   shader.vertexShader='varying vec3 vSnowWorld;varying vec3 vSnowNormal;\n'+shader.vertexShader;
   shader.vertexShader=shader.vertexShader.replace('#include <worldpos_vertex>','#include <worldpos_vertex>\nvSnowWorld=(modelMatrix*vec4(transformed,1.0)).xyz;vSnowNormal=normalize(mat3(modelMatrix)*objectNormal);');
   shader.fragmentShader='float snowHash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}\nfloat snowNoise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(snowHash(i),snowHash(i+vec2(1,0)),f.x),mix(snowHash(i+vec2(0,1)),snowHash(i+vec2(1,1)),f.x),f.y);}\nuniform float uPaperSnow;uniform sampler2D uSnowDepth;varying vec3 vSnowWorld;varying vec3 vSnowNormal;\n'+shader.fragmentShader;
   shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
    if(uPaperSnow>0.002){
    vec2 snowUV=vec2(vSnowWorld.x,-vSnowWorld.z)/26.0+0.5;
    float skyHeight=20.0-(texture2D(uSnowDepth,snowUV).r*23.9+0.1);
    float exposed=smoothstep(-0.045,0.025,vSnowWorld.y-skyHeight);
    float grain=0.18+0.52*snowNoise(vSnowWorld.xz*1.6)+0.20*snowNoise(vSnowWorld.xz*5.7);
    float coverage=smoothstep(0.0,0.24,uPaperSnow-grain*0.80)*smoothstep(0.28,0.82,vSnowNormal.y)*exposed;
    diffuseColor.rgb=mix(diffuseColor.rgb,vec3(0.83,0.86,0.83),coverage*(vSnowWorld.y<1.2?0.35:0.86));
    }
   `);
  };material.customProgramCacheKey=()=> 'paper-snow-cover-28';clones.set(original,material);return material;
 });object.material=Array.isArray(object.material)?materials:materials[0];}
 depthMaterial.dispose();
 return{frame:s=>{amount.value=s.eventWeather?.cover||0;},snapshot:()=>({coverage:amount.value,materials:clones.size,depthResolution:768}),dispose:()=>{target.dispose();for(const m of clones.values())m.dispose();}};
}
