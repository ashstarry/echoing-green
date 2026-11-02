exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
from mathutils.bvhtree import BVHTree
from collections import Counter
dg=bpy.context.evaluated_depsgraph_get();vv=[];ff=[];names=[]
def geometry(o):
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices) for t in me.loop_triangles];ev.to_mesh_clear();return v,f
for o in s.objects:
 if o.type not in ['MESH','CURVE'] or o.hide_render or any(c.hide_render or c.name.startswith('12_') for c in o.users_collection):continue
 if 'visible paper rain'in o.name:continue
 v,f=geometry(o);off=len(vv);vv+=v;ff.extend(tuple(off+i for i in t) for t in f);names.extend([o.name]*len(f))
world=BVHTree.FromPolygons(vv,ff,all_triangles=True);results=[]
for name,mode,steps in [('station_entry_door','slide',[0,.185,.37,.555,.74]),('bicycle_wheel_front','turn',[i*math.pi/4 for i in range(8)]),('bicycle_wheel_rear','turn',[i*math.pi/4 for i in range(8)]),('hill_windwheel__rotor','turn',[i*math.pi/4 for i in range(8)])]:
 o=bpy.data.objects[name];saved=o.matrix_basis.copy();own={x.name for x in [o]+list(o.children_recursive)};frames=[]
 for value in steps:
  o.matrix_basis=saved@(Matrix.Translation((value,0,0)) if mode=='slide' else Matrix.Rotation(value,4,'Y'));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();v=[];f=[];source=[]
  for x in [o]+list(o.children_recursive):
   if x.type not in ['MESH','CURVE']:continue
   a,b=geometry(x);off=len(v);v+=a;f.extend(tuple(off+i for i in t) for t in b);source.extend([x.name]*len(b))
  bv=BVHTree.FromPolygons(v,f,all_triangles=True);counts=Counter((source[a],names[b]) for a,b in bv.overlap(world) if names[b]not in own);frames.append({'value':value,'contacts':[{'part_mesh':a,'other':b,'pairs':n} for (a,b),n in counts.items()]})
 o.matrix_basis=saved;bpy.context.view_layer.update();results.append({'node':name,'mode':mode,'samples':frames})
record={'method':'Evaluated triangle overlap at sampled mechanical control poses; no character animation sweep','tests':results,'passed':not any(x['contacts'] for r in results for x in r['samples']),'limits':'Discrete poses only; no full continuous-time proof, cloth deformation, crowd movement or navigation.'};(OUT/'control-clearance-check.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2),flush=True)
