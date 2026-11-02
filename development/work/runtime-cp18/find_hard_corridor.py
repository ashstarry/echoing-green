import bpy,json,math,collections
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path.cwd();O=R/'outputs/runtime-checkpoint-18';A=R/'app/runtime-cp18/public/assets';s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
def chain(o):
 while o:yield o;o=o.parent
def geometry(o):
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear();return v,f
rails=[bpy.data.objects[x]for x in ['CP02 continuous rail','CP02 continuous rail.001']];points=[(rails[0].matrix_world@Vector(a.co[:3])+rails[1].matrix_world@Vector(b.co[:3]))*.5 for a,b in zip(rails[0].data.splines[0].points,rails[1].data.splines[0].points)];N=len(points);lengths=[0]
for i in range(N):lengths.append(lengths[-1]+(points[(i+1)%N]-points[i]).length)
L=lengths[-1]
def pose(distance,root):
 d=distance%L;j=next(i for i in range(N)if lengths[i+1]>=d);u=(d-lengths[j])/(lengths[j+1]-lengths[j]);p=points[j].lerp(points[(j+1)%N],u);t=(points[(j+1)%N]-points[j]).normalized();p.z+=.16
 return Matrix.Translation(p)@Matrix.Rotation(math.atan2(t.y,t.x),4,'Z')@Matrix.Diagonal((*root.scale,1))
vv=[];ff=[];nn=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 if any(a.get('decision_kind')in ['tram','plant','tree','light']for a in chain(o))or any(x in o.name.lower()for x in ['continuous rail','sleeper','rain','glint','ripple','studio floor']):continue
 v,f=geometry(o);off=len(vv);vv.extend(v);ff.extend(tuple(off+i for i in t)for t in f);nn.extend([o.name]*len(f))
world=BVHTree.FromPolygons(vv,ff,all_triangles=True);root=bpy.data.objects['tram_car_front'];inv=root.matrix_world.inverted();cv=[];cf=[]
for o in root.children_recursive:
 if o.type not in ['MESH','CURVE']:continue
 q,t=geometry(o);off=len(cv);cv.extend(inv@p for p in q);cf.extend(tuple(off+i for i in tri)for tri in t)
def clear(p,t):
 q=p.copy();q.z=.864;m=Matrix.Translation(q)@Matrix.Rotation(math.atan2(t.y,t.x),4,'Z')@Matrix.Diagonal((*root.scale,1));b=BVHTree.FromPolygons([m@x for x in cv],cf,all_triangles=True);return not b.overlap(world)
offsets=[];directions=[]
for i,p in enumerate(points):
 t=(points[(i+1)%N]-points[(i-1)%N]).normalized();normal=Vector((t.y,-t.x,0)).normalized();directions.append(normal);found=None
 for j in range(31):
  delta=j*.12
  if clear(p+normal*delta,t):found=delta;break
 offsets.append(found)
print('OFFSETS',max(x for x in offsets if x is not None),'unresolved',sum(x is None for x in offsets),flush=True)
# Broad smooth envelope, with padding for tangent changes and complete car overhang.
raw=[x if x is not None else 3.6 for x in offsets];profile=[]
for i in range(N):profile.append(max(0,max(raw[(i+k)%N]-.012*k*k for k in range(-18,19)))+.12)
for _ in range(6):profile=[sum(profile[(i+k)%N]for k in [-2,-1,0,1,2])/5 for i in range(N)]
new=[p+directions[i]*profile[i]for i,p in enumerate(points)];bad=[]
for i,p in enumerate(new):
 t=(new[(i+1)%N]-new[(i-1)%N]).normalized()
 if not clear(p,t):bad.append(i)
result={'original_points':[list(p)for p in points],'offsets':offsets,'profile':profile,'proposed_points':[list(p)for p in new],'failed_smoothed_points':bad};(O/'rail-corridor-hard-proposal.json').write_text(json.dumps(result,indent=2));print('SMOOTHED_FAILURES',bad,flush=True)
