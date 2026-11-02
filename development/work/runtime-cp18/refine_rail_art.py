import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path.cwd();A=R/'app/runtime-cp18/public/assets';O=R/'outputs/runtime-checkpoint-18';s=bpy.context.scene;path=json.loads((A/'rail-path.json').read_text());ps=[Vector(p)for p in path['points']];N=len(ps);normals=[]
for i in range(N):t=(ps[(i+1)%N]-ps[(i-1)%N]).normalized();normals.append(Vector((t.y,-t.x,0)))
def material(name,color):
 m=bpy.data.materials.get(name)or bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.9;return m
mats=[material('CP18 rail garden paper',(.105,.15,.17)),material('CP18 warm paper ballast',(.36,.34,.29)),material('CP18 cut rim slate',(.055,.095,.14)),material('CP18 cut rim middle',(.075,.125,.17)),material('CP18 cut rim pale edge',(.11,.16,.20))]
# Use a convex, softly rounded outer silhouette while retaining the checked track centerline.
def cross(o,a,b):return(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
xy=sorted(set((p.x+n.x*1.0,p.y+n.y*1.0)for p,n in zip(ps,normals)));lo=[]
for p in xy:
 while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
 lo.append(p)
hi=[]
for p in reversed(xy):
 while len(hi)>=2 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
 hi.append(p)
hull=lo[:-1]+hi[:-1];center=sum(ps,Vector())/N
# Radial intersection with the convex outline preserves point correspondence.
def outer_for(p):
 d=Vector((p.x-center.x,p.y-center.y));best=None
 for a,b in zip(hull,hull[1:]+hull[:1]):
  a=Vector(a)-Vector(center[:2]);b=Vector(b)-Vector(center[:2]);e=b-a;den=d.x*e.y-d.y*e.x
  if abs(den)<1e-9:continue
  t=(a.x*e.y-a.y*e.x)/den;u=(a.x*d.y-a.y*d.x)/den
  if t>0 and -.001<=u<=1.001:best=t if best is None else max(best,t)
 return Vector((center.x+d.x*(best or 1),center.y+d.y*(best or 1),0))
old=bpy.data.objects['CP18 supported rail ribbon'];verts=[];faces=[];mis=[]
for i,p in enumerate(ps):
 n=normals[i];inside=Vector(old.data.vertices[3*i].co);outer=outer_for(p)
 row=[(inside,.635),(p-n*.55,.635),(p+n*.55,.635),(outer,.635),(outer+n*.025,.40),(outer+n*.07,.05),(outer+n*.03,-.35),(outer-n*.07,-.72)]
 verts.extend((q.x,q.y,z)for q,z in row)
for i in range(N):
 j=(i+1)%N
 for k in range(7):faces.append((i*8+k,i*8+k+1,j*8+k+1,j*8+k));mis.append([0,1,0,4,2,3,2][k])
me=bpy.data.meshes.new('CP18 layered supported railway bank');me.from_pydata(verts,[],faces);me.update()
for m in mats:me.materials.append(m)
me.polygons.foreach_set('material_index',mis);old.data=me
bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp18/town-runtime.blend'));(O/'rail-art-refinement.json').write_text(json.dumps({'track_points_unchanged':True,'convex_outer_silhouette':True,'layered_paper_edge':4,'small_static_rocks':0,'no_core_architecture_transform_change':True},indent=2));print('RAIL_ART_REFINED')
