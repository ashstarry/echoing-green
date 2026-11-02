import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2];s=bpy.context.scene;cam=s.camera;Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));BACK=Vector((-RIGHT.y,RIGHT.x,0))
def px(p):
 v=world_to_camera_view(s,cam,p);return [round(v.x*1672,1),round((1-v.y)*941,1)]
def row(o):
 objs=[x for x in [o]+list(o.children_recursive) if x.type=='MESH' and not x.hide_render];points=[x.matrix_world@Vector(v) for x in objs for v in x.bound_box];uv=[px(p) for p in points];p=o.matrix_world.translation
 return {'name':o.name,'location':list(o.location),'scale':list(o.scale),'yaw':math.degrees(o.rotation_euler.z),'rbz':[p.dot(RIGHT),p.dot(BACK),p.z],'origin_px':px(p),'bbox_px':[min(v[0] for v in uv),min(v[1] for v in uv),max(v[0] for v in uv),max(v[1] for v in uv)] if uv else None,'children':[{'name':x.name,'location':list(x.location),'scale':list(x.scale),'type':x.type} for x in o.children]}
names=['tea_house','tea_house roof','station_main','CP02 station central roof','post_office','west_home','small_wood_home','quiet_home','paper_observatory','greenhouse','lantern_tree','plaza_ground','musician','listener','child_listener','station_attendant','station_traveler','waiting_passenger','waiting_passenger_2','Island paper layer 4','CP02 open street paving','CP02 pond','tram_car_front']
result={'objects':[row(bpy.data.objects[n]) for n in names if bpy.data.objects.get(n)],'plaza_meshes':[row(o) for o in s.objects if o.name.startswith(('Plaza ring','Tree planter','Circular bench','Bench leg'))],'lights':[{'name':o.name,'location':list(o.matrix_world.translation),'energy':o.data.energy,'color':list(o.data.color),'type':o.data.type,'rotation':list(o.rotation_euler)} for o in s.objects if o.type=='LIGHT'],'land_objects':[o.name for o in bpy.data.collections['00_Terrain'].objects]}
(ROOT/'work/modeling-cp08/composition-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps({'objects':[{k:v for k,v in x.items() if k!='children'} for x in result['objects']],'land':result['land_objects']},indent=2))
