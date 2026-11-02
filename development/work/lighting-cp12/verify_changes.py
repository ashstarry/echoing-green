import bpy,json,hashlib,array,math
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'work/lighting-cp12';OUT=ROOT/'outputs/lighting-checkpoint-12';s=bpy.context.scene
exec(compile((W/'scene_signature.py').read_text(),'<signature>','exec'))
def geometry(scene):
 dg=bpy.context.evaluated_depsgraph_get();rows={};total=0
 for o in scene.objects:
  if o.type not in ['MESH','CURVE']:continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();h=hashlib.sha256();v=array.array('f',[0.0])*(len(me.vertices)*3);me.vertices.foreach_get('co',v);h.update(v.tobytes());a=array.array('i',[0])*(len(me.loop_triangles)*3);me.loop_triangles.foreach_get('vertices',a);h.update(a.tobytes());rows[o.name]={'hash':h.hexdigest(),'world':[round(v,7)for r in ev.matrix_world for v in r]}
  if not o.hide_render and not any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):total+=len(me.loop_triangles)
  ev.to_mesh_clear()
 return rows,total
def triangles(objects):
 out=[]
 for o in objects:
  o.data.calc_loop_triangles()
  out.extend(sorted(tuple(round(x,6)for x in o.matrix_world@o.data.vertices[i].co)for i in t.vertices)for t in o.data.loop_triangles)
 return sorted(out)
reg=json.loads((OUT/'decision-entities.json').read_text());notes=json.loads((OUT/'revision-record.json').read_text());new_sig=scene_signature(s);new_geo,tris=geometry(s)
ids={o['decision_entity_id']for o in s.objects if o.get('decision_entity_id')};parts={(o['decision_owner'],o['decision_part_id'])for o in s.objects if o.get('decision_part_id')};assert ids=={e['id']for e in reg['entities']};assert len(ids)==191 and len(parts)==82
wingproof=[];wing_triangles={}
for row in notes['bird_wing_changes']:
 objs=[bpy.data.objects[name].children[0]for name in row['parts']];wing_triangles[row['removed_wing_mesh']]=triangles(objs)
 for name in row['parts']:
  p=bpy.data.objects[name];o=p.children[0];saved=p.matrix_basis.copy();before=[o.matrix_world@v.co for v in o.data.vertices];p.matrix_basis=saved@Matrix.Rotation(math.radians(20),4,'X');bpy.context.view_layer.update();after=[o.matrix_world@v.co for v in o.data.vertices];p.matrix_basis=saved;bpy.context.view_layer.update();restored=[o.matrix_world@v.co for v in o.data.vertices];move=max((a-b).length for a,b in zip(after,before));err=max((a-b).length for a,b in zip(restored,before));wingproof.append({'part':name,'vertex_motion':move,'restore_error':err,'passed':move>.01 and err<1e-6})
starrows=[e for e in reg['entities']if e['kind']=='star'];star_mats=[bpy.data.objects[e['blender_object']].active_material for e in starrows];moon=[m for m in bpy.data.materials if 'moon' in m.name.lower()];allm=star_mats+moon
before={m.name:m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value for m in allm};starproof=[]
for m in star_mats:
 p=m.node_tree.nodes['Principled BSDF'];saved=p.inputs['Emission Strength'].default_value;p.inputs['Emission Strength'].default_value=0
 unrelated=all(q.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value==before[q.name]for q in allm if q!=m)
 p.inputs['Emission Strength'].default_value=saved;starproof.append({'material':m.name,'other_emissions_unchanged':unrelated,'restored':p.inputs['Emission Strength'].default_value==saved})
assert len({m.name for m in star_mats})==5 and all(x['passed']for x in wingproof) and all(x['other_emissions_unchanged']and x['restored']for x in starproof)
(OUT/'sky-control-check.json').write_text(json.dumps({'passed':True,'bird_wing_rotate_restore':wingproof,'star_independent_emission':starproof,'scope':'Actual transform/material mutation and restore only; no animation, flight-path or continuous clearance proof.'},indent=2))
assert scene_signature(s)==new_sig
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'outputs/lighting-checkpoint-11/borrowed-wind-town-cp11.blend'));old_sig=scene_signature(bpy.context.scene);old_geo,old_tris=geometry(bpy.context.scene)
removed={r['removed_wing_mesh']for r in notes['bird_wing_changes']};star_names=set(notes['stars']);unexpected=[]
for name,old in old_sig['objects'].items():
 if name in removed:continue
 new=new_sig['objects'].get(name)
 if name in star_names:
  old=dict(old);new=dict(new)
  for key in ['entity_id']:old.pop(key,None);new.pop(key,None)
 if new!=old:unexpected.append(name)
changed=[name for name in old_geo if name not in removed and old_geo[name]!=new_geo.get(name)]
same_wings=all(triangles([bpy.data.objects[name]])==faces for name,faces in wing_triangles.items())
new_geo_names=sorted(set(new_geo)-set(old_geo));allowed_new=all(n.startswith(('CP12 floating lamp tray','CP12 lamp corner post','CP12 lamp top frame','CP12 folded lamp paper','CP12 paper_bird_'))for n in new_geo_names)
prior={}
for i in range(1,12):
 p=ROOT/('outputs/lighting-checkpoint-11'if i==11 else 'outputs/modeling-checkpoint-%02d'%i);name='borrowed-wind-town-cp%02d.blend'%i;manifest=json.loads((p/'file-manifest.json').read_text());prior['CP%02d'%i]=hashlib.sha256((p/name).read_bytes()).hexdigest()==manifest[name]['sha256']
samecam=new_sig['camera']==old_sig['camera'];samecollections=new_sig['collections']==old_sig['collections']
record={'passed':not unexpected and not changed and same_wings and allowed_new and samecam and samecollections and all(prior.values()),'source_model_sha256':hashlib.sha256((OUT/'borrowed-wind-town-cp12.blend').read_bytes()).hexdigest(),'camera_unchanged':samecam,'collection_visibility_unchanged':samecollections,'unexpected_object_changes':unexpected,'unexpected_evaluated_geometry_changes':changed,'original_bird_world_triangles_preserved':same_wings,'new_geometry_objects':new_geo_names,'new_geometry_only_water_lanterns_and_split_wings':allowed_new,'render_triangles':tris,'cp11_render_triangles':old_tris,'added_triangles':tris-old_tris,'previous_models_unchanged':prior,'entities':len(ids),'parts':len(parts),'inherited_cp10_scope':'Unchanged old architecture, terrain, residents and routes retain CP10 local spatial evidence. Current full contacts rerun with new water lanterns separately. No expanded whole-world or continuous-animation guarantee.','runtime_implemented':False,'browser_fps_measured':False}
(OUT/'validation.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2),flush=True);assert record['passed']
