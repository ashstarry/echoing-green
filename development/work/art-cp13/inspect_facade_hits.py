import bpy,json
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;tea=bpy.data.objects['tea_house'];f=s.camera.rotation_euler.to_quaternion()@Vector((0,0,-1));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for x in [-1.8,-1.4,-1.0,-.7,0,.7,1.,1.4,1.8]:
 for z in [2.7,2.9,3.1,3.25]:
  p=tea.matrix_world@Vector((x,-1.4,z));hit,pt,n,i,o,m=s.ray_cast(dg,p-f*40,f,distance=45);rows.append({'x':x,'z':z,'object':o.name if o else None,'local_hit':list(tea.matrix_world.inverted()@pt)if hit else None})
Path('work/art-cp13/facade-hits.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
