import bpy,json
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();r=bpy.data.objects['CP07 garden cluster 044'];vs=[];rows=[]
for o in r.children_recursive:
 if o.type!='MESH':continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();v=[ev.matrix_world@x.co for x in me.vertices];ev.to_mesh_clear();vs+=v;rows.append({'name':o.name,'lo':[min(x[i]for x in v)for i in range(3)],'hi':[max(x[i]for x in v)for i in range(3)]})
print(json.dumps({'root':list(r.matrix_world.translation),'bounds':[[min(x[i]for x in vs),max(x[i]for x in vs)]for i in range(3)],'rows':rows[:8]},indent=2))
