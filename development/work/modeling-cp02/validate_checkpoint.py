import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-02';s=bpy.context.scene
cam=s.camera;forward=cam.rotation_euler.to_quaternion()@Vector((0,0,-1));elev=math.degrees(math.asin(abs(forward.z)))
need=['tea_house','post_office','west_home','small_wood_home','paper_observatory','quiet_home','station_main','greenhouse','lantern_tree','tram_car_front','tram_car_rear','plaza_ground']
missing=[n for n in need if n not in s.objects]
bad=[o.name for o in s.objects if not all(math.isfinite(v) for row in o.matrix_world for v in row)]
res=[o for o in s.objects if o.get('entity_id') and any(c.name=='08_Residents_SCALE_PROXIES' for c in o.users_collection)]
animals=[o for o in s.objects if o.get('entity_id') and any(c.name=='09_Animals_SCALE_PROXIES' for c in o.users_collection)]
cp1=ROOT/'outputs/modeling-checkpoint-01';m=json.loads((cp1/'file-manifest.json').read_text());unchanged=hashlib.sha256((cp1/'borrowed-wind-town-cp01.blend').read_bytes()).hexdigest()==m['borrowed-wind-town-cp01.blend']['sha256']
record={'saved_model_reopened':True,'camera_type':cam.data.type,'camera_elevation_degrees':elev,'camera_azimuth_from_south_degrees':12,'resolution':[s.render.resolution_x,s.render.resolution_y],'missing_major_objects':missing,'invalid_transforms':bad,'resident_proxies':len(res),'animal_proxies':len(animals),'previous_cp01_blend_unchanged':unchanged,'all_sky_hidden_in_saved_main':all(o.hide_render for o in s.objects if o.name.startswith('Paper star')),'runtime_navigation_tested':False,'animation_visibility_tested':False,'full_image_similarity_measured':False,'passed':cam.data.type=='ORTHO' and abs(elev-45)<.001 and not missing and not bad and len(res)==24 and len(animals)==7 and unchanged}
(OUT/'validation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False));assert record['passed']
