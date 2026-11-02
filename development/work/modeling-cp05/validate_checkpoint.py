import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-05';s=bpy.context.scene;cam=s.camera
rec=json.loads((OUT/'revision-record.json').read_text());m=json.loads((OUT/'model-manifest.json').read_text());c=rec['camera_unchanged'];fwd=cam.rotation_euler.to_quaternion()@Vector((0,0,-1));view=Vector((-fwd.x,-fwd.y,0)).normalized()
camera_ok=all(abs(a-b)<1e-6 for a,b in zip(cam.location,c['location'])) and all(abs(a-b)<1e-6 for a,b in zip(cam.rotation_euler,c['rotation'])) and abs(cam.data.ortho_scale-c['ortho_scale'])<1e-6
tea=bpy.data.objects['tea_house'];angle=math.degrees(math.acos((tea.rotation_euler.to_quaternion()@Vector((0,-1,0))).dot(view)))
core_names=['post_office','west_home','small_wood_home','paper_observatory','quiet_home','greenhouse','station_main','tram_car_front','tram_car_rear','lantern_tree','plaza_ground','pond_boat','duck_0','duck_1']
unchanged_core={}
for n in core_names:
 o=bpy.data.objects[n];old=rec['baseline_asset_transforms'][n]['matrix_world'];unchanged_core[n]=all(abs(o.matrix_world[i][j]-old[i][j])<1e-5 for i in range(4) for j in range(4))
prior={}
for num in ['01','02','03','04']:
 p=ROOT/('outputs/modeling-checkpoint-'+num);file='borrowed-wind-town-cp'+num+'.blend';old=json.loads((p/'file-manifest.json').read_text());prior['CP'+num]=hashlib.sha256((p/file).read_bytes()).hexdigest()==old[file]['sha256']
res=[o for o in s.objects if o.get('entity_id') and any(c.name=='08_Residents_SCALE_PROXIES' for c in o.users_collection)];animals=[o for o in s.objects if o.get('entity_id') and any(c.name=='09_Animals_SCALE_PROXIES' for c in o.users_collection)]
dg=bpy.context.evaluated_depsgraph_get();visible=[]
for root in res:
 row={'resident':root.name}
 for label,z in [('head',1.08),('upper_body',.75)]:
  p=root.matrix_world@Vector((0,0,z));h,lo,no,fi,o,mat=s.ray_cast(dg,p-fwd*40,fwd,distance=41);a=o
  while a and a.parent:a=a.parent
  row[label]=a==root
 visible.append(row)
steps={prefix:len([o for o in s.objects if o.name.startswith(prefix+' tread ')]) for prefix in ['CP05_lower_stair','CP05_upper_stair']}
tread_check=[]
for name in steps:
 root=bpy.data.objects[name]
 for i in range(5):
  for x in [-.36,0,.36]:
   p=root.matrix_world@Vector((x,(i+.5)*.20,(i+1)*rec['terrace']['equal_riser']));h,lo,no,fi,o,mat=s.ray_cast(dg,p+Vector((0,0,.07)),Vector((0,0,-1)),distance=.18)
   tread_check.append({'flight':name,'step':i+1,'cross_offset':x,'surface':o.name if o else None,'passed':bool(h and abs(lo.z-p.z)<.035)})
ps=[]
for o in tea.children_recursive:
 if o.type=='MESH':ps.extend(world_to_camera_view(s,cam,o.matrix_world@v.co) for v in o.data.vertices)
bounds={'left':min(p.x for p in ps),'right':max(p.x for p in ps),'bottom':min(p.y for p in ps),'top':max(p.y for p in ps)}
invalid=[o.name for o in s.objects if not all(math.isfinite(v) for r in o.matrix_world for v in r)]
guide=bpy.data.collections['12_CP05_MOVEMENT_RESERVATIONS']
record={'saved_model_reopened':True,'camera_unchanged_from_cp04':camera_ok,'camera_type':cam.data.type,'camera_elevation_degrees':math.degrees(math.asin(abs(fwd.z))),'restaurant_horizontal_angle_degrees':angle,'restaurant_projected_bounds_normalized':bounds,'other_core_object_transforms_unchanged':unchanged_core,'prior_models_unchanged':prior,'resident_proxy_count':len(res),'animal_proxy_count':len(animals),'visibility_rechecked':visible,'stair_tread_counts':steps,'stair_surface_samples_rechecked':tread_check,'movement_guides_hidden':guide.hide_render and guide.hide_viewport,'invalid_transforms':invalid,'armature_count':sum(o.type=='ARMATURE' for o in s.objects),'render_resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'full_navigation_or_animation_tested':False,'overall_reference_similarity_score':None,'scope_note':'Static center rays, named core transforms and 30 tread points. Not complete collision, full-body motion or full-scene art fidelity validation.'}
record['passed']=camera_ok and abs(angle-25)<.001 and all(unchanged_core.values()) and all(prior.values()) and len(res)==24 and len(animals)==7 and all(r['head'] and r['upper_body'] for r in visible) and all(n==5 for n in steps.values()) and all(r['passed'] for r in tread_check) and not invalid and record['movement_guides_hidden'] and 0<bounds['left']<bounds['right']<1 and 0<bounds['bottom']<bounds['top']<1
(OUT/'validation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps({'passed':record['passed'],'angle':angle,'camera_unchanged':camera_ok,'other_core_unchanged':all(unchanged_core.values()),'prior_models_unchanged':prior,'heads':sum(r['head'] for r in visible),'upper_bodies':sum(r['upper_body'] for r in visible),'tread_samples':sum(r['passed'] for r in tread_check),'restaurant_bounds':bounds},ensure_ascii=False));assert record['passed']
