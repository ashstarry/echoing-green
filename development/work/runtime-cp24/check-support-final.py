import hashlib
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path.cwd();d=json.loads((R/'work/runtime-cp24/capture-round6/browser-mesh-motion.json').read_text());C=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
capture_path=R/'work/runtime-cp24/capture-round6/browser-mesh-motion.json'
_h=hashlib.sha256()
with capture_path.open('rb') as _f:
 for _chunk in iter(lambda:_f.read(1048576),b''):_h.update(_chunk)
capture_sha256=_h.hexdigest()
def mat(a):return C@Matrix([a[i:i+4]for i in range(0,16,4)]).transposed()
geos={int(k):{'v':[Vector(v[i:i+3])for i in range(0,len(v),3)],'f':[ix[i:i+3]for i in range(0,len(ix),3)]}for k,g in d['geometries'].items()for v,ix in [(g['vertices'],g['indices']or list(range(len(g['vertices'])//3)))]}
def tree(indices,frame):
 vv=[];ff=[]
 for i in indices:
  g=geos[d['meshes'][i]['gid']];m=mat(frame['matrices'][i]);off=len(vv);vv.extend(m@p for p in g['v']);ff.extend(tuple(off+k for k in t)for t in g['f'])
 return BVHTree.FromPolygons(vv,ff,all_triangles=True)
static=tree([i for i,n in enumerate(d['meshes'])if n['owner']=='scenery'and'WEB water'not in n['materials']],d['frames'][0]);cars=[i for i,n in enumerate(d['meshes'])if any(x.startswith('tram.')for x in n['chain'])];ids={a['id']for a in d['frames'][0]['state']['actors']}|set(d['frames'][0]['state'].get('localWalkers',{}))|{'resident.water_visitor','resident.station_traveler'};foot_mesh={id:[i for i,n in enumerate(d['meshes'])if id in n['chain']and'anim_ankle_'in n['name']]for id in ids};count=0;issues=[];maxgap=0
for fr in d['frames'][::4]:
 moving=tree(cars,fr)
 for id in ids:
  a=next((a for a in fr['state']['actors']if a['id']==id),None);r=fr['state']['residents'][id]
  if a and a['task']=='hop'and a['mode']=='idle'and a['reservation']is not None and fr['time']-r['started']<1.9:continue
  feet=[]
  for i in foot_mesh[id]:
   m=mat(fr['matrices'][i]);vs=[m@v for v in geos[d['meshes'][i]['gid']]['v']];z=min(v.z for v in vs);sole=[v for v in vs if v.z<z+.015];probes=list({tuple(round(q,5)for q in v):v for v in sole}.values());probes.append(sum(sole,Vector())/len(sole));gaps=[]
   for p in probes:
    found=[]
    for world in [static,moving]:
     hit,no,idx,dist=world.ray_cast(p+Vector((0,0,.045)),Vector((0,0,-1)),.5)
     if hit is not None and no.z>.4:found.append(hit.z)
    if found:gaps.append(p.z-max(found))
   acceptable=sorted(x for x in gaps if x>=-.006)
   if len(acceptable)>=2:feet.append(acceptable[1])
  count+=1
  if not feet or min(feet)>.05:issues.append({'time':fr['time'],'id':id,'foot_gaps':feet})
  elif feet:maxgap=max(maxgap,min(feet))
report={'capture_file':str(capture_path.relative_to(R)),'capture_sha256':capture_sha256,'passed':not issues,'actor_samples':count,'max_supported_foot_gap':maxgap,'issues':issues,'scope':'Actual decoded shoe soles, at least two support probes on either planted foot. Static paving/stairs/bridge plus moving carriage floors and boarding bridge. One-second samples; intentional child hops excluded. Not a continuous-time proof.'};(R/'outputs/runtime-checkpoint-24/support-final.json').write_text(json.dumps(report,indent=2));print('SUPPORT',report['passed'],count,'issues',len(issues));print(issues[:12])
