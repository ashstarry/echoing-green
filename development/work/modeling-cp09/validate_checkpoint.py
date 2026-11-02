import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-09';s=bpy.context.scene;cam=s.camera;rec=json.loads((OUT/'revision-record.json').read_text());registry=json.loads((OUT/'decision-entities.json').read_text());circulation=json.loads((OUT/'circulation-check.json').read_text())
s['checkpoint']='CP09 | reference spatial and ecosystem revision';s['review_status']='Environment art and Decision authoring interface ready for review; no runtime';s['simulation_status']='unimplemented'
aliases={e['blender_object']:e['id'] for e in registry['entities']}
for e in registry['entities']:
 if e['state'].get('occupied_by') in aliases:e['state']['occupied_by']=aliases[e['state']['occupied_by']]
 e['position']=list(bpy.data.objects[e['blender_object']].matrix_world.translation)
(OUT/'decision-entities.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2));None  # Read-only model validation; no resave
camera_ok=all(abs(a-b)<1e-6 for a,b in zip(cam.location,rec['cp07_camera']['location'])) and all(abs(a-b)<1e-6 for a,b in zip(cam.rotation_euler,rec['cp07_camera']['rotation'])) and abs(cam.data.ortho_scale-rec['cp07_camera']['ortho_scale'])<1e-6
prior={}
for num in ['01','02','03','04','05','06','07','08']:
 p=ROOT/('outputs/modeling-checkpoint-'+num);f='borrowed-wind-town-cp'+num+'.blend';m=json.loads((p/'file-manifest.json').read_text());prior['CP'+num]=hashlib.sha256((p/f).read_bytes()).hexdigest()==m[f]['sha256']
routes={}
for k,v in circulation['routes'].items():
 limit=.17 if k=='gallery_treads' else .05;routes[k]={'samples':v['sample_count'],'body_clear':v['body_clear_count']==v['sample_count'],'floor_support':all(p['floor_hit'] is not None and abs(p['floor_delta'])<=limit for p in v['samples']),'fully_occluded_samples':v['no_visible_body_count']}
dg=bpy.context.evaluated_depsgraph_get();rise=json.loads((ROOT/'outputs/modeling-checkpoint-05/revision-record.json').read_text())['terrace']['equal_riser'];stairs=[]
for name in ['CP05_lower_stair','CP05_upper_stair','CP06_restaurant_terrace_gallery']:
 root=bpy.data.objects[name];gallery='gallery'in name
 for i in range(5):
  for x in [-.32,0,.32]:
   y=(i+.5)*(rec['gallery']['tread_depth'] if gallery else .20);z=-(i+1)*rec['gallery']['riser_drop'] if gallery else(i+1)*rise;p=root.matrix_world@Vector((x,y,z));h,lo,no,fi,o,ma=s.ray_cast(dg,p+Vector((0,0,.075)),Vector((0,0,-1)),distance=.20);stairs.append({'stair':name,'step':i+1,'across':x,'hit':o.name if o else None,'passed':bool(h and abs(lo.z-p.z)<.04)})
entity_issues=[];ids=[e['id'] for e in registry['entities']];assert len(ids)==len(set(ids))
for e in registry['entities']:
 root=bpy.data.objects.get(e['blender_object'])
 if not root or root.get('decision_entity_id')!=e['id']:entity_issues.append(e['id']+' missing or mismatched root')
 for p in e['parts']:
  o=bpy.data.objects.get(p['blender_object'])
  if not o or o.get('decision_part_id')!=p['id'] or o.get('decision_owner')!=e['id']:entity_issues.append(e['id']+'/'+p['id']+' missing part')
 for key,v in e['state'].items():
  if key in ['carrier','rider','occupied_by'] and v and v not in ids:entity_issues.append(e['id']+' invalid '+key+' '+str(v))
unbound=[o.name for o in s.objects if (o.get('movable') or o.get('movable_part')) and not(o.get('decision_entity_id') or o.get('decision_part_id'))]
# Apply and restore real transforms to selected control nodes; no animation/API is implied.
def sample_ref(o):
 origin=o.matrix_world.translation;points=[]
 for x in [o]+list(o.children_recursive):
  if x.type=='MESH':points.extend((x.name,'MESH',v.index,0,x.matrix_world@v.co) for v in x.data.vertices)
  if x.type=='CURVE':
   for si,sp in enumerate(x.data.splines):points.extend((x.name,'CURVE',vi,si,x.matrix_world@Vector(v.co[:3])) for vi,v in enumerate(sp.points))
 return max(points,key=lambda p:(p[4]-origin).length_squared)[:4]
def sample(ref):
 name,kind,index,si=ref;o=bpy.data.objects[name];p=o.data.vertices[index].co if kind=='MESH' else Vector(o.data.splines[si].points[index].co[:3]);return o.matrix_world@p
proof=[]
for n,axis,delta in [('hill_windwheel__rotor',1,.37),('station_entry_door',0,.74),('bicycle_wheel_front',1,.45)]:
 o=bpy.data.objects[n];saved=o.matrix_basis.copy();ref=sample_ref(o);before=sample(ref);
 if n=='station_entry_door':o.matrix_basis=saved@Matrix.Translation((delta,0,0))
 else:o.rotation_euler[axis]+=delta
 bpy.context.view_layer.update();after=sample(ref);o.matrix_basis=saved;bpy.context.view_layer.update();restored=sample(ref);proof.append({'node':n,'point_moved':(after-before).length,'restore_error':(restored-before).length,'passed':(after-before).length>.001 and(restored-before).length<1e-5})
bike=bpy.data.objects['street_bicycle'];rider=bpy.data.objects['cyclist'];saved=bike.matrix_world.copy();ref=sample_ref(rider);before=sample(ref);shift=Vector((.2,0,0));bike.location+=shift;bpy.context.view_layer.update();after=sample(ref);bike.matrix_world=saved;bpy.context.view_layer.update();proof.append({'node':'bicycle with attached cyclist','motion_error':(after-before-shift).length,'passed':(after-before-shift).length<1e-5 and rider.parent==bike})
roof=[o for o in bpy.data.objects['tea_house'].children_recursive if o.name.startswith(('tea_house roof','tea_house shingle','tea_house gable'))];bad=[o.name for o in s.objects if not all(math.isfinite(v) for row in o.matrix_world for v in row)]
record={'camera_unchanged':camera_ok,'previous_models_unchanged':prior,'resident_count':sum(e['kind']=='resident' for e in registry['entities']),'animal_bird_fish_count':sum(e['kind']in ['animal','bird','fish'] for e in registry['entities']),'route_results':routes,'stair_samples':stairs,'resident_visibility':circulation['existing_resident_visibility'],'full_roof_preserved':all(not o.hide_render for o in roof),'finite_transforms':not bad,'decision_authoring':{'entities':len(ids),'parts':sum(len(e['parts']) for e in registry['entities']),'issues':entity_issues,'marked_movable_without_binding':unbound,'actual_transform_and_restore_checks':proof,'provider_call_executed':False,'actions_implemented':False},'limits':'Static geometry and authoring checks only. No full-body clips, all-town navigation, crowd behavior, provider integration or browser FPS validation.'}
outdoor=['gallery_treads','terrace_main','stairs_to_terrace','stall_approach'];record['passed']=camera_ok and all(prior.values()) and not entity_issues and not unbound and all(x['passed'] for x in proof) and all(x['passed'] for x in stairs) and all(v['body_clear'] and v['floor_support'] for v in routes.values()) and all(routes[k]['fully_occluded_samples']==0 for k in outdoor) and all(v['head'] and v['upper_body'] for v in record['resident_visibility']) and record['full_roof_preserved'] and not bad
contacts=json.loads((OUT/'full-body-contact-check.json').read_text());controls=json.loads((OUT/'control-clearance-check.json').read_text());record['full_body_current_pose_check']=contacts['passed'];record['sampled_control_clearance']=controls['passed'];record['passed']=record['passed'] and contacts['passed'] and controls['passed'];record['source_model_sha256']=hashlib.sha256((OUT/'borrowed-wind-town-cp09.blend').read_bytes()).hexdigest()
(OUT/'validation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps({'passed':record['passed'],'entity_issues':entity_issues,'unbound':unbound,'proof':proof,'bad_stairs':[x for x in stairs if not x['passed']],'route_results':routes},ensure_ascii=False,indent=2));assert record['passed']
