import bpy,json,hashlib,array
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'work/lighting-cp11';OUT=ROOT/'outputs/lighting-checkpoint-11'
exec(compile((WORK/'scene_signature.py').read_text(),'<signature>','exec'))
def evaluated_geometry(scene):
 dg=bpy.context.evaluated_depsgraph_get();rows={};total=0
 for o in scene.objects:
  if o.type not in ['MESH','CURVE']:continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();h=hashlib.sha256();a=array.array('f',[0.0])*(len(me.vertices)*3);me.vertices.foreach_get('co',a);h.update(a.tobytes());a=array.array('i',[0])*(len(me.loop_triangles)*3);me.loop_triangles.foreach_get('vertices',a);h.update(a.tobytes());rows[o.name]={'hash':h.hexdigest(),'world':[round(v,7)for r in ev.matrix_world for v in r]}
  if not o.hide_render and not any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):total+=len(me.loop_triangles)
  ev.to_mesh_clear()
 return rows,total
master=OUT/'borrowed-wind-town-cp11.blend';new_sig=scene_signature(bpy.context.scene);new_geo,tris=evaluated_geometry(bpy.context.scene);rig=json.loads((OUT/'lighting-rig.json').read_text());reg=json.loads((OUT/'decision-entities.json').read_text());entities={o['decision_entity_id']for o in bpy.context.scene.objects if o.get('decision_entity_id')};parts={(o['decision_owner'],o['decision_part_id'])for o in bpy.context.scene.objects if o.get('decision_part_id')};assert entities=={e['id']for e in reg['entities']};assert len(parts)==76
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'outputs/modeling-checkpoint-10/borrowed-wind-town-cp10.blend'));old_sig=scene_signature(bpy.context.scene);old_geo,old_tris=evaluated_geometry(bpy.context.scene);changed=sorted(k for k in set(new_geo)|set(old_geo)if new_geo.get(k)!=old_geo.get(k));same_sig=new_sig==old_sig
prior={}
for i in range(1,11):
 p=ROOT/('outputs/modeling-checkpoint-%02d'%i);name='borrowed-wind-town-cp%02d.blend'%i;manifest=json.loads((p/'file-manifest.json').read_text());prior['CP%02d'%i]=hashlib.sha256((p/name).read_bytes()).hexdigest()==manifest[name]['sha256']
inherited={}
for name in ['validation.json','full-body-contact-check.json','station-bend-world-check.json','control-clearance-check.json','circulation-check.json']:
 p=ROOT/'outputs/modeling-checkpoint-10'/name;r=json.loads(p.read_text());inherited[name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'passed':r.get('passed','See route samples in circulation-check.json')}
record={'passed':same_sig and not changed and all(prior.values()) and tris==old_tris,'source_model_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'cp10_sha256':hashlib.sha256((ROOT/'outputs/modeling-checkpoint-10/borrowed-wind-town-cp10.blend').read_bytes()).hexdigest(),'camera_geometry_hierarchy_visibility_equal':same_sig,'evaluated_geometry_equal':not changed,'changed_geometry_objects':changed,'render_triangles':tris,'cp10_render_triangles':old_tris,'previous_models_unchanged':prior,'entities':len(entities),'parts':len(parts),'active_cycles_lights':rig['active_light_count'],'inherited_cp10_spatial_checks':inherited,'new_collision_runs_performed':False,'reason':'No mesh, curve, object transform, hierarchy or visibility changes; evaluated geometry compared directly to CP10. Existing spatial test scope is inherited, not expanded.','browser_visual_qa':False,'browser_fps_measured':False,'animation_or_simulation_implemented':False};(OUT/'validation.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2),flush=True);assert record['passed']
