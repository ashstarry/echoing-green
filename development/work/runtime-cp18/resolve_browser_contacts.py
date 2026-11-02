import bpy,json,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path.cwd();data=json.loads((R/'outputs/runtime-checkpoint-18/browser-mesh-collision-locations.json').read_text());dg=bpy.context.evaluated_depsgraph_get();v=[];f=[];names=[]
for o in bpy.context.scene.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vv=[ev.matrix_world@p.co for p in me.vertices];ff=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear();off=len(v);v.extend(vv);f.extend(tuple(off+i for i in x)for x in ff);names.extend([o.name]*len(ff))
w=BVHTree.FromPolygons(v,f,all_triangles=True);rows=[]
for issue in data['issues']:
 for c in issue['contacts']:
  h,n,i,d=w.find_nearest(Vector(c['point']));rows.append({'time':issue['time'],'subject':issue['subject'],'part':c['a'][1],'obstacle':names[i],'distance':d,'point':c['point']})
(R/'outputs/runtime-checkpoint-18/browser-contact-source-names.json').write_text(json.dumps(rows,indent=2));print(collections.Counter((r['subject'],r['part'],r['obstacle'])for r in rows).most_common(40))
