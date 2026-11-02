exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
from mathutils.bvhtree import BVHTree
def chain(o):
 a=[]
 while o:a.append(o);o=o.parent
 return a
def move(o,d):
 factor=o.parent.matrix_world@o.matrix_parent_inverse if o.parent else Matrix.Identity(4);o.location+=factor.to_3x3().inverted()@Vector(d)
def points(o):return [o.matrix_world@v.co for v in o.data.vertices]
dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];owners=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render or any(c.hide_render or c.name.startswith('12_') for c in o.users_collection):continue
 name=o.name.lower()
 if any(k in name for k in ['roof','shingle','seat','bench','table','soil']):continue
 if not any(k in name for k in ['floor','paving','platform','deck','tread','landing','step','island paper layer','stone ring','west balcony','balcony corner']):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();off=len(vs);vs.extend(ev.matrix_world@v.co for v in me.vertices)
 for t in me.loop_triangles:fs.append(tuple(off+i for i in t.vertices));owners.append(o.name)
 ev.to_mesh_clear()
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True);feet=[]
for root in [o for o in s.objects if o.get('decision_kind')=='resident' and o.name!='cyclist']:
 shoes=[o for o in root.children_recursive if o.type=='MESH' and o.name.startswith('Shoe')];adjust=[];hits=[]
 for shoe in shoes:
  ps=points(shoe);low=min(p.z for p in ps);corners=[p for p in ps if p.z<low+.002];xypts=corners+[sum(corners,Vector())/len(corners)] if corners else ps
  for p in xypts:
   q,n,idx,d=floor.ray_cast(p+Vector((0,0,.40)),Vector((0,0,-1)),.85)
   if q is not None:adjust.append(q.z-low+.003);hits.append(owners[idx])
 if adjust:dz=max(adjust);move(root,(0,0,dz));feet.append({'actor':root.name,'delta_z':dz,'supports':sorted(set(hits))})
 else:feet.append({'actor':root.name,'missing_support':True})
bpy.context.view_layer.update();seat_map={'elder':'CP02 elder bench','quiet_reader':'CP05_overlook_bench','musician':'musician_stool','listener':'listener_seat','waiting_passenger':'station_seat_A','waiting_passenger_2':'station_seat_B'};seat_records=[]
for actorname,seatname in seat_map.items():
 actor=bpy.data.objects[actorname];seat=bpy.data.objects[seatname];thighs=[o for o in actor.children_recursive if o.type=='MESH' and o.name.startswith('Seated thigh')];target=min(p.z for o in thighs for p in points(o))-.005
 tops=[o for o in seat.children_recursive if o.type=='MESH' and (('seat' in o.name.lower() and not any(k in o.name.lower() for k in ['leg','back','upright'])) or o.name.startswith('CP02 seat'))];tops=[o for o in tops if not any(k in o.name for k in ['cushion','book'])]
 oldtop=max(p.z for o in tops for p in points(o));dz=target-oldtop
 for o in tops:move(o,(0,0,dz))
 for o in seat.children_recursive:
  if o.name.startswith(('CP07 folded bench cushion','CP07 bench closed book','CP07 bench book paper edge')):move(o,(0,0,dz))
 bpy.context.view_layer.update();bottom=min(p.z for o in tops for p in points(o))
 for o in seat.children_recursive:
  if o.type!='MESH' or not any(k in o.name.lower() for k in ['leg','foot']):continue
  ps=points(o);lo=min(p.z for p in ps);hi=max(p.z for p in ps)
  if hi-lo<.04:continue
  o.data=o.data.copy();inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co;p.z=lo+(p.z-lo)*(bottom-lo)/(hi-lo);v.co=inv@p
  o.data.update()
 seat_records.append({'actor':actorname,'seat':seatname,'seat_top_world':target,'top_shift':dz,'thigh_to_seat_gap':.005})
bpy.context.view_layer.update();rec=json.loads((OUT/'revision-record.json').read_text());rec['foot_and_seat_fit']={'feet':feet,'seats':seat_records,'method':'Actual sole vertices raycast against explicit support geometry; actual thigh minimum surface used for seat height. Mounted cyclist uses pedals instead.'};(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'contact-fitted.blend'));print('FOOT_AND_SEAT_FIT',json.dumps(feet),flush=True)
