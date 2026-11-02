import bpy,json,time
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path.cwd();O=R/'outputs/runtime-checkpoint-22';names={x['name']for x in json.loads((O/'final-rail-flower-adjustment.json').read_text())['objects']};dg=bpy.context.evaluated_depsgraph_get();vv=[];ff=[]
for name in names:
 o=bpy.data.objects[name];ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();off=len(vv);vv.extend(ev.matrix_world@v.co for v in m.vertices);ff.extend(tuple(off+k for k in t.vertices)for t in m.loop_triangles);ev.to_mesh_clear()
flower=BVHTree.FromPolygons(vv,ff,all_triangles=True);fb=([min(v[k]for v in vv)for k in range(3)],[max(v[k]for v in vv)for k in range(3)]);data=json.loads((R/'work/runtime-cp22/browser-mesh-motion.json').read_text());prior=json.loads((O/'browser-full-cast-final.json').read_text());subjects=set(prior['subject_groups']);groups={id:[]for id in subjects};C=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
def matrix(a):return C@Matrix([a[i:i+4]for i in range(0,16,4)]).transposed()
geos={int(k):{'v':[Vector(v[i:i+3])for i in range(0,len(v),3)],'f':[ix[i:i+3]for i in range(0,len(ix),3)]}for k,g in data['geometries'].items()for v,ix in [(g['vertices'],g['indices']or list(range(len(g['vertices'])//3)))]}
for g in geos.values():
 lo=[min(v[k]for v in g['v'])for k in range(3)];hi=[max(v[k]for v in g['v'])for k in range(3)];g['box']=[Vector((x,y,z))for x in [lo[0],hi[0]]for y in [lo[1],hi[1]]for z in [lo[2],hi[2]]]
for i,n in enumerate(data['meshes']):
 id=next((id for id in reversed(n['chain'])if id in subjects),None)
 if id:groups[id].append(i)
issues=[];tested=0;broad=0
for fr in data['frames']:
 for id,indices in groups.items():
  bb=[];mats={}
  for i in indices:
   m=matrix(fr['matrices'][i]);mats[i]=m;bb.extend(m@v for v in geos[data['meshes'][i]['gid']]['box'])
  broad+=1
  if not bb or any(max(v[k]for v in bb)<fb[0][k]or min(v[k]for v in bb)>fb[1][k]for k in range(3)):continue
  v=[];f=[]
  for i in indices:
   g=geos[data['meshes'][i]['gid']];off=len(v);v.extend(mats[i]@p for p in g['v']);f.extend(tuple(off+j for j in t)for t in g['f'])
  pairs=BVHTree.FromPolygons(v,f,all_triangles=True).overlap(flower);tested+=1
  if pairs:issues.append({'time':fr['time'],'subject':id,'pairs':len(pairs)})
result={'passed':not issues,'all_recorded_dynamic_assembly_bounds_checked':broad,'nearby_actual_mesh_checks':tested,'frames':len(data['frames']),'issues':issues,'moved_objects_retained':len(names),'scope':'Final evaluated flower geometry against every recorded decoded moving assembly. Other geometry/animation rules unchanged from the complete 260-second browser sweep. This is a targeted correction recheck, not an additional fresh full-world run.'};(O/'final-rail-flower-recheck.json').write_text(json.dumps(result,indent=2));print(result);assert result['passed']
