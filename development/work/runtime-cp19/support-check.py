import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path.cwd();d=json.loads((R/'work/runtime-cp19/browser-mesh-motion.json').read_text());C=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
def mat(a):return C@Matrix([a[i:i+4]for i in range(0,16,4)]).transposed()
nav=json.loads((R/'app/runtime-cp19/public/assets/navigation.json').read_text());ids={a['id']for a in nav['actors']if a['entry']};geos={int(k):{'v':[Vector(v[i:i+3])for i in range(0,len(v),3)],'f':[ix[i:i+3]for i in range(0,len(ix),3)]}for k,g in d['geometries'].items()for v,ix in [(g['vertices'],g['indices']or list(range(len(g['vertices'])//3)))]}
vv=[];ff=[]
for i,n in enumerate(d['meshes']):
 if n['owner']!='scenery':continue
 g=geos[n['gid']];m=mat(d['frames'][0]['matrices'][i]);off=len(vv);vv.extend(m@v for v in g['v']);ff.extend(tuple(off+k for k in f)for f in g['f'])
tree=BVHTree.FromPolygons(vv,ff,all_triangles=True);issues=[];count=0;max_gap=0
for frame in d['frames'][::4]:
 for id in ids:
  feet=[]
  for i,n in enumerate(d['meshes']):
   if id in n['chain']and 'anim_ankle_'in n['name']:
    m=mat(frame['matrices'][i]);vs=[m@v for v in geos[n['gid']]['v']];z=min(v.z for v in vs);sole=[v for v in vs if v.z<z+.015];p=sum(sole,Vector())/len(sole);hit,no,idx,dist=tree.ray_cast(p+Vector((0,0,.045)),Vector((0,0,-1)),.5)
    if hit is not None and no.z>.4:feet.append(z-hit.z)
  count+=1
  if not feet or min(feet)>.08 or min(feet)<-.06:issues.append({'time':frame['time'],'id':id,'foot_gaps':feet})
  elif feet:max_gap=max(max_gap,min(feet))
q={'passed':not issues,'walking_actor_samples':count,'maximum_lower_foot_gap':max_gap,'issues':issues,'scope':'Actual browser boot mesh sole centers against static scene, every 2 seconds. At least one lower foot supported within [-.06,.08] scene units; swing foot allowed to lift. Discrete coarse support diagnostic, not all corners/continuous proof.'};(R/'outputs/runtime-checkpoint-19/browser-walking-support.json').write_text(json.dumps(q,indent=2));print(q['passed'],count,'issues',len(issues))
