import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];names=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 if 'Fox' in o.name or o.name=='garden_fox':continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear();off=len(vs);vs+=v;fs.extend(tuple(off+i for i in t)for t in f);names.extend([o.name]*len(f))
w=BVHTree.FromPolygons(vs,fs,all_triangles=True);r=bpy.data.objects['garden_fox'];print('FOX',list(r.matrix_world.translation),list(r.matrix_world.to_scale()))
for dx,dy in [(0,0),(.3,0),(-.3,0),(0,.3),(0,-.3),(1,0),(-1,0),(0,1),(0,-1)]:
 p=r.matrix_world.translation+Vector((dx,dy,0));h,n,i,d=w.ray_cast(Vector((p.x,p.y,.95)),Vector((0,0,-1)),1);print('RAY',dx,dy,list(h)if h else None,list(n)if n else None,names[i]if i is not None else None)
