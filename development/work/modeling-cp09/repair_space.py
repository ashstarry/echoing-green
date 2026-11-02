exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
from mathutils.bvhtree import BVHTree
rec=json.loads((ROOT/'outputs/modeling-checkpoint-08/revision-record.json').read_text());rec['checkpoint']='CP09';rec['source_checkpoint']='CP08';rec['requested_focus']='Eliminate current visible interpenetrations, restore west-side mass, reference-led clustered planting, real boat hull, rich warm music-box lighting'
def ancestors(o):
 a=[]
 while o:a.append(o);o=o.parent
 return a
def translate_world(o,d):
 factor=o.parent.matrix_world@o.matrix_parent_inverse if o.parent else Matrix.Identity(4);o.location+=factor.to_3x3().inverted()@Vector(d)
def set_world_position(o,p):translate_world(o,Vector(p)-o.matrix_world.translation);bpy.context.view_layer.update()
def transform_mesh(o,frame,fn):
 if o.type!='MESH':return
 o.data=o.data.copy();m=frame.inverted()@o.matrix_world;inv=o.matrix_world.inverted()@frame
 for v in o.data.vertices:v.co=inv@fn(m@v.co)
 o.data.update()
def map_z(o,frame,oldbase,newbase,factor):
 def fn(p):p.z=newbase+(p.z-oldbase)*factor;return p
 transform_mesh(o,frame,fn)

# Restore the western architecture's accepted vertical hierarchy.
old7=json.loads((ROOT/'outputs/modeling-checkpoint-07/revision-record.json').read_text())['baseline_asset_transforms'];restored={}
for name in ['west_home','small_wood_home','post_office']:
 o=bpy.data.objects[name];before=o.scale.z;o.scale.z=Vector((old7[name][0][2],old7[name][1][2],old7[name][2][2])).length;restored[name]=[before,o.scale.z]
bpy.context.view_layer.update()

# Keep the station shallow, but give real clear headroom beneath flatter roofs.
st=bpy.data.objects['station_main'];frame=st.matrix_world.copy()
for o in list(st.children_recursive):
 if o.type!='MESH':continue
 chain=ancestors(o);central=any(x.name=='CP08 station central roof' for x in chain);wing=next((x for x in chain if x.name.startswith('CP08 station wing ') and x.type=='EMPTY'),None)
 if central:map_z(o,frame,1.77,2.03,.24/.43)
 elif wing:
  left=wing.location.x<0;map_z(o,frame,1.68 if left else 1.58,1.98 if left else 1.93,.16/.29)
 elif o.name.startswith('CP08 station open column'):
  x=(frame.inverted()@o.matrix_world.translation).x;old=1.68 if x<0 else 1.58;target=1.98 if x<0 else 1.93;map_z(o,frame,.16,.16,(target-.16)/(old-.16))
 elif o.name.startswith(('CP08 ticket room pier','CP08 ticket rear wall','CP08 ticket timber')):map_z(o,frame,.16,.16,(1.98-.16)/(1.70-.16))
 elif o.name.startswith('CP08 ticket lintel'):map_z(o,frame,1.65,1.98,1)
 # Slight front platform extension; keep the rail-side limit explicit.
 elif o.name=='CP08 station platform':
  def platform(p):
   if p.y<0:p.y*=1.02/.86
   return p
  transform_mesh(o,frame,platform)
for root in [o for o in st.children_recursive if o.get('decision_kind')=='light']:
 p=frame.inverted()@root.matrix_world.translation;p.z=1.78;set_world_position(root,frame@p)
door=bpy.data.objects['station_entry_door'];p=frame.inverted()@door.matrix_world.translation;p.y=-.51;set_world_position(door,frame@p)
for o in door.children_recursive:map_z(o,door.matrix_world.copy(),0,0,1.60/1.28)
door['decision_actuation']='slide_local_X';door['control_axis']='local X';door['travel_open']=.74;door['hinge_axis']='not used; changed to a sliding paper panel'

# Stage the occupants in the actual open bays, outside the ticket walls and door.
station_places={'station_attendant':(-3.34,-.55),'station_traveler':(-.35,-.76),'waiting_passenger':(-2.40,-.37),'waiting_passenger_2':(2.58,-.37)}
for name,(x,y) in station_places.items():
 root=bpy.data.objects[name];root.rotation_euler.z=st.rotation_euler.z;set_world_position(root,frame@Vector((x,y,.18)))
for seat,actor in [('station_seat_A','waiting_passenger'),('station_seat_B','waiting_passenger_2')]:
 o=bpy.data.objects[seat];o.rotation_euler.z=st.rotation_euler.z;set_world_position(o,bpy.data.objects[actor].matrix_world@Vector((0,.07,0)))

# A real open ground-floor shop replaces the old solid body behind the counters.
COL=cols['02_Teahouse_Market'];tea=bpy.data.objects['tea_house'];erase(bpy.data.objects['tea_house paper body'])
foundation=bpy.data.objects['tea_house foundation'];map_z(foundation,tea.matrix_world,0,0,.25)
for name in [o.name for o in tea.children_recursive if o.name.startswith('tea_house porch step')]:erase(bpy.data.objects[name])
for o in list(tea.children_recursive):
 if o.name.startswith('tea_house front window'):
  local=tea.matrix_world.inverted()@o.matrix_world.translation
  if local.z<2.0:translate_world(o,tea.matrix_world.to_3x3()@Vector((0,1.66,0)))
with under(tea):
 box('CP09 shop continuous floor',(0,-.50,.035),(5.3,1.80,.06),woodlight)
 box('CP09 shop back wall',(0,.34,1.10),(5.30,.10,2.10),walls)
 for x in [-2.65,2.65]:box('CP09 shop end wall',(x,-.48,1.10),(.08,1.65,2.10),walls)
 for x in [-.90,.90]:box('CP09 shop bay upright',(x,-1.34,1.07),(.06,.08,2.04),wood)
for name,x in [('vendor_bread',-1.80),('vendor_flower',0),('vendor_lamp',1.80)]:
 actor=bpy.data.objects[name];actor.rotation_euler.z=tea.rotation_euler.z;set_world_position(actor,tea.matrix_world@Vector((x,-1.28,.064)))

# A useful west balcony, with a deep enough floor in front of the gable.
COL=cols['03_Post_Residential'];home=bpy.data.objects['west_home'];floor=bpy.data.objects['CP02 west balcony']
def deck_shape(p):
 p.y=-1.15+(p.y+1.15)*(1.20/.80);return p
transform_mesh(floor,home.matrix_world,deck_shape)
for o in home.children:
 if o.name.startswith(('CP02 balcony baluster','CP02 balcony handrail')):
  p=home.matrix_world.inverted()@o.matrix_world.translation;p.y=-2.35;set_world_position(o,home.matrix_world@p)
with under(home):
 for x in [-1.18,1.18]:
  beam('CP09 balcony side handrail',(x,-2.35,1.99),(x,-1.2,1.99),.035,woodlight)
  beam('CP09 balcony diagonal bracket',(x,-1.30,.65),(x,-2.20,1.27),.045,wood)
# Move the annex a modest distance left to separate its roof from the new usable balcony.
translate_world(bpy.data.objects['small_wood_home'],-RIGHT*.42)
porch=bpy.data.objects['porch_resident'];porch.rotation_euler=(0,0,home.rotation_euler.z);porch.scale=(1.08,1.08,1.08);set_world_position(porch,home.matrix_world@Vector((-.15,-2.02,1.38)))

# Seated people face their activities, rather than putting their legs inside the planter.
listener=bpy.data.objects['listener'];mus=bpy.data.objects['musician'];d=mus.matrix_world.translation-listener.matrix_world.translation;listener.rotation_euler.z=math.atan2(d.y,d.x)+PI/2;seat=bpy.data.objects['listener_seat'];seat.rotation_euler.z=listener.rotation_euler.z;set_world_position(seat,listener.matrix_world@Vector((0,.07,0)))
plaza=bpy.data.objects['plaza_ground'];lp=listener.matrix_world.translation
for name in [o.name for o in plaza.children if o.name.startswith(('CP08 tree bench slat','CP08 tree seat support')) and Vector((o.matrix_world.translation.x-lp.x,o.matrix_world.translation.y-lp.y,0)).length<.63]:erase(bpy.data.objects[name])
for name in ['quiet_reader','elder']:
 o=bpy.data.objects[name];translate_world(o,o.matrix_world.to_quaternion()@Vector((0,-.085,0)))
translate_world(bpy.data.objects['gardener'],-RIGHT*.25);translate_world(bpy.data.objects['strolling_parent'],RIGHT*.28)
if bpy.data.objects.get('garden_planter_13'):translate_world(bpy.data.objects['garden_planter_13'],-RIGHT*.18)
translate_world(bpy.data.objects['garden_child'],-RIGHT*.22-BACK*.12)

# Rider geometry is fitted to real saddle, grips, crank and pedals in bicycle coordinates.
COL=cols['08_Residents_SCALE_PROXIES'];bike=bpy.data.objects['street_bicycle'];rider=bpy.data.objects['cyclist'];set_world_position(rider,bike.matrix_world@Vector((-.12,0,.405)));bpy.context.view_layer.update()
for name in [o.name for o in rider.children if o.type=='MESH' and o.name.startswith(('Seated thigh','Seated shin','Shoe','CP08 cycling upper','CP08 cycling lower','CP08 cycling hand'))]:erase(bpy.data.objects[name])
def rider_local(p):return rider.matrix_world.inverted()@(bike.matrix_world@Vector(p))
with under(rider):
 for side in [-1,1]:
  hip=(-.12,side*.12,.835);knee=(.18,side*.22,.62 if side<0 else .53);foot=(.11 if side<0 else -.07,side*.23,.49 if side<0 else .29)
  beam('CP09 cyclist thigh',rider_local(hip),rider_local(knee),.066,navy);beam('CP09 cyclist shin',rider_local(knee),rider_local((foot[0],foot[1],foot[2]+.05)),.053,navy)
  shoe=box('CP09 cyclist shoe',rider_local(foot),(.12,.22,.075),dark);shoe.rotation_euler.z=0
  shoulder=(-.12,side*.15,1.265);elbow=(.08,side*.22,1.02);hand=(.30,side*.18,.925)
  beam('CP09 cyclist upper sleeve',rider_local(shoulder),rider_local(elbow),.068,coatmats[2]);beam('CP09 cyclist forearm',rider_local(elbow),rider_local(hand),.052,coatmats[2]);ico('CP09 cyclist hand',rider_local(hand),(.046,.044,.05),skin)
COL=cols['04_Station_Tram']
with under(bike):
 beam('CP09 crank axle',(.02,-.22,.34),(.02,.22,.34),.022,dark)
 for side in [-1,1]:
  endpoint=(.11 if side<0 else -.07,side*.23,.4475 if side<0 else .2475);beam('CP09 crank arm',(.02,side*.17,.34),endpoint,.015,gold);box('CP09 cycle pedal',endpoint,(.18,.13,.025),dark)

bpy.context.view_layer.update();rec['structural_repairs']={'western_height_restoration':restored,'station_roof_eaves':[2.03,1.98,1.93],'station_platform_front_local_y':-1.02,'station_occupants':station_places,'station_door':'sliding local X .74, ID retained','ground_floor_shop_opened':True,'annex_left_shift':.42,'balcony_front_local_y':-2.35,'cyclist_saddle_crank_and_limbs_refitted':True};(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'structural-repair.blend'));print('CP09_STRUCTURE_REPAIRED',flush=True)
