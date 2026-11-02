import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path.cwd();A=R/'app/runtime-cp42/public/assets';reg=json.loads((A/'runtime-registry.json').read_text());kinds={e['id']:e['kind']for e in reg['entities']};root=bpy.data.objects['pond_boat'];bpy.data.objects['CP09_oar_left'].rotation_euler.z-=.55;bpy.data.objects['CP09_oar_right'].rotation_euler.z+=.55;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();inv=root.matrix_world.inverted();bv=[];bf=[]
def lineage(o):
 while o:yield o;o=o.parent
for o in root.children_recursive:
 if o.type not in ['MESH','CURVE']:continue
 ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();off=len(bv);bv.extend(inv@(ev.matrix_world@v.co)for v in m.vertices);bf.extend(tuple(off+i for i in t.vertices)for t in m.loop_triangles);ev.to_mesh_clear()
vs=[];fs=[];names=[]
for o in bpy.context.scene.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or root in list(lineage(o))or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 chain=list(lineage(o));owner=next((p.get('decision_entity_id')for p in chain if p.get('decision_entity_id')),None);name=o.name.lower()
 if kinds.get(owner)in['resident','animal','fish','bird','plant','tree','bicycle','tram','weather','water_lantern']or any(t in name for t in ['cp02 pond','water glint','ripple','wake','rain','flower','petal','leaf','foliage','grass','studio floor']):continue
 ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@x.co for x in m.vertices];f=[tuple(t.vertices)for t in m.loop_triangles];ev.to_mesh_clear()
 if not v or max(p.x for p in v)<4.5 or min(p.x for p in v)>11.5 or max(p.y for p in v)<-4 or min(p.y for p in v)>1:continue
 off=len(vs);vs.extend(v);fs.extend(tuple(off+i for i in t)for t in f);names.extend([o.name]*len(f))
world=BVHTree.FromPolygons(vs,fs,all_triangles=True);home=root.matrix_world.translation.copy();shape=root.matrix_world.copy();shape.translation=Vector((0,0,0));nodes=[];grid={};step=.18
for iy in range(9):
 for ix in range(13):
  x=home.x+ix*step;y=home.y+(iy-4)*step
  matrix=Matrix.Translation(Vector((x,y,home.z)))@shape;body=BVHTree.FromPolygons([matrix@v for v in bv],bf,all_triangles=True)
  hits=body.overlap(world)
  if hits:
   if ix in[3,6,9]and iy==4:print('HIT',ix,sorted(set(names[j]for i,j in hits))[:12])
   continue
  grid[f'{ix},{iy}']=len(nodes);nodes.append([x,y,home.z,ix,iy])
edges=[]
for p in nodes:
 edges.append([grid[f'{p[3]+dx},{p[4]+dy}']for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)]if f'{p[3]+dx},{p[4]+dy}'in grid])
start=grid.get('0,4');assert start is not None,'Original boat unexpectedly overlaps hard scene';seen={start};todo=[start];prev={start:None}
while todo:
 for n in edges[todo.pop(0)]:
  if n not in seen:seen.add(n);prev[n]=next(i for i,e in enumerate(edges)if n in e and i in seen and i!=n);todo.append(n)
# BFS predecessors without the component traversal shortcut.
prev={start:None};q=[start]
for i in q:
 for n in edges[i]:
  if n not in prev:prev[n]=i;q.append(n)
far=max(prev,key=lambda i:math.hypot(nodes[i][0]-home.x,nodes[i][1]-home.y));path=[];n=far
while n is not None:path.insert(0,n);n=prev[n]
assert len(path)>4,(len(nodes),len(path));points=[nodes[i][:3]for i in path];length=sum((Vector(points[i])-Vector(points[i-1])).length for i in range(1,len(points)))
poly=[];pond=bpy.data.objects['CP02 pond'];coords=[pond.matrix_world@v.co for v in pond.data.vertices];z=max(v.z for v in coords);top=[v for v in coords if abs(v.z-z)<1e-4];center=sum(top,Vector())/len(top);top.sort(key=lambda v:math.atan2(v.y-center.y,v.x-center.x));points2=sorted(set((v.x,v.y)for v in top))
def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
lo=[]
for p in points2:
 while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
 lo.append(p)
hi=[]
for p in reversed(points2):
 while len(hi)>=2 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
 hi.append(p)
poly=lo[:-1]+hi[:-1]
support=[]
for x,y in[(-6.16,-2.14),(-5.96,-2.14),(-5.76,-2.14),(-6.16,-1.98),(-5.96,-1.98),(-5.76,-1.98)]:
 hit,normal,index,d=world.ray_cast(Vector((x,y,1.1)),Vector((0,0,-1)),.6);support.append({'x':x,'y':y,'z':hit.z if hit else None,'object':names[index]if hit else None})
(R/'work/runtime-cp42/memory-support.json').write_text(json.dumps(support,indent=2))
float_nodes=[];float_grid={};float_step=.18
for iy in range(23):
 for ix in range(35):
  x=5.0+ix*float_step;y=-3.3+iy*float_step
  inside=False;j=len(poly)-1
  for i in range(len(poly)):
   a=poly[i];b=poly[j]
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
   j=i
  if not inside:continue
  verts=[];faces=[]
  for z in [.642,.90]:
   verts.extend(Vector((x+math.cos(k*math.pi/4)*.23,y+math.sin(k*math.pi/4)*.23,z))for k in range(8))
  for k in range(8):
   j=(k+1)%8;faces.extend([(k,j,8+j),(k,8+j,8+k)])
  faces.extend([(0,k,k+1)for k in range(1,7)]);faces.extend([(8,8+k+1,8+k)for k in range(1,7)])
  if BVHTree.FromPolygons(verts,faces,all_triangles=True).overlap(world):continue
  float_grid[f'{ix},{iy}']=len(float_nodes);float_nodes.append([x,y,.66,ix,iy])
float_edges=[]
for p in float_nodes:float_edges.append([float_grid[f'{p[3]+dx},{p[4]+dy}']for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)]if f'{p[3]+dx},{p[4]+dy}'in float_grid])
floating=[{'id':e['id'],'p':e['position'],'radius':.22 if e['kind']=='plant' else .28}for e in reg['entities']if e['id'].startswith('plant.water_lily_')or e['kind']=='water_lantern']
data={'home':list(home),'yaw':root.matrix_world.to_euler().z,'path':points,'oneWayLength':length,'pondPolygon':poly,'floatNodes':[p[:3]for p in float_nodes],'floatEdges':float_edges,'floating':floating,'checkedPoses':len(nodes),'oarFold':[-.55,.55],'scope':'Original hull and resting oars against hard static scene; floating leaves/lamps/animals are handled separately. Out-and-back drift keeps authored heading.'}
m=json.loads((A/'motion-activities.json').read_text());m['boatRoute']=data;(A/'motion-activities.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));(R/'outputs/runtime-checkpoint-42/boat-route-check.json').write_text(json.dumps({'candidate_nodes':nodes,'connected':len(prev),**data},indent=2));print('FLOAT_NODES',len(float_nodes));print('BOAT_ROUTE',len(nodes),'path',len(points),'distance',length)
