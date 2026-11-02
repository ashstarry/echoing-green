import bpy,json
from mathutils import Vector
from pathlib import Path
s=bpy.context.scene;d=bpy.context.evaluated_depsgraph_get();rows=[]
for x in[-6.16,-5.96,-5.76]:
 for y in[-2.14,-1.98]:
  hit,p,no,index,o,m=s.ray_cast(d,Vector((x,y,1.1)),Vector((0,0,-1)),distance=.8);rows.append({'x':x,'y':y,'z':p.z if hit else None,'object':o.name if hit else None})
Path('work/runtime-cp42/memory-support-actual.json').write_text(json.dumps(rows,indent=2));print(rows)
