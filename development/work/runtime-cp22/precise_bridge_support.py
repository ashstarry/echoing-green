import bpy,json
from pathlib import Path
R=Path.cwd();A=R/'app/runtime-cp22/public/assets';dg=bpy.context.evaluated_depsgraph_get();triangles=[]
for o in bpy.context.scene.objects:
 if not o.name.startswith('CP02 bridge deck'):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices]
 for t in me.loop_triangles:
  a,b,c=[v[i]for i in t.vertices];n=(b-a).cross(c-a)
  if n.length>1e-8 and n.normalized().z>.65:triangles.append([list(a),list(b),list(c)])
 ev.to_mesh_clear()
p=A/'local-support.json';data=json.loads(p.read_text());data['bridge']['triangles']=triangles;p.write_text(json.dumps(data,separators=(',',':')));print('PRECISE_BRIDGE_TRIANGLES',len(triangles))
