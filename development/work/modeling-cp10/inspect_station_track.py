exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
dg=bpy.context.evaluated_depsgraph_get();out={}
for name in ['station_main','CP08 station platform','tram_car_front','tram_car_rear','station_attendant','station_traveler','waiting_passenger','waiting_passenger_2','station_seat_A','station_seat_B','post_office','musician','listener']:
 root=bpy.data.objects[name];vv=[]
 for o in [root]+list(root.children_recursive):
  if o.type not in ['MESH','CURVE']:continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();vv.extend(ev.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
 out[name]={'origin_rb':[root.matrix_world.translation.dot(RIGHT),root.matrix_world.translation.dot(BACK),root.matrix_world.translation.z],'rotation':list(root.rotation_euler),'scale':list(root.scale),'rb_bounds':[[min(p.dot(ax)for p in vv),max(p.dot(ax)for p in vv)]for ax in [RIGHT,BACK,Vector((0,0,1))]],'children':[o.name for o in root.children]}
rails=[]
for o in s.objects:
 if o.name.startswith('CP02 continuous rail'):
  if o.type=='CURVE':pts=[o.matrix_world@Vector(p.co[:3])for sp in o.data.splines for p in sp.points]
  else:pts=[o.matrix_world@v.co for v in o.data.vertices]
  rails.append({'name':o.name,'type':o.type,'points_rb':[[p.dot(RIGHT),p.dot(BACK),p.z]for p in pts],'bevel':o.data.bevel_depth if o.type=='CURVE' else None})
out['rails']=rails;(WORK/'station-track-baseline.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items()if k!='rails'},indent=2));print('RAILS',[(r['name'],len(r['points_rb']),r['bevel'])for r in rails])
