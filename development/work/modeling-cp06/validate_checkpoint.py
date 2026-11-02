import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-06';s=bpy.context.scene;cam=s.camera;rec=json.loads((OUT/'revision-record.json').read_text());circulation=json.loads((OUT/'circulation-check.json').read_text())
c=rec['camera'];camera_ok=all(abs(a-b)<1e-6 for a,b in zip(cam.location,c['location'])) and all(abs(a-b)<1e-6 for a,b in zip(cam.rotation_euler,c['rotation'])) and abs(cam.data.ortho_scale-c['ortho_scale'])<1e-6
names=['tea_house','post_office','west_home','small_wood_home','paper_observatory','quiet_home','greenhouse','station_main','tram_car_front','tram_car_rear','lantern_tree','plaza_ground','pond_boat','duck_0','duck_1']
core={}
for n in names:
 o=bpy.data.objects[n];old=rec['baseline_asset_transforms'][n];core[n]=all(abs(o.matrix_world[i][j]-old[i][j])<1e-5 for i in range(4) for j in range(4))
prior={}
for num in ['01','02','03','04','05']:
 p=ROOT/('outputs/modeling-checkpoint-'+num);f='borrowed-wind-town-cp'+num+'.blend';m=json.loads((p/'file-manifest.json').read_text());prior['CP'+num]=hashlib.sha256((p/f).read_bytes()).hexdigest()==m[f]['sha256']
res=[o for o in s.objects if o.get('entity_id') and any(c.name=='08_Residents_SCALE_PROXIES' for c in o.users_collection)];animals=[o for o in s.objects if o.get('entity_id') and any(c.name=='09_Animals_SCALE_PROXIES' for c in o.users_collection)]
fwd=cam.rotation_euler.to_quaternion()@Vector((0,0,-1));dg=bpy.context.evaluated_depsgraph_get();visibility=[]
for root in res:
 row={'resident':root.name}
 for key,z in [('head',1.08),('upper_body',.75)]:
  p=root.matrix_world@Vector((0,0,z));h,lo,no,fi,o,ma=s.ray_cast(dg,p-fwd*40,fwd,distance=41);a=o
  while a and a.parent:a=a.parent
  row[key]=a==root
 visibility.append(row)
stair_samples=[];old=json.loads((ROOT/'outputs/modeling-checkpoint-05/revision-record.json').read_text());rise=old['terrace']['equal_riser']
for name in ['CP05_lower_stair','CP05_upper_stair','CP06_restaurant_terrace_gallery']:
 root=bpy.data.objects[name];gallery='gallery' in name
 for i in range(5):
  for x in [-.32,0,.32]:
   y=(i+.5)*(rec['gallery']['tread_depth'] if gallery else .20);z=-(i+1)*rec['gallery']['riser_drop'] if gallery else (i+1)*rise;p=root.matrix_world@Vector((x,y,z));h,lo,no,fi,o,ma=s.ray_cast(dg,p+Vector((0,0,.075)),Vector((0,0,-1)),distance=.20)
   stair_samples.append({'name':name,'step':i+1,'across':x,'surface':o.name if o else None,'delta':None if not h else lo.z-p.z,'passed':bool(h and abs(lo.z-p.z)<.04)})
route_results={}
outdoor=['gallery_treads','terrace_main','stairs_to_terrace','stall_approach']
for k,v in circulation['routes'].items():
 limit=.17 if k=='gallery_treads' else .05
 support=all(p['floor_hit'] is not None and abs(p['floor_delta'])<=limit for p in v['samples'])
 route_results[k]={'samples':v['sample_count'],'body_clear':v['body_clear_count']==v['sample_count'],'center_support':support,'fully_occluded_samples':v['no_visible_body_count'],'outdoor_samples_observable':v['no_visible_body_count']==0 if k in outdoor else None,'tested_width':v['tested_width']}
bad=[o.name for o in s.objects if not all(math.isfinite(v) for r in o.matrix_world for v in r)];guide=bpy.data.collections[rec['guide_collection']]
roof=[o for o in bpy.data.objects['tea_house'].children_recursive if o.name.startswith(('tea_house roof','tea_house shingle','tea_house gable'))]
record={'saved_model_reopened':True,'camera_unchanged':camera_ok,'camera_elevation':math.degrees(math.asin(abs(fwd.z))),'selected_core_transforms_unchanged':core,'previous_models_unchanged':prior,'resident_count':len(res),'animal_count':len(animals),'resident_visibility':visibility,'route_results':route_results,'stair_samples':stair_samples,'guides_hidden':guide.hide_render and guide.hide_viewport,'full_roof_visible_in_saved_normal_view':all(not o.hide_render for o in roof),'finite_transforms':not bad,'armatures':sum(o.type=='ARMATURE' for o in s.objects),'animations_or_navigation_implemented':False,'all_town_motion_tested':False,'overall_image_similarity_score':None,'limits':'Static geometry sample checks, selected current poses, and inspection views. Full limb animation, crowds, avoidance, live rendering and all-world routes remain untested.'}
record['passed']=camera_ok and all(core.values()) and all(prior.values()) and len(res)==24 and len(animals)==7 and all(v['head'] and v['upper_body'] for v in visibility) and all(v['body_clear'] and v['center_support'] for v in route_results.values()) and all(route_results[k]['outdoor_samples_observable'] for k in outdoor) and all(v['passed'] for v in stair_samples) and record['guides_hidden'] and record['full_roof_visible_in_saved_normal_view'] and not bad
(OUT/'validation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps({'passed':record['passed'],'routes':route_results,'stair_passes':sum(v['passed'] for v in stair_samples),'stair_total':len(stair_samples),'bad_stairs':[v for v in stair_samples if not v['passed']],'core_unchanged':all(core.values()),'old_files_unchanged':all(prior.values())},ensure_ascii=False,indent=2));assert record['passed']
