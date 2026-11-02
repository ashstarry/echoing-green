import bpy,json
from pathlib import Path
from mathutils import Vector
rows=[]
for o in bpy.context.scene.objects:
 if any(k in o.name for k in ['CP02 bridge landing','CP08 garden low retaining','garden_planter_02','CP08 ticket','CP08 station open','CP08 activity seat']):
  if o.type not in ['MESH','CURVE']:continue
  ps=[o.matrix_world@Vector(v)for v in o.bound_box];rows.append({'name':o.name,'parent':o.parent.name if o.parent else None,'bounds':[[min(v[k]for v in ps)for k in range(3)],[max(v[k]for v in ps)for k in range(3)]],'origin':list(o.matrix_world.translation),'matrix':[list(r)for r in o.matrix_world]})
Path('work/runtime-cp30/detail-obstacles.json').write_text(json.dumps(rows,indent=2));print('DONE',len(rows))
