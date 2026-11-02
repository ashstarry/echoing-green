import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path.cwd();d=json.loads((R/'work/runtime-cp20/browser-mesh-motion.json').read_text());C=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
def mat(a):return C@Matrix([a[i:i+4]for i in range(0,16,4)]).transposed()
nav=json.loads((R/'app/runtime-cp20/public/assets/navigation.json').read_text());ids={a['id']for a in nav['actors']if a['entry']};geos={int(k):{'v':[Vector(v[i:i+3])for i in range(0,len(v),3)],'f':[ix[i:i+3]for i in range(0,len(ix),3)]}for k,g in d['geometries'].items()for v,ix in [(g['vertices'],g['indices']or list(range(len(g['vertices'])//3)))]}
vv=[];ff=[]
for i,n in enumerate(d['meshes']):
 if n['owner']!='scenery':continue
 g=geos[n['gid']];m=mat(d['frames'][0]['matrices'][i]);off=len(vv);vv.extend(m@v for v in g['v']);ff.extend(tuple(off+k for k in f)for f in g['f'])
tree=BVHTree.FromPolygons(vv,ff,all_triangles=True);issues=[];count=0;max_gap=0
for frame in d['frames'][::4]:
 for id in ids:
  actor=next(a for a in frame['state']['actors']if a['id']==id);r=frame['state']['residents'][id];elapsed=frame['time']-r['started']
  if actor['task']=='hop'and actor['mode']=='idle'and actor['reservation']is not None and elapsed<1.9:continue
  feet=[]
  for i,n in enumerate(d['meshes']):
   if id in n['chain']and 'anim_ankle_'in n['name']:
    m=mat(frame['matrices'][i]);vs=[m@v for v in geos[n['gid']]['v']];z=min(v.z for v in vs);sole=[v for v in vs if v.z<z+.015];probes=list({tuple(round(x,5)for x in v):v for v in sole}.values());probes.append(sum(sole,Vector())/len(sole));gaps=[]
    for p in probes:
     hit,no,idx,dist=tree.ray_cast(p+Vector((0,0,.045)),Vector((0,0,-1)),.5)
     if hit is not None and no.z>.4:gaps.append(z-hit.z)
    if len(gaps)>=2:feet.append(sorted(gaps)[1])
  count+=1
  if not feet or min(feet)>.05 or min(feet)<-.06:issues.append({'time':frame['time'],'id':id,'foot_gaps':feet})
  elif feet:max_gap=max(max_gap,min(feet))
q={'passed':not issues,'walking_actor_samples':count,'maximum_lower_foot_gap':max_gap,'issues':issues,'scope':'Actual browser boot sole vertices plus center against static scene every 2 seconds. At least two support probes on the lower foot within [-.06,.05] scene units. Explicit intentional hop phases skipped; swing foot may lift. Handles grout gaps beneath a center without treating them as unsupported feet; not a continuous proof.'};(R/'outputs/runtime-checkpoint-20/browser-walking-support.json').write_text(json.dumps(q,indent=2));print(q['passed'],count,'issues',len(issues))
