import bpy,json
from pathlib import Path
from mathutils import Vector
A=Path.cwd()/'app/runtime-cp18/public/assets';r=json.loads((A/'runtime-registry.json').read_text())
for e in r['entities']:
 if e['id']in ['curtain.restaurant_upper_noren','boat.pond_boat']:
  root=bpy.data.objects[e['blender_object']];print(e['id'],'root',list(root.matrix_world.translation))
  for p in e['parts']:
   o=bpy.data.objects[p['blender_object']];print(p['id'],list(o.location),list(o.scale),list(o.rotation_euler),list(o.matrix_world.translation))
o=bpy.data.objects['CP02 bridge landing east'];print('LANDING',list(o.matrix_world.translation),list(o.dimensions),list(o.rotation_euler))
