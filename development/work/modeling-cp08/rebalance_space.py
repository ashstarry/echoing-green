import bpy,math,json,ast,random
from pathlib import Path
from mathutils import Vector,Matrix
from contextlib import contextmanager
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-08';WORK=ROOT/'work/modeling-cp08';s=bpy.context.scene;cam=s.camera;PI=math.pi;Z=.61;R=random.Random(80825);PARENT=None;assets=[]
cols={c.name:c for c in bpy.data.collections};COL=cols['01_Plaza'];templates={k:bpy.data.meshes['Shared '+k] for k in ['cube','sphere','ico','cyl']}
src=ast.parse((ROOT/'work/modeling-cp02/refine_and_present.py').read_text());node=next(n for n in src.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='aliases' for t in n.targets));exec(compile(ast.Module(body=[node],type_ignores=[]),'<aliases>','exec'))
for k,n in aliases.items():globals()[k]=bpy.data.materials[n]
src=ast.parse((ROOT/'work/modeling-cp01/build_town.py').read_text());allow={'setmat','mesh','unit','primitive','box','cyl','ellipsoid','ico','beam','taper','path','ring','asset','under','window','lantern','leaf','roof','ellipse_solid','person'};exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allow],type_ignores=[]),'<helpers>','exec'))
leafmesh=bpy.data.meshes['Shared folded leaf'];flower_mesh=bpy.data.meshes['CP07 shared five-petal paper flower | 106 triangles'];coatmats=[bpy.data.materials['Resident coat '+str(i)] for i in range(6)];terr=[bpy.data.materials['Paper land layer '+str(i)] for i in range(5)]
Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));BACK=Vector((-RIGHT.y,RIGHT.x,0));FWD=Q@Vector((0,0,-1));UP=Q@Vector((0,1,0))
def rb(r,b,z=Z):
 p=RIGHT*r+BACK*b;p.z=z;return p
def xy(pixel,z=Z):
 p=cam.location+RIGHT*((pixel[0]/1672-.5)*cam.data.ortho_scale)+UP*((.5-pixel[1]/941)*cam.data.ortho_scale/(1672/941));return p+FWD*((z-p.z)/FWD.z)
def pixel(p):
 v=world_to_camera_view(s,cam,p);return [v.x*1672,(1-v.y)*941]
def erase(o):
 names=[c.name for c in o.children_recursive]+[o.name]
 for n in names:
  x=bpy.data.objects.get(n)
  if x:bpy.data.objects.remove(x,do_unlink=True)
def variant(base,name,c):
 m=base.copy();m.name=name;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.diffuse_color=(*c,1);return m
def bloom(name,p,scale,mat,parent=None):
 o=bpy.data.objects.new(name,flower_mesh);COL.objects.link(o);o.location=p;o.scale=(scale,scale,scale);o.rotation_euler=(.15,R.uniform(-.2,.2),R.random()*2*PI);o.parent=parent or PARENT;o.material_slots[0].link='OBJECT';o.material_slots[0].material=mat;return o
rec=json.loads((ROOT/'outputs/modeling-checkpoint-07/revision-record.json').read_text());rec['checkpoint']='CP08';rec['source_checkpoint']='CP07';rec['intent']='Reference-led spatial rebalancing: sparse outer flowers, visible social plaza, garden and pond composition, decision-addressable movable assets'
rec['cp07_core_transforms']={n:[list(v) for v in bpy.data.objects[n].matrix_world] for n in ['tea_house','post_office','west_home','small_wood_home','paper_observatory','quiet_home','greenhouse','station_main','tram_car_front','tram_car_rear','lantern_tree','plaza_ground','pond_boat','duck_0','duck_1']}
rec['cp07_camera']={'location':list(cam.location),'rotation':list(cam.rotation_euler),'ortho_scale':cam.data.ortho_scale};cam.name='Camera_Main_CP08_43deg'

# Sparse, intentionally uneven outer clusters replace the continuous garland.
outer=[]
def outside(p):
 r=p.dot(RIGHT);b=p.dot(BACK);return (r/12.0)**2+((b+.65)/6.3)**2>1.08
for o in s.objects:
 if o.name.startswith('CP07 garden cluster') and outside(o.matrix_world.translation):outer.append(o)
targets=[(70,470),(105,575),(177,650),(290,717),(408,766),(528,796),(1035,820),(1150,793),(1360,735),(1479,640),(1580,503)]
keep=set()
for target in targets:
 if outer:keep.add(min(outer,key=lambda o:sum((a-b)**2 for a,b in zip(pixel(o.matrix_world.translation),target))).name)
removed=[]
for o in outer:
 if o.name not in keep:removed.append(o.name);erase(o)
 else:o.scale*=R.uniform(.72,.88)
# Remove the small old outside garnish as well, so it cannot retain a second ring.
old_removed=0
for o in list(s.objects):
 if o.parent or o.type!='MESH' or not any(c.name=='07_Paper_Foliage' for c in o.users_collection):continue
 if o.name.startswith(('CP02 edge planting','Perimeter paper planting')) and outside(o.matrix_world.translation):bpy.data.objects.remove(o,do_unlink=True);old_removed+=1
rec['outer_planting']={'clusters_before':len(outer),'clusters_kept':sorted(keep),'clusters_removed':removed,'old_garnish_meshes_removed':old_removed,'design':'Small asymmetrical groups with visible stretches of cut-paper edge and rail bed'}

# Reduce blocking roof volumes while retaining ground-level positions.
home=bpy.data.objects['west_home'];resident=bpy.data.objects['porch_resident'];balcony_local=home.matrix_world.inverted()@resident.location
for name,zfac in [('west_home',.88),('post_office',.88),('quiet_home',.78),('greenhouse',.84)]:bpy.data.objects[name].scale.z*=zfac
bpy.data.objects['greenhouse'].scale.y*=.90;bpy.context.view_layer.update();resident.location=home.matrix_world@balcony_local
for n in ['tram_car_front','tram_car_rear']:bpy.data.objects[n].scale.z=1.0

# Rebuild the foreground station with a shallower footprint and a low stepped roof.
# The old station's roof visually covered the musician, despite his head ray passing.
COL=cols['04_Station_Tram'];erase(bpy.data.objects['station_main']);station=asset('station_main',rb(-3.65,-4.65),math.atan2(RIGHT.y,RIGHT.x))
with under(station):
 box('CP08 station platform',(0,0,.09),(7.8,1.72,.18),ivory)
 for xx in [-.91,.91]:box('CP08 ticket room pier',(xx,.10,.93),(1.10,.94,1.54),walls)
 box('CP08 ticket lintel',(0,.10,1.65),(2.92,.94,.16),walls)
 box('CP08 ticket rear wall',(0,.56,.94),(2.92,.08,1.56),walls)
 for xx in [-1.45,-.36,.36,1.45]:box('CP08 ticket timber',(xx,-.40,.98),(.075,.08,1.60),wood)
 for xx in [-.91,.91]:window('CP08 ticket window',xx,-.405,1.05,.72,.77)
 roof('CP08 station central',3.05,1.9,1.77,.43,'y')
 for xx,eave in [(-2.85,1.68),(2.85,1.58)]:
  wing=asset('CP08 station wing '+str(xx),(xx,0,0));wing.parent=station
  with under(wing):roof('CP08 station wing',2.42,1.70,eave,.29,'x')
  for x in [xx-.92,xx+.92]:
   for y in [-.65,.63]:beam('CP08 station open column',(x,y,.16),(x,y,eave),.048,wood)
 for xx in [-3.8,-2.7,-1.65,-.6,.65,1.75,2.85,3.8]:lantern('CP08 station paper lantern',(xx,-.59,1.39),.86)
 for xx in [-2.9,2.8]:
  box('CP08 waiting seat',(xx,.18,.47),(1.15,.32,.07),woodlight)
  for x in [xx-.44,xx+.44]:box('CP08 waiting seat leg',(x,.18,.29),(.07,.22,.43),wood)
 for j in range(2):box('CP08 station rear step',(0,.98+j*.18,.12-j*.05),(1.04,.30,.08),ivory)
 door=asset('station_entry_door',(-.34,-.44,.17));door.parent=station;door['entity_kind']='door';door['movable']=True;door['hinge_axis']='local Z';door['state']='closed'
 with under(door):
  box('CP08 station door panel',(.34,0,.64),(.66,.045,1.28),woodlight)
  box('CP08 station door paper',(.34,-.028,.80),(.50,.018,.78),windowdim)
  for x in [.15,.34,.53]:box('CP08 station door lattice',(x,-.04,.80),(.02,.025,.78),wood)
  cyl('CP08 station door handle',(.58,-.065,.60),.028,.02,gold).rotation_euler.x=PI/2
station['footprint_width']=7.8;station['footprint_depth']=1.72;station['roof_design']='Low foreground silhouettes; old musician obstruction removed'

# Give the social center smaller stone units and a clear planted tree seat.
COL=cols['01_Plaza'];plaza=bpy.data.objects['plaza_ground'];center=plaza.matrix_world.translation.copy();erase(plaza);plaza=asset('plaza_ground',center)
stoneA=variant(ivory,'CP08 plaza | warm limestone',(.62,.53,.40));stoneB=variant(ivory,'CP08 plaza | light edge',(.70,.61,.46));stoneC=variant(ivory,'CP08 plaza | dusty rose',(.64,.51,.40))
with under(plaza):
 for j in range(13):
  r0=.80+j*.272;r1=r0+.257;n=max(22,round(2*PI*(r0+r1)/2/.29));vs=[];fs=[]
  for i in range(n):
   a=2*PI*(i+.02)/n+j*.034;b=2*PI*(i+.98)/n+j*.034;k=len(vs)
   vs.extend([(r*math.cos(t),r*math.sin(t),z) for z in [.012,.044] for r,t in [(r0,a),(r1,a),(r1,b),(r0,b)]])
   fs.extend([tuple(k+x for x in face) for face in [(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
  o=mesh('CP08 plaza stone ring %02d'%j,vs,fs,R.choice([stoneA,stoneA,stoneB,stoneC]))
 cyl('CP08 central planted soil',(0,0,.18),.88,.25,sage)
 ring('CP08 planter folded rim',(0,0,.26),.92,.055,woodlight,48)
 for i in range(18):
  a=2*PI*i/18
  if i in [10,11,12]:continue
  ob=box('CP08 tree bench slat',(1.19*math.cos(a),1.19*math.sin(a),.43),(.42,.28,.06),woodlight,(0,0,a+PI/2))
  for rr in [1.10,1.28]:box('CP08 tree seat support',(rr*math.cos(a),rr*math.sin(a),.23),(.055,.055,.39),wood)
 for i in range(24):
  a=i*2.4;leaf('CP08 planted tree base',(.70*math.cos(a),.70*math.sin(a),.24),(.28,.38,.3),R.choice([sage,blueleaf,leafcream]),(.2,.2,a))

# The central crown is an airy umbrella at reference scale, not a tall flower ball.
tree=bpy.data.objects['lantern_tree']
for o in tree.children:
 if any(k in o.name for k in ['blossom','petal','canopy underside']):
  o.location.x*=.87;o.location.y*=.87;o.location.z=1.95+(o.location.z-2.2)*.62;o.scale*=.91
 if o.name.startswith('CP07 tree root flare'):erase(o)
# Keep trunk silhouette connected to the lowered crown without changing the root anchor.
for o in tree.children:
 if 'branch' in o.name:o.scale.z*=.84;o.location.z*=.91

# Make the guitar, hands, legs and seat readable as one complete activity silhouette.
COL=cols['08_Residents_SCALE_PROXIES'];mus=bpy.data.objects['musician'];mus.rotation_euler.z=math.radians(-12)
for o in list(s.objects):
 if o.name.startswith('CP07 folded collar'):erase(o)
with under(mus):
 for o in list(mus.children):
  if o.name.startswith(('Upper sleeve','Lower sleeve','Hand')):erase(o)
 for sign,elbow,hand in [(-1,(-.28,-.18,.69),(-.05,-.40,.61)),(1,(.27,-.16,.80),(.51,-.35,.83))]:
  beam('CP08 musician upper sleeve',(sign*.15,0,.86),elbow,.07,coatmats[0]);beam('CP08 musician lower sleeve',elbow,hand,.055,coatmats[0]);ico('CP08 musician hand',hand,(.052,.046,.06),skin)
COL=cols['01_Plaza'];seat=asset('musician_stool',mus.location,mus.rotation_euler.z)
with under(seat):
 box('CP08 musician stool seat',(0,.04,.44),(.47,.35,.07),woodlight)
 for x in [-.16,.16]:
  for y in [-.08,.16]:box('CP08 musician stool leg',(x,y,.23),(.065,.065,.43),wood)
seat['movable']=True;seat['entity_kind']='seat';seat['occupied_by']='musician'

# A deeper cut-paper pedestal keeps the scale of the reference without enlarging all props.
for o in s.objects:
 if o.name.startswith('Island paper layer'):
  o.data=o.data.copy()
  for v in o.data.vertices:v.co.z=Z+(v.co.z-Z)*1.4
bpy.data.objects['Indigo studio floor'].location.z-=.46

# Calibrate warm focal light and quieter blue fill; no frame-rate claim is implied.
for m in [amber,bpy.data.materials.get('CP05 shaded restaurant lantern paper')]:
 if m:
  p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(1,.36,.055,1);p.inputs['Emission Color'].default_value=(1,.32,.04,1);p.inputs['Emission Strength'].default_value=1.30 if m==amber else .72
for name,power in [('Soft overhead blue hour',800),('Quiet front paper fill',330),('Warm lantern tree pool',100),('Tea frontage warm bounce',120),('Station warm bounce',85),('Greenhouse soft interior',65)]:bpy.data.objects[name].data.energy=power
bpy.data.objects['Warm lantern tree pool'].data.color=(1,.43,.13)
bpy.data.objects['Station warm bounce'].location=station.location+Vector((0,-.60,1.4))
COL=cols['10_Lighting']
for i in range(7):
 a=2*PI*i/7;d=bpy.data.lights.new('CP08 tree lantern spill '+str(i),'POINT');d.energy=5.5;d.color=(1,.35,.055);d.shadow_soft_size=.26;o=bpy.data.objects.new(d.name,d);COL.objects.link(o);o.location=tree.matrix_world@Vector((1.0*math.cos(a),.7*math.sin(a),1.72))
for o in s.objects:
 if o.type=='LIGHT' and o.name.startswith('CP07 local lantern pool'):o.data.energy=13
s.world.node_tree.nodes['Background'].inputs[1].default_value=.28
rec['spatial_rebalance']={'station_old_depth':2.85,'station_new_depth':1.72,'station_center_rb':[-3.65,-4.65],'canopy_xy_factor':.87,'canopy_height_compressed':True,'pedestal_depth_factor':1.4,'smaller_roof_volumes':['west_home','post_office','quiet_home','greenhouse'],'camera_changed':False,'musician_action_space_revealed_by_station_rebuild':True}
rec['baseline_asset_transforms']={n:[list(v) for v in bpy.data.objects[n].matrix_world] for n in rec['cp07_core_transforms']}
rec['material_pipeline']='Retained CP07 built-in ImageGen-derived washi/cedar normals; no AI repainting of model renders'
bpy.context.view_layer.update();rec['baseline_asset_transforms']={n:[list(v) for v in bpy.data.objects[n].matrix_world] for n in rec['cp07_core_transforms']}
(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
for me in bpy.data.meshes:
 if not me.users or not me.polygons or me.uv_layers:continue
 uv=me.uv_layers.new(name='UVMap')
 for poly in me.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(poly.normal[i]))]
  for li in poly.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]*2,p[axes[1]]*2)
for o in s.objects:
 if o.type=='CURVE':o.data.bevel_resolution=min(o.data.bevel_resolution,1)
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100;s.cycles.samples=64;s.render.filepath=str(WORK/'space-rebalance.png');bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'space-rebalance.blend'));bpy.ops.render.render(write_still=True);print('CP08_SPATIAL_DRAFT_READY',flush=True)
