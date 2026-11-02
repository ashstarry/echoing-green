import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-03';s=bpy.context.scene
cam=s.camera;fwd=cam.rotation_euler.to_quaternion()@Vector((0,0,-1));elev=math.degrees(math.asin(abs(fwd.z)))
missing=[n for n in ['tea_house','post_office','west_home','small_wood_home','paper_observatory','quiet_home','station_main','greenhouse','lantern_tree','tram_car_front','tram_car_rear','CP03_hill_stair'] if n not in s.objects]
invalid=[o.name for o in s.objects if not all(math.isfinite(v) for row in o.matrix_world for v in row)]
res=[o for o in s.objects if o.get('entity_id') and any(c.name=='08_Residents_SCALE_PROXIES' for c in o.users_collection)]
animals=[o for o in s.objects if o.get('entity_id') and any(c.name=='09_Animals_SCALE_PROXIES' for c in o.users_collection)]
unchanged={}
for cp in ['01','02']:
 p=ROOT/('outputs/modeling-checkpoint-'+cp);f='borrowed-wind-town-cp'+cp+'.blend';m=json.loads((p/'file-manifest.json').read_text());unchanged['CP'+cp]=hashlib.sha256((p/f).read_bytes()).hexdigest()==m[f]['sha256']
guide=bpy.data.collections['12_CP03_MOVEMENT_RESERVATIONS']
stairs=[o for o in s.objects if o.name.startswith('CP03 stair solid riser')]
tops=[]
for o in stairs:
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];tops.append(max(v.z for v in pts))
record={'saved_model_reopened':True,'main_camera_name':cam.name,'camera_type':cam.data.type,'camera_elevation_degrees':elev,'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'missing_objects':missing,'invalid_transforms':invalid,'resident_proxy_count':len(res),'animal_proxy_count':len(animals),'previous_models_unchanged':unchanged,'stairs_count':len(stairs),'stair_top_levels':sorted(tops),'movement_guides_hidden_in_main':guide.hide_render and guide.hide_viewport,'armatures':sum(o.type=='ARMATURE' for o in s.objects),'animation_or_navigation_tested':False,'overall_reference_similarity_score':None}
record['passed']=cam.data.type=='ORTHO' and abs(elev-43)<.001 and not missing and not invalid and len(res)==24 and len(animals)==7 and all(unchanged.values()) and len(stairs)==8 and guide.hide_render and guide.hide_viewport and s.render.resolution_percentage==100
(OUT/'validation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False));assert record['passed']
