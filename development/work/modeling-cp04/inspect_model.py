import bpy,math,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene;cam=s.camera;FWD=cam.rotation_euler.to_quaternion()@Vector((0,0,-1));dg=bpy.context.evaluated_depsgraph_get()
def ray(p):
 h,loc,n,fi,o,m=s.ray_cast(dg,p-FWD*40,FWD,distance=41);r=o
 while r and r.parent:r=r.parent
 return o.name if o else None,r.name if r else None
rows=[]
for r in s.objects:
 if not r.get('entity_id') or not any(c.name=='08_Residents_SCALE_PROXIES' for c in r.users_collection):continue
 row={'resident':r.name,'samples':{}}
 for name,z in [('head',1.08),('upper_body',.75)]:
  p=r.matrix_world@Vector((0,0,z));o,root=ray(p);q=world_to_camera_view(s,cam,p)
  row['samples'][name]={'clear':root==r.name,'first_hit':o,'root':root,'pixel':[q.x*1672,(1-q.y)*941]}
 rows.append(row)
faces=[]
for name,front,side in [('tea_house',(0,-1.39,2.78),(-2.70,-.63,2.78)),('west_home',(.70,-1.27,1.6),(-1.46,.58,1.54))]:
 r=bpy.data.objects[name];view=Vector((-FWD.x,-FWD.y,0)).normalized();q=r.rotation_euler.to_quaternion()
 faces.append({'entity':name,'front_normal_angle':math.degrees(math.acos((q@Vector((0,-1,0))).dot(view))),'side_normal_angle':math.degrees(math.acos((q@Vector((-1,0,0))).dot(view))),'front_sample_first_hit':ray(r.matrix_world@Vector(front)),'side_sample_first_hit':ray(r.matrix_world@Vector(side))})
record={'resident_visibility':rows,'facade_samples':faces}
(Path(__file__).resolve().parent/'inspection.json').write_text(json.dumps(record,indent=2))
print(json.dumps({'blocked_residents':[r for r in rows if not all(x['clear'] for x in r['samples'].values())],'facades':faces},indent=2))
