import bpy,json,math
from mathutils import Vector
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene;cam=s.camera;fwd=cam.rotation_euler.to_quaternion()@Vector((0,0,-1));dg=bpy.context.evaluated_depsgraph_get()
rows=[]
for root in s.objects:
 if not root.get('entity_id') or not any(c.name=='08_Residents_SCALE_PROXIES' for c in root.users_collection):continue
 row={'resident':root.name,'world':list(root.location),'samples':{}}
 for label,p in [('head',root.matrix_world@Vector((0,0,1.08))),('torso',root.matrix_world@Vector((0,0,.75)))]:
  h,loc,no,fi,o,ma=s.ray_cast(dg,p-fwd*40,fwd,distance=41);anc=o
  while anc and anc.parent:anc=anc.parent
  q=world_to_camera_view(s,cam,p)
  row['samples'][label]={'clear':anc==root,'hit':o.name if o else None,'root':anc.name if anc else None,'pixel':[q.x*1672,(1-q.y)*941]}
 rows.append(row)
data={'residents':rows,'station_parts':[{'name':o.name,'p':list(o.location),'s':list(o.scale),'parent':o.parent.name if o.parent else None} for o in bpy.data.objects['station_main'].children]}
(Path(__file__).resolve().parent/'draft-inspection.json').write_text(json.dumps(data,indent=2))
print(json.dumps([r for r in rows if not all(v['clear'] for v in r['samples'].values())],indent=2))
