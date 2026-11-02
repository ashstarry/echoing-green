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
def sample(distance):
 d=distance%L;j=next(i for i in range(N)if lengths[i+1]>=d);u=(d-lengths[j])/(lengths[j+1]-lengths[j]);return points[j].lerp(points[(j+1)%N],u)
def pose(distance,root):
 d=distance%L;j=next(i for i in range(N)if lengths[i+1]>=d);u=(d-lengths[j])/(lengths[j+1]-lengths[j]);p=points[j].lerp(points[(j+1)%N],u);t=(sample(distance+1.166)-sample(distance-1.166)).normalized();p.z+=.124
 return Matrix.Translation(p)@Matrix.Rotation(math.atan2(t.y,t.x),4,'Z')@Matrix.Diagonal((*root.scale,1))
vv=[];ff=[];nn=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 if any(a.get('decision_kind')=='tram'for a in chain(o))or any(x in o.name.lower()for x in ['continuous rail','sleeper','visible paper rain','glint','ripple','studio floor']):continue
 v,f=geometry(o);off=len(vv);vv.extend(v);ff.extend(tuple(off+i for i in t)for t in f);nn.extend([o.name]*len(f))
world=BVHTree.FromPolygons(vv,ff,all_triangles=True);cars=[]
for name in ['tram_car_front','tram_car_rear']:
 root=bpy.data.objects[name];inv=root.matrix_world.inverted();v=[];f=[];bn=[]
 for o in root.children_recursive:
  if o.type not in ['MESH','CURVE']:continue
  q,t=geometry(o);off=len(v);v.extend(inv@p for p in q);f.extend(tuple(off+i for i in tri)for tri in t);bn.extend([o.name]*len(t))
 issues=[]
 for k in range(1200):
  d=L*k/1200;m=pose(d,root);body=BVHTree.FromPolygons([m@p for p in v],f,all_triangles=True);pairs=set((bn[i],nn[j])for i,j in body.overlap(world))
  if pairs:issues.append({'distance':d,'pairs':[list(p)for p in pairs]})
 orig=root.matrix_world.translation;nearest=min(range(N),key=lambda i:(points[i]-orig).length);cars.append({'id':root.get('decision_entity_id'),'yaw':root.matrix_world.to_euler().z,'scale':list(root.scale),'start_distance':lengths[nearest],'initial_nearest_distance':(points[nearest]-Vector((orig.x,orig.y,points[nearest].z))).length,'issues':issues})
print(json.dumps({'length':L,'points':N,'cars':[{'id':c['id'],'bad_poses':len(c['issues']),'obstacles':collections.Counter(p[1]for row in c['issues']for p in row['pairs']).most_common(25)}for c in cars]},indent=2))
result={'coordinates':'Blender Z up','points':[list(p)for p in points],'lengths':lengths,'length':L,'root_height_above_rail':.124,'cars':cars,'poses_per_car':1200,'passed':not any(c['issues']for c in cars),'scope':'Actual 240-point closed centerline between both model rail curves. Full car evaluated-mesh samples every ~0.057 units; excludes intended rails/sleepers and own train assembly.'};(O/'rail-clearance-final.json').write_text(json.dumps(result,indent=2));(A/'rail-path.json').write_text(json.dumps({k:v for k,v in result.items()if k!='cars'}|{'cars':[{k:v for k,v in c.items()if k!='issues'}for c in cars]},indent=2))
