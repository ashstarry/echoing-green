exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
import copy
reg=json.loads((ROOT/'outputs/modeling-checkpoint-09/decision-entities.json').read_text());reg['source_checkpoint']='CP10';reg['preserved_cp09_entity_ids']=len(reg['entities']);reg['cp10_new_entity_ids']=[]
bpy.context.view_layer.update()
for row in reg['entities']:
 o=bpy.data.objects[row['blender_object']];assert o['decision_entity_id']==row['id'];row['position']=list(o.matrix_world.translation)
 for part in row['parts']:part['local_matrix']=[list(r)for r in bpy.data.objects[part['blender_object']].matrix_local]
for a in reg['anchors']:
 for suffix in ['_activity','_approach']:
  if a['id'].endswith(suffix):
   o=bpy.data.objects.get(a['id'][:-len(suffix)])
   if o:a['position']=list(o.matrix_world@Vector((0,-.7,0)))if suffix=='_approach'else list(o.matrix_world.translation)
reg['paths']['station_rail_exclusion']={'record':'station-bend-world-check.json','role':'Authoring clearance for the station bend; not implemented rail motion or navigation'};(OUT/'decision-entities.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2))
for me in bpy.data.meshes:
 if not me.users or not me.polygons or me.uv_layers:continue
 uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  axes=[i for i in range(3)if i!=max(range(3),key=lambda i:abs(p.normal[i]))]
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*2,v[axes[1]]*2)
rec=json.loads((OUT/'revision-record.json').read_text());actual=bpy.data.objects['station_main'].matrix_world.inverted()@bpy.data.objects['station_traveler'].matrix_world.translation;rec['station_rail_repair']['traveler_station_local_x']=actual.x;rec['station_rail_repair']['traveler_station_local_y']=actual.y;(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
s['checkpoint']='CP10 | station bend clearance repair';s['review_status']='Station rail correction for review; runtime and animation remain unimplemented';s.camera.name='Camera_CP10_Main_43deg';s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100;s.render.filepath=str(OUT/'01-overview.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp10.blend'));print('CP10_MASTER_SAVED',flush=True)
