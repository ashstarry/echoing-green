import bpy,math,json,ast,random,bmesh
from pathlib import Path
from mathutils import Vector
from contextlib import contextmanager
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-05';WORK=ROOT/'work/modeling-cp05'
s=bpy.context.scene;R=random.Random(2507);PI=math.pi;Z=.61;PARENT=None;assets=[];cols={c.name:c for c in bpy.data.collections};COL=cols['02_Teahouse_Market']
src=ast.parse((ROOT/'work/modeling-cp02/refine_and_present.py').read_text());node=next(n for n in src.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='aliases' for t in n.targets));exec(compile(ast.Module(body=[node],type_ignores=[]),'<aliases>','exec'))
for k,n in aliases.items():globals()[k]=bpy.data.materials[n]
terr=[bpy.data.materials['Paper land layer '+str(i)] for i in range(5)]
templates={k:bpy.data.meshes['Shared '+k] for k in ['cube','sphere','ico','cyl']};leafmesh=bpy.data.meshes['Shared folded leaf']
src=ast.parse((ROOT/'work/modeling-cp01/build_town.py').read_text());allowed={'setmat','mesh','unit','primitive','box','cyl','ellipsoid','beam','taper','path','ring','asset','under','window','lantern','leaf','flower','plant'}
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allowed],type_ignores=[]),'<helpers>','exec'))
cam=s.camera;cam.name='Camera_Main_CP05_43deg';W,H=1672,941;s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100
Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));UP=Q@Vector((0,1,0));FWD=Q@Vector((0,0,-1));BACK=Vector((-RIGHT.y,RIGHT.x,0));ORTHO=cam.data.ortho_scale
def xy(p,z=Z):
 o=cam.location+RIGHT*((p[0]/W-.5)*ORTHO)+UP*((.5-p[1]/H)*ORTHO/(W/H));return o+FWD*((z-o.z)/FWD.z)
def pix(p):
 q=world_to_camera_view(s,cam,p);return [q.x*W,(1-q.y)*H]
def erase(o):
 for c in list(o.children):erase(c)
 bpy.data.objects.remove(o,do_unlink=True)
def remove_prefix(prefixes):
 for name in [o.name for o in s.objects if o.name.startswith(prefixes)]:
  o=bpy.data.objects.get(name)
  if o:erase(o)
baseline={o.name:{'matrix_world':[list(r) for r in o.matrix_world],'scale':list(o.scale)} for o in s.objects if o.get('entity_id')}
camera_record={'location':list(cam.location),'rotation':list(cam.rotation_euler),'ortho_scale':ORTHO}

# A broad front with a readable side: 25 degrees off the horizontal view, not 45.
tea=bpy.data.objects['tea_house'];old=tea.matrix_world.copy();pivot=old@Vector((0,-2.1,0))
names=['vendor_bread','vendor_flower','vendor_lamp','customer_two','customer_three'];local={n:old.inverted()@bpy.data.objects[n].matrix_world for n in names}
tea.rotation_euler.z=math.radians(37);tea.scale=(1.04,.80,.86);bpy.context.view_layer.update();tea.location+=pivot-tea.matrix_world@Vector((0,-2.1,0));bpy.context.view_layer.update()
for n,m in local.items():
 # Follow location/orientation but retain the original person's uniform scale.
 o=bpy.data.objects[n];p=tea.matrix_world@m;oldscale=o.scale.copy();o.matrix_world=p;o.scale=oldscale

# The restaurant gets an actual side entrance and a clear place for later decoration.
side=bpy.data.objects['CP04 tea west facade']
for o in list(side.children):
 if (o.name.startswith('CP04 tea west shoji') and o.location.x>0 and o.location.z<1.70) or (o.name.startswith('CP04 tea west sill') and o.location.z<1):erase(o)
with under(side):
 box('CP05 entrance dark recess',(.63,.008,.94),(.82,.03,1.62),dark)
 window('CP05 restaurant door shoji',.63,-.022,.96,.72,1.45,dim=True)
 box('CP05 entrance threshold',(.63,-.10,.18),(.94,.22,.12),woodlight)
 for i in range(3):
  x=.63+(i-1)*.245;mesh('CP05 entrance noren '+str(i),[(x-.115,-.12,1.73),(x+.115,-.12,1.73),(x+.108,-.15,1.40),(x,-.18,1.42),(x-.108,-.15,1.40)],[(0,1,2,3,4)],navy2)
with under(tea):
 box('CP05 entry upper step',(-2.95,-.63,.095),(.55,.94,.19),ivory)
 box('CP05 entry lower step',(-3.27,-.63,.035),(.38,1.02,.07),ivory)
 # Side pots stay behind the entrance, clear of its approach and the market aisle.
 for xx,yy in [(-3.03,.68),(3.04,-1.04)]:
  box('CP05 restaurant outer planter',(xx,yy,.20),(.42,.82,.40),woodlight)
  for dy in [-.23,.05,.27]:plant('CP05 restaurant boundary foliage',xx,yy+dy,.38,.52,pot=False)
 for xx in [-2.29,2.29]:
  box('CP05 balcony flower box',(xx,-1.54,2.31),(.52,.28,.22),woodlight)
  for dx in [-.15,.08]:plant('CP05 balcony foliage',xx+dx,-1.54,2.41,.32,pot=False)
 # A recessed sign surface; final lettering/identity has not been selected.
 box('CP05 restaurant sign frame',(0,-1.79,2.08),(1.02,.09,.27),wood)
 box('CP05 restaurant sign face',(0,-1.845,2.08),(.91,.018,.19),woodlight)
 for xx in [-.19,0,.19]:cyl('CP05 wind emblem',(xx,-1.86,2.08),.035,.012,navy).rotation_euler.x=PI/2

# Larger ribbed lanterns read as paper craft; their emission is kept restrained.
for o in list(tea.children):
 if o.name.startswith('Tea lantern'):erase(o)
lampmat=amber.copy();lampmat.name='CP05 shaded restaurant lantern paper'
bs=lampmat.node_tree.nodes.get('Principled BSDF')
if bs and 'Emission Strength' in bs.inputs:bs.inputs['Emission Strength'].default_value*=.65
def paper_lantern(name,p,scale=1):
 x,y,z=p;r=.145*scale;hh=.34*scale
 ellipsoid(name+' paper',p,(r,r,hh*.52),lampmat)
 for dz in [-hh*.48,hh*.48]:cyl(name+' cap',(x,y,z+dz),r*.62,.024*scale,wood)
 for i in range(8):
  a=i*PI/4;pts=[]
  for j in range(9):
   t=-PI*.43+j*PI*.86/8;rr=r*math.cos(t)*1.015;pts.append((x+rr*math.cos(a),y+rr*math.sin(a),z+hh*.52*math.sin(t)))
  path(name+' rib',pts,.006*scale,woodlight)
 beam(name+' cord',(x,y,z+hh*.49),(x,y,z+hh*.49+.14*scale),.008*scale,wood)
with under(tea):
 for i in range(11):paper_lantern('CP05 restaurant paper lantern',(-2.35+i*.47,-1.64,3.12),.90)

# Rebuild only the upper-right terrace assembly. The house and all other districts stay put.
remove_prefix(('CP03_hill_stair','CP03 upper terrace layer','CP03 upper edge fence','CP03 hill retaining joint','CP03 residence terrace layer'))
COL=cols['06_Hillside'];TOP=1.85;BASE=Z+.018;N1=N2=5;rise=(TOP-BASE)/(N1+N2);MID=BASE+N1*rise
D1=(RIGHT*.45+BACK*math.sqrt(1-.45**2)).normalized();D2=(-RIGHT*math.sqrt(1-.45**2)+BACK*.45).normalized()
A=xy((1128,300),BASE);run=1.0;landing_center=A+D1*(run+.42);landing_center.z=MID
B=landing_center+D2*.42;B.z=MID;C=B+D2*run;C.z=TOP
def slab(name,points,top,depth,mat):
 n=len(points);vs=[(p.x,p.y,top-depth) for p in points]+[(p.x,p.y,top) for p in points];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 o=mesh(name,vs,fs,mat);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();return o
cross=Vector((D2.y,-D2.x,0));edgepts=sorted([C+cross*.57,C-cross*.57],key=lambda p:pix(p)[0])
outline=[xy(p,TOP) for p in [(1003,154),(1095,119),(1238,137),(1244,177),(1198,202)]]+[edgepts[1],edgepts[0],xy((1035,185),TOP)]
for i in range(4):slab('CP05 upper terrace stone layer '+str(i),outline,BASE+(TOP-BASE)*(i+1)/4,(TOP-BASE)/4+.012,terr[3 if i<3 else 4])
def flight(name,start,direction,count,riser,tread,width,rail_side):
 root=asset(name,start,math.atan2(direction.y,direction.x)-PI/2,'actual stair flight with even rises and clear treads')
 with under(root):
  for i in range(count):
   h=(i+1)*riser;box(name+' tread %02d'%i,(0,(i+.5)*tread,h/2),(width,tread+.006,h),ivory)
   box(name+' nosing %02d'%i,(0,i*tread+.025,h+.006),(width+.018,.045,.012),cream)
  railpts=[]
  for i in [0,2,4,5]:
   yy=i*tread;zz=min(i+1,count)*riser;x=rail_side*(width/2+.045)
   beam(name+' rail post',(x,yy,zz),(x,yy,zz+.43),.025,wood);railpts.append((x,yy,zz+.43))
  path(name+' handrail',railpts,.03,woodlight)
 return root
lower=flight('CP05_lower_stair',A,D1,N1,rise,run/N1,1.04,-1)
upper=flight('CP05_upper_stair',B,D2,N2,rise,run/N2,1.04,1)
landing=asset('CP05_middle_landing',landing_center,math.atan2(D1.y,D1.x)-PI/2,'turning and resting landing; connection to residence walk')
with under(landing):
 box('CP05 middle landing solid',(0,0,(BASE-MID)/2),(1.14,1.14,MID-BASE),terr[3])
 box('CP05 middle landing cap',(0,0,.016),(1.16,1.16,.032),ivory)
 for xx in [-.40,0,.40]:box('CP05 middle landing paving seam',(xx,0,.034),(.012,1.10,.004),woodlight)
 for xx in [-.53,.53]:beam('CP05 landing back rail post',(xx,.53,.03),(xx,.53,.46),.025,wood)
 beam('CP05 landing back handrail',(-.53,.53,.46),(.53,.53,.46),.03,woodlight)
with under(lower):box('CP05 bottom landing',(0,-.25,.025),(1.26,.53,.05),ivory)
with under(upper):box('CP05 top landing',(0,run+.16,N2*rise-.015),(1.23,.42,.065),ivory)

# Residence-side walk connects the intermediate landing to the existing house's front.
house=bpy.data.objects['quiet_home'];bpy.context.view_layer.update()
hp=[house.matrix_world@Vector((x,y,0)) for x,y in [(-2.2,-1.58),(1.65,-1.58),(1.65,1.5),(-2.2,1.5)]]
for i in range(3):slab('CP05 residence footing '+str(i),hp,.82+i*.23,.24,terr[3 if i<2 else 4])
walk1=house.matrix_world@Vector((-1.85,.68,0));walk2=house.matrix_world@Vector((-1.85,-1.5,0))
def walk_deck(name,p,q,width,ztop):
 mid=(p+q)/2;mid.z=ztop-.035;d=q-p
 box(name,mid,(d.xy.length+.04,width,.07),woodlight,(0,0,math.atan2(d.y,d.x)))
walk_deck('CP05 landing to residence link',landing_center+Vector((D1.y,-D1.x,0))*.49,walk1,.56,1.286)
walk_deck('CP05 residence side walk',walk1,walk2,.52,1.286)

# Stone joints and discrete pavers break up the blank slab without covering the arrival.
def inside(p,poly):
 yes=False;j=len(poly)-1
 for i in range(len(poly)):
  a,b=poly[i],poly[j]
  if ((a.y>p.y)!=(b.y>p.y)) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:yes=not yes
  j=i
 return yes
mins=[min(p[i] for p in outline) for i in range(2)];maxs=[max(p[i] for p in outline) for i in range(2)]
for ix in range(math.floor(mins[0]/.35),math.ceil(maxs[0]/.35)):
 for iy in range(math.floor(mins[1]/.34),math.ceil(maxs[1]/.34)):
  p=Vector(((ix+.5)*.35+(iy%2)*.175,(iy+.5)*.34,TOP+.012));corners=[p+Vector((dx,dy,0)) for dx,dy in [(-.16,-.15),(.16,-.15),(.16,.15),(-.16,.15)]]
  if all(inside(q,outline) for q in corners):box('CP05 terrace paving',p,(.322,.308,.018),cream if R.random()<.25 else ivory)
# Border rail follows the back edge, keeping the front/arrival open.
for p,q in zip(outline[:4],outline[1:4]):
 count=max(2,round((q-p).length/.55))
 for i in range(count+1):
  v=p.lerp(q,i/count);v.z=TOP+.03;beam('CP05 terrace fence post',v,v+Vector((0,0,.50)),.032,wood)
 for z in [.22,.48]:path('CP05 terrace fence rail',[tuple(p+Vector((0,0,z))),tuple(q+Vector((0,0,z)))],.028,woodlight)
for p,q in zip(outline[3:]+outline[:1],outline[4:]+outline[:1]+outline[1:2]):
 if (q-p).length<.3:continue
 for i in range(max(1,int((q-p).length/.42))):
  v=p.lerp(q,(i+.5)/max(1,int((q-p).length/.42)))
  beam('CP05 terrace stone joint',Vector((v.x,v.y,BASE+.12)),Vector((v.x,v.y,TOP-.08)),.008,woodlight)

# A slatted bench, small edge planting and two terrace lanterns support a clear overlook.
reader=bpy.data.objects['quiet_reader'];reader.location=xy((1138,146),TOP+.025)
reader.rotation_euler.z=math.radians(-8)
bench=bpy.data.objects['CP02 quiet bench'];erase(bench)
bench=asset('CP05_overlook_bench',reader.location,reader.rotation_euler.z)
with under(bench):
 for yy in [-.12,0,.12]:box('CP05 bench seat slat',(0,yy,.45),(1.07,.105,.065),woodlight)
 for zz in [.60,.74,.88]:box('CP05 bench back slat',(0,.20,zz),(1.07,.06,.10),woodlight)
 for xx in [-.43,.43]:
  for yy in [-.11,.16]:box('CP05 bench leg',(xx,yy,.24),(.055,.055,.43),wood)
  beam('CP05 bench rear upright',(xx,.20,.25),(xx,.20,.95),.028,wood)
tree=bpy.data.objects['district_tree_4'];tree.location=xy((1046,141),TOP);tree.scale*=.80
wind=bpy.data.objects['hill_windwheel'];wind.location=xy((1194,181),TOP)
returner=bpy.data.objects['returning_resident'];returner.location=landing_center+Vector((0,0,.035));returner.rotation_euler.z=math.atan2(D2.y,D2.x)+PI/2
for ppx in [(1009,159),(1080,131),(1217,157)]:
 p=xy(ppx,TOP+.02)
 box('CP05 terrace planter',p+Vector((0,0,.15)),(.42,.46,.30),woodlight)
 for dx,dy in [(-.10,-.10),(.11,.10)]:plant('CP05 terrace boundary planting',p.x+dx,p.y+dy,TOP+.30,.47,pot=False)
for n,ppx in [(13,(1029,172)),(12,(1159,229))]:
 prefix='CP02 street lantern '+str(n)+' ';foot=bpy.data.objects[prefix+'foot'];old=foot.location-Vector((0,0,.06));dest=xy(ppx,TOP+.025 if n==13 else MID+.025)
 for o in s.objects:
  if o.name.startswith(prefix):o.location+=dest-old

s['checkpoint']='CP05 | broad restaurant facade and two-flight terrace stair; stop for review'
record={'checkpoint':'CP05','source_checkpoint':'CP04','camera_unchanged':camera_record,'restaurant':{'world_yaw_degrees':37,'front_normal_to_horizontal_camera_degrees':25,'scale':list(tea.scale),'front_ground_pivot_preserved':list(pivot),'details':['side entrance and noren','ribbed paper lantern row','corner flower boxes','boundary planters','blank framed sign with simple wind marks']},'terrace':{'lower_count':N1,'upper_count':N2,'equal_riser':rise,'tread_depth':run/N1,'flight_clear_width':1.04,'landing_size':1.14,'base':BASE,'mid':MID,'top':TOP,'lower_world':list(A),'middle_world':list(landing_center),'upper_start_world':list(B),'upper_end_world':list(C),'upper_outline_world':[list(p) for p in outline]},'baseline_asset_transforms':baseline,'scope_note':'Only restaurant and upper-right terrace plus associated residents/decor are revised. Other core buildings and main camera remain unchanged. Real Blender geometry; no runtime or rigs.'}
(OUT/'revision-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.samples=48;s.cycles.use_denoising=True;s.render.resolution_percentage=75;s.render.filepath=str(WORK/'draft.png')
bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'draft.blend'));bpy.ops.render.render(write_still=True);print('CP05_DRAFT_READY',flush=True)
