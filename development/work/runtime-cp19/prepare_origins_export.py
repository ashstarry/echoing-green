import bpy,json,runpy
from pathlib import Path
R=Path.cwd();A=R/'app/runtime-cp19/public/assets';r=json.loads((A/'runtime-registry.json').read_text());origins={}
for e in r['entities']:
 o=bpy.data.objects[e['blender_object']];origins[e['id']]={'p':list(o.matrix_world.translation),'yaw':o.matrix_world.to_euler().z,'scale':list(o.matrix_world.to_scale())}
p=A/'motion-activities.json';d=json.loads(p.read_text())if p.exists()else{'clips':{}};d['origins']=origins;p.write_text(json.dumps(d,indent=2))
runpy.run_path(str(R/'work/runtime-cp19/export_runtime.py'))
