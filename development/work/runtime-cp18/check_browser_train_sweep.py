import json,time,collections
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path.cwd();D=json.loads((R/'work/runtime-cp18/browser-mesh-motion.json').read_text());T=json.loads((R/'work/runtime-cp18/browser-train-sweep.json').read_text());nodes=D['meshes'];base=D['frames'][0];name_to_index={n['name']:i for i,n in enumerate(nodes)};geom={int(k):([Vector(g['vertices'][i:i+3])for i in range(0,len(g['vertices']),3)],[tuple((g['indices']or list(range(len(g['vertices'])//3)))[i:i+3])for i in range(0,len(g['indices']or list(range(len(g['vertices'])//3))),3)])for k,g in D['geometries'].items()};C=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
def matrix(a):return C@Matrix([a[i:i+4]for i in range(0,16,4)]).transposed()
def build(rows):
 v=[];f=[];names=[]
 for index,mat in rows:
  n=nodes[index];vv,ff=geom[n['gid']];m=matrix(mat);off=len(v);v.extend(m@p for p in vv);f.extend(tuple(off+j for j in t)for t in ff);names.extend([n['name']]*len(ff))
 return BVHTree.FromPolygons(v,f,all_triangles=True),names
world,wn=build([(i,base['matrices'][i])for i,n in enumerate(nodes)if not any(x.startswith('tram.')for x in n['chain'])]);issues=[];begin=time.time();cars=['tram.tram_car_front','tram.tram_car_rear']
for k,fr in enumerate(T['frames']):
 bodies={};uncoupled={}
 for id in cars:
  rows=[(name_to_index[n['name']],mat)for n,mat in zip(T['meshes'],fr['matrices'])if n['owner']==id];body,bn=build(rows);bodies[id]=(body,bn);uncoupled[id]=build([(i,m)for i,m in rows if 'coupler'not in nodes[i]['name']]);p=collections.Counter((bn[a],wn[b])for a,b in body.overlap(world))
  if p:issues.append({'distance':fr['distance'],'car':id,'pairs':[[a,b,c]for(a,b),c in p.items()]})
 a,an=uncoupled[cars[0]];b,bn=uncoupled[cars[1]];hits=collections.Counter((an[i],bn[j])for i,j in a.overlap(b))
 if hits:issues.append({'distance':fr['distance'],'car_pair':True,'pairs':[[a,b,c]for(a,b),c in hits.items()]})
 if k%200==0:print(k,'issues',len(issues),'seconds',round(time.time()-begin,1),flush=True)
result={'passed':not issues,'actual_browser_car_poses':len(T['frames'])*2,'car_pair_samples':len(T['frames']),'sample_distance':67.4709777666/len(T['frames']),'issues':issues,'scope':'Decoded browser geometry with actual procedural wheel steering/spin and coupling placement, sampled through entire rail loop. Scene at opening pose; separate 102-second combined animation test covers moving surroundings. Car-to-car excludes the intentional attached coupler only.'};(R/'outputs/runtime-checkpoint-18/browser-train-full-loop-check.json').write_text(json.dumps(result,indent=2));print('TRAIN_SWEEP_DONE',len(issues))
