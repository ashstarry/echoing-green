import bpy,json,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();groups=collections.defaultdict(lambda:{'objects':0,'triangles':0});meshes={};tris=0
largest=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE'] or o.hide_render or any(c.hide_render or c.name.startswith('12_') for c in o.users_collection):continue
 ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();n=len(m.loop_triangles);tris+=n;col=o.users_collection[0].name;groups[col]['objects']+=1;groups[col]['triangles']+=n;largest.append((n,o.name))
 if o.type=='MESH':meshes[o.data.name]={'users':o.data.users,'vertices':len(o.data.vertices),'faces':len(o.data.polygons)}
 ev.to_mesh_clear()
data={'objects':len(s.objects),'render_triangles':tris,'render_mesh_objects':sum(x['objects'] for x in groups.values()),'collections':groups,'unique_source_meshes':len(meshes),'materials':len(bpy.data.materials),'images':len(bpy.data.images),'largest':sorted(largest,reverse=True)[:25],'lights':[{'name':o.name,'type':o.data.type,'power':o.data.energy,'location':list(o.location)} for o in s.objects if o.type=='LIGHT'],'bench_children':[{'name':o.name,'location':list(o.location),'scale':list(o.scale)} for o in bpy.data.objects['CP05_overlook_bench'].children]}
(ROOT/'work/modeling-cp07/draft-audit.json').write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))

Q=s.camera.rotation_euler.to_quaternion();from mathutils import Vector
right=Q@Vector((1,0,0));back=Vector((-right.y,right.x,0))
for name in ['lantern_tree','district_tree_0','district_tree_1','district_tree_2','district_tree_3','greenhouse','station_main','tea_house','CP02 pond','CP02 restrained flower bed leaf.282']:
 o=bpy.data.objects.get(name)
 if o:print('DETAIL',name,'rb',o.matrix_world.translation.dot(right),o.matrix_world.translation.dot(back),'loc',list(o.location),'scale',list(o.scale),'children',[(c.name,list(c.location),list(c.scale)) for c in list(o.children)[:20]])
print('MATS',[(m.name,list(m.diffuse_color)) for m in bpy.data.materials])
