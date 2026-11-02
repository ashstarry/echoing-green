import bpy,json
from mathutils import Vector
from pathlib import Path
rows=[]
for o in bpy.data.objects:
 if o.name in ['post_office','west_home','small_wood_home','quiet_home'] or (any(x in o.name for x in ['post_office','west_home','small_wood_home','quiet_home']) and any(x in o.name for x in ['body','door','pane','foundation'])):
  pts=[o.matrix_world@Vector(p) for p in o.bound_box] if o.type=='MESH' else []
  rows.append(dict(name=o.name,type=o.type,position=list(o.matrix_world.translation),matrix=[list(x) for x in o.matrix_world],bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)] if pts else None))
Path('work/runtime-cp39/home-geometry.json').write_text(json.dumps(rows,indent=2));print('Wrote',len(rows),'home geometry records')
