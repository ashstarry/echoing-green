import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path.cwd();reg=json.loads((R/'app/runtime-cp22/public/assets/runtime-registry.json').read_text());out={}
for id in ['resident.quiet_reader','resident.returning_resident','resident.water_visitor','resident.water_companion','book.terrace_reader_book','umbrella.carried_umbrella','bicycle.cp07_parked_bicycle','resident.elder','resident.listener','resident.upper_diner_0']:
 e=next(e for e in reg['entities']if e['id']==id);r=bpy.data.objects[e['blender_object']];row={'root':list(r.matrix_world.translation),'matrix':[list(x)for x in r.matrix_world],'objects':[]}
 for o in r.children_recursive:
  if o.type not in ['MESH','CURVE']:continue
  b=[o.matrix_world@Vector(v)for v in o.bound_box];row['objects'].append({'name':o.name,'parent':o.parent.name,'min':[min(v[k]for v in b)for k in range(3)],'max':[max(v[k]for v in b)for k in range(3)],'center':list(o.matrix_world.translation)})
 out[id]=row
out['stairs']=[]
for o in bpy.context.scene.objects:
 if any(t in o.name.lower()for t in ['cp05 stair','cp05 upper','cp05 lower','cp06','cp05 landing','terrace deck']):
  if o.type not in ['MESH','CURVE']:continue
  b=[o.matrix_world@Vector(v)for v in o.bound_box];out['stairs'].append({'name':o.name,'min':[min(v[k]for v in b)for k in range(3)],'max':[max(v[k]for v in b)for k in range(3)]})
(R/'work/runtime-cp22/props-routes-inspect.json').write_text(json.dumps(out,indent=2));print('INSPECTED')
