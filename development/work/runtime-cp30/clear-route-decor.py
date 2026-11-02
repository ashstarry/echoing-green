import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path.cwd();reg=json.loads((R/'app/runtime-cp30/public/assets/runtime-registry.json').read_text());by={e['blender_object']:e for e in reg['entities']};report=[]
names=set()
for k,v in json.loads((R/'work/runtime-cp30/route-obstacles-v2.json').read_text()).items():
 if k in ['stair_exit','gardener','assistant']:
  for row in v:names.update(row['obstacles'])
for name in sorted(names):
 o=bpy.data.objects[name];chain=[];p=o
 while p:chain.append(p.name);p=p.parent
 report.append({'name':name,'chain':chain,'position':list(o.matrix_world.translation)})
(R/'work/runtime-cp30/decor-chains.json').write_text(json.dumps(report,indent=2));print('DECOR_CHAINS',len(report))
