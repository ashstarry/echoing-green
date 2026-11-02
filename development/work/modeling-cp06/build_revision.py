import bpy,math,json,ast,random,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
from contextlib import contextmanager
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-06';WORK=ROOT/'work/modeling-cp06';s=bpy.context.scene;cam=s.camera
R=random.Random(2606);PI=math.pi;Z=.61;PARENT=None;assets=[];cols={c.name:c for c in bpy.data.collections};COL=cols['02_Teahouse_Market']
src=ast.parse((ROOT/'work/modeling-cp02/refine_and_present.py').read_text());node=next(n for n in src.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='aliases' for t in n.targets));exec(compile(ast.Module(body=[node],type_ignores=[]),'<aliases>','exec'))
for k,n in aliases.items():globals()[k]=bpy.data.materials[n]
terr=[bpy.data.materials['Paper land layer '+str(i)] for i in range(5)];templates={k:bpy.data.meshes['Shared '+k] for k in ['cube','sphere','ico','cyl']};leafmesh=bpy.data.meshes['Shared folded leaf']
src=ast.parse((ROOT/'work/modeling-cp01/build_town.py').read_text());allow={'setmat','mesh','unit','primitive','box','cyl','ellipsoid','beam','taper','path','ring','asset','under','window','lantern','leaf','flower','plant'}
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allow],type_ignores=[]),'<helpers>','exec'))
src=ast.parse((ROOT/'work/modeling-cp05/revise_restaurant_terrace.py').read_text());exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in ['slab','inside']],type_ignores=[]),'<terrain helpers>','exec'))
cam.name='Camera_Main_CP06_43deg';W,H=1672,941;s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100
Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));UP=Q@Vector((0,1,0));FWD=Q@Vector((0,0,-1));BACK=Vector((-RIGHT.y,RIGHT.x,0));Z=.61
def rb(r,b,z=1.85):
 p=RIGHT*r+BACK*b;p.z=z;return p
def erase(o):
 for c in list(o.children):erase(c)
 bpy.data.objects.remove(o,do_unlink=True)
def remove_prefix(prefix):
 for name in [o.name for o in s.objects if o.name.startswith(prefix)]:
  o=bpy.data.objects.get(name)
  if o:erase(o)
baseline={o.name:[list(r) for r in o.matrix_world] for o in s.objects if o.get('entity_id')}
oldrec=json.loads((ROOT/'outputs/modeling-checkpoint-05/revision-record.json').read_text());oldpoly=[Vector(p) for p in oldrec['terrace']['upper_outline_world']]
def area(poly):return abs(sum(poly[i].x*poly[(i+1)%len(poly)].y-poly[(i+1)%len(poly)].x*poly[i].y for i in range(len(poly)))/2)

# Side stall: keep the restaurant's 25-degree view and add a real perpendicular bay.
tea=bpy.data.objects['tea_house'];side=bpy.data.objects['CP04 tea west facade']
for o in side.children:
 if o.name.startswith('CP05 entrance') or o.name.startswith('CP05 restaurant door'):o.location.x+=.25
for o in tea.children:
 if o.name.startswith('CP05 entry '):o.location.y-=.25
 # The old rear corner planter occupied the future stall counter.
 if o.name.startswith('CP05 restaurant outer planter') and o.location.x<0:erase(o)
for name in [o.name for o in tea.children if o.name.startswith('CP05 restaurant boundary foliage') and o.location.x<0]:erase(bpy.data.objects[name])
stall=asset('CP06_restaurant_side_stall',(-2.70,.50,0),-PI/2,'side serving bay, canopy and counter');stall.parent=tea
with under(stall):
 box('CP06 side stall plinth',(0,-.49,.045),(1.72,1.08,.09),ivory)
 box('CP06 side stall counter',(0,-.72,.72),(1.48,.52,.12),woodlight)
 box('CP06 side stall counter front',(0,-.99,.39),(1.47,.07,.58),wood)
 for xx in [-.69,0,.69]:box('CP06 stall counter frame',(xx,-1.03,.40),(.05,.04,.58),woodlight)
 for xx in [-.83,.83]:beam('CP06 side stall post',(xx,-1.02,.08),(xx,-1.02,2.13),.04,wood)
 for i in range(7):
  xx=-.90+i*.30;box('CP06 folded side awning',(xx,-.48,2.07),(.30,1.34,.035),cream if i%2 else navy2,(.16,0,0))
 beam('CP06 side awning front',(-1.05,-1.15,1.96),(1.05,-1.15,1.96),.035,wood)
 for xx in [-.50,0,.50]:
  cyl('CP06 side tray',(xx,-.73,.80),.16,.025,wood)
  for dx in [-.055,.055]:ellipsoid('CP06 side stall tea bun',(xx+dx,-.73,.85),(.06,.06,.045),cream)
 cyl('CP06 side kettle',( .50,-.45,.93),.12,.21,navy2)
 beam('CP06 kettle spout',(.58,-.45,.94),(.72,-.45,1.02),.025,woodlight)
 lantern('CP06 side stall lantern',(-.72,-.18,1.83),.85)
# Move the small flowering tree to the bay's edge, not in front of its serving opening.
tree2=bpy.data.objects['district_tree_2'];tree2.location+=-RIGHT*.48+BACK*.25
buyer=bpy.data.objects['courier'];buyer.location=tea.matrix_world@Vector((-4.30,.10,0));buyer.rotation_euler.z=tea.rotation_euler.z-PI/2

# A real upper dining floor replaces the previously solid upper half of the building.
FLOOR=2.255;body=bpy.data.objects['tea_house paper body'];body.location.z=(.20+2.15)/2;body.scale.z=1.95
room=asset('CP06_upper_dining_layout');room.parent=tea
with under(room):
 box('CP06 upper dining floor',(0,0,FLOOR-.06),(5.30,2.70,.12),woodlight)
 box('CP06 upper back wall',(0,1.35,(FLOOR+3.65)/2),(5.30,.09,3.65-FLOOR),walls)
 box('CP06 upper west wall',(-2.65,0,(FLOOR+3.65)/2),(.09,2.70,3.65-FLOOR),walls)
 # Two jamb wall segments leave a 1.08-world-unit side door at the gable center.
 for yy in [-1.015,1.015]:box('CP06 upper east door jamb wall',(2.65,yy,(FLOOR+3.65)/2),(.09,.67,3.65-FLOOR),walls)
 for xx in [-2.61,-.52,.52,2.61]:box('CP06 upper front timber',(xx,-1.35,3.0),(.08,.10,1.55),wood)
 # Tables are set against the rear; a clear central aisle remains at y = 0.
 for j,xx in enumerate([-1.30,.85]):
  box('CP06 dining table top',(xx,.93,FLOOR+.80),(.67,.50,.065),woodlight)
  for dx in [-.24,.24]:
   for yy in [.77,1.09]:box('CP06 dining table leg',(xx+dx,yy,FLOOR+.39),(.055,.055,.78),wood)
  for side_sign in [-1,1]:
   chair=asset('CP06 dining chair %s %s'%(j,side_sign),(xx+side_sign*.62,.93,FLOOR),-side_sign*PI/2);chair.parent=room
   with under(chair):
    box('CP06 dining seat',(0,0,.53),(.56,.46,.065),woodlight)
    for cx in [-.22,.22]:
     for cy in [-.17,.17]:box('CP06 dining chair leg',(cx,cy,.25),(.045,.045,.50),wood)
    for zz in [.72,.91]:box('CP06 dining back slat',(0,.20,zz),(.56,.055,.10),woodlight)
  for dx in [-.16,.16]:cyl('CP06 dining cup',(xx+dx,.93,FLOOR+.87),.055,.08,cream)

# Remove upper side screens and notch the gable for the actual full-height door.
east=bpy.data.objects['tea_house east windows']
for o in list(east.children):
 if o.location.z>2.1:erase(o)
roof=bpy.data.objects['tea_house roof']
gable=next(o for o in roof.children if o.name.startswith('tea_house gable') and 'trim' not in o.name and o.type=='MESH' and sum(v.co.x for v in o.data.vertices)/len(o.data.vertices)>0)
x=max(v.co.x for v in gable.data.vertices);eave=min(v.co.z for v in gable.data.vertices);peak=max(v.co.z for v in gable.data.vertices);half=max(abs(v.co.y) for v in gable.data.vertices)
me=bpy.data.meshes.new('CP06 notched gable mesh');me.from_pydata([(x,y,z) for y,z in [(-half,eave),(-.68,eave),(-.68,4.05),(.68,4.05),(.68,eave),(half,eave),(0,peak)]],[],[tuple(range(7))]);me.materials.append(walls);me.update();gable.data=me
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
with under(tea):
 for yy in [-.70,.70]:box('CP06 upper exit door frame',(2.90,yy,(FLOOR+4.05)/2),(.08,.055,4.05-FLOOR),wood)
 box('CP06 upper exit header',(2.90,0,4.09),(.10,1.46,.065),wood)
 box('CP06 upper exit landing',(2.94,0,FLOOR-.05),(.62,1.42,.10),woodlight)

# Enlarge the upper overlook toward its front/left; shift the existing two flights
# together so the new floor does not cover their treads. Other buildings are fixed.
COL=cols['06_Hillside'];TOP=1.85;BASE=oldrec['terrace']['base'];MID=oldrec['terrace']['mid'];rise=oldrec['terrace']['equal_riser']
shift=-BACK*.65-RIGHT*.20
for name in ['CP05_lower_stair','CP05_upper_stair','CP05_middle_landing','returning_resident']:bpy.data.objects[name].location+=shift
lower=bpy.data.objects['CP05_lower_stair'];upper=bpy.data.objects['CP05_upper_stair'];middle=bpy.data.objects['CP05_middle_landing'];bpy.context.view_layer.update()
lower_side=lower.rotation_euler.to_quaternion()@Vector((1,0,0));q=bpy.data.objects['quiet_home'].matrix_world@Vector((-1.85,.68,0));p=middle.location+lower_side*.49;d=q-p;link=bpy.data.objects['CP05 landing to residence link'];link.location=(p+q)/2;link.location.z=MID+.004-.035;link.scale=(d.xy.length+.04,.56,.07);link.rotation_euler.z=math.atan2(d.y,d.x)
remove_prefix(('CP05 upper terrace stone layer','CP05 terrace paving','CP05 terrace fence','CP05 dressed paper stone','CP05 terrace planter','CP05 terrace boundary planting'))
outline_rb=[(1.95,6.15),(2.35,6.80),(3.70,7.05),(6.54,6.82),(6.72,5.75),(5.889,5.075),(3.838,5.985),(3.325,4.967),(2.85,5.0)]
outline=[rb(r,b,TOP) for r,b in outline_rb]
for i in range(4):slab('CP06 terrace stone layer '+str(i),outline,BASE+(TOP-BASE)*(i+1)/4,(TOP-BASE)/4+.012,terr[3 if i<3 else 4])
mins=[min(p[i] for p in outline) for i in range(2)];maxs=[max(p[i] for p in outline) for i in range(2)]
for ix in range(math.floor(mins[0]/.35),math.ceil(maxs[0]/.35)):
 for iy in range(math.floor(mins[1]/.34),math.ceil(maxs[1]/.34)):
  p=Vector(((ix+.5)*.35+(iy%2)*.175,(iy+.5)*.34,TOP+.012));corners=[p+Vector((dx,dy,0)) for dx,dy in [(-.16,-.15),(.16,-.15),(.16,.15),(-.16,.15)]]
  if all(inside(q,outline) for q in corners):box('CP06 terrace paving',p,(.322,.308,.018),ivory)
for p,q in zip(outline[:5],outline[1:5]):
 n=max(2,round((q-p).length/.58))
 for i in range(n+1):
  v=p.lerp(q,i/n);beam('CP06 terrace boundary post',v+Vector((0,0,.03)),v+Vector((0,0,.53)),.028,wood)
 for z in [.23,.50]:path('CP06 terrace boundary rail',[tuple(p+Vector((0,0,z))),tuple(q+Vector((0,0,z)))],.028,woodlight)
for p,q in zip(outline[4:],outline[5:]+outline[:1]):
 length=(q-p).xy.length;ang=math.atan2((q-p).y,(q-p).x);n=max(1,round(length/.42))
 for row in range(4):
  for i in range(n):
   v=p.lerp(q,(i+.5)/n);v.z=BASE+.16+row*.28;box('CP06 terrace facing stone',v,(length/n*.94,.035,.25),terr[3 if (i+row)%3 else 2],(0,0,ang))
bench=bpy.data.objects['CP05_overlook_bench'];bench.location=rb(5.35,6.72,TOP+.024);bench.rotation_euler.z=math.radians(12)
reader=bpy.data.objects['quiet_reader'];reader.location=bench.location;reader.rotation_euler.z=bench.rotation_euler.z
box('CP06 bench inset pad',rb(5.35,6.72,TOP+.012),(1.28,.64,.024),ivory,(0,0,math.radians(12)))
tree=bpy.data.objects['district_tree_4'];tree.location=rb(2.40,6.48,TOP+.022);tree.scale=(.46,.46,.60)
wind=bpy.data.objects['hill_windwheel'];wind.location=rb(6.30,5.76,TOP+.022)
for r,b in [(2.50,5.40),(6.35,6.40)]:
 p=rb(r,b,TOP+.02);box('CP06 edge planter',p+Vector((0,0,.15)),(.40,.40,.30),woodlight,(0,0,math.radians(12)));plant('CP06 edge planter foliage',p.x,p.y,TOP+.31,.42,pot=False)
prefix='CP02 street lantern 13 ';dest=rb(2.17,6.15,TOP+.022);delta=dest-(bpy.data.objects[prefix+'foot'].location-Vector((0,0,.06)))
for o in s.objects:
 if o.name.startswith(prefix):o.location+=delta

# Restaurant upper door -> short descending gallery -> expanded overlook.
bpy.context.view_layer.update();floor_z=(tea.matrix_world@Vector((0,0,FLOOR))).z
start=tea.matrix_world@Vector((3.18,0,FLOOR));end=rb(2.85,5.80,TOP+.021);v=Vector((end.x-start.x,end.y-start.y,0));length=v.length;D=v.normalized();N=5;drop=(floor_z-end.z)/N
gallery=asset('CP06_restaurant_terrace_gallery',start,math.atan2(D.y,D.x)-PI/2,'real upper-floor connection with five shallow steps')
with under(gallery):
 for i in range(N):
  yy=(i+.5)*length/N;zz=-(i+1)*drop
  box('CP06 gallery tread %02d'%i,(0,yy,zz-.04),(1.02,length/N+.01,.08),woodlight)
  box('CP06 gallery nosing %02d'%i,(0,i*length/N+.025,zz+.005),(1.04,.045,.01),cream)
 for side_sign in [-1,1]:
  beam('CP06 gallery stringer',(side_sign*.43,0,-.12),(side_sign*.43,length,-N*drop-.12),.055,wood)
  points=[]
  for i in [0,2,4,5]:
   yy=i*length/N;zz=-min(i+1,N)*drop;beam('CP06 gallery guard post',(side_sign*.54,yy,zz),(side_sign*.54,yy,zz+.48),.026,wood);points.append((side_sign*.54,yy,zz+.48))
  path('CP06 gallery handrail',points,.03,woodlight)
 # Visible support posts make the low space below read as structure, not a passage.
 for yy,zz in [(0,0),(length,-N*drop)]:
  for xx in [-.43,.43]:beam('CP06 gallery support',(xx,yy,BASE-floor_z),(xx,yy,zz-.08),.045,wood)

# Store explicit role-based routes. These are design paths, not a live simulation.
bpy.context.view_layer.update()
terrace_route=[rb(r,b,TOP+.022) for r,b in [(2.85,5.80),(3.30,6.35),(4.25,6.50),(5.35,5.90),(5.85,5.90)]]
dining_route=[tea.matrix_world@Vector((x,0,FLOOR)) for x in [-1.8,0,2.40,2.90,3.18]]
gallery_steps=[gallery.matrix_world@Vector((0,(i+.5)*length/N,-(i+1)*drop)) for i in range(N)]
upper_end=upper.matrix_world@Vector((0,1.0,5*rise));upper_end.z=TOP+.022
arrival=[upper_end,rb(3.10,5.75,TOP+.022),rb(3.30,6.35,TOP+.022)]
record={'checkpoint':'CP06','source_checkpoint':'CP05','camera':{'location':list(cam.location),'rotation':list(cam.rotation_euler),'ortho_scale':cam.data.ortho_scale},'baseline_asset_transforms':baseline,'terrace':{'old_area':area(oldpoly),'new_area':area(outline),'outline_world':[list(p) for p in outline],'outline_right_back':outline_rb,'stair_assembly_shift':list(shift),'top_level':TOP,'lower_riser':rise,'floor_area_is_gross_not_net_usable':True},'side_stall':{'root':'CP06_restaurant_side_stall','counter_width_local':1.48,'counter_depth_local':.52,'canopy_width_local':2.10,'entrance_retained':True},'upper_dining':{'floor_local':FLOOR,'floor_world':floor_z,'tables':2,'chairs':4,'door_clear_width_world':1.36*.80,'door_clear_height_world':(4.05-FLOOR)*.86,'roof_kept_in_normal_view':True},'gallery':{'count':N,'riser_drop':drop,'tread_depth':length/N,'width':1.02,'start_world':list(start),'end_world':list(end)},'routes':{'dining_to_door':[list(p) for p in dining_route],'gallery_treads':[list(p) for p in gallery_steps],'terrace_main':[list(p) for p in terrace_route],'stairs_to_terrace':[list(p) for p in arrival]},'role_zones':{'through_routes':['upper dining aisle','side door and gallery','terrace main walk','stair arrival'],'stopping':['bench forecourt','terrace turning area'],'actions':['side stall service','chair pull-out and standing space','upper dining tables']},'notes':'Real modeling and geometric circulation reservations. No behavior engine, pathfinding, rigging or 24/7 service.'}
(OUT/'revision-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
s['checkpoint']='CP06 | side stall, expanded terrace, upper dining and connected circulation';s['review_status']='STOP at next inspectable checkpoint for user review'
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.samples=48;s.cycles.use_denoising=True;s.render.resolution_percentage=75;s.render.filepath=str(WORK/'draft.png');bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'draft.blend'));bpy.ops.render.render(write_still=True);print('CP06_DRAFT_READY',flush=True)
