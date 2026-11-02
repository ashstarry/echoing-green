import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path.cwd();A=R/'app/runtime-cp22/public/assets';reg=json.loads((A/'runtime-registry.json').read_text());reader=bpy.data.objects['quiet_reader'];seat=bpy.data.objects[next(e['blender_object']for e in reg['entities']if e['id']=='seat.cp05_overlook_bench')];dg=bpy.context.evaluated_depsgraph_get();vv=[];ff=[]
for o in seat.children_recursive:
 if o.type not in ['MESH','CURVE']:continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();off=len(vv);vv.extend(ev.matrix_world@v.co for v in me.vertices);ff.extend(tuple(off+i for i in t.vertices)for t in me.loop_triangles);ev.to_mesh_clear()
tree=BVHTree.FromPolygons(vv,ff,all_triangles=True);rows=[]
for x in [.30,.32,.34,.36]:
 for y in [-.02,-.06,-.10]:
  p=reader.matrix_world@Vector((x,y,.8));hit,no,idx,d=tree.ray_cast(p,Vector((0,0,-1)),.7)
  if hit is not None and no.z>.7:
   local=reader.matrix_world.inverted()@hit;rows.append({'point':[x,local.z+.047,-y],'local_support_z':local.z,'world_support':list(hit),'x':x,'y':y})
rows.sort(key=lambda r:abs(r['x']-.30)+abs(r['y']+.02));assert rows, 'No real bench support';chosen=rows[0];s=json.loads((A/'actor-sockets.json').read_text());s['resident.quiet_reader']['cupStorage']=chosen['point'];(A/'actor-sockets.json').write_text(json.dumps(s,indent=2));(R/'outputs/runtime-checkpoint-22/reader-cup-support.json').write_text(json.dumps({'chosen':chosen,'candidates':rows},indent=2));print(chosen)
