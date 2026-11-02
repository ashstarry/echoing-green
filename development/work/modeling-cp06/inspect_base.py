import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];s=bpy.context.scene;cam=s.camera;rec=json.loads((ROOT/'outputs/modeling-checkpoint-05/revision-record.json').read_text());poly=rec['terrace']['upper_outline_world']
q=cam.rotation_euler.to_quaternion();right=q@Vector((1,0,0));back=Vector((-right.y,right.x,0))
area=abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)
names=['tea_house','quiet_home','quiet_reader','CP05_overlook_bench','hill_windwheel','district_tree_4','district_tree_2','CP05_upper_stair','CP05_middle_landing','courier','customer_one']
data={'terrace_area':area,'outline_right_back':[[Vector(p).dot(right),Vector(p).dot(back)] for p in poly],'roots':{n:{'location':list(bpy.data.objects[n].location),'matrix':[list(r) for r in bpy.data.objects[n].matrix_world],'scale':list(bpy.data.objects[n].scale)} for n in names},'basis':{'right':list(right),'back':list(back)}}
(Path(__file__).parent/'base-inspection.json').write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))
