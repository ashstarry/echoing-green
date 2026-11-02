import bpy,json
from pathlib import Path
R=Path.cwd();rows=json.loads((R/'work/runtime-cp20/flower-cluster-source.json').read_text())
for r in rows:
 o=bpy.data.objects[r['name']];p=r['position'];o.location=(p[0],p[1]-.35,p[2])
bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp20/town-runtime.blend'));print('WHOLE_CLUSTER',len(rows))
