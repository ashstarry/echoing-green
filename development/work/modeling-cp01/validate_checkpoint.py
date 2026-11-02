import bpy,math,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-01'
s=bpy.context.scene
required=['tea_house','post_office','west_home','small_wood_home','paper_observatory','quiet_home','station_main','greenhouse','lantern_tree','tram_car_front','tram_car_rear','Camera_Main_CP01','Camera_Plan_CP01']
missing=[n for n in required if n not in s.objects]
bad=[]
for o in s.objects:
 if not all(math.isfinite(x) for row in o.matrix_world for x in row):bad.append(o.name)
res=[o for o in s.objects if o.get('entity_id') and any(c.name=='08_Residents_SCALE_PROXIES' for c in o.users_collection)]
animals=[o for o in s.objects if o.get('entity_id') and any(c.name=='09_Animals_SCALE_PROXIES' for c in o.users_collection)]
r={'opened_saved_blend':True,'missing_required_roots':missing,'nonfinite_transforms':bad,'resident_proxy_count':len(res),'animal_proxy_count':len(animals),'armature_count':sum(o.type=='ARMATURE' for o in s.objects),'main_camera_saved':s.camera.name=='Camera_Main_CP01','images_packed':[im.name for im in bpy.data.images if im.packed_file],'scene_objects':len(s.objects),'live_web_or_simulation_tested':False,'passed':not missing and not bad and len(res)==20 and len(animals)==7 and s.camera.name=='Camera_Main_CP01'}
(OUT/'validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False))
assert r['passed']
