import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path.cwd();base=json.loads((R/'outputs/art-checkpoint-16/scene-signature.json').read_text());rows=[]
for name in ['greenhouse','post_office','quiet_home','small_wood_home','station_main','tea_house','west_home']:
 ob=bpy.data.objects[name];actual=[v for row in ob.matrix_world for v in row];before=base['objects'][name]['matrix'];delta=max(abs(a-b)for a,b in zip(actual,before));rows.append({'object':name,'max_transform_delta':delta,'equal_within_1e_5':delta<1e-5})
cam=bpy.context.scene.camera;mat=[v for row in cam.matrix_world for v in row];delta=max(abs(a-b)for a,b in zip(mat,base['camera']['matrix']));direction=cam.matrix_world.to_quaternion()@Vector((0,0,-1));elevation=math.degrees(math.asin(abs(direction.z)));result={'core_roots':rows,'camera_matrix_max_delta':delta,'camera_elevation_degrees':elevation,'blender_camera_ortho_scale':cam.data.ortho_scale,'browser_framing_note':'Same 43-degree viewing direction; orthographic framing enlarged to 29.8 nominal width with sky margin for the fireworks.','passed':all(x['equal_within_1e_5']for x in rows)and delta<1e-5};(R/'outputs/runtime-checkpoint-18/core-baseline-check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
