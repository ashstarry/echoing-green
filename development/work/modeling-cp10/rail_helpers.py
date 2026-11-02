import math,bpy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
def ancestry(o):
 while o:
  yield o;o=o.parent
def geometry(o,dg):
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear();return v,f
def car_local(root):
 dg=bpy.context.evaluated_depsgraph_get();inv=root.matrix_world.inverted();vs=[];fs=[];names=[]
 for o in root.children_recursive:
  if o.type not in ['MESH','CURVE']or o.hide_render:continue
  v,f=geometry(o,dg);off=len(vs);vs.extend(inv@p for p in v);fs.extend(tuple(off+i for i in t)for t in f);names.extend([o.name]*len(f))
 return vs,fs,names
front=bpy.data.objects['tram_car_front'];rail_center=front.matrix_world.translation-RIGHT*(12*math.cos(-1.13))-BACK*(6.3*math.sin(-1.13));rail_center.z=.864
T0,T1=-2.55,-1.27;COUNT=321;times=[T0+(T1-T0)*i/(COUNT-1)for i in range(COUNT)]
def pose(root,t):
 p=rail_center+RIGHT*(12*math.cos(t))+BACK*(6.3*math.sin(t));p.z=root.matrix_world.translation.z;d=RIGHT*(-12*math.sin(t))+BACK*(6.3*math.cos(t));return Matrix.Translation(p)@Matrix.Rotation(math.atan2(d.y,d.x),4,'Z')@Matrix.Diagonal((*root.scale,1))
front_local,_,_=car_local(front);rear_local,_,_=car_local(bpy.data.objects['tram_car_rear']);polys=[]
for root,vertices in [(front,front_local),(bpy.data.objects['tram_car_rear'],rear_local)]:
 lo=[min(p[i]for p in vertices)for i in range(3)];hi=[max(p[i]for p in vertices)for i in range(3)]
 for t in times:
  m=pose(root,t);v=[m@Vector((x,y,0))for x,y in [(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]];polys.append([(p.dot(RIGHT),p.dot(BACK))for p in v])
def envelope_back_at(r):
 vals=[]
 for poly in polys:
  if not min(p[0]for p in poly)-1e-8<=r<=max(p[0]for p in poly)+1e-8:continue
  for a,b in zip(poly,poly[1:]+poly[:1]):
   if min(a[0],b[0])-1e-8<=r<=max(a[0],b[0])+1e-8 and abs(b[0]-a[0])>1e-8:vals.append(a[1]+(b[1]-a[1])*(r-a[0])/(b[0]-a[0]))
 return max(vals)if vals else -100
