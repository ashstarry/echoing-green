import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
R=Path.cwd();reg=json.loads((R/'app/runtime-cp22/public/assets/runtime-registry.json').read_text());e=next(e for e in reg['entities']if e['id']=='boat.pond_boat');boat=bpy.data.objects[e['blender_object']];own={x.name for x in [boat]+list(boat.children_recursive)};dg=bpy.context.evaluated_depsgraph_get();vv=[];ff=[];names=[]
def geom(o):
 ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@p.co for p in m.vertices];f=[tuple(t.vertices)for t in m.loop_triangles];ev.to_mesh_clear();return v,f
for o in bpy.context.scene.objects:
 if o.name in own or o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection)or (o.active_material and o.active_material.name=='Layered paper water')or any(t in o.name.lower()for t in ['water glint','water ripple','duck wake','visible paper rain']):continue
 v,f=geom(o);off=len(vv);vv.extend(v);ff.extend(tuple(off+k for k in tri)for tri in f);names.extend([o.name]*len(f))
world=BVHTree.FromPolygons(vv,ff,all_triangles=True);parts={p['id']:bpy.data.objects[p['blender_object']]for p in e['parts']};base={k:o.matrix_basis.copy()for k,o in parts.items()};results=[]
for sign in [-1,1]:
 for amp in [.04,.065,.09,.12]:
  hits=[]
  for j in range(32):
   t=j/32*math.pi*2
   for side in ['left','right']:
    key='oar_'+side;o=parts[key];z=-.07+math.sin(t)*.025 if side=='left'else math.sin(t+1)*.06;x=sign*(1 if side=='left'else -1)*amp*(.5+.5*math.sin(t));pos,quat,scale=base[key].decompose();o.matrix_basis=Matrix.LocRotScale(pos,quat@Quaternion((0,0,1),z)@Quaternion((1,0,0),x),scale)
   bpy.context.view_layer.update()
   for side in ['left','right']:
    vs=[];fs=[]
    for o in parts['oar_'+side].children_recursive:
     if o.type not in ['MESH','CURVE']:continue
     v,f=geom(o);off=len(vs);vs.extend(v);fs.extend(tuple(off+k for k in tri)for tri in f)
    if vs:
     b=BVHTree.FromPolygons(vs,fs,all_triangles=True);contact=sorted(set(names[j]for i,j in b.overlap(world)))
     if contact:hits.append({'phase':j,'side':side,'objects':contact})
  results.append({'sign':sign,'amplitude':amp,'failures':hits})
(R/'outputs/runtime-checkpoint-22/oar-motion-sweep.json').write_text(json.dumps(results,indent=2));print([(r['sign'],r['amplitude'],len(r['failures']))for r in results])
