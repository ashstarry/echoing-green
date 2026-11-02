import * as THREE from 'three';
export const ART_PRESETS={
 lantern:{label:'暮色纸灯匣',exposure:1.12,tone:THREE.ACESFilmicToneMapping,hemi:.85,key:2.25,fill:.62,bounce:.35,ambient:.08,ao:.90,bloom:.20,threshold:1.05,local:1.12,emission:1.50,background:['#37333f','#65535b','#44404b']},
 washi:{label:'暖纸剧场',exposure:1.16,tone:THREE.AgXToneMapping,hemi:.95,key:2.65,fill:.60,bounce:.45,ambient:.08,ao:.92,bloom:.21,threshold:1.10,local:1.35,emission:1.65,background:['#242630','#51454a','#302e37']},
 velvet:{label:'紫暮灯市',exposure:1.15,tone:THREE.NeutralToneMapping,hemi:.90,key:2.3,fill:.62,bounce:.45,ambient:.08,ao:.85,bloom:.18,threshold:1.10,local:1.10,emission:1.45,background:['#24222c','#4d4044','#30292f']}
};
function backdrop(colors){
 const c=document.createElement('canvas');c.width=c.height=1024;const x=c.getContext('2d');
 x.fillStyle=colors[0];x.fillRect(0,0,1024,1024);
 const g=x.createRadialGradient(500,490,55,500,490,770);g.addColorStop(0,colors[1]);g.addColorStop(.64,colors[2]);g.addColorStop(1,colors[0]);x.fillStyle=g;x.fillRect(0,0,1024,1024);
 // Broad, almost invisible paper folds live at the margins, away from the miniature.
 x.save();x.filter='blur(24px)';
 x.strokeStyle='rgba(226,195,170,.055)';x.lineWidth=40;x.beginPath();x.moveTo(-180,155);x.bezierCurveTo(60,5,220,270,525,-120);x.stroke();
 x.strokeStyle='rgba(158,174,190,.055)';x.lineWidth=65;x.beginPath();x.moveTo(790,1160);x.bezierCurveTo(1160,840,660,750,1180,290);x.stroke();x.restore();
 const glow=x.createRadialGradient(495,770,15,495,770,400);glow.addColorStop(0,'rgba(205,147,108,.07)');glow.addColorStop(1,'rgba(205,147,108,0)');x.fillStyle=glow;x.fillRect(0,0,1024,1024);
 const d=x.getImageData(0,0,1024,1024);let seed=821;
 for(let y=0;y<1024;y++)for(let z=0;z<1024;z++){const i=(y*1024+z)*4;seed=(Math.imul(seed,1664525)+1013904223)>>>0;const n=(seed/4294967296-.5)*2.3+Math.sin(y*.67+z*.017)*.32;d.data[i]+=n;d.data[i+1]+=n;d.data[i+2]+=n;}
 x.putImageData(d,0,0);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t;
}
function paperTexture(){const c=document.createElement('canvas');c.width=c.height=256;const x=c.getContext('2d'),d=x.createImageData(256,256);let seed=441;for(let y=0;y<256;y++)for(let z=0;z<256;z++){seed=(Math.imul(seed,1664525)+1013904223)>>>0;const v=250+(seed/4294967296-.5)*8+Math.sin(z*.85+y*.06)*1.0;const i=(y*256+z)*4;d.data[i]=d.data[i+1]=d.data[i+2]=v;d.data[i+3]=255;}x.putImageData(d,0,0);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(2,2);return t;}
export function createArtDirection({scene,asset,renderer,rail,registry}){
 const skyIds=new Set(registry.entities.filter(e=>['bird','star','celestial','weather'].includes(e.kind)).map(e=>e.id));asset.traverse(o=>{if(!o.isMesh)return;let p=o;while(p){if(skyIds.has(p.userData.entity_id)){o.castShadow=false;break;}p=p.parent;}});
 const paper=paperTexture(),originals=new Map();asset.traverse(o=>{if(!o.isMesh)return;for(const m of Array.isArray(o.material)?o.material:[o.material])if(!originals.has(m)){originals.set(m,{color:m.color?.clone(),emission:m.emissiveIntensity,roughness:m.roughness,normal:m.normalScale?.clone()});if(m.name==='WEB paper'||m.name==='WEB wood'){m.map=paper;m.roughness=m.name==='WEB paper'?.96:.84;if(m.normalScale)m.normalScale.setScalar(m.name==='WEB paper'?.48:.40);m.needsUpdate=true;}}});
 const group=new THREE.Group();group.name='art.lantern_cabinet';group.userData.static_decoration=true;scene.add(group);
 const xs=rail.points.map(p=>p[0]),ys=rail.points.map(p=>p[1]),cx=(Math.min(...xs)+Math.max(...xs))/2,cz=-(Math.min(...ys)+Math.max(...ys))/2,rx=(Math.max(...xs)-Math.min(...xs))/2+1.10,rz=(Math.max(...ys)-Math.min(...ys))/2+1.10;
 const base=new THREE.Mesh(new THREE.LatheGeometry([new THREE.Vector2(0,-.25),new THREE.Vector2(.98,-.25),new THREE.Vector2(1,-.21),new THREE.Vector2(1,.07),new THREE.Vector2(.985,.10),new THREE.Vector2(0,.10)],128),new THREE.MeshStandardMaterial({color:0x30292a,roughness:.74,metalness:.08}));base.name='CP21 dark craft plinth';base.scale.set(rx,1,rz);base.position.set(cx,-.86,cz);base.castShadow=true;base.receiveShadow=true;group.add(base);
 const rim=new THREE.Mesh(new THREE.CylinderGeometry(1,1,.016,128,1,true),new THREE.MeshStandardMaterial({color:0x967348,roughness:.63,metalness:.25}));rim.name='CP21 fine warm inlay';rim.scale.set(rx*1.001,1,rz*1.001);rim.position.set(cx,-.81,cz);group.add(rim);
 const shadow=new THREE.Mesh(new THREE.PlaneGeometry(150,150),new THREE.ShadowMaterial({color:0x0d0d15,opacity:.28,depthWrite:false}));shadow.name='CP21 soft stage shadow';shadow.rotation.x=-Math.PI/2;shadow.position.y=-1.16;shadow.receiveShadow=true;scene.add(shadow);
 const hemi=new THREE.HemisphereLight(0xb8c6df,0xac6a3d,1),ambient=new THREE.AmbientLight(0xffdeb5,.08);scene.add(hemi,ambient);
 const sun=new THREE.DirectionalLight(0xffd4a1,2.3);sun.position.set(-8,16,7);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-16,right:16,top:13,bottom:-13,near:.5,far:50});sun.shadow.normalBias=.020;sun.shadow.bias=-.0001;sun.shadow.radius=3;scene.add(sun,sun.target);
 const fill=new THREE.DirectionalLight(0x9db9dc,.6);fill.position.set(11,8,-7);const bounce=new THREE.DirectionalLight(0xffbf83,.4);bounce.position.set(1,6,12);scene.add(fill,bounce);
 const lights=[];const rows=[[[0,-.7,2.7],0xff9d42,7.0,4.8],[[-2.6,2.6,3.4],0xffa445,4.6,4.6],[[-5.6,-2.1,2.8],0xffac54,2.8,3.6],[[-2,-5.3,2.9],0xffab4e,3.2,4.0],[[6,2.5,3.1],0xffaa50,3.8,4.1],[[9,-1.4,2.7],0xffae60,2.6,3.5],[[4.4,7,3.5],0xffaa50,2.5,3.6]];
 for(const[p,c,i,d]of rows){const l=new THREE.PointLight(c,i,d,0);l.position.set(p[0],p[2],-p[1]);l.userData.artIntensity=i;l.userData.baseIntensity=i;scene.add(l);lights.push(l);}
 let background=null;function apply(name='lantern'){const p=ART_PRESETS[name]||ART_PRESETS.lantern;renderer.toneMapping=p.tone;renderer.toneMappingExposure=p.exposure;hemi.intensity=p.hemi;ambient.intensity=p.ambient;sun.intensity=p.key;fill.intensity=p.fill;bounce.intensity=p.bounce;for(const l of lights)l.intensity=l.userData.baseIntensity=l.userData.artIntensity*p.local;for(const[m,b]of originals){if(b.emission>0&&!/star|crescent|bird|Moon|Cloud/.test(m.name)){m.emissiveIntensity=b.emission*p.emission;m.needsUpdate=true;}}background?.dispose();background=backdrop(p.background);scene.background=background;return p;}
 const preset=apply(new URLSearchParams(location.search).get('art')||'lantern');return{lights,apply,preset,globalLights:{hemi,ambient,sun,fill,bounce},backgroundFactory:backdrop,base:group,shadow,stage:{center:[cx,cz],radii:[rx,rz],max_y:-.76,min_y:-1.11},resources:{paper,background}};
}
