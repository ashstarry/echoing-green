import bpy,math,json,ast,random
from pathlib import Path
from mathutils import Vector
from contextlib import contextmanager
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-04';WORK=ROOT/'work/modeling-cp04'
s=bpy.context.scene;R=random.Random(2506);PI=math.pi;PARENT=None;assets=[];cols={c.name:c for c in bpy.data.collections};COL=cols['02_Teahouse_Market']
source=ast.parse((ROOT/'work/modeling-cp02/refine_and_present.py').read_text())
node=next(n for n in source.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='aliases' for t in n.targets))
exec(compile(ast.Module(body=[node],type_ignores=[]),'<aliases>','exec'))
for k,n in aliases.items():globals()[k]=bpy.data.materials[n]
templates={k:bpy.data.meshes['Shared '+k] for k in ['cube','sphere','ico','cyl']}
source=ast.parse((ROOT/'work/modeling-cp01/build_town.py').read_text())
allowed={'setmat','mesh','unit','primitive','box','cyl','ellipsoid','beam','taper','path','ring','asset','under','window','lantern'}
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in allowed],type_ignores=[]),'<helpers>','exec'))
cam=s.camera;cam.name='Camera_Main_CP04_43deg';FWD=cam.rotation_euler.to_quaternion()@Vector((0,0,-1));camera_original={'location':list(cam.location),'rotation':list(cam.rotation_euler),'ortho_scale':cam.data.ortho_scale,'elevation':math.degrees(math.asin(abs(FWD.z)))}
records=[]
def revise(name,anchor,companions=(),depth=None):
 o=bpy.data.objects[name];before=o.matrix_world.copy();pivot=before@Vector(anchor)
 local={n:before.inverted()@bpy.data.objects[n].matrix_world for n in companions};old_yaw=math.degrees(o.rotation_euler.z);old_scale=list(o.scale)
 o.rotation_euler.z=math.radians(57)
 if depth is not None:o.scale.y=depth
 bpy.context.view_layer.update();o.location+=pivot-o.matrix_world@Vector(anchor);bpy.context.view_layer.update()
 for n,m in local.items():bpy.data.objects[n].matrix_world=o.matrix_world@m
 records.append({'entity':name,'yaw_before':old_yaw,'yaw_after':57,'front_normal_to_camera_in_ground_plane_deg':45,'pivot_world':list(pivot),'pivot_local':anchor,'scale_before':old_scale,'scale_after':list(o.scale),'carried_residents':list(companions)})
revise('tea_house',(0,-2.1,.66),['vendor_bread','vendor_flower','vendor_lamp','customer_one','customer_two','customer_three'],depth=.88)
revise('west_home',(0,-1.72,0),['porch_resident'],depth=.80)
revise('paper_observatory',(0,0,0))

# Develop the actually exposed west walls. Existing front/east geometry stays intact.
tea=bpy.data.objects['tea_house'];COL=cols['02_Teahouse_Market']
with under(tea):
 side=asset('CP04 tea west facade',(-2.685,0,0),-PI/2,'modeled side wall windows and framing');side.parent=tea
 with under(side):
  for floor,z in enumerate([1.03,2.78]):
   for xx in [-.63,.63]:window('CP04 tea west shoji',xx,0,z,.83,.94,dim=floor==0)
   box('CP04 tea west sill',(0,-.048,z-.50),(2.65,.11,.085),wood)
  for xx in [-1.32,0,1.32]:box('CP04 tea west wall timber',(xx,-.04,1.91),(.075,.09,3.42),wood)
  box('CP04 tea west lintel',(0,-.055,3.61),(2.72,.11,.12),wood)
 # Return around the left corner; keep the depth inside the side eave zone.
 box('CP04 tea balcony return',(-2.84,-.30,2.19),(.57,2.65,.13),woodlight)
 for yy in [-1.62,-.85,0,.85]:
  beam('CP04 tea return baluster',(-3.10,yy,2.24),(-3.10,yy,2.88),.037,wood)
 for z in [2.43,2.88]:beam('CP04 tea return rail',(-3.10,-1.68,z),(-3.10,.98,z),.041,wood)
 for yy in [-.80,.30]:lantern('CP04 tea side lantern',(-2.98,yy,3.16),.75)
 # Gable structure stays within the existing triangular side roof silhouette.
 beam('CP04 tea west gable king post',(-2.89,0,3.70),(-2.89,0,4.60),.045,wood)
 beam('CP04 tea west gable tie',(-2.89,-1.45,3.73),(-2.89,1.45,3.73),.045,wood)
 for sign in [-1,1]:beam('CP04 tea west gable brace',(-2.89,sign*1.36,3.74),(-2.89,0,4.57),.040,wood)

COL=cols['03_Post_Residential'];home=bpy.data.objects['west_home']
with under(home):
 side=asset('CP04 west home west facade',(-1.435,0,0),-PI/2,'modeled exposed side windows and framing');side.parent=home
 with under(side):
  for xx in [-.58,.58]:window('CP04 west home side shoji',xx,0,1.54,.72,1.05,dim=True)
  for xx in [-1.2,0,1.2]:box('CP04 west home side timber',(xx,-.038,1.42),(.075,.085,2.55),wood)
  for z in [.25,1.0,2.66]:box('CP04 west home side rail',(0,-.05,z),(2.47,.10,.085),wood)
 box('CP04 home balcony corner',(-1.32,-1.52,1.30),(.30,.72,.12),woodlight)

# The round lookout has no orthogonal facades; rotate and add a second window bank
# so its round form also has separated warm openings on the newly exposed side.
look=bpy.data.objects['paper_observatory']
with under(look):
 side=asset('CP04 lookout west windows',(-.97,0,0),-PI/2,'secondary apertures on round tower');side.parent=look
 with under(side):
  for zz in [1.10,2.40]:window('CP04 lookout west shoji',0,0,zz,.42,.60,dim=True)

s['checkpoint']='CP04 | camera unchanged; two-face view of rear and upper-left architecture'
s['two_face_view']='Tea house and west home front normals are 45 degrees from the horizontal view vector; actual side windows and corner timber added.'
bpy.context.view_layer.update()
record={'checkpoint':'CP04','source':'CP03','camera_unchanged':camera_original,'building_revisions':records,'new_visible_side_detail':['tea house west window banks, timber, corner balcony, lanterns, gable bracing','west home side shoji and timber','round lookout secondary window bank'],'note':'Camera elevation and building yaw are separate angles. Reference is an art target, not a calibrated orthographic drawing.'}
(OUT/'revision-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.use_denoising=True;s.cycles.samples=48;s.render.resolution_percentage=75;s.render.filepath=str(WORK/'draft.png')
bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'draft.blend'))
bpy.ops.render.render(write_still=True);print('CP04_TWO_FACES_DRAFT_READY',flush=True)
