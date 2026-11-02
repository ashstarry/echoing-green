import bpy,json,math,time,collections
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path.cwd();O=R/'outputs/runtime-checkpoint-19';data=json.loads((R/'work/runtime-cp19/browser-mesh-motion.json').read_text());nodes=data['meshes'];frames=data['frames'];geoms={int(k):{'v':[Vector(v[i:i+3])for i in range(0,len(v),3)],'f':[tuple(ix[i:i+3])for i in range(0,len(ix),3)]}for k,g in data['geometries'].items()for v,ix in [(g['vertices'],g['indices']or list(range(len(g['vertices'])//3)))]};C=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
def matrix(flat):return C@Matrix([flat[i:i+4]for i in range(0,16,4)]).transposed()
# Real browser matrices, decoded geometry and renderer hierarchy, including parented riders and letters.
subject=set(a['id']for a in frames[0]['state']['actors'])|set(frames[0]['state']['movers'])|set(frames[0]['state']['diners'])|{'tram.tram_car_front','tram.tram_car_rear','boat.pond_boat','kite.plaza_kite','water_lantern.pond_paper_lantern_0','water_lantern.pond_paper_lantern_1','resident.vendor_bread','resident.vendor_flower','resident.vendor_lamp','resident.musician','resident.station_attendant','resident.station_traveler'}
subject|={e['id']for e in json.loads((R/'app/runtime-cp19/public/assets/runtime-registry.json').read_text())['entities']if e['kind']in ['windmill','resident','door'] or ('dining_chair'in e['id'])}
groups=collections.defaultdict(list);scenery=[]
for i,n in enumerate(nodes):
 group=next((x for x in reversed(n['chain'])if x in subject),None)
 if group:groups[group].append(i)
 else:scenery.append(i)
static=[i for i in scenery if all(max(abs(a-b)for a,b in zip(fr['matrices'][i],frames[0]['matrices'][i]))<1e-7 for fr in frames)];dynamic=[i for i in scenery if i not in static]
def bvh(indices,fr):
 vv=[];ff=[];nn=[]
 for i in indices:
  n=nodes[i]
  if any(m=='WEB water'for m in n['materials']):continue
  g=geoms[n['gid']];m=matrix(fr['matrices'][i]);off=len(vv);vv.extend(m@p for p in g['v']);ff.extend(tuple(off+k for k in f)for f in g['f']);nn.extend((i,j)for j in range(len(g['f'])))
 if not vv:return None,[],None
 bounds=([min(p[k]for p in vv)for k in range(3)],[max(p[k]for p in vv)for k in range(3)])
 return BVHTree.FromPolygons(vv,ff,all_triangles=True),nn,bounds
base,bnames,_=bvh(static,frames[0]);issues=[];count=0;begin=time.time();samples=[]
def boxoverlap(a,b):return a and b and all(a[0][k]<=b[1][k]and a[1][k]>=b[0][k]for k in range(3))
# Water-painted glints are liquid decoration, not solid collision surfaces.
source_v=[];source_f=[];source_names=[];dg=bpy.context.evaluated_depsgraph_get()
for obj in bpy.context.scene.objects:
 if obj.type not in ['MESH','CURVE']or obj.hide_render or any(c.hide_render or c.name.startswith('12_')for c in obj.users_collection):continue
 ev=obj.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();q=[ev.matrix_world@p.co for p in me.vertices];t=[tuple(x.vertices)for x in me.loop_triangles];ev.to_mesh_clear();off=len(source_v);source_v.extend(q);source_f.extend(tuple(off+k for k in tri)for tri in t);source_names.extend([obj.name]*len(t))
source_tree=BVHTree.FromPolygons(source_v,source_f,all_triangles=True);liquid_contacts=[]
def summarize(pairs,an,bn):
 out={}
 for i,j in pairs:
  ai,at=an[i];bi,bt=bn[j];key=(nodes[ai]['owner'],nodes[ai]['name'],nodes[bi]['owner'],nodes[bi]['name'])
  if key not in out:
   g=geoms[nodes[bi]['gid']];m=matrix(fr['matrices'][bi]);tri=g['f'][bt];point=sum((m@g['v'][k]for k in tri),Vector())/3
   hit,normal,source_idx,dist=source_tree.find_nearest(point);source_name=source_names[source_idx]if source_idx is not None else ''
   if dist is not None and dist<.003 and any(word in source_name.lower()for word in ['water glint','water ripple','duck wake']):
    liquid_contacts.append({'time':fr['time'],'subject':nodes[ai]['owner'],'effect':source_name});continue
   out[key]={'a':list(key[:2]),'b':list(key[2:]),'triangle_pairs':0,'point':list(point),'source_obstacle':source_name}
  out[key]['triangle_pairs']+=1
 return list(out.values())
for fi,fr in enumerate(frames):
 env,en,_=bvh(dynamic,fr);bodies={id:bvh(ix,fr)for id,ix in groups.items()}
 for id,(body,bn,bb)in bodies.items():
  canopy_indices=[k for k in groups[id] if nodes[k]['name'].endswith('_rain_canopy')]
  own_body_indices=[k for k in groups[id] if not nodes[k]['name'].startswith('runtime_')]
  if canopy_indices and own_body_indices:
   canopy,cn,cb=bvh(canopy_indices,fr); own,ownn,ownb=bvh(own_body_indices,fr)
   if canopy and own and boxoverlap(cb,ownb):
    cp=summarize(canopy.overlap(own),cn,ownn)
    if cp:issues.append({'time':fr['time'],'subject':id,'own_canopy':True,'contacts':cp})
  count+=1;pairs=summarize(body.overlap(base),bn,bnames) if base else[]
  if env:pairs+=summarize(body.overlap(env),bn,en)
  if pairs:issues.append({'time':fr['time'],'subject':id,'contacts':pairs})
 ids=list(bodies)
 for a,id in enumerate(ids):
  body,bn,bb=bodies[id]
  for other in ids[a+1:]:
   if id.startswith('tram.')and other.startswith('tram.'):
    body,bn,bb=bvh([k for k in groups[id]if 'coupler'not in nodes[k]['name']],fr);other_body=bvh([k for k in groups[other]if 'coupler'not in nodes[k]['name']],fr)
   else:other_body=bodies[other]
   b,on,ob=other_body
   if not boxoverlap(bb,ob):continue
   pairs=summarize(body.overlap(b),bn,on)
   if pairs:issues.append({'time':fr['time'],'subject':id,'other':other,'contacts':pairs})
 if fi%20==0:print('FRAME',fi,'/',len(frames),'issues',len(issues),'seconds',round(time.time()-begin,1),flush=True)
result={'passed':not issues,'duration':frames[-1]['time'],'frame_interval':.5,'body_poses':count,'subject_groups':list(groups),'static_meshes':len(static),'animated_environment_meshes':len(dynamic),'issues':issues,'intended_liquid_effect_contacts':len(liquid_contacts),'umbrella_own_body_checked':True,'scope':'Actual decoded browser meshes and recorded world matrices; static scenery plus animated foliage/curtains and pairwise subject bodies. Water intentionally excluded; own articulated assemblies and attached train coupling excluded. Discrete samples only, not a continuous-time guarantee.'};(O/'browser-full-cast-final.json').write_text(json.dumps(result,indent=2));print('DONE',count,'issues',len(issues),'seconds',round(time.time()-begin,1))
