exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
rec=json.loads((OUT/'revision-record.json').read_text());bpy.context.view_layer.update()
def move(o,d):
 f=o.parent.matrix_world@o.matrix_parent_inverse if o.parent else Matrix.Identity(4);o.location+=f.to_3x3().inverted()@Vector(d)
# Hanging lights are in front of the sliding panel's travel plane, above the passengers.
st=bpy.data.objects['station_main']
for o in st.children_recursive:
 if o.get('decision_kind')=='light':
  p=st.matrix_world.inverted()@o.matrix_world.translation;delta=st.matrix_world.to_3x3()@Vector((0,-.82-p.y,0));move(o,delta)
# Pinwheel blades remain in front of the mast through a complete turn.
wind=bpy.data.objects['hill_windwheel'];frame=wind.matrix_world.copy()
for o in wind.children_recursive:
 if o.type=='MESH' and o.name.startswith('Folded wind vane'):
  o.data=o.data.copy();m=frame.inverted()@o.matrix_world;inv=o.matrix_world.inverted()@frame
  for v in o.data.vertices:p=m@v.co;p.y=-.16+(p.y+.12)*.35;v.co=inv@p
  o.data.update()
# Forks and stays straddle the wheels, instead of crossing the rotating spoke plane.
COL=cols['04_Station_Tram'];bike=bpy.data.objects['street_bicycle']
for name in [o.name for o in bike.children if o.name.startswith('CP08 cycle frame')]:erase(bpy.data.objects[name])
with under(bike):
 for a,b in [((-.1,0,.70),(.04,0,.30)),((-.1,0,.70),(.34,0,.67)),((.34,0,.67),(.04,0,.30)),((.34,0,.67),(.30,0,.91))]:beam('CP09 cycle main tube',a,b,.018,navy)
 for side in [-1,1]:
  for a,b in [((-.48,side*.075,.31),(-.16,side*.075,.31)),((-.16,side*.075,.31),(.04,0,.30)),((-.48,side*.075,.31),(-.21,side*.075,.61)),((-.21,side*.075,.61),(-.1,0,.70)),((.48,side*.075,.31),(.34,side*.075,.67)),((.34,side*.075,.67),(.30,0,.91))]:beam('CP09 separated fork and stay',a,b,.014,navy)
 for x in [-.48,.48]:beam('CP09 cycle axle',(x,-.10,.31),(x,.10,.31),.012,gold)
for name in ['bicycle_wheel_rear','bicycle_wheel_front']:
 wheel=bpy.data.objects[name]
 for n in [o.name for o in wheel.children if o.name.startswith('CP08 cycle spoke')]:erase(bpy.data.objects[n])
 with under(wheel):
  for j in range(10):
   a=j*PI/5;beam('CP09 wheel spoke',(.042*math.cos(a),0,.042*math.sin(a)),(.279*math.cos(a),0,.279*math.sin(a)),.004,woodlight)
  n=16;v=[];f=[]
  for y in [-.040,.040]:
   for r in [.018,.040]:v.extend([(r*math.cos(j*2*PI/n),y,r*math.sin(j*2*PI/n)) for j in range(n)])
  for j in range(n):k=(j+1)%n;f.extend([(j,k,n+k,n+j),(2*n+j,3*n+j,3*n+k,2*n+k),(j,2*n+j,2*n+k,k),(n+j,n+k,3*n+k,3*n+j)])
  mesh('CP09 hollow wheel hub',v,f,gold)
# The kite line is part of its controllable assembly; the current endpoint remains at the hand.
kite=bpy.data.objects['plaza_kite'];line=bpy.data.objects['CP02 kite string'];basis=line.matrix_basis.copy();factor=line.parent.matrix_world@line.matrix_parent_inverse if line.parent else Matrix.Identity(4)
node=bpy.data.objects.new('plaza_kite__tether',None);COL.objects.link(node);node.parent=kite;node['decision_part_id']='tether';node['decision_owner']=kite['decision_entity_id'];node['control_kind']='endpoint_deformation';bpy.context.view_layer.update();line.parent=node;line.matrix_parent_inverse=node.matrix_world.inverted()@factor;line.matrix_basis=basis
rec['motion_clearance_details']={'station_lantern_y':-.82,'wind_vane_plane':'Forward of mast, with folded relief retained','bike_frame':'Paired forks/stays beside wheel plane; .018 hub hole around .012 axle','kite_tether':'Separate deformation node; hand endpoint preserved'}
for me in bpy.data.meshes:
 if not me.users or not me.polygons or me.uv_layers:continue
 uv=me.uv_layers.new(name='UVMap')
 for poly in me.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(poly.normal[i]))]
  for li in poly.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]*2,p[axes[1]]*2)
bpy.context.view_layer.update();(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'final-geometry.blend'));print('CP09_MOTION_CLEARANCE_READY',flush=True)
