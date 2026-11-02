import bpy
from mathutils import Vector
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
for o in s.objects:
 if o.type=='MESH'and any(k in o.name.lower() for k in ['paving','plaza','ground']) and not any(k in o.name.lower()for k in ['stone ring','kite','petal','flower']):
  ev=o.evaluated_get(dg);me=ev.to_mesh();v=[ev.matrix_world@p.co for p in me.vertices];print(o.name, min(p.z for p in v),max(p.z for p in v));ev.to_mesh_clear()
