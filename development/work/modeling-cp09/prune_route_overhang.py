exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
from mathutils.bvhtree import BVHTree
rec=json.loads((OUT/'revision-record.json').read_text());circ=json.loads((OUT/'circulation-check.json').read_text());points=[]
pts=circ['routes']['terrace_main']['samples']
for i,row in enumerate(pts):
 p=Vector(row['foot']);nextp=Vector(pts[min(i+1,len(pts)-1)]['foot']);prev=Vector(pts[max(0,i-1)]['foot']);d=nextp-prev;d.z=0;d.normalize();side=Vector((-d.y,d.x,0))
 for offset in [-.18,0,.18]:
  for z in [.5,.8,1.1,1.2]:points.append(p+side*offset+Vector((0,0,z)))
dg=bpy.context.evaluated_depsgraph_get();remove=[]
for o in s.objects:
 if not o.name.startswith('CP09 rear pink blossom') or o.type!='MESH':continue
 ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();bv=BVHTree.FromPolygons([ev.matrix_world@v.co for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],all_triangles=True);ev.to_mesh_clear()
 if any(bv.find_nearest(p)[3]<.265 for p in points):remove.append(o.name)
for n in remove:erase(bpy.data.objects[n])
rec['last_clearance_repairs']['additional_overhanging_blossoms_pruned']=remove;(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));print('PRUNED',remove,flush=True)
