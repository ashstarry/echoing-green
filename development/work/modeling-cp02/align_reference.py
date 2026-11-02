import bpy, math, json, ast, random
from pathlib import Path
from mathutils import Vector, Matrix
from contextlib import contextmanager
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-02';OUT.mkdir(exist_ok=True)
scene=bpy.context.scene;Z=.61;PI=math.pi;R=random.Random(2502);PARENT=None;assets=[]
cols={c.name:c for c in bpy.data.collections};COL=cols['00_Terrain']
aliases={'ivory':'Washi | warm ivory','cream':'Washi | pale edge','walls':'Shoji walls | ivory','navy':'Roof paper | indigo','navy2':'Roof paper | slate','navy3':'Roof paper | faded','wood':'Cedar frame','woodlight':'Cut wood edges','dark':'Ink dark','amber':'Lantern | gentle amber','windowmat':'Shoji | transmitted honey','windowdim':'Shoji | quiet window','glass':'Greenhouse paper panes','red':'Vermilion lacquer paper','gold':'Aged brass','railmat':'Rail | warm iron','pink':'Sakura paper | blush','pinklight':'Sakura paper | pale','pinkdark':'Sakura paper | muted','sage':'Paper foliage | gray sage','blueleaf':'Paper foliage | blue slate','leafcream':'Paper foliage | cream','green':'Greenhouse leaves','water':'Layered paper water','waterline':'Cut ripple | soft blue','skin':'Paper doll | skin','orange':'Fox paper','white':'Warm white paper','ground':'World backdrop | indigo'}
for key,name in aliases.items():globals()[key]=bpy.data.materials[name]
terr=[bpy.data.materials['Paper land layer '+str(i)] for i in range(5)]
coatmats=[bpy.data.materials['Resident coat '+str(i)] for i in range(6)]
templates={k:bpy.data.meshes['Shared '+k] for k in ['cube','sphere','ico','cyl']}
leafmesh=bpy.data.meshes['Shared folded leaf']
source=ast.parse((ROOT/'work/modeling-cp01/build_town.py').read_text())
allowed={'relink','setmat','mesh','unit','primitive','box','cyl','ellipsoid','ico','beam','taper','path','ring','asset','under','ellipse_solid','window','roof','house','lantern','pointlight','lamppost','leaf','flower','plant','tree','person'}
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in allowed],type_ignores=[]),'<CP01 geometry helpers>','exec'))

def erase(ob):
 for child in list(ob.children):erase(child)
 bpy.data.objects.remove(ob,do_unlink=True)
def erase_prefix(prefixes):
 for o in list(scene.objects):
  if o.name.startswith(tuple(prefixes)) and o.name in bpy.data.objects:erase(o)

# Exact 45-degree elevation, orthographic camera. No automatic angle/zoom fitting.
W,H=1672,941;ORTHO=27.2;YAW=math.radians(12)
cam=bpy.data.objects['Camera_Main_CP01'];cam.name='Camera_Main_CP02_45deg'
target=Vector((0,0,Z));cam.location=target+Vector((math.sin(YAW)*30,-math.cos(YAW)*30,30))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=ORTHO;scene.camera=cam
scene.render.resolution_x=W;scene.render.resolution_y=H;scene.render.resolution_percentage=65
bpy.context.view_layer.update()
Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));UP=Q@Vector((0,1,0));FWD=Q@Vector((0,0,-1));BACK=Vector((-RIGHT.y,RIGHT.x,0))
def xy(pixel,z=Z):
 u,v=pixel[0]/W,1-pixel[1]/H
 orig=cam.location+RIGHT*((u-.5)*ORTHO)+UP*((v-.5)*ORTHO/(W/H))
 return orig+FWD*((z-orig.z)/FWD.z)
def pixel(p):
 q=world_to_camera_view(scene,cam,p);return [q.x*W,(1-q.y)*H]
landmarks=[]
def place(name,pix,anchor=(0,0,0),scale=None,z=Z,yaw=None):
 ob=bpy.data.objects[name]
 if scale:ob.scale=scale
 if yaw is not None:ob.rotation_euler.z=yaw
 local=Vector(anchor);local=Vector([local[i]*ob.scale[i] for i in range(3)]);local=ob.rotation_euler.to_quaternion()@local
 dest=xy(pix,z+local.z);ob.location=dest-local
 bpy.context.view_layer.update()
 actual=pixel(ob.matrix_world@Vector(anchor))
 landmarks.append({'entity':name,'anchor_local':list(anchor),'reference_pixel':list(pix),'render_pixel':actual,'definition':'Manually selected reference landmark; projection alignment only, not whole-image similarity.'})
 return ob
def group(name,objects,pivot):
 root=asset(name,pivot)
 bpy.context.view_layer.update()
 for o in objects:
  old=o.matrix_world.copy();o.parent=root;o.matrix_world=old
 return root

print('CP02: camera and reference placement',flush=True)
# Land is wider in world coordinates. All placement follows image landmarks.
base_center=xy((836,525),Z)
for o in scene.objects:
 if o.name.startswith('Island paper layer'):
  o.scale.x=13.30/11.8;o.scale.y=7.4/8.25;o.rotation_euler.z=math.atan2(RIGHT.y,RIGHT.x);o.location.x=base_center.x;o.location.y=base_center.y
erase_prefix(['Quiet hill terrace','Hill stair'])

# Main buildings: shallower footprints open the streets; no uniform character shrinking.
place('tea_house',(803,302),(0,-2.1,.66),(.96,.72,.94),yaw=0)
place('post_office',(440,500),(0,-1.68,0),(.86,.70,.85),yaw=0)
place('west_home',(343,421),(0,-1.72,0),(.94,.72,1.0),yaw=0)
place('small_wood_home',(268,466),(0,-1.38,0),(.91,.70,.92),yaw=0)
place('paper_observatory',(430,322),(0,-.75,0),(.84,.84,.82),yaw=0)
place('quiet_home',(1238,305),(0,-1.5,0),(.85,.75,.88),z=1.28,yaw=0)
place('greenhouse',(1292,410),(0,-1.25,0),(1.05,.85,.94),yaw=0)
place('hill_windwheel',(1190,191),(0,0,0),(.93,.93,.93),z=1.35,yaw=-YAW)

# Rebuild the low station as an open, broad platform with stepped roof volumes.
erase(bpy.data.objects['station_main']);COL=cols['04_Station_Tram']
st=asset('station_main')
with under(st):
 box('CP02 station platform',(0,-.35,.09),(7.9,2.85,.18),ivory)
 box('CP02 ticket room',(0,.37,1.06),(2.65,1.35,2.12),walls)
 for xx in [-1.32,1.32]:box('CP02 station timber',(xx,-.31,1.1),(.10,.10,2.2),wood)
 window('CP02 ticket left',-.68,-.34,1.25,.86,1.10)
 window('CP02 ticket right',.68,-.34,1.25,.86,1.10)
 roof('CP02 station central',2.95,2.15,2.2,.90,'y')
 for sx in [-2.7,2.7]:
  for xx in [sx-1.05,sx+1.05]:
   for yy in [-1.1,.7]:beam('CP02 station open column',(xx,yy,.16),(xx,yy,1.95),.06,wood)
  # Each low wing remains open on the side facing the viewer.
  wing=asset('CP02 station wing '+str(sx),(sx,.05,0));wing.parent=st
  with under(wing):roof('CP02 wing',2.55,2.10,2.0,.45,'x')
  box('CP02 platform bench',(sx,-.15,.48),(1.45,.38,.08),woodlight)
  for xx in [sx-.55,sx+.55]:box('CP02 bench foot',(xx,-.15,.29),(.07,.27,.45),wood)
 for xx in [-3.5,-2.3,-1.0,0,1.0,2.3,3.5]:lantern('CP02 station lamp',(xx,-.52,1.70),.72)
 for j in range(3):box('CP02 station rear step',(0,1.15+j*.20,.15-j*.045),(3.7,.34,.09),ivory)
place('station_main',(625,702),(0,-1.55,.10),(1,1,1),yaw=0)

# Rail center and front arc are aligned independently from the island silhouette.
erase_prefix(['Continuous rail','Railway sleeper','Paper fence'])
rail_center=xy((836,492),Z);rx,ry=12.0,6.30
def rail_at(t,off=0):
 p=rail_center+RIGHT*(rx*math.cos(t))+BACK*(ry*math.sin(t))
 n=(RIGHT*(math.cos(t)/rx)+BACK*(math.sin(t)/ry)).normalized();p+=n*off;p.z=Z+.13;return p
for off in [-.36,.36]:path('CP02 continuous rail',[tuple(rail_at(i*2*PI/240,off)) for i in range(240)],.032,railmat,True)
for i in range(190):
 t=i*2*PI/190;p=rail_at(t);d=RIGHT*(-rx*math.sin(t))+BACK*(ry*math.cos(t));ang=math.atan2(d.y,d.x)
 box('CP02 sleeper',(p.x,p.y,Z+.07),(.15,1.08,.09),woodlight,(0,0,ang))
for name,t in [('tram_car_front',-1.17),('tram_car_rear',-1.43)]:
 ob=bpy.data.objects[name];p=rail_at(t);ob.location=(p.x,p.y,Z+.29);ob.scale=(1.10,1.05,1.30)
 d=RIGHT*(-rx*math.sin(t))+BACK*(ry*math.cos(t));ob.rotation_euler.z=math.atan2(d.y,d.x)

# Plaza ring and benches use a shared ground anchor and grow without consuming streets.
COL=cols['01_Plaza']
plaza_objects=[o for o in scene.objects if o.name.startswith(('Plaza ring','Tree planter rim','Circular bench segment','Bench leg'))]
plaza=group('plaza_ground',plaza_objects,(-.7,-.25,Z))
place('plaza_ground',(813,491),scale=(1.16,1.16,1.0))
place('lantern_tree',(813,491),(0,0,0),(1.12,1.12,1.0),z=Z+.16)
erase_prefix(['Market approach','Station approach','Post street','Water path'])

# Water is genuinely moved/resized with the bank/bridge geometry, not image scaling.
COL=cols['05_Water_Garden']
erase_prefix(['Pond paper surface','Water ripple','Water lily','Rain ripple','Bridge deck','Bridge post','Bridge handrail','Rain cloud','Rain silver'])
pond_center=xy((1320,548),Z+.025)
pond=ellipse_solid('CP02 pond',3.1,2.2,Z+.025,.07,water,n=80,jitter=.015)
pond.rotation_euler.z=math.atan2(RIGHT.y,RIGHT.x);pond.location.x=pond_center.x;pond.location.y=pond_center.y
left=xy((1152,448),Z+.14);right=xy((1510,560),Z+.14);span=right-left;side=Vector((-span.y,span.x,0)).normalized();L=span.length
for i in range(28):
 u=i/27;p=left+span*u;p.z+=.33*math.sin(PI*u)
 box('CP02 bridge deck',p,(L/27+.018,1.05,.08),woodlight,(0,-.33*PI/L*math.cos(PI*u),math.atan2(span.y,span.x)))
for sign in [-1,1]:
 rail=[]
 for i in range(13):
  u=i/12;p=left+span*u+side*(sign*.54);p.z+=.33*math.sin(PI*u)
  q=p+Vector((0,0,.62));beam('CP02 bridge post',p,q,.033,wood);rail.append(tuple(q))
 path('CP02 bridge handrail',rail,.038,woodlight)
# Landings and short stairs are real independent geometry at the two banks.
for label,p in [('west',left),('east',right)]:box('CP02 bridge landing '+label,(p.x,p.y,Z+.10),(1.2,1.2,.20),ivory,(0,0,math.atan2(span.y,span.x)))
place('pond_boat',(1210,526),scale=(1.1,1.1,1.0),z=Z+.11,yaw=.20)
for name,pix in [('duck_0',(1291,564)),('duck_1',(1341,575))]:place(name,pix,scale=(1.08,1.08,1.08),z=Z+.08)

# Single connected rear terrace supports the higher dwellings.
COL=cols['00_Terrain']
hillcenter=xy((1187,308),Z)
for i in range(3):
 ob=ellipse_solid('CP02 quiet terrace '+str(i),2.8-i*.2,1.7-i*.15,Z+.23+i*.24,.27,terr[3 if i<2 else 4],n=40)
 ob.location.x=hillcenter.x;ob.location.y=hillcenter.y
# An actual stepped connection from the market path to the raised house.
a=xy((1084,297),Z);b=xy((1138,234),1.25)
for i in range(9):
 p=a.lerp(b,(i+.5)/9);box('CP02 hill stair',p,(.9,(b-a).length/9+.05,.13),ivory,(0,0,math.atan2((b-a).y,(b-a).x)-PI/2))

# Continuous paving over the open interior. Discrete paving is one lightweight mesh.
COL=cols['01_Plaza'];vs=[];fs=[]
for j in range(-19,20):
 for i in range(-34,35):
  u=i*.39+(j%2)*.195;v=j*.39
  if (u/11.55)**2+(v/6.0)**2>1:continue
  p=rail_center+RIGHT*u+BACK*v;p.z=Z+.016
  dp=p-pond_center
  if (dp.dot(RIGHT)/3.15)**2+(dp.dot(BACK)/2.25)**2<1:continue
  dp=p-bpy.data.objects['plaza_ground'].location
  if math.hypot(dp.x,dp.y)<3.80:continue
  k=len(vs)
  for x,y in [(-.183,-.183),(.183,-.183),(.183,.183),(-.183,.183)]:vs.append(tuple(p+RIGHT*x+BACK*y))
  fs.append((k,k+1,k+2,k+3))
mesh('CP02 open street paving',vs,fs,ivory)

# Reposition named actors to visible reference zones; same people are not shrunk.
COL=cols['08_Residents_SCALE_PROXIES']
person_targets={'postman':(478,506),'elder':(213,463),'porch_resident':(333,366),'vendor_bread':(866,294),'vendor_lamp':(951,295),'customer_one':(930,303),'customer_two':(1024,300),'courier':(644,337),'musician':(669,510),'listener':(758,525),'child_listener':(717,520),'kite_child':(968,527),'child_parent':(1033,548),'gardener':(1230,407),'water_visitor':(1460,568),'station_attendant':(548,687),'station_traveler':(594,690),'waiting_passenger':(686,698),'quiet_reader':(1113,168),'returning_resident':(1149,218)}
for name,pix in person_targets.items():
 ob=bpy.data.objects[name];fac=.90 if 'child' in name else 1.08
 z=Z
 if name=='porch_resident':z=2.00
 if name in ['quiet_reader','returning_resident']:z=1.30
 if name.startswith('station_') or name=='waiting_passenger':z=Z+.18
 place(name,pix,scale=(fac,fac,fac),z=z)
for name,pix,coat,pose in [('waiting_passenger_2',(754,707),3,'sit'),('vendor_flower',(786,320),2,'stand'),('customer_three',(980,358),3,'stand'),('water_companion',(1422,553),4,'stand')]:
 person(name,0,0,0,coat,Z,pose);place(name,pix,scale=(1.08,1.08,1.08),z=Z+.08 if 'waiting' in name else Z)
# Left-home porch balcony supports the resident instead of a floating figure.
COL=cols['03_Post_Residential'];home=bpy.data.objects['west_home']
with under(home):
 box('CP02 west balcony',(0,-1.55,1.46),(2.45,.75,.12),woodlight)
 for xx in [-1.15,0,1.15]:beam('CP02 balcony baluster',(xx,-1.9,1.5),(xx,-1.9,2.15),.035,wood)
 beam('CP02 balcony handrail',(-1.25,-1.9,2.15),(1.25,-1.9,2.15),.035,woodlight)
# The figure is placed on the real porch top, keeping the nearest chosen reference anchor.
porch=bpy.data.objects['porch_resident'];p=home.matrix_world@Vector((-.3,-1.5,1.55));porch.location=p

# Rebuild planted edges in smaller clusters, leaving the broad main routes clear.
COL=cols['07_Paper_Foliage']
erase_prefix(['Perimeter paper planting','Street planter','Greenhouse plant'])
for i in range(92):
 t=i*2*PI/92
 # Preserve front platform accesses and bridge landing.
 if -2.1<t-2*PI<-1.05:continue
 p=rail_center+RIGHT*(11.20*math.cos(t))+BACK*(5.72*math.sin(t))
 if 4.1<t<5.3:continue
 plant('CP02 edge planting',p.x,p.y,Z,R.uniform(.65,1.05),pot=False)
for i,pix in enumerate([(182,490),(268,495),(358,511),(395,519),(521,473),(569,405),(590,334),(707,312),(864,342),(1060,344),(1145,364),(1190,409),(1350,402),(1395,438),(1507,589),(1152,631),(1051,594),(886,611),(805,699),(365,637)]):
 p=xy(pix);plant('CP02 street planter '+str(i),p.x,p.y,Z,R.uniform(.75,1.00))
tree_targets=[((119,352),1.0),((496,198),.9),((565,320),.9),((1005,184),1.0),((1096,182),1.03),((1472,440),1.0),((132,535),.85)]
for i,(pix,sc) in enumerate(tree_targets):place('district_tree_'+str(i),pix,scale=(sc,sc,sc))
g=bpy.data.objects['greenhouse']
with under(g):
 for x in [-.85,0,.85]:
  for y in [-.6,.0,.6]:plant('CP02 greenhouse plant',x,y,.65,.55,green)
for pix in [(1225,592),(1270,607),(1370,605),(1391,567),(1257,548),(1357,526)]:
 p=xy(pix,Z+.055);cyl('CP02 lily leaf',p,.17,.015,sage);flower('CP02 lily',p+Vector((0,0,.03)),.25,pinklight)
place('garden_fox',(1146,420),scale=(1.05,1.05,1.05))
place('doorstep_cat',(259,465),scale=(1,1,1))
for i,pix in enumerate([(213,138),(287,86),(1423,155)]):place('paper_bird_'+str(i),pix,scale=(.65,.65,.65),z=5.4)

# Lanterns placed around the actual circulation landmarks, not in movement space.
COL=cols['01_Plaza'];erase_prefix(['Street lantern'])
lamp_pixels=[(157,398),(252,462),(380,515),(573,516),(585,335),(1051,427),(1110,403),(1087,352),(1436,553),(1508,600),(1577,555),(1450,339),(1119,235),(1050,179)]
for i,pix in enumerate(lamp_pixels):
 p=xy(pix);lamppost('CP02 street lantern '+str(i),p.x,p.y)

# Paper rain cloud and strings remain real meshes/curves, calibrated to the reference.
COL=cols['05_Water_Garden'];cloudmat=bpy.data.materials['Cloud | softly filled paper']
cloud=asset('CP02_paper_cloud',xy((1540,261),5.5))
cloud.rotation_euler=cam.rotation_euler
with under(cloud):
 for layer in range(3):
  for x,y,r in [(-1.0,0,.42),(-.60,.35,.52),(0,.4,.58),(.6,.3,.52),(1.0,0,.43)]:
   ob=cyl('CP02 layered paper cloud',(x,y+layer*.02,layer*.035),r,.035,cloudmat)
for i in range(28):
 p0=cloud.matrix_world@Vector((R.uniform(-1.15,1.15),-.25,0));p1=p0.copy();p1.z=Z+.10
 beam('CP02 paper rain',p0,p1,.0045,waterline)

# Sky props and kite keep the reference framing, not the old automatic-fit layout.
def stage_in_image(ob,pix,depth=22):
 ob.location=cam.location+FWD*depth+RIGHT*((pix[0]/W-.5)*ORTHO)+UP*((.5-pix[1]/H)*ORTHO/(W/H));ob.rotation_euler=cam.rotation_euler
stage_in_image(bpy.data.objects['Paper crescent'],(1507,98))
for i,pix in enumerate([(102,90),(251,36),(680,45),(1293,91),(1605,170)]):stage_in_image(bpy.data.objects['Paper star '+str(i)],pix)
erase_prefix(['Kite string','Kite ribbon'])
kite=bpy.data.objects['Red paper kite'];kite.location=xy((965,406),3.5)
hand=bpy.data.objects['kite_child'].matrix_world@Vector((.20,-.10,.65));path('CP02 kite string',[tuple(hand),tuple(hand.lerp(kite.location,.50)+Vector((.10,0,0))),tuple(kite.location)],.005,cream)
path('CP02 kite ribbon',[tuple(kite.location+Vector((.1,0,-.25))),tuple(kite.location+Vector((.5,.1,-.5))),tuple(kite.location+Vector((.9,.05,-.55)))],.022,red)

# Light placement follows moved buildings and tree; keep the approved warm hierarchy.
COL=cols['10_Lighting']
for name,anchor in [('Warm lantern tree pool','lantern_tree'),('Tea frontage warm bounce','tea_house'),('Station warm bounce','station_main'),('Post office warm bounce','post_office')]:
 l=bpy.data.objects[name];ob=bpy.data.objects[anchor]
 local={'lantern_tree':(0,0,1.8),'tea_house':(0,-1.85,2.1),'station_main':(0,-.75,1.75),'post_office':(0,-1.35,1.2)}[anchor]
 l.location=ob.matrix_world@Vector(local)
 if l.type=='LIGHT' and l.data.type=='AREA':l.rotation_euler=(ob.location-l.location).to_track_quat('-Z','Y').to_euler()
bpy.data.objects['Soft overhead blue hour'].data.energy=1450
bpy.data.objects['Quiet front paper fill'].data.energy=650
world=scene.world.node_tree.nodes['Background'];world.inputs[0].default_value=(.14,.23,.42,1);world.inputs[1].default_value=.28
p=ground.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.035,.075,.19,1);p.inputs['Emission Color'].default_value=(.035,.075,.19,1);p.inputs['Emission Strength'].default_value=.28
scene.view_settings.exposure=-.1
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 scene.cycles.device='GPU'
except Exception:scene.cycles.device='CPU'
scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.render.filepath=str(OUT/'draft-alignment.png')
scene['checkpoint']='CP02 reference-space revision, fixed orthographic 45-degree elevation'
scene['not_final']='Spatial/architectural checkpoint; proxies remain unrigged, no simulation or web runtime. Landmark projection is not full image reconstruction.'
bpy.context.view_layer.update()
(OUT/'landmark-alignment.json').write_text(json.dumps({'reference_resolution':[W,H],'camera_elevation_degrees':45,'camera_type':'ORTHO','azimuth_from_south_degrees':12,'orthographic_scale':ORTHO,'landmarks':landmarks,'note':'Manual reference anchor annotations. Small projection errors only confirm the chosen anchor placement; they do not measure visual fidelity.'},ensure_ascii=False,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp02.blend'))
print('CP02_SAVED',len(scene.objects),'objects',flush=True)
bpy.ops.render.render(write_still=True)
print('CP02_DRAFT_READY',flush=True)
