import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-09';old=bpy.context.scene;reg=json.loads((OUT/'decision-entities.json').read_text());expected=json.loads((OUT/'web-asset-validation.json').read_text());positions={e['id']:bpy.data.objects[e['blender_object']].matrix_world.translation.copy() for e in reg['entities']};new=bpy.data.scenes.new('CP09 GLB control verification');bpy.context.window.scene=new
source_parts={(e['id'],p['id']):bpy.data.objects[p['blender_object']].matrix_world.translation.copy() for e in reg['entities'] for p in e['parts']}
new.world=old.world.copy();new.view_settings.view_transform=old.view_settings.view_transform;new.view_settings.look=old.view_settings.look;new.view_settings.exposure=old.view_settings.exposure;new.view_settings.gamma=old.view_settings.gamma
for o in old.objects:
 if o.type=='LIGHT' or o==old.camera or o.name=='Indigo studio floor':
  n=o.copy();n.data=o.data.copy();new.collection.objects.link(n);n.parent=None;n.matrix_world=o.matrix_world
  if o==old.camera:new.camera=n
bpy.ops.import_scene.gltf(filepath=str(OUT/'borrowed-wind-town-cp09-web.glb'));bpy.context.view_layer.update();entities={o['entity_id']:o for o in new.objects if o.get('entity_id')};parts={(o['owner_entity'],o['part_id']):o for o in new.objects if o.get('part_id')};assert set(entities)==set(positions)
part_position_errors={key:(parts[key].matrix_world.translation-p).length for key,p in source_parts.items()};assert max(part_position_errors.values())<1e-4
position_errors={k:(entities[k].matrix_world.translation-p).length for k,p in positions.items()};assert max(position_errors.values())<1e-4
for e in reg['entities']:
 if e.get('parent_entity'):assert entities[e['id']].parent==entities[e['parent_entity']]
 for p in e['parts']:assert parts[(e['id'],p['id'])].parent==entities[e['id']]
meshes=[o for o in new.objects if o.type=='MESH' and not o.name.startswith('Indigo studio floor')];triangles=0
for o in meshes:o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
assert triangles==expected['triangles'];bad=[o.name for o in new.objects if not all(math.isfinite(v) for row in o.matrix_world for v in row)];assert not bad
def probe(o):
 points=[(x,v.index,x.matrix_world@v.co) for x in o.children_recursive if x.type=='MESH' for v in x.data.vertices];obj,idx,p=max(points,key=lambda q:(q[2]-o.matrix_world.translation).length_squared);return obj,idx
proof=[]
for key,axis in [(('windmill.hill_windwheel','rotor'),'Y'),(('bicycle.street_bicycle','bicycle_wheel_front'),'Y')]:
 o=parts[key];obj,i=probe(o);saved=o.matrix_basis.copy();before=obj.matrix_world@obj.data.vertices[i].co;o.matrix_basis=saved@Matrix.Rotation(.37,4,axis);bpy.context.view_layer.update();after=obj.matrix_world@obj.data.vertices[i].co;o.matrix_basis=saved;bpy.context.view_layer.update();restored=obj.matrix_world@obj.data.vertices[i].co;proof.append({'part':list(key),'movement':(after-before).length,'restore_error':(restored-before).length,'passed':(after-before).length>.02 and(restored-before).length<1e-5})
assert all(p['passed'] for p in proof)
record={'passed':True,'decoded_triangles':triangles,'entities_preserved':len(entities),'movable_parts_preserved':len(parts),'max_entity_position_error':max(position_errors.values()),'max_part_position_error':max(part_position_errors.values()),'hierarchies_preserved':True,'actual_post_import_transform_checks':proof,'glb_sha256':hashlib.sha256((OUT/'borrowed-wind-town-cp09-web.glb').read_bytes()).hexdigest(),'source_model_sha256':hashlib.sha256((OUT/'borrowed-wind-town-cp09.blend').read_bytes()).hexdigest(),'render_lighting':'Blender master lights reused for asset inspection; not in GLB and not a browser screenshot','api_executed':False,'runtime_implemented':False,'browser_fps_measured':False};(OUT/'glb-roundtrip-check.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
new.cycles.device='CPU';new.render.threads_mode='FIXED';new.render.threads=4
if old.compositing_node_group:
 new.compositing_node_group=old.compositing_node_group.copy()
 for n in new.compositing_node_group.nodes:
  if n.bl_idname=='CompositorNodeRLayers':n.scene=new
new.render.engine='CYCLES';new.cycles.samples=48;new.cycles.use_denoising=True;new.render.resolution_x=1672;new.render.resolution_y=941;new.render.resolution_percentage=100;new.render.filepath=str(OUT/'09-glb-roundtrip.png');bpy.ops.render.render(write_still=True);print('GLB_ROUNDTRIP_COMPLETE',json.dumps(record),flush=True)
