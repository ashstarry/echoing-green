import bpy,json,math,time,collections
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path.cwd();OUT=ROOT/'app/runtime-cp30/public/assets';REPORT=ROOT/'outputs/runtime-checkpoint-30';s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();reg=json.loads((OUT/'runtime-registry.json').read_text());nav=json.loads((OUT/'navigation.json').read_text());walkers={a['id']for a in nav['actors']}|set(json.loads((OUT/'motion-activities.json').read_text())['clips'])|{'resident.cyclist','kite.plaza_kite'}
def chain(o):
 while o:
  yield o;o=o.parent
def geom(o):
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear();return v,f
vv=[];ff=[];names=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 owner=next((x.get('decision_entity_id')for x in chain(o)if x.get('decision_entity_id')),None)
 if any(x.get('decision_entity_id')in walkers for x in chain(o)) or any(k in o.name.lower()for k in ['visible paper rain','glint','ripple','studio floor']):continue
 v,f=geom(o);off=len(vv);vv.extend(v);ff.extend(tuple(off+i for i in t)for t in f);names.extend([o.name]*len(f))
world=BVHTree.FromPolygons(vv,ff,all_triangles=True);checks=[]
# Connect authored standing positions to the conservative grid. Full original body at sampled orientations.
for a in nav['actors']:
 e=next(e for e in reg['entities']if e['id']==a['id']);r=bpy.data.objects[e['blender_object']];orig=r.matrix_world.copy();inv=orig.inverted();v=[];f=[]
 for o in r.children_recursive:
  if o.type!='MESH':continue
  q,t=geom(o);off=len(v);v.extend(inv@p for p in q);f.extend(tuple(off+i for i in t)for t in t)
 valid=None;failures=[]
 for node in a['nearest']:
  target=nav['nodes'][node];p0=Vector(a['position']);p1=Vector((target[0],target[1],target[2]-.02*a['scale'][2]+.006));yaw=math.atan2(p1.y-p0.y,p1.x-p0.x)+math.pi/2;delta=math.atan2(math.sin(yaw-a['yaw']),math.cos(yaw-a['yaw']));bad=set();count=0
  for k in range(17):
   u=k/16;p=p0.lerp(p1,u);angle=a['yaw']+delta*min(1,u*3);m=Matrix.Translation(p)@Matrix.Rotation(angle,4,'Z')@Matrix.Diagonal((*a['scale'],1));body=BVHTree.FromPolygons([m@x for x in v],f,all_triangles=True)
   for i,j in body.overlap(world):
    if 'plaza stone ring' not in names[j]:bad.add(names[j])
   count+=1
  if not bad:valid=node;checks.append({'id':a['id'],'node':node,'samples':count,'passed':True,'note':'Paving contacts excluded from rigid rest-pose test; browser articulated foot support and contacts must be checked separately.'});break
  failures.append({'node':node,'obstacles':list(bad)[:10]})
 a['entry']=[valid]if valid is not None else[]
 if valid is None:checks.append({'id':a['id'],'passed':False,'attempts':failures})
(OUT/'navigation.json').write_text(json.dumps(nav,separators=(',',':')));(REPORT/'entry-motion-check.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
