const status=document.querySelector('#status'),button=document.querySelector('#run'),iframe=document.querySelector('#town');
const send=async(type,value)=>{const r=await fetch('/qa-chunk',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type,value})});if(!r.ok)throw Error(await r.text());};
button.onclick=async()=>{button.disabled=true;try{const t=iframe.contentWindow.__town;if(!t?.ready)throw Error('小镇还在加载，请稍后');t.setCaptureMode(true);t.reset();t.apply({festival:'quiet'});t.advance(1);
 const meshes=[],geometries={},gids=new Map();t.asset.traverse(o=>{if(!o.isMesh)return;let a=o;while(a){if(!a.visible)return;a=a.parent;}const chain=[];a=o;while(a){if(a.userData.entity_id)chain.push(a.userData.entity_id);a=a.parent;}const logical=t.registry.entities.find(e=>e.id===chain[0])?.state?.owner;if(logical?.startsWith('resident.')&&!chain.includes(logical))chain.push(logical);let gid=gids.get(o.geometry.uuid);if(gid===undefined){gid=gids.size;gids.set(o.geometry.uuid,gid);geometries[gid]={vertices:Array.from(o.geometry.attributes.position.array),indices:o.geometry.index?Array.from(o.geometry.index.array):null};}meshes.push({o,gid,owner:chain[0]||'scenery',chain,name:o.name,materials:(Array.isArray(o.material)?o.material:[o.material]).map(m=>m.name)});});
 status.textContent='正在保存真实模型几何';await send('begin',{meshes:meshes.map(({o,...m})=>m)});let geomBatch={},size=0;const geometryEntries=Object.entries(geometries);for(let n=0;n<geometryEntries.length;n++){const[id,g]=geometryEntries[n],bytes=JSON.stringify(g).length;if(size+bytes>8500000&&size){await send('geometry',geomBatch);geomBatch={};size=0;status.textContent=`保存模型几何 ${n}/${geometryEntries.length}`;}geomBatch[id]=g;size+=bytes;}if(size)await send('geometry',geomBatch);await send('metadata_done',null);let batch=[];const errors=[];
 const macro=d=>t.queuePlan(Object.entries(d).map(([target,action])=>({kind:'macro',target,action})));
 const plan=(target,action)=>{try{t.queuePlan([{kind:'resident',target,action}]);}catch(e){errors.push({target,action,error:e.message});}};
 for(let k=0;k<=1200;k++){
  if(k)for(let i=0;i<5;i++){t.stepOnly();t.present(.5);t.present(1);}
  if(k===8)plan('resident.quiet_reader','reading_break');
  if(k===16){plan('resident.gardener','garden_round');plan('resident.vendor_bread','counter_service');}
  if(k===24)plan('resident.water_visitor','pond_company');
  if(k===32)plan('resident.upper_diner_0','supper_and_rest');
  if(k===48)plan('resident.returning_resident','overlook_round');
  if(k===60)plan('resident.musician','music_interlude');
  if(k===80)plan('resident.postman','letter_round');
  if(k===180)macro({weather:'rain'});
  if(k===260)macro({weather:'clear'});
  if(k===340)macro({day_phase:'day'});
  if(k===380)plan('resident.station_traveler','ride_once');
  if(k===520)macro({day_phase:'night'});
  if(k===560)macro({festival:'fireworks'});
  if(k===720){plan('resident.porch_resident','go_window');plan('resident.water_companion','umbrella_close');}
  if(k===760)macro({weather:'snow'});
  if(k===860){macro({weather:'clear',festival:'quiet'});plan('resident.upper_diner_1','supper_and_rest');}
  if(k===900)plan('resident.water_visitor','pond_company');
  if(k===940)plan('resident.returning_resident','overlook_round');
  if(k===1100){t.requestObjectAction('kite.plaza_kite','calm');t.requestObjectAction('windmill.hill_windwheel','stop');}
  t.scene.updateMatrixWorld(true);const state=t.getState();batch.push({time:state.time,state,matrices:meshes.map(m=>m.o.matrixWorld.elements.slice()),lines:(()=>{const lines=[];t.scene.traverse(o=>{if(o.isLine&&o.userData.runtimeRole==='kite_tether'){const a=o.geometry.attributes.position,m=o.matrixWorld.elements,points=[];for(let j=0;j<a.count;j++){const x=a.getX(j),y=a.getY(j),z=a.getZ(j);points.push([m[0]*x+m[4]*y+m[8]*z+m[12],m[1]*x+m[5]*y+m[9]*z+m[13],m[2]*x+m[6]*y+m[10]*z+m[14]]);}lines.push(points);}});return lines;})()});
  if(batch.length===10){await send('frames',batch);batch=[];status.textContent=`实际模拟 ${Math.round(state.time)} / 300 秒；已保存 ${k+1} 帧`;
   if(k%40===39)t.render();await new Promise(r=>setTimeout(r,0));}
 }
 if(batch.length)await send('frames',batch);const summary={done:true,frames:1201,interval:.25,seconds:t.getState().time,meshes:meshes.length,errors,runtimeBindings:t.runtimeBindings(),finalJobs:t.getState().intentRuntime.jobs};await send('end',summary);status.textContent='完成：已保存 1201 帧真实模型矩阵与动作状态。';
}catch(e){status.textContent='检查失败：'+e.message;button.disabled=false;}};
