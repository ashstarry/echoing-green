import * as THREE from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';

// Stable identities, not a random outfit on each visit. Colors are sRGB swatches.
// Garments remain rigid children of the existing torso/head controls.
export const WARDROBE=Object.freeze({
 assistant_gardener:['#b49ba9','#e0ccb3','#526559','beret','apron','#eee0bb'],
 child_listener:['#72959a','#dec8a2','#4e6075','knit','scarf','#e4bb65'],
 child_parent:['#728374','#e4d7b7','#4f5868','none','vest','#beaa89'],
 child_runner:['#c17849','#7b5a48','#535875','knit','scarf','#edcf92'],
 courier:['#b9a372','#596f75','#525c68','cap','satchel','#83614b'],
 customer_one:['#a15f63','#dbc4aa','#666175','beret','scarf','#dfbea0'],
 customer_two:['#858b91','#4d626d','#4e5764','cap','vest','#c8b9a0'],
 customer_three:['#b79c64','#b49b7b','#4f5d68','none','scarf','#799996'],
 elder:['#a793ad','#ded2bb','#695d68','bun','shawl','#dfc4a0'],
 garden_child:['#a8ae75','#c8b398','#5f715f','broad','scarf','#e9c696'],
 gardener:['#7e9273','#ccb17d','#555d68','broad','apron','#c6b393'],
 kite_child:['#b95849','#d3af70','#535975','cap','vest','#d98c66'],
 listener:['#c39d98','#6c5356','#746374','bob','shawl','#e4c5a3'],
 market_browser:['#8b7997','#cbb9ae','#555969','beret','satchel','#ad7f5d'],
 musician:['#557d91','#b7a085','#46576a','cap','scarf','#d3ae71'],
 porch_resident:['#789588','#646b5b','#606478','none','vest','#cebc92'],
 postman:['#536e87','#486377','#515d6c','cap','satchel','#b28656'],
 quiet_reader:['#b99c66','#7a665b','#5b6072','beret','scarf','#7c9395'],
 returning_resident:['#a75445','#ad815e','#595a69','none','scarf','#ead3ab'],
 station_attendant:['#496b7c','#47606c','#454f61','cap','vest','#879da1'],
 station_traveler:['#9f6a65','#c7b8a2','#536273','broad','satchel','#806954'],
 strolling_parent:['#c8b89b','#665c55','#687172','bob','shawl','#829991'],
 upper_diner_0:['#769287','#615449','#526174','none',null,'#cdbb91'],
 upper_diner_1:['#9e616a','#5a4845','#65545d','none',null,'#d4bd92'],
 vendor_bread:['#b7a17b','#e3d4ae','#5b6970','cap','apron','#eddbb8'],
 vendor_flower:['#77907c','#b6a78b','#616779','none','apron','#d9c797'],
 vendor_lamp:['#4f7780','#738591','#535e6b','cap','apron','#cfb795'],
 waiting_passenger:['#8c8980','#665b54','#646679','cap','scarf','#cda376'],
 waiting_passenger_2:['#b19973','#7d6474','#575e70','beret','vest','#829587'],
 water_companion:['#8c9da6','#645e76','#536575','knit','scarf','#d5b09d'],
 water_visitor:['#b36359','#704e59','#665968','beret','shawl','#dfc69d'],
 cyclist:['#8a9d86','#bdaa82','#556e70','cap',null,'#d3b985']
});
const oldCoats=[[.045,.12,.25],[.48,.07,.045],[.25,.32,.24],[.52,.31,.09],[.16,.21,.27],[.48,.30,.28],[.22,.35,.29],[.40,.10,.095]];
const near=(r,g,b,c)=>(r-c[0])**2+(g-c[1])**2+(b-c[2])**2<.00045;
export function applyResidentWardrobe({entities,parts}){
 const report=[];let addedTriangles=0,addedMeshes=0;
 const colorCache=new Map(),matCache=new Map();
 const color=hex=>{if(!colorCache.has(hex))colorCache.set(hex,new THREE.Color(hex));return colorCache.get(hex);};
 const mat=hex=>{if(!matCache.has(hex))matCache.set(hex,new THREE.MeshStandardMaterial({name:'Folded wardrobe paper',color:hex,roughness:.98}));return matCache.get(hex);};
 const box=(x,y,z,sx,sy,sz,rz=0)=>{const g=new THREE.BoxGeometry(sx,sy,sz);g.rotateZ(rz);g.translate(x,y,z);return g;};
 function attach(parent,geometries,hex,name){if(!parent||!geometries.length)return;const g=mergeGeometries(geometries,false);geometries.forEach(x=>x.dispose());const m=new THREE.Mesh(g,mat(hex));m.name=name;m.castShadow=true;m.receiveShadow=true;m.userData.wardrobeDecoration=true;parent.add(m);addedMeshes++;addedTriangles+=(g.index?.count||g.attributes.position.count)/3;}
 for(const[key,look]of Object.entries(WARDROBE)){
  const id='resident.'+key,root=entities.get(id);if(!root)continue;
  const[coat,hat,trousers,shape,accessory,accent]=look;let recolored=0,hatVertices=0;
  root.traverse(m=>{
   if(!m.isMesh||!m.geometry.attributes.color)return;
   let owner=m;while(owner&&!owner.userData.entity_id)owner=owner.parent;if(owner!==root)return; // Books, letters and umbrellas keep their own materials.
   m.geometry=m.geometry.clone();const g=m.geometry,c=g.attributes.color,p=g.attributes.position;
   const isHead=/anim_head|\/head/.test(m.name),hatIndices=new Set();
   for(let i=0;i<c.count;i++){
    const r=c.getX(i),gg=c.getY(i),b=c.getZ(i);let replacement=null;
    if(oldCoats.some(old=>near(r,gg,b,old))){replacement=isHead?hat:coat;if(isHead)hatIndices.add(i);}
    else if(isHead&&key==='elder'&&near(r,gg,b,[.018,.025,.045])&&(p.getZ(i)<.115||p.getY(i)>.16))replacement='#968f86';
    else if(([[.034,.065,.16],[.0262,.0482,.1301],[.055,.12,.19]].some(v=>near(r,gg,b,v)))&&/leg|knee|thigh|shin|hip/.test(m.name))replacement=trousers;
    if(replacement){const v=color(replacement);c.setXYZ(i,v.r,v.g,v.b);recolored++;}
   }
   if(hatIndices.size){
    hatVertices+=hatIndices.size;
    if(['none','bob','bun'].includes(shape)){
     const old=g.index,indices=[];for(let j=0;j<(old?.count||p.count);j+=3){const tri=[0,1,2].map(k=>old?old.getX(j+k):j+k);if(!tri.every(i=>hatIndices.has(i)))indices.push(...tri);}g.setIndex(indices);
    }else{
     let min=Infinity,max=-Infinity;for(const i of hatIndices){min=Math.min(min,p.getY(i));max=Math.max(max,p.getY(i));}
     for(const i of hatIndices){let x=p.getX(i),y=p.getY(i),z=p.getZ(i);const crown=y>min+(max-min)*.58;
      if(shape==='beret'){x*=1.08;y=min+(y-min)*.60+.065;z*=.83;x+=.027;}
      if(shape==='knit'){x*=crown?.99:.76;z*=.73;y=min+(y-min)*1.18;}
      if(shape==='broad'){y+=.025;if(!crown){x*=1.26;z=(z-.06)*1.15+.03;}}
      p.setXYZ(i,x,y,z);
     }
     p.needsUpdate=true;g.computeVertexNormals();
    }
   }
   c.needsUpdate=true;g.computeBoundingBox();g.computeBoundingSphere();
  });
  // Upstairs guests use authored matrix poses rather than the standard controls.
  if(!key.startsWith('upper_diner')){
   const head=parts.get(id+'/anim_head'),torso=parts.get(id+'/anim_torso')||root;
   root.updateWorldMatrix(true,true);const headHeight=head?root.worldToLocal(head.getWorldPosition(new THREE.Vector3())).y:.98;
   const torsoOffset=torso===root?0:root.worldToLocal(torso.getWorldPosition(new THREE.Vector3())).y;
   const collarY=headHeight-.045-torsoOffset;
   if(accessory==='scarf')attach(torso,[box(0,collarY,.035,.31,.065,.29),box(.074,collarY-.15,.199,.085,.28,.021,-.09)],accent,'Folded short scarf');
   if(accessory==='shawl')attach(torso,[box(0,collarY-.06,.025,.36,.09,.29),box(-.105,collarY-.19,.197,.11,.27,.025,-.16),box(.11,collarY-.16,.197,.11,.21,.025,.16)],accent,'Folded shoulder shawl');
   if(accessory==='apron')attach(torso,[box(0,collarY-.32,.214,.27,.41,.022),box(0,collarY-.105,.186,.14,.14,.022),box(0,collarY-.45,.232,.13,.075,.018)],accent,'Paper apron with pocket');
   if(accessory==='vest')attach(torso,[box(-.09,collarY-.25,.205,.13,.35,.022),box(.09,collarY-.25,.205,.13,.35,.022)],accent,'Contrasting vest panels');
   if(accessory==='satchel')attach(torso,[box(.145,collarY-.33,.232,.17,.16,.075),box(.03,collarY-.20,.224,.035,.41,.018,-.40)],accent,'Folded cross-body satchel');
   if(head&&['bob','bun','none'].includes(shape)){
    const hair=key==='elder'?'#aaa49b':key==='porch_resident'?'#5a4b43':'#51433f';
    if(shape==='bun'){const g=new THREE.IcosahedronGeometry(.08,0);g.scale(1,.9,.8);g.translate(0,.22,-.10);attach(head,[g],hair,'Folded hair knot');}
    if(shape==='bob')attach(head,[box(-.133,.07,-.005,.048,.23,.22),box(.133,.07,-.005,.048,.23,.22),box(0,.055,-.12,.23,.21,.04)],hair,'Folded bob silhouette');
   }
  }
  root.userData.wardrobe={coat,hat,trousers,shape,accessory};report.push({id,recolored,hatVertices,shape,accessory});
 }
 return{residents:report,addedMeshes,addedTriangles};
}
