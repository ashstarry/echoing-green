exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
exec(compile((WORK/'rail_helpers.py').read_text(),'<rail helpers>','exec'))
import sys,collections,hashlib
baseline='--baseline'in sys.argv;whole='--world'in sys.argv;dg=bpy.context.evaluated_depsgraph_get();station=bpy.data.objects['station_main'];roots=[station]+[bpy.data.objects[n]for n in ['station_attendant','station_traveler','waiting_passenger','waiting_passenger_2','station_seat_A','station_seat_B']]
def field(objects):
 vs=[];fs=[];names=[]
 for o in objects:
  if o.type not in ['MESH','CURVE']or o.hide_render:continue
  v,f=geometry(o,dg);off=len(vs);vs.extend(v);fs.extend(tuple(off+i for i in t)for t in f);names.extend([o.name]*len(f))
 return BVHTree.FromPolygons(vs,fs,all_triangles=True),names
obstacles={o.name:o for root in roots for o in [root]+list(root.children_recursive)}
if whole:
 obstacles={}
 for o in s.objects:
  if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
  if o.name.startswith(('CP02 continuous rail','CP02 sleeper'))or any(a.get('decision_kind')=='tram'for a in ancestry(o)):continue
  if 'visible paper rain'in o.name:continue
  corners=[o.matrix_world@Vector(v)for v in o.bound_box]
  if min(p.dot(RIGHT)for p in corners)>3.8 or max(p.dot(RIGHT)for p in corners)<-12.5 or min(p.dot(BACK)for p in corners)>-2.3:continue
  obstacles[o.name]=o
world,owners=field(obstacles.values());rail,names=field([o for o in s.objects if o.name.startswith(('CP02 continuous rail','CP02 sleeper'))]);platform=bpy.data.objects.get('CP10 curved station platform')or bpy.data.objects['CP08 station platform'];pv,pf=geometry(platform,dg);pb=BVHTree.FromPolygons(pv,pf,all_triangles=True);track_contacts=sorted({names[b]for a,b in pb.overlap(rail)})
rows=[]
for root in [bpy.data.objects['tram_car_front'],bpy.data.objects['tram_car_rear']]:
 vs,fs,sources=car_local(root);bad=[]
 for i,t in enumerate(times):
  m=pose(root,t);bv=BVHTree.FromPolygons([m@p for p in vs],fs,all_triangles=True);pairs=bv.overlap(world)
  if pairs:bad.append({'sample':i,'parameter':t,'objects':sorted({owners[b]for a,b in pairs}),'triangle_pairs':len(pairs)})
 rows.append({'car':root.name,'samples':len(times),'failing_samples':len(bad),'contacts':bad});print('CAR_CHECK',root.name,len(bad),'/',len(times),flush=True)
# Every actual shoe sole corner must be supported by this platform, not the rail bed.
support=[]
for name in ['station_attendant','station_traveler','waiting_passenger','waiting_passenger_2']:
 for o in bpy.data.objects[name].children_recursive:
  if o.type!='MESH'or not o.name.startswith('Shoe'):continue
  vv,_=geometry(o,dg);lo=min(p.z for p in vv)
  for p in [p for p in vv if p.z<lo+.001]:
   hit,n,idx,d=pb.ray_cast(p+Vector((0,0,.02)),Vector((0,0,-1)),.30);gap=p.z-hit.z if hit is not None else None;support.append({'actor':name,'shoe':o.name,'point':list(p),'platform_hit':hit is not None,'gap':gap,'passed':hit is not None and -.001<=gap<=.012})
edge=[]
if not baseline:
 for x,y in json.loads((OUT/'revision-record.json').read_text())['station_rail_repair']['front_edge_local']:
  p=station.matrix_world@Vector((x,y,0));edge.append(p.dot(BACK)-envelope_back_at(p.dot(RIGHT)))
record={'checkpoint':'CP09 baseline'if baseline else'CP10','rail_sleeper_platform_contacts':track_contacts,'car_mesh_checks':rows,'sampled_car_poses':sum(r['samples']for r in rows),'parameter_interval':[T0,T1],'platform_sole_support':support,'minimum_platform_back_axis_margin':min(edge)if edge else None,'passed':not track_contacts and all(r['failing_samples']==0 for r in rows)and all(r['passed']for r in support),'obstacle_scope':'All visible scene geometry near the station bend except rail/sleepers and the train itself'if whole else'Station architecture and its waiting people/seats','scope':'Local station bend only. Both complete car meshes including fixed parts and current coupling piece, sampled against station and waiting people/seats. Conservative XY boxes define the platform exclusion edge. Not a working rail simulator, continuous-time proof, all-town route or passenger movement test.'}
p=(WORK/'cp09-station-rail-baseline.json')if baseline else(OUT/('station-bend-world-check.json'if whole else'station-rail-check.json'));p.write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps({'passed':record['passed'],'track_contacts':track_contacts,'car_failures':[r['failing_samples']for r in rows],'unsupported_soles':[r for r in support if not r['passed']],'platform_margin':record['minimum_platform_back_axis_margin']},indent=2),flush=True)
