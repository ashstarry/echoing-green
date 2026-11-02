import bpy,json,math,time,collections
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path.cwd();OUT=ROOT/'app/runtime-cp17/public/assets';REPORT=ROOT/'outputs/runtime-checkpoint-17';s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();reg=json.loads((OUT/'runtime-registry.json').read_text());nav=json.loads((OUT/'navigation.json').read_text());walkers={a['id']for a in nav['actors']}
def chain(o):
 while o:
  yield o;o=o.parent
def geom(o):
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear();return v,f
vv=[];ff=[];names=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 owner=next((x.get('decision_entity_id')for x in chain(o)if x.get('decision_entity_id')),None)
 if owner in walkers or any(k in o.name.lower()for k in ['rain','glint','ripple','studio floor']):continue
 v,f=geom(o);off=len(vv);vv.extend(v);ff.extend(tuple(off+i for i in t)for t in f);names.extend([o.name]*len(f))
world=BVHTree.FromPolygons(vv,ff,all_triangles=True);checks=[]
# Full loop train geometry survey, including car overhang; first use is gated by this result.
front=bpy.data.objects['tram_car_front'];rear=bpy.data.objects['tram_car_rear'];Q=s.camera.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));BACK=Vector((-RIGHT.y,RIGHT.x,0));center=front.matrix_world.translation-RIGHT*12*math.cos(-1.13)-BACK*6.3*math.sin(-1.13);center.z=.864
railvs=[];railfs=[];railnames=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 if any(x in [front,rear]for x in chain(o))or any(x in o.name.lower()for x in ['continuous rail','sleeper','rain','glint','ripple','studio floor']):continue
 v,f=geom(o);off=len(railvs);railvs.extend(v);railfs.extend(tuple(off+i for i in t)for t in f);railnames.extend([o.name]*len(f))
railworld=BVHTree.FromPolygons(railvs,railfs,all_triangles=True);trainrows=[]
for root in [front,rear]:
 v=[];f=[];inv=root.matrix_world.inverted()
 for o in root.children_recursive:
  if o.type not in ['MESH','CURVE']:continue
  q,t=geom(o);off=len(v);v.extend(inv@p for p in q);f.extend(tuple(off+i for i in t)for t in t)
 rows=[]
 for k in range(721):
  t=-math.pi+2*math.pi*k/720;p=center+RIGHT*12*math.cos(t)+BACK*6.3*math.sin(t);d=RIGHT*(-12*math.sin(t))+BACK*(6.3*math.cos(t));yaw=math.atan2(d.y,d.x);m=Matrix.Translation(p)@Matrix.Rotation(yaw,4,'Z')@Matrix.Diagonal((*root.scale,1));body=BVHTree.FromPolygons([m@x for x in v],f,all_triangles=True);bad=set(railnames[j]for i,j in body.overlap(railworld));rows.append({'t':t,'bad':list(bad)})
 trainrows.append({'id':root.get('decision_entity_id'),'poses':rows})
rail={'center':list(center),'right':list(RIGHT),'back':list(BACK),'radius':[12,6.3],'full_loop_pass':all(not r['bad']for car in trainrows for r in car['poses']),'cars':trainrows}
(REPORT/'rail-motion-check.json').write_text(json.dumps(rail,indent=2));print(json.dumps({'passed':rail['full_loop_pass'],'right':list(RIGHT),'failures':[sum(bool(x['bad'])for x in c['poses'])for c in trainrows]}))
