import bpy,math,json,ast,random,bmesh
from pathlib import Path
from mathutils import Vector
from contextlib import contextmanager
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-06';WORK=ROOT/'work/modeling-cp06';s=bpy.context.scene;cam=s.camera;PI=math.pi;Z=.61;R=random.Random(2607);PARENT=None;assets=[]
COL=bpy.data.collections['06_Hillside'];templates={k:bpy.data.meshes['Shared '+k] for k in ['cube','sphere','ico','cyl']}
src=ast.parse((ROOT/'work/modeling-cp01/build_town.py').read_text());allow={'setmat','mesh','unit','primitive','box','cyl','beam','path','asset','under'};exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allow],type_ignores=[]),'<helpers>','exec'))
src=ast.parse((ROOT/'work/modeling-cp05/revise_restaurant_terrace.py').read_text());exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='slab'],type_ignores=[]),'<slab>','exec'))
wood=bpy.data.materials['Cedar frame'];woodlight=bpy.data.materials['Cut wood edges'];cream=bpy.data.materials['Washi | pale edge'];ivory=bpy.data.materials['Washi | warm ivory']
Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));BACK=Vector((-RIGHT.y,RIGHT.x,0));FWD=Q@Vector((0,0,-1))
def rb(r,b,z=1.85):
 p=RIGHT*r+BACK*b;p.z=z;return p
def erase(o):
 for c in list(o.children):erase(c)
 bpy.data.objects.remove(o,do_unlink=True)
rec=json.loads((OUT/'revision-record.json').read_text());TOP=rec['terrace']['top_level'];tea=bpy.data.objects['tea_house'];FLOOR=rec['upper_dining']['floor_local'];floor_z=rec['upper_dining']['floor_world']

# Edge planting must not sit in the route's head/shoulder space.
blue=bpy.data.objects['district_tree_3'];blue.location=rb(6.25,6.62,TOP+.022);blue.scale=(.42,.42,.48)
pink=bpy.data.objects['district_tree_4'];pink.location=rb(2.45,6.70,TOP+.022);pink.scale=(.30,.30,.50)
tree2=bpy.data.objects['district_tree_2'];tree2.location-=RIGHT*.25;tree2.scale*=.80
prefix='CP02 street lantern 13 ';dest=rb(6.40,6.10,TOP+.022);old=bpy.data.objects[prefix+'foot'].location-Vector((0,0,.06));delta=dest-old
for o in s.objects:
 if o.name.startswith(prefix):o.location+=delta
oldpot=rb(6.35,6.40,TOP+.02);delta=rb(6.20,6.62,TOP+.02)-oldpot
for o in s.objects:
 if o.name.startswith(('CP06 edge planter','CP06 edge planter foliage')) and not o.parent and (o.location.xy-oldpot.xy).length<.35:o.location+=delta
oldpot=rb(2.50,5.40,TOP+.02);delta=rb(2.35,6.40,TOP+.02)-oldpot
for o in s.objects:
 if o.name.startswith(('CP06 edge planter','CP06 edge planter foliage')) and not o.parent and (o.location.xy-oldpot.xy).length<.35:o.location+=delta
for n in ['quiet_reader','CP05_overlook_bench']:
 o=bpy.data.objects[n];o.location=rb(5.78,6.66,TOP+.021);o.rotation_euler.z=math.radians(12)
bpy.data.objects.remove(bpy.data.objects['CP06 bench inset pad'],do_unlink=True)

# The gallery starts beyond a splayed level landing so turning bodies do not
# collide with an upper landing corner while descending.
erase(bpy.data.objects['CP06_restaurant_terrace_gallery']);bpy.data.objects.remove(bpy.data.objects['CP06 upper exit landing'],do_unlink=True)
p0=tea.matrix_world@Vector((3.18,0,FLOOR));end=rb(3.00,5.55,TOP+.021);D=Vector((end.x-p0.x,end.y-p0.y,0)).normalized();start=p0+D*.25;start.z=floor_z;cross=Vector((-D.y,D.x,0));length=(end-start).xy.length
pdoor1=tea.matrix_world@Vector((2.60,-.70,FLOOR));pdoor2=tea.matrix_world@Vector((2.60,.70,FLOOR))
slab('CP06 splayed upper door landing',[pdoor1,start-cross*.57,start+cross*.57,pdoor2],floor_z,.10,woodlight)
N=5;drop=(floor_z-end.z)/N;gallery=asset('CP06_restaurant_terrace_gallery',start,math.atan2(D.y,D.x)-PI/2,'five-step gallery with a full turning landing at the upper door')
with under(gallery):
 for i in range(N):
  yy=(i+.5)*length/N;zz=-(i+1)*drop;box('CP06 gallery tread %02d'%i,(0,yy,zz-.04),(1.02,length/N+.01,.08),woodlight);box('CP06 gallery nosing %02d'%i,(0,i*length/N+.025,zz+.005),(1.04,.045,.01),cream)
 for sign in [-1,1]:
  beam('CP06 gallery stringer',(sign*.43,0,-.12),(sign*.43,length,-N*drop-.12),.055,wood)
  points=[]
  for i in ([1,2] if sign==-1 else [1,2,4,5]):
   yy=i*length/N;zz=-min(i+1,N)*drop;beam('CP06 gallery guard post',(sign*.54,yy,zz),(sign*.54,yy,zz+.48),.026,wood);points.append((sign*.54,yy,zz+.48))
  path('CP06 gallery handrail',points,.03,woodlight)
  for yy,zz in [(0,0),(length,-N*drop)]:beam('CP06 gallery support',(sign*.43,yy,.628-floor_z),(sign*.43,yy,zz-.08),.045,wood)
bpy.context.view_layer.update()
rec['gallery'].update({'start_world':list(start),'end_world':list(end),'tread_depth':length/N,'riser_drop':drop,'splayed_upper_landing':True})
rec['routes']['dining_to_door']=[list(tea.matrix_world@Vector((x,0,FLOOR))) for x in [-1.8,0,2.4,2.9,3.18]]+[list(start)]
rec['routes']['gallery_treads']=[list(gallery.matrix_world@Vector((0,(i+.5)*length/N,-(i+1)*drop))) for i in range(N)]
rec['routes']['terrace_main']=[list(rb(r,b,TOP+.022)) for r,b in [(3.00,5.55),(3.30,6.35),(4.25,6.50),(5.35,5.90),(5.65,5.90)]]
rec['roof_preference']='User selected keeping the complete roof; physical indoor occlusion is acceptable when entry/exit at the door remains legible. No sudden visibility toggles are implemented.'
rec['route_refinement']=['Edge trees and lamp cleared from shoulder/head space','Bench shifted off the corner-cutting line','Level splayed landing before the descending gallery','Gallery entry railing begins beyond the turning point']
(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.samples=48;s.render.resolution_percentage=75;s.render.filepath=str(WORK/'refined.png');bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'refined.blend'));bpy.ops.render.render(write_still=True);print('CP06_REFINED_READY',flush=True)
