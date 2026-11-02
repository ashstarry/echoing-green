import bpy, math, json, ast, random
from pathlib import Path
from mathutils import Vector
from contextlib import contextmanager
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/modeling-checkpoint-03'; WORK=ROOT/'work/modeling-cp03'
s=bpy.context.scene; R=random.Random(2504); PI=math.pi; Z=.61; PARENT=None; assets=[]
cols={c.name:c for c in bpy.data.collections}; COL=cols['00_Terrain']
# Reuse the exact geometric vocabulary of the prior editable checkpoint.
base=ast.parse((ROOT/'work/modeling-cp02/refine_and_present.py').read_text())
aliases_node=next(n for n in base.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='aliases' for t in n.targets))
exec(compile(ast.Module(body=[aliases_node],type_ignores=[]),'<material aliases>','exec'))
for k,n in aliases.items():globals()[k]=bpy.data.materials[n]
terr=[bpy.data.materials['Paper land layer '+str(i)] for i in range(5)]
templates={k:bpy.data.meshes['Shared '+k] for k in ['cube','sphere','ico','cyl']}
leafmesh=bpy.data.meshes['Shared folded leaf']
src=ast.parse((ROOT/'work/modeling-cp01/build_town.py').read_text())
allowed={'setmat','mesh','unit','primitive','box','cyl','ellipsoid','beam','taper','path','ring','asset','under','ellipse_solid','window','roof','lantern','leaf','flower','plant'}
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allowed],type_ignores=[]),'<geometry helpers>','exec'))

cam=bpy.data.objects['Camera_Main_CP02_45deg']; cam.name='Camera_Main_CP03_43deg'
target=Vector((0,0,Z)); yaw=math.radians(12); elev=math.radians(43)
cam.location=target+Vector((30*math.sin(yaw),-30*math.cos(yaw),30*math.tan(elev)))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
s.camera=cam; W,H=1672,941; s.render.resolution_x=W; s.render.resolution_y=H; s.render.resolution_percentage=100
bpy.context.view_layer.update()
Q=cam.rotation_euler.to_quaternion(); RIGHT=Q@Vector((1,0,0)); UP=Q@Vector((0,1,0)); FWD=Q@Vector((0,0,-1)); BACK=Vector((-RIGHT.y,RIGHT.x,0)); ORTHO=cam.data.ortho_scale
def xy(pixel,z=Z):
 p=cam.location+RIGHT*((pixel[0]/W-.5)*ORTHO)+UP*((.5-pixel[1]/H)*ORTHO/(W/H))
 return p+FWD*((z-p.z)/FWD.z)
def pixel(p):
 q=world_to_camera_view(s,cam,p); return [q.x*W,(1-q.y)*H]
def erase(o):
 for c in list(o.children):erase(c)
 bpy.data.objects.remove(o,do_unlink=True)
def remove_prefix(prefix):
 for o in list(s.objects):
  if o.name.startswith(prefix) and o.name in bpy.data.objects:erase(o)
changes=[]
def turn_building(name,deg,anchor,companions=()):
 o=bpy.data.objects[name]; before=o.matrix_world.copy(); pivot=before@Vector(anchor)
 locals_={n:before.inverted()@bpy.data.objects[n].matrix_world for n in companions}
 oldyaw=math.degrees(o.rotation_euler.z); o.rotation_euler.z=math.radians(deg)
 bpy.context.view_layer.update(); o.location+=pivot-o.matrix_world@Vector(anchor)
 bpy.context.view_layer.update()
 for n,m in locals_.items():bpy.data.objects[n].matrix_world=o.matrix_world@m
 changes.append({'entity':name,'yaw_before_deg':oldyaw,'yaw_after_deg':deg,'retained_pivot_world':list(pivot),'pivot_local':list(anchor),'carried_residents':list(companions)})

# Turn individual facades, keeping the doorway/counter in its existing place.
# The reference main roof rises toward screen-right, revealing its left gable.
turn_building('tea_house',28,(0,-2.1,.66),['vendor_bread','vendor_flower','vendor_lamp','customer_one','customer_two','customer_three'])
turn_building('west_home',27,(0,-1.72,0),['porch_resident'])
turn_building('post_office',25,(0,-1.68,0))
turn_building('quiet_home',-13,(0,-1.5,0))
turn_building('greenhouse',-19,(0,-1.25,0),['gardener'])

# Replace the flat rear slab and partly buried steps with a legible stepped hill.
remove_prefix(('CP02 quiet terrace','CP02 connected rear paper terrace','CP02 hill stair'))
COL=cols['06_Hillside']
def polygon_slab(name,points,top,depth,mat):
 n=len(points); v=[(p.x,p.y,top-depth) for p in points]+[(p.x,p.y,top) for p in points]
 f=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,v,f,mat)
TOP=1.65
outline_pixels=[(1003,154),(1119,121),(1244,149),(1241,183),(1198,202),(1130,190),(1035,187)]
outline=[xy(p,TOP) for p in outline_pixels]
for i,(zt,depth) in enumerate([(1.0,.40),(1.34,.34),(TOP,.31)]):
 polygon_slab('CP03 upper terrace layer '+str(i),outline,zt,depth,terr[3 if i<2 else 4])
# Broad but localized pad beneath the upper-right house: no slab through the stair flight.
home=bpy.data.objects['quiet_home']; bpy.context.view_layer.update()
hp=[home.matrix_world@Vector((x,y,0)) for x,y in [(-1.65,-1.55),(1.65,-1.55),(1.65,1.50),(-1.65,1.50)]]
for i in range(3):polygon_slab('CP03 residence terrace layer '+str(i),hp,.82+i*.23,.24,terr[3 if i<2 else 4])

a=xy((1123,296),Z+.018); b=xy((1130,190),TOP); d=Vector((b.x-a.x,b.y-a.y,0)); L=d.length; D=d.normalized(); SIDE=Vector((D.y,-D.x,0))
stair_yaw=math.atan2(D.y,D.x)-PI/2; N=8; width=1.06; rise=(TOP-a.z)/N
stair=asset('CP03_hill_stair',a,stair_yaw,'eight actual stepped treads, clear route; no navigation implementation')
with under(stair):
 for i in range(N):
  z=(i+1)*rise
  box('CP03 stair solid riser %02d'%i,(0,(i+.5)*L/N,z/2),(width,L/N+.008,z),ivory)
  box('CP03 stair paper nosing %02d'%i,(0,i*L/N+.025,z+.006),(width+.025,.05,.012),cream)
 # Rail behind the flight in the image; the near edge remains visibly open.
 for i in [0,2,4,6,8]:
  z=min(i+1,N)*rise; yy=i*L/N
  beam('CP03 stair handrail post',(-width/2-.045,yy,z),(-width/2-.045,yy,z+.45),.026,wood)
 path('CP03 stair continuous handrail',[(-width/2-.045,i*L/N,min(i+1,N)*rise+.45) for i in range(N+1)],.03,woodlight)
 box('CP03 lower stair landing',(0,-.35,.025),(1.38,.70,.05),ivory)
 box('CP03 upper stair landing',(0,L+.18,TOP-a.z-.025),(1.40,.40,.05),ivory)

# Retaining joints establish readable height without filling the walking surface.
for i in range(5):
 u=i/5; p=outline[-1].lerp(outline[-2],u)
 beam('CP03 hill retaining joint',Vector((p.x,p.y,.65)),Vector((p.x,p.y,TOP-.08)),.012,woodlight)
edge=[outline[0],outline[1],outline[2],outline[3]]
for j in range(len(edge)-1):
 p,q=edge[j],edge[j+1]; count=max(2,round((q-p).length/.65))
 for i in range(count+1):
  t=p.lerp(q,i/count);t.z=TOP+.02;beam('CP03 upper edge fence post',t,t+Vector((0,0,.48)),.027,wood)
 path('CP03 upper edge fence rail',[tuple(p+Vector((0,0,.35))),tuple(q+Vector((0,0,.35)))],.029,woodlight)

reader=bpy.data.objects['quiet_reader']; bench=bpy.data.objects['CP02 quiet bench']
reader.location=xy((1106,164),TOP); bench.location=reader.location
reader.rotation_euler.z=math.radians(-8);bench.rotation_euler.z=reader.rotation_euler.z
wind=bpy.data.objects['hill_windwheel'];wind.location=xy((1191,184),TOP)
resident=bpy.data.objects['returning_resident']; step_index=4
resident.location=a+D*((step_index+.5)*L/N); resident.location.z=a.z+(step_index+1)*rise
resident.rotation_euler.z=stair_yaw+PI
# Move the occluding canopy behind the seated reader instead of hiding the resident.
t=bpy.data.objects['district_tree_4'];t.location=xy((1067,144),TOP);t.scale*=.84

s['checkpoint']='CP03 | modest camera adjustment, facade orientations, upper-right staircase'
s['camera_user_revision']='User approved lowering CP02 45-degree elevation slightly; now 43 degrees, same orthographic scale and azimuth.'
s['future_detail_rule']='Keep protected ground areas and camera sightlines; check after every detailing pass. Guides are design reservations, not navigation.'
bpy.context.view_layer.update()
record={'checkpoint':'CP03','source_checkpoint':'CP02','camera':{'type':cam.data.type,'elevation_degrees':43,'previous_elevation_degrees':45,'azimuth_degrees':12,'orthographic_scale':ORTHO},'building_turns':changes,'stair':{'steps':N,'width':width,'horizontal_tread':L/N,'riser_height':rise,'lower_level':a.z,'upper_level':TOP,'lower_world':list(a),'upper_world':list(b)},'note':'Directions are manual reference-based corrections, not calibrated reconstruction. People remain unrigged proxies.'}
(OUT/'revision-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.use_denoising=True;s.cycles.samples=48;s.render.resolution_percentage=75
s.render.filepath=str(WORK/'draft.png')
bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'cp03-draft.blend'))
bpy.ops.render.render(write_still=True)
print('CP03_DRAFT_READY',flush=True)
