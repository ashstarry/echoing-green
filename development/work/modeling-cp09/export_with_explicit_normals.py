"""Build a separate, unrigged GLB candidate. Never overwrite the editable master.
Batch static pieces by district; keep residents, animals and key moving props separate.
Color variation is carried by vertex colors, with two shared tangent-space normal maps.
This is geometry/material preparation, not a claim of browser visual parity or FPS.
"""
import bpy,json,math,time,collections
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-09';WORK=ROOT/'work/modeling-cp09';s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();start=time.time()
classes={};material_cache={};groups={};source_tris=0;source_objects=0
normal_paper=bpy.data.images['washi-normal.png'];normal_wood=bpy.data.images['cedar-normal.png']
def category(m):
 if m.name in material_cache:return material_cache[m.name]
 p=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
 color=tuple(p.inputs['Base Color'].default_value) if p else tuple(m.diffuse_color)
 alpha=p.inputs['Alpha'].default_value if p else 1;emission=p.inputs['Emission Strength'].default_value if p else 0;metal=p.inputs['Metallic'].default_value if p else 0
 if alpha<.99:key='glass'
 elif emission>0:key='emissive '+m.name
 elif metal>.3:key='metal'
 elif m.name=='Layered paper water':key='water'
 elif any(x in m.name.lower() for x in ['wood','cedar']):key='wood'
 else:key='paper'
 if key not in classes:
  mat=bpy.data.materials.new('WEB '+key);mat.use_nodes=True;pp=mat.node_tree.nodes['Principled BSDF'];pp.inputs['Base Color'].default_value=(1,1,1,1);pp.inputs['Roughness'].default_value=.84 if key in ['paper','wood'] else (.48 if key in ['water','glass'] else .5);pp.inputs['Metallic'].default_value=.6 if key=='metal' else 0
  vc=mat.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='Color';mat.node_tree.links.new(vc.outputs['Color'],pp.inputs['Base Color'])
  if key=='glass':pp.inputs['Alpha'].default_value=alpha;pp.inputs['Transmission Weight'].default_value=.08;mat.surface_render_method='DITHERED'
  if key.startswith('emissive'):
   pp.inputs['Emission Color'].default_value=p.inputs['Emission Color'].default_value;pp.inputs['Emission Strength'].default_value=emission
  if key in ['paper','wood','water']:
   tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=normal_wood if key=='wood' else normal_paper;n=mat.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.30 if key=='wood' else .26;mat.node_tree.links.new(tex.outputs['Color'],n.inputs['Color']);mat.node_tree.links.new(n.outputs['Normal'],pp.inputs['Normal'])
  classes[key]=mat
 material_cache[m.name]=(key,color);return key,color
def ancestry(o):
 out=[o]
 while out[-1].parent:out.append(out[-1].parent)
 return out
registry=json.loads((OUT/'decision-entities.json').read_text())
node_sources={}
def group_for(o):
 chain=ancestry(o)
 for r in chain:
  if r.get('decision_part_id'):
   key='part/'+r.get('decision_owner','')+'/'+r['decision_part_id'];node_sources[key]=r.name;return key,r.matrix_world.copy()
  if r.get('decision_entity_id'):
   key='entity/'+r['decision_entity_id']+'/body';node_sources[key]=r.name;return key,r.matrix_world.copy()
 return 'district/'+o.users_collection[0].name,None
for index,o in enumerate(list(s.objects)):
 if o.type not in ['MESH','CURVE'] or o.hide_render or o.name=='Indigo studio floor' or any(c.hide_render or c.name.startswith('12_') for c in o.users_collection):continue
 key,origin=group_for(o)
 if key not in groups:groups[key]={'origin':origin,'v':[],'f':[],'mi':[],'uv':[],'color':[],'normal':[],'mats':[],'names':[],'smooth':[]}
 g=groups[key];ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();source_tris+=len(me.loop_triangles);source_objects+=1;g['names'].append(o.name);offset=len(g['v']);matrix=(origin.inverted()@ev.matrix_world) if origin is not None else ev.matrix_world;normal_matrix=matrix.to_3x3().inverted_safe().transposed();g['v'].extend(tuple(matrix@v.co) for v in me.vertices)
 uv=me.uv_layers.active
 for poly in me.polygons:
  m=o.material_slots[poly.material_index].material if len(o.material_slots)>poly.material_index else None
  if m is None:m=bpy.data.materials['Washi | warm ivory']
  mk,col=category(m)
  if mk not in g['mats']:g['mats'].append(mk)
  g['f'].append(tuple(offset+i for i in poly.vertices));g['mi'].append(g['mats'].index(mk));g['smooth'].append(poly.use_smooth)
  axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(poly.normal[i]))]
  for li in poly.loop_indices:
   vv=me.vertices[me.loops[li].vertex_index].co;g['uv'].extend(tuple(uv.data[li].uv) if uv else (vv[axes[0]]*2,vv[axes[1]]*2));g['color'].extend((*col[:3],1.0));g['normal'].append(tuple((normal_matrix@me.corner_normals[li].vector).normalized()))
 ev.to_mesh_clear()
 if source_objects%2000==0:print('COLLECTED',source_objects,flush=True)
# Work on a new scene; the master remains untouched on disk.
old_scene=s;new=bpy.data.scenes.new('CP09 browser asset staging');bpy.context.window.scene=new
mapping={};node_map={}
# Create actual logical entity and movable-part nodes, then retain their parent hierarchy.
for row in registry['entities']:
 old=bpy.data.objects[row['blender_object']];n=bpy.data.objects.new('entity/'+row['id'],None);new.collection.objects.link(n);n.matrix_world=old.matrix_world;n['entity_id']=row['id'];n['source_object']=old.name;n['decision_entity_id']=row['id'];n['kind']=row['kind'];n['actions']=','.join(a['id'] for a in row['actions']);n['runtime_status']='authoring only; clips/executors unimplemented';node_map[old.name]=n
 for pp in row['parts']:
  oldp=bpy.data.objects[pp['blender_object']];p=bpy.data.objects.new('part/'+row['id']+'/'+pp['id'],None);new.collection.objects.link(p);p.matrix_world=oldp.matrix_world;p['part_id']=pp['id'];p['owner_entity']=row['id'];p['control_kind']=pp['control'];p['control_axis']=pp.get('axis') or '';node_map[oldp.name]=p
for oldname,n in node_map.items():
 old=bpy.data.objects[oldname];parent=next((a for a in ancestry(old)[1:] if a.name in node_map),None)
 if parent:
  mw=n.matrix_world.copy();n.parent=node_map[parent.name];n.matrix_world=mw
for key,g in groups.items():
 me=bpy.data.meshes.new(key);me.from_pydata(g['v'],[],g['f']);me.update();ob=bpy.data.objects.new(key,me);new.collection.objects.link(ob)
 if g['origin'] is not None:
  ob.parent=node_map[node_sources[key]];ob.matrix_basis.identity();ob['rig_status']='unrigged staging mesh; editable body parts preserved in master'
 for mk in g['mats']:me.materials.append(classes[mk])
 me.polygons.foreach_set('material_index',g['mi']);me.polygons.foreach_set('use_smooth',g['smooth']);uv=me.uv_layers.new(name='UVMap');uv.data.foreach_set('uv',g['uv']);c=me.color_attributes.new(name='Color',type='BYTE_COLOR',domain='CORNER');c.data.foreach_set('color',g['color']);me.normals_split_custom_set(g['normal']);ob['source_object_count']=len(g['names']);mapping[key]={'source_object_count':len(g['names']),'materials':g['mats'],'source_names':g['names']}
cam=old_scene.camera.copy();cam.data=cam.data.copy();new.collection.objects.link(cam);new.camera=cam;new['asset_status']='Geometry/material candidate only; no runtime, rigs, navigation, baked lighting or FPS validation';new['source_checkpoint']='CP09'
new.render.resolution_x=1672;new.render.resolution_y=941
options={'filepath':str(OUT/'borrowed-wind-town-cp09-web.glb'),'export_format':'GLB','use_active_scene':True,'export_cameras':True,'export_lights':False,'export_animations':False,'export_extras':True,'export_materials':'EXPORT','export_vertex_color':'ACTIVE','export_all_vertex_colors':False,'export_draco_mesh_compression_enable':True,'export_draco_mesh_compression_level':6,'export_draco_position_quantization':16,'export_draco_normal_quantization':12,'export_draco_texcoord_quantization':14,'export_draco_color_quantization':10}
print('EXPORTING',len(groups),'batches',len(classes),'materials',source_tris,'triangles',flush=True)
bpy.ops.export_scene.gltf(**options)
(OUT/'web-batch-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2));(OUT/'web-export-record.json').write_text(json.dumps({'source_objects':source_objects,'source_triangles':source_tris,'batches':len(groups),'logical_entities':len(registry['entities']),'logical_nodes_and_parts':len(node_map),'all_entity_and_part_boundaries_preserved':True,'material_classes':list(classes),'draw_primitives_upper_estimate':sum(len(g['mats']) for g in groups.values()),'normal_maps':['textures/washi-normal.png','textures/cedar-normal.png'],'light_export':False,'baked_lighting':False,'requires_draco_decoder':True,'unrigged':True,'web_fps_measured':False,'export_options':options,'seconds':time.time()-start},ensure_ascii=False,indent=2));print('WEB_ASSET_COMPLETE',time.time()-start,flush=True)
