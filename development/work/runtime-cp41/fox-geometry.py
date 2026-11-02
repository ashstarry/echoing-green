import bpy,json
from pathlib import Path
from mathutils import Vector
root=bpy.data.objects['garden_fox'];rows=[]
for o in [root]+list(root.children_recursive):
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(p)for p in o.bound_box];rows.append({'name':o.name,'part':o.get('decision_part_id'),'position':list(o.matrix_world.translation),'local_position':list(o.location),'bounds':[[min(p[i]for p in pts),max(p[i]for p in pts)]for i in range(3)]})
Path('work/runtime-cp41/fox-geometry.json').write_text(json.dumps({'root_matrix':[list(x)for x in root.matrix_world],'objects':rows},indent=2));print('FOX_GEOMETRY',len(rows))
