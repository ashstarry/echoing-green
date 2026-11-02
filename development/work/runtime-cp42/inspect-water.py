import bpy,json
from pathlib import Path
from mathutils import Vector
rows=[]
for o in bpy.context.scene.objects:
 if o.type not in ['MESH','CURVE']:continue
 chain=[];p=o
 while p:chain.append(p.name);p=p.parent
 n=o.name.lower()
 if not(any(t in n for t in ['water','counter','post_office bench','mooring','tether','rope'])or'pond_boat'in chain):continue
 pts=[o.matrix_world@Vector(p)for p in o.bound_box];d={'name':o.name,'parents':chain,'matrix':[list(x)for x in o.matrix_world],'bounds':[[min(p[i]for p in pts),max(p[i]for p in pts)]for i in range(3)]}
 if ('water' in n or 'pond_boat' in chain)and o.type=='MESH':d['vertices']=[list(o.matrix_world@v.co)for v in o.data.vertices];d['faces']=[list(p.vertices)for p in o.data.polygons]
 rows.append(d)
Path('work/runtime-cp42/water-geometry.json').write_text(json.dumps(rows,indent=2));print('WATER_RECORDS',len(rows))
