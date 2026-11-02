import bpy,json
from pathlib import Path
from mathutils import Vector
r=json.loads(Path('app/runtime-cp21/public/assets/runtime-registry.json').read_text())['entities']
for e in r:
 if e['kind']=='umbrella':
  o=bpy.data.objects[e['blender_object']];print('UMBRELLA',o.name,'parent',o.parent.name if o.parent else None,'origin',list(o.matrix_world.translation))
for n in ['water_visitor','water_companion']:
 o=bpy.data.objects[n];print(n,'yaw',o.matrix_world.to_euler().z,'scale',list(o.scale),'hands',[(x.name,list(x.matrix_world.translation))for x in o.children_recursive if x.name.startswith('Hand')])
