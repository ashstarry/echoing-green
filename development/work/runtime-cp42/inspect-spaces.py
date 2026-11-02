import bpy,json
from pathlib import Path
from mathutils import Vector
rows=[]
for o in bpy.context.scene.objects:
 if o.type not in ['MESH','CURVE']:continue
 n=o.name.lower()
 if any(t in n for t in ['pond','boat','mooring','tether','post_office front','post_office bench','tea counter','tea_house counter','street_lantern']):
  pts=[o.matrix_world@Vector(p)for p in o.bound_box];row={'name':o.name,'parent':o.parent.name if o.parent else None,'position':list(o.matrix_world.translation),'bounds':[[min(p[i]for p in pts),max(p[i]for p in pts)]for i in range(3)]}
  if any(t in n for t in ['water','pond basin'])and o.type=='MESH':row['vertices']=[list(o.matrix_world@v.co)for v in o.data.vertices];row['faces']=[list(p.vertices)for p in o.data.polygons]
  rows.append(row)
Path('work/runtime-cp42/scene-spaces.json').write_text(json.dumps(rows,indent=2));print('SPACE_RECORDS',len(rows))
