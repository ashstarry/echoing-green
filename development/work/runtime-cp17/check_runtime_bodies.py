import bpy,json,math,collections
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path.cwd();OUT=ROOT/'outputs/runtime-checkpoint-17';assets=ROOT/'app/runtime-cp17/public/assets';nav=json.loads((assets/'navigation.json').read_text());reg=json.loads((assets/'runtime-registry.json').read_text());trace=json.loads((OUT/'motion-trace.json').read_text());s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();ids={a['id']for a in nav['actors']if a['entry']};body={};wv=[];wf=[];wn=[]
def chain(o):
 while o:
  yield o;o=o.parent
def geo(o):
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear();return v,f
for e in reg['entities']:
 if e['id']not in ids:continue
 root=bpy.data.objects[e['blender_object']];inv=root.matrix_world.inverted();chunks=[]
 for o in root.children_recursive:
  if o.type!='MESH':continue
  v,f=geo(o);p=next((a for a in chain(o)if a.get('decision_part_id')),None);chunks.append({'v':[inv@x for x in v],'f':f,'name':o.name,'part':p.get('decision_part_id')if p else'', 'pivot':p.location.copy()if p else Vector((0,0,0))})
 body[e['id']]={'chunks':chunks,'scale':root.matrix_world.to_scale()}
for o in s.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 if any(a.get('decision_entity_id')in ids for a in chain(o))or any(k in o.name.lower()for k in ['rain','glint','ripple','studio floor']):continue
 v,f=geo(o);off=len(wv);wv.extend(v);wf.extend(tuple(off+i for i in t)for t in f);wn.extend([o.name]*len(f))
world=BVHTree.FromPolygons(wv,wf,all_triangles=True);issues=[];count=0;ground_contacts=0
for frame in trace:
 for a in frame['actors']:
  b=body[a['id']];m=Matrix.Translation(Vector(a['p']))@Matrix.Rotation(a['yaw'],4,'Z')@Matrix.Diagonal((*b['scale'],1));vv=[];ff=[];nn=[];gait=math.sin(a['phase']*9)*.19 if a['mode']=='walk'else 0
  for c in b['chunks']:
   part=c['part'];angle=0;pivot=c['pivot'];shift=Vector((0,0,0))
   if part.startswith('anim_leg_'):angle=gait*(1 if part.endswith('left')else-1);shift.z=abs(gait)*.24
   if part.startswith('anim_arm_'):angle=-gait*(1 if part.endswith('left')else-1)*.5
   rot=Matrix.Rotation(angle,4,'X');off=len(vv);vv.extend(m@(pivot+rot@(v-pivot)+shift)for v in c['v']);ff.extend(tuple(off+i for i in f)for f in c['f']);nn.extend([c['name']]*len(c['f']))
  bvh=BVHTree.FromPolygons(vv,ff,all_triangles=True);pairs=set((nn[i],wn[j])for i,j in bvh.overlap(world));count+=1
  if pairs:issues.append({'time':frame['time'],'id':a['id'],'position':a['p'],'pairs':list(pairs)})
result={'passed':not issues,'sampled_seconds':trace[-1]['time'],'body_poses':count,'sample_interval_seconds':.5,'issues':issues,'scope':'Actual evaluated body triangles with runtime root positions, turns, rigid arm/leg gait and foot lift. Static geometry and stationary residents included. Discrete 0.5s samples, not a continuous collision proof. Pairwise moving-resident envelopes tested separately.'};(OUT/'runtime-body-check.json').write_text(json.dumps(result,indent=2));print(json.dumps({'passed':result['passed'],'body_poses':count,'issues':len(issues),'examples':issues[:5]},indent=2))
