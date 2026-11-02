exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
import copy,hashlib
reg=json.loads((ROOT/'outputs/modeling-checkpoint-08/decision-entities.json').read_text());old={e['id']:e for e in reg['entities']};rows=[]
def lineage(o):
 while o:
  yield o;o=o.parent
bpy.context.view_layer.update()
for root in sorted([o for o in s.objects if o.get('decision_entity_id')],key=lambda o:o['decision_entity_id']):
 eid=root['decision_entity_id'];kind=root['decision_kind'];row=copy.deepcopy(old.get(eid,{}))
 if not row:
  acts=json.loads(root.get('decision_actions','[]'));row={'id':eid,'label':root.name,'kind':kind,'blender_object':root.name,'actions':[{'id':a,'implementation':'declared; executor/animation not implemented','preconditions':'Executor validates eligible state, occupancy, reachability and conflicts.','parameters':{'target':'Optional eligible entity or anchor ID'}} for a in acts],'state':{},'anchors':[],'runtime_ready':False,'requires_animation_binding':False}
  if kind in ['tree','plant']:row['actuation']='foliage_part_and_material'
  if kind=='light':row['actuation']='entity_material_and_light';row['state']={'on':True};row['material_override']='Per-entity material/light state; never mutate shared material globally.'
  for a in row['actions']:
   if a['id']=='set_brightness':a['parameters']={'level':['off','low','medium','high']}
   if a['id']=='set_warmth':a['parameters']={'palette':['warm','neutral','cool']}
   if a['id']=='bloom_state':a['parameters']={'phase':['closed','opening','open']}
 row['position']=list(root.matrix_world.translation);row['blender_object']=root.name;row['parent_entity']=next((o['decision_entity_id'] for o in list(lineage(root))[1:] if o.get('decision_entity_id')),None)
 row['parts']=[{'id':p['decision_part_id'],'blender_object':p.name,'control':p.get('control_kind'),'axis':p.get('control_axis'),'local_matrix':[list(r) for r in p.matrix_local]} for p in root.children_recursive if p.get('decision_part_id') and p.get('decision_owner')==eid]
 if kind=='resident':row['body_component_sources']=[o.name for o in root.children_recursive if o.type=='MESH' and next((a for a in lineage(o) if a.get('decision_entity_id')),None)==root]
 if root.name=='station_entry_door':row['actuation']='slide_local_X';row['travel_limit']={'axis':'local X','closed':0,'open_delta':.74};row['hinge_rotation_used']=False
 if root.name=='pond_boat':row['geometry_note']='Hollow hull, interior benches and independently pivoted oars. Liquid intersection is intentional; not a physics implementation.'
 if root.name=='plaza_kite':row['tether_note']='Explicit tether control node and hand endpoint; deformation and animated hand attachment remain unimplemented.'
 root['decision_manifest']='decision-entities.json';root['decision_status']='authoring_only_runtime_unimplemented';rows.append(row)
assert set(old).issubset({e['id'] for e in rows})
for a in reg['anchors']:
 for suffix in ['_activity','_approach']:
  if a['id'].endswith(suffix):
   o=bpy.data.objects.get(a['id'][:-len(suffix)])
   if o:a['position']=list(o.matrix_world@Vector((0,-.7,0))) if suffix=='_approach' else list(o.matrix_world.translation)
reg['entities']=rows;reg['entity_count']=len(rows);reg['source_checkpoint']='CP09';reg['preserved_cp08_entity_ids']=len(old);reg['new_entity_ids']=sorted({r['id'] for r in rows}-set(old));reg['parts_count']=sum(len(r['parts']) for r in rows);reg['paths']['existing_local_routes']=json.loads((OUT/'revision-record.json').read_text())['routes'];reg['rules'].append('Current-pose geometry validation does not validate future action animation; every action needs swept contact and support checks before release.')
(OUT/'decision-entities.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2))
rec=json.loads((OUT/'revision-record.json').read_text());rec['decision_authoring']={'entity_count':len(rows),'parts_count':reg['parts_count'],'cp08_ids_preserved':len(old),'api_calls':0,'status':'Authoring contract only; current modeled poses validated separately'};rec['render_verification']={'renderer':'Cycles CPU for final delivery','reason':'CPU used for final renders; some black surfaces were traced to duplicate/copanar source geometry and repaired separately','visual_target':'Approved v3 soft-light, no baseline replacement'};(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
s['checkpoint']='CP09 | contact repairs, western silhouette, paper gardens and warm lighting';s['review_status']='Model and current poses for user review; animation/runtime not implemented';s['simulation_status']='unimplemented';s.camera.name='Camera_CP09_Main_43deg';s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100;s.cycles.samples=96;s.render.filepath=str(OUT/'01-overview.png');bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp09.blend'));print('CP09_MASTER_SAVED',len(rows),reg['parts_count'],flush=True)
