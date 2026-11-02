import bpy,json,math,collections
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R=Path.cwd();A=R/'app/runtime-cp18/public/assets';O=R/'outputs/runtime-checkpoint-18';s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();path=json.loads((A/'rail-path.json').read_text());points=[Vector(p)for p in path['points']];N=len(points)
def chain(o):
 while o:yield o;o=o.parent
def geo(o):
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear();return v,f
original=json.loads((R/'outputs/art-checkpoint-16/scene-signature.json').read_text())['objects']
restore_names=['district_tree_0','district_tree_6','CP07 garden cluster 002','CP07 garden cluster 005','CP07 garden cluster 039','CP07 garden cluster 044','CP07 garden cluster 052','garden_planter_10','street_lantern_10']
for name in restore_names:
 values=original[name]['matrix'];bpy.data.objects[name].matrix_world=Matrix([values[i:i+4]for i in range(0,16,4)])
ribbon=bpy.data.objects['CP18 supported rail ribbon'];mesh=ribbon.data;verts=[list(v.co)for v in mesh.vertices];faces=[list(p.vertices)[::-1]for p in mesh.polygons];mats=[p.material_index for p in mesh.polygons]
for i in range(N):
 t=(points[(i+1)%N]-points[(i-1)%N]).normalized();n=Vector((t.y,-t.x,0));p=points[i]+n*1.15
 for j,z in [(1,.635),(2,-.72)]:verts[3*i+j]=[p.x,p.y,z]
mesh.clear_geometry();mesh.from_pydata(verts,[],faces);mesh.polygons.foreach_set('material_index',mats);mesh.update();bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
intruders=json.loads((R/'work/runtime-cp18/rail-intruders.json').read_text())
newcheck=json.loads((O/'rail-sweep-before-decor-clearance.json').read_text());names=set(p[1]for c in newcheck['cars']for row in c['issues']for p in row['pairs']);roots={}
for n in names:
 root=next((a for a in chain(bpy.data.objects[n])if a.get('decision_kind')in ['plant','tree','light']),None)
 if root:roots[root.name]=root
 else:print('UNOWNED_HARD',n)
# Conservative swept box field. Complete evaluated decoration meshes are checked against it.
ev=[];ef=[];tangents=[];normals=[]
for i,p in enumerate(points):
 t=(points[(i+1)%N]-points[(i-1)%N]).normalized();n=Vector((t.y,-t.x,0));tangents.append(t);normals.append(n)
 for k in range(3):
  q=p.lerp(points[(i+1)%N],k/3);base=len(ev)
  for z in [.765,2.53]:
   for a,b in [(-1.80,-.64),(1.72,-.64),(1.72,.64),(-1.8,.64)]:ev.append(q+t*a+n*b+Vector((0,0,z-q.z)))
  ef.extend(tuple(base+j for j in f)for f in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
envelope=BVHTree.FromPolygons(ev,ef)
# Hard obstacles; low ground surfaces are intentionally valid support, not forbidden volume.
hv=[];hf=[];gv=[];gf=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 owner=next((a for a in chain(o)if a.get('decision_kind')),None)
 if owner and owner.get('decision_kind')in ['plant','tree','light','tram']:continue
 v,f=geo(o)
 if not v:continue
 if (not owner and max(p.z for p in v)<.71 and not any(k in o.name.lower()for k in ['rail','sleeper'])) or o.name=='CP18 supported rail ribbon':
  off=len(gv);gv.extend(v);gf.extend(tuple(off+j for j in tri)for tri in f)
 elif (owner and owner.get('decision_kind')in ['resident','animal','bicycle','boat']) or any(a.name in ['tea_house','west_home','post_office','station_main','greenhouse','small_wood_home','hill_home']for a in chain(o)):
  off=len(hv);hv.extend(v);hf.extend(tuple(off+j for j in tri)for tri in f)
hard=BVHTree.FromPolygons(hv,hf,all_triangles=True);ground=BVHTree.FromPolygons(gv,gf,all_triangles=True);kd=KDTree(N)
for i,p in enumerate(points):kd.insert(Vector((p.x,p.y,0)),i)
kd.balance()
def collides(v,f):
 b=BVHTree.FromPolygons(v,f,all_triangles=True)
 if b.overlap(envelope)or b.overlap(hard):return True
 for p in v[::max(1,len(v)//120)]:
  if not .765<p.z<2.53:continue
  _,i,d=kd.find(Vector((p.x,p.y,0)));delta=p-points[i]
  if abs(delta.dot(normals[i]))<.64 and abs(delta.dot(tangents[i]))<.3:return True
 return False
record=[]
for root in roots.values():
 orig=root.matrix_world.copy();vs=[];fs=[]
 for o in root.children_recursive:
  if o.type not in ['MESH','CURVE']:continue
  v,f=geo(o);off=len(vs);vs.extend(v);fs.extend(tuple(off+j for j in tri)for tri in f)
 center=Vector((sum(p.x for p in vs)/len(vs),sum(p.y for p in vs)/len(vs),0));_,idx,_=kd.find(center);n=normals[idx];t=tangents[idx];pivot=orig.translation;found=None
 candidates=[]
 for scale in ([1,.85,.70,.55]if root.get('decision_kind')in ['tree','plant']else[1]):
  for radial in [0,.3,-.3,.6,-.6,.9,-.9,1.2,-1.2,1.5,-1.5]:
   for along in [0,.4,-.4,.8,-.8,1.2,-1.2,1.6,-1.6,2.0,-2.0,2.8,-2.8]:
    for yaw in ([0,.5,-.5,1.0,-1.0,math.pi/2]if root.get('decision_kind')=='plant'else[0]):candidates.append((abs(radial)+abs(along)*.8+abs(yaw)*.12+(1-scale)*3,radial,along,yaw,scale))
 for _,radial,along,yaw,scale in sorted(candidates):
  delta=n*radial+t*along;position=pivot+delta
  hit,normal,i,d=ground.ray_cast(Vector((position.x,position.y,.95)),Vector((0,0,-1)),.42)
  if hit is None or normal.z<.65 or hit.z>.70:continue
  delta.z=max(0,hit.z-.610)+.004
  transform=Matrix.Translation(pivot+delta)@Matrix.Rotation(yaw,4,'Z')@Matrix.Diagonal((scale,scale,1,1))@Matrix.Translation(-pivot);v=[transform@p for p in vs]
  if not collides(v,fs):found=(transform,delta,yaw,scale);break
 if found:
  root.matrix_world=found[0]@orig;bpy.context.view_layer.update();record.append({'id':root.get('decision_entity_id'),'delta':list(found[1]),'yaw_delta':found[2],'horizontal_scale':found[3],'passed':True});print('MOVED',root.name,list(found[1]),found[2],found[3],flush=True)
 else:record.append({'id':root.get('decision_entity_id'),'passed':False});print('UNRESOLVED',root.name,flush=True)
(O/'rail-decor-clearance-final.json').write_text(json.dumps(record,indent=2));reg=json.loads((A/'runtime-registry.json').read_text())
for e in reg['entities']:e['position']=list(bpy.data.objects[e['blender_object']].matrix_world.translation)
(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp18/town-runtime.blend'));print('DONE',sum(x['passed']for x in record),'/',len(record))
