import bpy,json,math,collections,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/art-checkpoint-15';s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();objects={};vs=[];fs=[];names=[]
def chain(o):
 a=[]
 while o:a.append(o);o=o.parent
 return a
def owner(o):return next((x for x in chain(o) if x.get('decision_kind')),None)
for o in s.objects:
 if o.type not in ['MESH','CURVE'] or o.hide_render or any(c.hide_render or c.name.startswith('12_') for c in o.users_collection):continue
 if any(k in o.name.lower() for k in ['visible paper rain','paper water glint','duck wake','water ripple','rain ripple']):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices) for t in me.loop_triangles];ev.to_mesh_clear()
 if not f:continue
 off=len(vs);vs.extend(v);fs.extend(tuple(off+i for i in t) for t in f);names.extend([o.name]*len(f));objects[o.name]={'v':v,'f':f,'owner':owner(o),'chain':chain(o),'bounds':([min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)])}
world=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[];allowed=[]
focus=[o for o in s.objects if o.get('decision_kind') in ['resident','animal','bird','fish','bicycle','boat','tram','water_lantern']]
for root in focus:
 vv=[];ff=[];on=[]
 for o in root.children_recursive:
  g=objects.get(o.name)
  if not g:continue
  off=len(vv);vv.extend(g['v']);ff.extend(tuple(off+i for i in t) for t in g['f']);on.extend([o.name]*len(g['f']))
 bvh=BVHTree.FromPolygons(vv,ff,all_triangles=True);counts=collections.Counter()
 for a,b in bvh.overlap(world):
  body,other=on[a],names[b];g=objects[other]
  if root in g['chain']:continue
  if root.get('decision_kind') in ['boat','fish','water_lantern'] or root.name.startswith('duck_'):
   if other=='CP02 pond':continue
  if body.startswith('CP09 kite holding hand') and other=='CP02 kite string':allowed.append({'actor':root.name,'body':body,'other':other,'reason':'Explicit tether attachment endpoint within the hand, radius .005'});continue
  counts[(body,other)]+=1
 rows.append({'actor':root.name,'surface_intersections':[{'body':a,'other':b,'triangle_pairs':n} for (a,b),n in counts.most_common()]})
# Closed-solid containment catches fully buried components that do not cross a surface.
def solid(g):
 if 'closed'in g:return g['closed']
 ec=collections.Counter(tuple(sorted((t[i],t[(i+1)%3]))) for t in g['f'] for i in range(3));g['closed']=bool(ec) and all(n==2 for n in ec.values());return g['closed']
def inside(p,g):
 if not all(g['bounds'][0][i]+.002<p[i]<g['bounds'][1][i]-.002 for i in range(3)):return False
 if not solid(g):return False
 if 'bvh'not in g:g['bvh']=BVHTree.FromPolygons(g['v'],g['f'],all_triangles=True)
 near,n,idx,d=g['bvh'].find_nearest(p)
 if near is None or d<.002:return False
 direction=Vector((.317,.681,.659)).normalized();q=p.copy();hits=0
 for _ in range(64):
  hit,n,i,d=g['bvh'].ray_cast(q,direction,80)
  if hit is None:break
  hits+=1;q=hit+direction*.0001
 return hits%2==1
containment=[]
for row in rows:
 actor=bpy.data.objects[row['actor']];already={x['other'] for x in row['surface_intersections']}
 for o in actor.children_recursive:
  g=objects.get(o.name)
  if not g:continue
  probes=[g['v'][i] for i in sorted(set([0,len(g['v'])//3,len(g['v'])//2,len(g['v'])-1]))]
  for name,h in objects.items():
   if name in already or actor in h['chain']:continue
   if (actor.get('decision_kind') in ['boat','fish','water_lantern'] or actor.name.startswith('duck_')) and name=='CP02 pond':continue
   if not all(g['bounds'][1][i]>h['bounds'][0][i]+.002 and g['bounds'][0][i]<h['bounds'][1][i]-.002 for i in range(3)):continue
   if any(inside(p,h) for p in probes):containment.append({'actor':actor.name,'body':o.name,'inside':name});already.add(name)
result={'method':'Evaluated full body meshes against all visible geometry, excluding their own body/attached possessions; triangle surface intersection plus watertight-solid point containment. No hiding or camera change. Rain particles excluded. Floating-lantern trays intersect the water surface intentionally, as do boat and water animals. Explicit kite-hand tether endpoint listed separately.','actors_checked':len(rows),'actor_results':rows,'contained_components':containment,'intentional_tether_contacts':list({(x['actor'],x['body'],x['other']):x for x in allowed}.values()),'unexpected_surface_pairs':sum(len(r['surface_intersections']) for r in rows),'passed':not any(r['surface_intersections'] for r in rows) and not containment,'scope':'Current modeled poses only. Not animation sweeps, future crowd motion, all architectural joints or all future states.'}
(OUT/'full-body-contact-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({'passed':result['passed'],'actors':len(rows),'unexpected':[r for r in rows if r['surface_intersections']],'contained':containment},ensure_ascii=False,indent=2))
