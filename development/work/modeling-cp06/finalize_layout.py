import bpy,math,json,ast,random
from pathlib import Path
from mathutils import Vector,Matrix
from contextlib import contextmanager
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-06';s=bpy.context.scene;cam=s.camera;PI=math.pi;PARENT=None;assets=[];R=random.Random(2608);Z=.61
COL=bpy.data.collections['02_Teahouse_Market'];templates={k:bpy.data.meshes['Shared '+k] for k in ['cube','sphere','ico','cyl']}
src=ast.parse((ROOT/'work/modeling-cp01/build_town.py').read_text());allow={'setmat','mesh','unit','primitive','box','cyl','asset','under'};exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allow],type_ignores=[]),'<helpers>','exec'))
wood=bpy.data.materials['Cedar frame'];woodlight=bpy.data.materials['Cut wood edges'];dark=bpy.data.materials['Ink dark']
Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));UP=Q@Vector((0,1,0));BACK=Vector((-RIGHT.y,RIGHT.x,0));FWD=Q@Vector((0,0,-1));W,H=1672,941
def rb(r,b,z=1.872):
 p=RIGHT*r+BACK*b;p.z=z;return p
def xy(pixel,z):
 p=cam.location+RIGHT*((pixel[0]/W-.5)*cam.data.ortho_scale)+UP*((.5-pixel[1]/H)*cam.data.ortho_scale/(W/H));return p+FWD*((z-p.z)/FWD.z)
def erase(o):
 for c in list(o.children):erase(c)
 bpy.data.objects.remove(o,do_unlink=True)
rec=json.loads((OUT/'revision-record.json').read_text());tea=bpy.data.objects['tea_house'];FLOOR=rec['upper_dining']['floor_local'];room=bpy.data.objects['CP06_upper_dining_layout']
# The old dormers were solid cubes protruding below the roof into headroom.
# Trim their hidden undersides to the existing roof plane, preserving the outline.
for o in tea.children_recursive:
 if o.name.startswith('CP02 dormer body'):
  mat=o.active_material;parent_y=o.parent.location.y
  bottom=[(x,y,4.67-abs(parent_y+y)/1.6+.008) for x,y in [(-.26,-.26),(.26,-.26),(.26,.26),(-.26,.26)]]
  top=[(x,y,4.38) for x,y,z in bottom];me=bpy.data.meshes.new('CP06 roof-aligned dormer shell');me.from_pydata(bottom+top,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.materials.append(mat);me.update();o.data=me;o.matrix_basis=Matrix.Identity(4)
bpy.data.objects['district_tree_2'].location+=BACK*.45
# Two clearly spaced dining positions, each with a pull-back/standing space toward
# the aisle; avoid forcing four chairs into an undersized passage.
for n in [o.name for o in room.children if o.name.startswith('CP06 dining chair')]:
 o=bpy.data.objects.get(n)
 if o:erase(o)
with under(room):
 for j,x in enumerate([-1.30,.85]):
  chair=asset('CP06 dining chair '+str(j),(x,.20,FLOOR),PI);chair.parent=room
  with under(chair):
   box('CP06 dining seat',(0,0,.53),(.56,.46,.065),woodlight)
   for xx in [-.22,.22]:
    for yy in [-.17,.17]:box('CP06 dining chair leg',(xx,yy,.25),(.045,.045,.50),wood)
   for zz in [.72,.91]:box('CP06 dining back slat',(0,.20,zz),(.56,.055,.10),woodlight)
bpy.context.view_layer.update()
rec['upper_dining']['chairs']=2;rec['upper_dining']['standing_local_positions']=[[-1.30,-.42,FLOOR],[.85,-.42,FLOOR]]
rec['upper_dining']['dormer_undersides_trimmed_to_roof_plane']=True
start_gallery=Vector(rec['gallery']['start_world'])
rec['routes']['dining_to_door']=[list(tea.matrix_world@Vector(p)) for p in [(-1.30,-.42,FLOOR),(-1.30,-.60,FLOOR),(2.0,-.60,FLOOR),(2.40,0,FLOOR),(2.90,0,FLOOR),(3.18,0,FLOOR)]]+[list(start_gallery)]
rec['routes']['seat_to_aisle_left']=[list(tea.matrix_world@Vector(p)) for p in [(-1.30,-.42,FLOOR),(-1.30,-.60,FLOOR)]]
rec['routes']['seat_to_aisle_right']=[list(tea.matrix_world@Vector(p)) for p in [(.85,-.42,FLOOR),(.85,-.60,FLOOR)]]
rec['routes']['stall_approach']=[list(tea.matrix_world@Vector(p)) for p in [(-3.70,-2.70,0),(-4.35,-1.65,0),(-4.20,.10,0)]]
rec['movement_policy']={'through':'Walk continuously through the aisle, doorway, gallery and stairs; avoid parking in these passages.','door':'Visible entry/exit at the real doorway; full roof retained; physical indoor occlusion is expected.','bench':'Stand into the reserved front space, turn, then merge into the walk; nearby walkers yield during this transition.','stall':'One service position and a separate approach/waiting recess; return toward the street after the interaction.','viewpoint':'Short stay at the windmill-side viewing point; return along the same walk.','implementation_status':'Spatial design and local geometric checks only; no runtime teleport/hide logic, locomotion, avoidance or scheduler has been implemented.'}

# Rebuild inspection-only guides, separating circulation from short interaction zones.
old=bpy.data.collections.get('12_CP05_MOVEMENT_RESERVATIONS')
if old:
 for o in list(old.objects):bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.collections.remove(old)
guide=bpy.data.collections.new('12_CP06_CIRCULATION_AND_ACTION_ZONES');s.collection.children.link(guide);COL=guide
teal=bpy.data.materials['GUIDE ONLY | walking clearance cyan'];amber=bpy.data.materials['GUIDE ONLY | action clearance amber']
def band(name,pts,width):
 vs=[];fs=[]
 for a,b in zip(pts,pts[1:]):
  p,q=Vector(a),Vector(b);d=q-p
  if d.xy.length<.001:continue
  side=Vector((-d.y,d.x,0)).normalized()*width/2;k=len(vs);vs.extend([tuple(p-side+Vector((0,0,.035))),tuple(p+side+Vector((0,0,.035))),tuple(q+side+Vector((0,0,.035))),tuple(q-side+Vector((0,0,.035)))]);fs.append((k,k+1,k+2,k+3))
  # Interpolated ribbons are only an inspection overlay, not actual ramps.
 o=mesh(name,vs,fs,teal);o['guide_only']=True;o['reserved_width']=width;return o
for key,pts in rec['routes'].items():band('CP06 guide '+key,pts,.70 if key=='stall_approach' else .86)
zones=[]
for name,p,radius in [('terrace_turn',rb(3.30,6.20),.55),('bench_rise',rb(5.78,6.18),.35),('viewpoint',rb(5.65,5.90),.30)]:
 o=cyl('CP06 action '+name,p+Vector((0,0,.043)),radius,.012,amber);o['guide_only']=True;zones.append({'name':name,'center':list(p),'radius':radius,'kind':'brief action/transition; not permanent occupancy of the through route'})
for i,p in enumerate(rec['upper_dining']['standing_local_positions']):
 w=tea.matrix_world@Vector(p);cyl('CP06 chair standing zone '+str(i),w+Vector((0,0,.04)),.32,.012,amber);zones.append({'name':'chair_stand_'+str(i),'center':list(w),'radius':.32,'kind':'standing destination; seated-to-standing animation still untested'})
label_points={'A':tea.matrix_world@Vector((-1.30,-.42,FLOOR)),'B':tea.matrix_world@Vector((2.80,0,FLOOR)),'C':Vector(rec['routes']['gallery_treads'][2]),'D':rb(3.30,6.20),'E':rb(5.78,6.18)}
for label,p in label_points.items():
 cu=bpy.data.curves.new('CP06 zone label '+label,'FONT');cu.body=label;cu.align_x='CENTER';cu.size=.27;cu.extrude=.002;cu.materials.append(dark);o=bpy.data.objects.new('CP06 zone label '+label,cu);guide.objects.link(o);o.location=p+Vector((0,0,.07))
guide.hide_render=True;guide.hide_viewport=True
rec['action_zones']=zones;rec['guide_collection']=guide.name;rec['inspection_labels']={'A':'起身并进入走道','B':'门口转向与让行','C':'连廊通过','D':'上楼后转身','E':'长椅起身过渡'}
(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))

cams=bpy.data.collections['11_Cameras']
def camera(name,focus,scale,elevation=None):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);cams.objects.link(o);d.type='ORTHO';d.ortho_scale=scale
 if elevation is None:o.rotation_euler=cam.rotation_euler;o.location=focus-FWD*30
 else:
  off=Vector((math.sin(math.radians(12))*30,-math.cos(math.radians(12))*30,30*math.tan(math.radians(elevation))));o.location=focus+off;o.rotation_euler=(focus-o.location).to_track_quat('-Z','Y').to_euler()
 return o
camera('Camera_CP06_SideStall',tea.matrix_world@Vector((-2.2,-.3,1.8)),7.8)
camera('Camera_CP06_Terrace',rb(4.40,5.80,1.6),8.8)
camera('Camera_CP06_CirculationCutaway',Vector((.4,5.1,1.7)),13.8,68)
plan=bpy.data.objects['Camera_Plan_CP05'];plan.name='Camera_Plan_CP06'
s.camera=cam;s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100;s.cycles.samples=96;s.render.filepath=str(OUT/'01-overview.png')
s['checkpoint']='CP06 | side stall, usable overlook, connected dining/door/gallery route';s['roof_policy']='Keep full roof in normal view; real doorway transition; inspection cutaway is not normal runtime rendering.';s['review_status']='STOP for user review before further modeling/runtime'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp06.blend'));print('CP06_LAYOUT_SAVED',flush=True)
