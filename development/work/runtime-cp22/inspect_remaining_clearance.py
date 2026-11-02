import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path.cwd();reg=json.loads((R/'app/runtime-cp22/public/assets/runtime-registry.json').read_text());e=next(e for e in reg['entities']if e['id']=='plant.garden_planter_00');o=bpy.data.objects[e['blender_object']];vs=[p.matrix_world@Vector(v)for p in o.children_recursive if p.type in ['MESH','CURVE']for v in p.bound_box];row={'id':e['id'],'root':o.name,'position':list(o.matrix_world.translation),'min':[min(v[k]for v in vs)for k in range(3)],'max':[max(v[k]for v in vs)for k in range(3)]};print(json.dumps(row,indent=2));(R/'work/runtime-cp22/landing-planter.json').write_text(json.dumps(row,indent=2))
