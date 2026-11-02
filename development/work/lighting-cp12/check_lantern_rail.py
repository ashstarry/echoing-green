import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/lighting-checkpoint-12';s=bpy.context.scene;Q=s.camera.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));BACK=Vector((-RIGHT.y,RIGHT.x,0))
exec(compile((ROOT/'work/modeling-cp10/rail_helpers.py').read_text(),'<rail helpers>','exec'))
dg=bpy.context.evaluated_depsgraph_get();vv=[];ff=[];names=[];lamps=[o for o in s.objects if o.get('decision_kind')=='water_lantern']
for root in lamps:
 for o in root.children_recursive:
  if o.type!='MESH':continue
  v,f=geometry(o,dg);off=len(vv);vv.extend(v);ff.extend(tuple(off+i for i in t)for t in f);names.extend([o.name]*len(f))
world=BVHTree.FromPolygons(vv,ff,all_triangles=True);rows=[]
for root in [bpy.data.objects['tram_car_front'],bpy.data.objects['tram_car_rear']]:
 v,f,names_car=car_local(root);fail=[];boxhits=[]
 for i in range(281):
  t=-1.4+i*1.4/280;m=pose(root,t);pts=[m@p for p in v];tree=BVHTree.FromPolygons(pts,f,all_triangles=True);pairs=tree.overlap(world)
  if pairs:fail.append({'sample':i,'objects':sorted({names[b]for a,b in pairs})})
  lo=[min(p[j]for p in v)for j in range(3)];hi=[max(p[j]for p in v)for j in range(3)];inv=m.inverted()
  # Also reject lantern vertices fully inside the conservative whole-car box.
  if any(all(lo[j]-.001<(inv@p)[j]<hi[j]+.001 for j in range(3))for p in vv):boxhits.append(i)
 rows.append({'car':root.name,'samples':281,'surface_failures':fail,'conservative_car_box_hits':boxhits})
pond=bpy.data.objects['CP02 pond'];v,f=geometry(pond,dg);water=BVHTree.FromPolygons(v,f,all_triangles=True);support=[]
for root in lamps:
 tray=next(o for o in root.children if o.name.startswith('CP12 floating lamp tray'));v,f=geometry(tray,dg)
 for p in v:
  h,n,i,d=water.ray_cast(p+Vector((0,0,.1)),Vector((0,0,-1)),.3);support.append({'lamp':root.name,'corner':list(p),'water_hit':h is not None})
record={'passed':all(not r['surface_failures']and not r['conservative_car_box_hits']for r in rows)and all(p['water_hit']for p in support),'car_checks':rows,'sampled_car_poses':562,'water_support':support,'scope':'Both complete cars at 281 front/right-arc poses each against two new lanterns. Triangle intersections plus conservative car-box containment; water ray checks at tray corners. Not continuous sweeps, complete-loop clearance or a drift/rail simulation.'}
(OUT/'water-lantern-placement-check.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2));assert record['passed']
