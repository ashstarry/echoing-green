import bpy, math, json, ast, random
from pathlib import Path
from mathutils import Vector
from contextlib import contextmanager
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-02';s=bpy.context.scene;R=random.Random(2503);PI=math.pi;Z=.61;PARENT=None;assets=[]
cols={c.name:c for c in bpy.data.collections};COL=cols['00_Terrain']
aliases={'ivory':'Washi | warm ivory','cream':'Washi | pale edge','walls':'Shoji walls | ivory','navy':'Roof paper | indigo','navy2':'Roof paper | slate','navy3':'Roof paper | faded','wood':'Cedar frame','woodlight':'Cut wood edges','dark':'Ink dark','amber':'Lantern | gentle amber','windowmat':'Shoji | transmitted honey','windowdim':'Shoji | quiet window','glass':'Greenhouse paper panes','red':'Vermilion lacquer paper','gold':'Aged brass','railmat':'Rail | warm iron','pink':'Sakura paper | blush','pinklight':'Sakura paper | pale','pinkdark':'Sakura paper | muted','sage':'Paper foliage | gray sage','blueleaf':'Paper foliage | blue slate','leafcream':'Paper foliage | cream','green':'Greenhouse leaves','water':'Layered paper water','waterline':'Cut ripple | soft blue','skin':'Paper doll | skin','orange':'Fox paper','white':'Warm white paper','ground':'World backdrop | indigo'}
for k,n in aliases.items():globals()[k]=bpy.data.materials[n]
terr=[bpy.data.materials['Paper land layer '+str(i)] for i in range(5)];coatmats=[bpy.data.materials['Resident coat '+str(i)] for i in range(6)]
templates={k:bpy.data.meshes['Shared '+k] for k in ['cube','sphere','ico','cyl']};leafmesh=bpy.data.meshes['Shared folded leaf']
src=ast.parse((ROOT/'work/modeling-cp01/build_town.py').read_text());allowed={'setmat','mesh','unit','primitive','box','cyl','ellipsoid','beam','taper','path','ring','asset','under','ellipse_solid','window','roof','lantern','leaf','flower','plant'}
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allowed],type_ignores=[]),'<geometry helpers>','exec'))
cam=bpy.data.objects['Camera_Main_CP02_45deg'];s.camera=cam;W,H=1672,941
s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100
Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));UP=Q@Vector((0,1,0));FWD=Q@Vector((0,0,-1));BACK=Vector((-RIGHT.y,RIGHT.x,0));ORTHO=cam.data.ortho_scale
def xy(pixel,z=Z):
 orig=cam.location+RIGHT*((pixel[0]/W-.5)*ORTHO)+UP*((.5-pixel[1]/H)*ORTHO/(W/H))
 return orig+FWD*((z-orig.z)/FWD.z)
def pix(p):
 a=world_to_camera_view(s,cam,p);return [a.x*W,(1-a.y)*H]

# Station silhouette: the taller gabled ticket room sits to the left of the platform center.
st=bpy.data.objects['station_main']
for o in list(st.children):
 if o.name.startswith(('CP02 ticket','CP02 station timber','CP02 station central roof')):o.location.x-=1.2
wing=bpy.data.objects.get('CP02 station wing 2.7')
if wing:wing.location.x=2.15;wing.scale.x=1.45
COL=cols['04_Station_Tram']
with under(st):
 beam('CP02 revised inner canopy post',(.55,-1.10,.16),(.55,-1.10,1.95),.06,wood)
 beam('CP02 long canopy support',(-3.75,-1.1,1.87),(3.8,-1.1,1.87),.045,wood)

# Add the two small roof dormers visible in the reference; no main camera change.
COL=cols['02_Teahouse_Market'];tea=bpy.data.objects['tea_house']
with under(tea):
 for xx in [-1.25,.65]:
  d=asset('CP02 tea dormer '+str(xx),(xx,-.77,0));d.parent=tea
  with under(d):
   box('CP02 dormer body',(0,0,4.14),(.52,.52,.48),walls)
   window('CP02 dormer shoji',0,-.28,4.18,.31,.36)
   roof('CP02 dormer',.69,.66,4.40,.25,'y')

# A connected rear terrace supports the bench, windwheel and residents.
COL=cols['00_Terrain']
outline_pixels=[(1015,178),(1124,140),(1228,158),(1316,241),(1268,298),(1165,324),(1046,284)]
outline=[xy(p,1.30) for p in outline_pixels]
for k in range(3):
 ztop=.80+k*.25;depth=.26;center=sum(outline,Vector())/len(outline);scale=1.04-k*.025
 top=[Vector((center.x+(p.x-center.x)*scale,center.y+(p.y-center.y)*scale,ztop)) for p in outline]
 v=[tuple(p-Vector((0,0,depth))) for p in top]+[tuple(p) for p in top];n=len(top)
 f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 mesh('CP02 connected rear paper terrace '+str(k),v,f,terr[3 if k<2 else 4])

# Clear, supported proxy placement on balcony, bench and bridge.
home=bpy.data.objects['west_home']
for o in home.children:
 if o.name.startswith(('CP02 west balcony','CP02 balcony baluster','CP02 balcony handrail')):o.location.z-=.16
bpy.context.view_layer.update()
bpy.data.objects['porch_resident'].location=home.matrix_world@Vector((-.3,-1.5,1.38))
COL=cols['06_Hillside']
reader=bpy.data.objects['quiet_reader']
for name,ob in [('quiet',reader),('elder',bpy.data.objects['elder'])]:
 parent=asset('CP02 '+name+' bench',ob.location,ob.rotation_euler.z)
 with under(parent):
  box('CP02 seat',(0,.03,.45),(.80,.38,.075),woodlight)
  box('CP02 backrest',(0,.20,.73),(.80,.06,.40),woodlight)
  for xx in [-.30,.30]:box('CP02 bench legs',(xx,.03,.23),(.065,.26,.44),wood)
g=bpy.data.objects['greenhouse'];bpy.data.objects['gardener'].location=g.matrix_world@Vector((-1.80,-1.16,0))
left=xy((1152,448),Z+.14);right=xy((1510,560),Z+.14);span=right-left;side=Vector((-span.y,span.x,0)).normalized()
for name,u,offset in [('water_visitor',.88,.17),('water_companion',.72,-.17)]:
 p=left+span*u+side*offset;p.z+=.33*math.sin(PI*u);bpy.data.objects[name].location=p
COL=cols['05_Water_Garden'];umbrella_at=left+span*.78+Vector((0,0,1.95))
verts=[tuple(umbrella_at+Vector((0,0,.15)))]+[tuple(umbrella_at+Vector((.56*math.cos(i*PI/4),.56*math.sin(i*PI/4),-.12))) for i in range(8)]
mesh('CP02 paper umbrella',verts,[(0,i+1,(i+1)%8+1) for i in range(8)],red)
beam('CP02 umbrella handle',umbrella_at+Vector((0,0,-.85)),umbrella_at+Vector((0,0,.13)),.014,wood)

# Rain endpoints must be evaluated after the cloud transform update.
for o in list(s.objects):
 if o.name.startswith('CP02 paper rain'):bpy.data.objects.remove(o,do_unlink=True)
bpy.context.view_layer.update();cloud=bpy.data.objects['CP02_paper_cloud']
for i in range(25):
 p0=cloud.matrix_world@Vector((R.uniform(-1.1,1.1),-.34,0));p1=p0.copy();p1.z=Z+.10
 beam('CP02 visible paper rain',p0,p1,.0045,waterline)

# Small-scale paper plant masses follow the reference edges without filling walking space.
COL=cols['07_Paper_Foliage']
for j,pixelpoint in enumerate([(123,514),(184,527),(265,560),(332,586),(400,607),(898,679),(1006,664),(1091,651),(1136,619),(1510,616),(1542,511),(1487,421),(1170,386),(1118,287),(1017,195),(970,180),(506,276),(468,296),(555,359)]):
 p=xy(pixelpoint,Z)
 for k in range(3):
  off=Vector((R.uniform(-.22,.22),R.uniform(-.22,.22),0));q=p+off;plant('CP02 restrained flower bed',q.x,q.y,Z,R.uniform(.48,.75),pot=False)

# Record final (not pre-adjustment) projection and visibility measurements.
bpy.context.view_layer.update()
align=json.loads((OUT/'landmark-alignment.json').read_text())
for a in align['landmarks']:
 ob=bpy.data.objects.get(a['entity'])
 if ob:
  a['render_pixel']=pix(ob.matrix_world@Vector(a['anchor_local']))
  a['error_pixels']=math.dist(a['reference_pixel'],a['render_pixel'])
  if a['entity'] in ['porch_resident','gardener','water_visitor','water_companion']:a['note']='Proxy adjusted to an actual support surface; not a locked reference pose.'
align['camera_elevation_degrees']=math.degrees(math.asin(abs(FWD.z)))
align['physical_adjustments_after_initial_placement']=True
(OUT/'landmark-alignment.json').write_text(json.dumps(align,ensure_ascii=False,indent=2))
deps=bpy.context.evaluated_depsgraph_get();visibility=[]
for ob in s.objects:
 if not ob.get('entity_id') or not any(c.name=='08_Residents_SCALE_PROXIES' for c in ob.users_collection):continue
 head=next((o for o in ob.children if o.name.startswith('Head')),None)
 if not head:continue
 p=head.matrix_world.translation;start=p-FWD*40
 hit,loc,n,face,hitob,mat=s.ray_cast(deps,start,FWD,distance=50)
 ancestor=hitob
 while ancestor and ancestor.parent:ancestor=ancestor.parent
 visibility.append({'resident':ob.name,'head_first_hit':hitob.name if hitob else None,'unoccluded_head_center_ray':bool(ancestor==ob),'pixel':pix(p)})
roots=[o for o in s.objects if o.get('entity_id')]
manifest={'checkpoint':'CP02','scope':'Reference-aligned spatial modeling revision; stop for user review',
 'camera':{'type':'ORTHO','elevation_degrees':align['camera_elevation_degrees'],'orthographic_scale':cam.data.ortho_scale,'location':list(cam.location),'rotation_euler':list(cam.rotation_euler)},
 'reference':'approved-reference.png','source_checkpoint':'CP01','objects':len(s.objects),
 'resident_proxy_count':sum(any(c.name=='08_Residents_SCALE_PROXIES' for c in o.users_collection) for o in roots),
 'animal_proxy_count':sum(any(c.name=='09_Animals_SCALE_PROXIES' for c in o.users_collection) for o in roots),
 'head_visibility_sampling':visibility,'note':'Single head-center ray is a diagnostic only, not an animation-visibility guarantee. Manual anchors are not a full fidelity metric.',
 'not_implemented':['final character rigs','navigation/collision system','continuous social simulation','web renderer','24/7 backend']}
(OUT/'model-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
s['checkpoint']='CP02 | 45-degree orthographic, reference landmarks, open activity spaces';s['reference_matching_note']='Manual anchors guide layout. Not pixel-identical restoration or finished materials.'
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.samples=96;s.cycles.use_denoising=True
s.render.filepath=str(OUT/'01-overview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp02.blend'))
bpy.ops.render.render(write_still=True);print('CP02_OVERVIEW_READY',flush=True)
# Diagram views are separate; the saved main camera remains locked at 45 degrees.
maincam=s.camera
plan=bpy.data.objects['Camera_Plan_CP01'];plan.name='Camera_Plan_CP02'
land=[o for o in s.objects if o.name.startswith('Island paper layer')]
center=Vector((land[-1].location.x,land[-1].location.y,0))
plan.location=center+Vector((0,0,36));plan.rotation_euler=(center-plan.location).to_track_quat('-Z','Y').to_euler();plan.data.ortho_scale=29.0
s.camera=plan;s.render.resolution_x=1500;s.render.resolution_y=1000;s.cycles.samples=40
for o in s.objects:
 if o.name.startswith(('Paper crescent','Paper star','CP02 layered paper cloud','CP02 visible paper rain')):o.hide_render=True
s.render.filepath=str(OUT/'02-plan.png');bpy.ops.render.render(write_still=True)
print('CP02_PLAN_READY_STOP_FOR_REVIEW',flush=True)
