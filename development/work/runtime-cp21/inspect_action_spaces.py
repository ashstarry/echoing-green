import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path.cwd();rows={}
for name in ['quiet_home','station_main','tram_car_front','tram_car_rear','returning_resident','water_visitor','water_companion']:
 root=bpy.data.objects.get(name)
 if not root:continue
 own=[root]+list(root.children_recursive);rows[name]={'root':list(root.matrix_world.translation),'yaw':root.matrix_world.to_euler().z,'scale':list(root.matrix_world.to_scale()),'objects':[]}
 for o in own:
  if o.type not in ['MESH','CURVE']:continue
  corners=[o.matrix_world@Vector(v)for v in o.bound_box];rows[name]['objects'].append({'name':o.name,'parent':o.parent.name if o.parent else None,'min':[min(v[k]for v in corners)for k in range(3)],'max':[max(v[k]for v in corners)for k in range(3)],'material':o.active_material.name if o.active_material else None})
(R/'work/runtime-cp21/action-space-audit.json').write_text(json.dumps(rows,indent=2));print(json.dumps({n:{'root':r['root'],'count':len(r['objects']),'parts':[o['name']for o in r['objects']if any(k in o['name'].lower()for k in ['body','door','wall','floor','step','roof'])]}for n,r in rows.items()},indent=2))
