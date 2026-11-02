import bpy,json
from mathutils import Vector
from pathlib import Path
R=Path.cwd();out={}
for name in ['vendor_bread','water_visitor','returning_resident']:
 root=bpy.data.objects[name];inv=root.matrix_world.inverted();rows=[]
 for o in bpy.context.scene.objects:
  if o.type not in ['MESH','CURVE']:continue
  if name=='vendor_bread' and (o.name in ['Stall counter'] or o.name.startswith('CP07 ceramic serving bowl') and (o.matrix_world.translation-root.matrix_world.translation).length<1.2):
   v=[inv@(o.matrix_world@Vector(v))for v in o.bound_box];rows.append({'name':o.name,'min':[min(p[k]for p in v)for k in range(3)],'max':[max(p[k]for p in v)for k in range(3)]})
 out[name]=rows
(R/'work/runtime-cp22/contact-spaces.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
