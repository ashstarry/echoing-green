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
record={'passed':True,'decoded_triangles':triangles,'entities_preserved':len(entities),'movable_parts_preserved':len(parts),'max_entity_position_error':max(position_errors.values()),'max_part_position_error':max(part_position_errors.values()),'hierarchies_preserved':True,'actual_post_import_transform_checks':proof,'glb_sha256':hashlib.sha256((OUT/'borrowed-wind-town-cp09-web.glb').read_bytes()).hexdigest(),'source_model_sha256':hashlib.sha256((OUT/'borrowed-wind-town-cp09.blend').read_bytes()).hexdigest(),'render_lighting':'Blender master lights reused for asset inspection; not in GLB and not a browser screenshot','api_executed':False,'runtime_implemented':False,'browser_fps_measured':False};None

q=new.camera.rotation_euler.to_quaternion();right=q@Vector((1,0,0));up=q@Vector((0,1,0));fwd=q@Vector((0,0,-1));scale=new.camera.data.ortho_scale;dg=bpy.context.evaluated_depsgraph_get()
for x,y in [(1167,240),(1167,245),(1169,248),(1166,235),(1174,249)]:
 p=new.camera.location+right*((x/1672-.5)*scale)+up*((.5-y/941)*scale/(1672/941));h,loc,no,fi,o,ma=new.ray_cast(dg,p,fwd,distance=80)
 if o:
  poly=o.data.polygons[fi];m=o.material_slots[poly.material_index].material;cols=o.data.color_attributes.active_color;colors=[list(cols.data[i].color)for i in poly.loop_indices]if cols else[];uv=o.data.uv_layers.active;uvs=[list(uv.data[i].uv)for i in poly.loop_indices]if uv else[]
  print('DARK',x,y,o.name,fi,m.name,list(no),'COLORS',colors,'UV',uvs,'WORLD',list(loc),flush=True)
