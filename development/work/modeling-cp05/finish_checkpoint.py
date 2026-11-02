import bpy,math,json,ast,random,bmesh
from mathutils import Vector
from pathlib import Path
from contextlib import contextmanager
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-05';s=bpy.context.scene;cam=s.camera;R=random.Random(2508);PI=math.pi;PARENT=None;assets=[]
cols={c.name:c for c in bpy.data.collections};COL=cols['06_Hillside'];templates={k:bpy.data.meshes['Shared '+k] for k in ['cube','sphere','ico','cyl']}
src=ast.parse((ROOT/'work/modeling-cp01/build_town.py').read_text());allowed={'setmat','mesh','unit','primitive','box','cyl','beam','path'}
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allowed],type_ignores=[]),'<helpers>','exec'))
src=ast.parse((ROOT/'work/modeling-cp05/revise_restaurant_terrace.py').read_text());exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='slab'],type_ignores=[]),'<slab>','exec'))
wood=bpy.data.materials['Cedar frame'];woodlight=bpy.data.materials['Cut wood edges'];ivory=bpy.data.materials['Washi | warm ivory'];terr=[bpy.data.materials['Paper land layer '+str(i)] for i in range(5)]
W,H=1672,941;s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100;Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));UP=Q@Vector((0,1,0));FWD=Q@Vector((0,0,-1));ORTHO=cam.data.ortho_scale
def xy(p,z=.61):
 v=cam.location+RIGHT*((p[0]/W-.5)*ORTHO)+UP*((.5-p[1]/H)*ORTHO/(W/H));return v+FWD*((z-v.z)/FWD.z)
def pix(p):
 a=world_to_camera_view(s,cam,p);return [a.x*W,(1-a.y)*H]
rec=json.loads((OUT/'revision-record.json').read_text());t=rec['terrace'];BASE,MID,TOP=t['base'],t['mid'],t['top'];rise=t['equal_riser'];run=t['tread_depth']*5
upper=bpy.data.objects['CP05_upper_stair'];lower=bpy.data.objects['CP05_lower_stair'];landing=bpy.data.objects['CP05_middle_landing']
# Move the complete stair/turning assembly slightly away from the residence walk.
# Both flights retain their mutual alignment; reshape the terrace's stair opening.
lower_side=lower.rotation_euler.to_quaternion()@Vector((1,0,0));stair_shift=-lower_side*.38
for root in [lower,upper,landing,bpy.data.objects['returning_resident']]:root.location+=stair_shift
for key in ['lower_world','middle_world','upper_start_world','upper_end_world']:t[key]=list(Vector(t[key])+stair_shift)
outline=[Vector(p) for p in t['upper_outline_world']]
for i in [5,6]:outline[i]+=stair_shift
t['upper_outline_world']=[list(p) for p in outline];t['assembly_clearance_shift_world']=list(stair_shift)
for o in list(s.objects):
 if o.name.startswith(('CP05 upper terrace stone layer','CP05 terrace paving')):bpy.data.objects.remove(o,do_unlink=True)
for i in range(4):slab('CP05 upper terrace stone layer '+str(i),outline,BASE+(TOP-BASE)*(i+1)/4,(TOP-BASE)/4+.012,terr[3 if i<3 else 4])
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
  if all(inside(v,outline) for v in corners):box('CP05 terrace paving',p,(.322,.308,.018),ivory)
bpy.context.view_layer.update()
house=bpy.data.objects['quiet_home'];p=landing.location+lower_side*.49;q=house.matrix_world@Vector((-1.85,.68,0));d=q-p
link=bpy.data.objects['CP05 landing to residence link'];link.location=(p+q)/2;link.location.z=1.286-.035;link.scale=(d.xy.length+.04,.56,.07);link.rotation_euler.z=math.atan2(d.y,d.x)
# Make the upper flight read as a supported stone stair, not a floating slab.
o=box('CP05 upper flight stone support',(0,run/2,-(MID-BASE)/2),(1.035,run+.015,MID-BASE),terr[3]);o.parent=upper
# Keep the lower flight free of the neighbouring house foundation; the small
# residence walk has visible brackets instead of a broad solid pad through steps.
for o in list(s.objects):
 if o.name.startswith('CP05 residence footing'):bpy.data.objects.remove(o,do_unlink=True)
house=bpy.data.objects['quiet_home'];hp=[house.matrix_world@Vector((x,y,0)) for x,y in [(-1.65,-1.58),(1.65,-1.58),(1.65,1.5),(-1.65,1.5)]]
for i in range(3):slab('CP05 residence footing '+str(i),hp,.82+i*.23,.24,terr[3 if i<2 else 4])
for yy in [-1.15,-.10,.65]:
 a=house.matrix_world@Vector((-1.55,yy,-.42));b=house.matrix_world@Vector((-2.10,yy,-.01));beam('CP05 residence walkway bracket',a,b,.034,wood)
# Clear the landing from the lamp and give the bench a little more room in front.
dest=xy((1080,280),.61);prefix='CP02 street lantern 12 ';old=bpy.data.objects[prefix+'foot'].location-Vector((0,0,.06))
for o in s.objects:
 if o.name.startswith(prefix):o.location+=dest-old
newbench=xy((1138,137),TOP+.025);bpy.data.objects['quiet_reader'].location=newbench;bpy.data.objects['CP05_overlook_bench'].location=newbench
bpy.data.objects['hill_windwheel'].location.z=TOP+.021
# Flush the final lower tread, turning landing and adjacent timber walk.
bpy.data.objects['CP05 middle landing cap'].location.z=-.014
for o in s.objects:
 if o.name.startswith('CP05 middle landing paving seam'):o.location.z=.003
walk_shift=MID+.004-1.286
for name in ['CP05 residence side walk','CP05 landing to residence link']:bpy.data.objects[name].location.z+=walk_shift
bpy.context.view_layer.update()
for o in s.objects:
 if o.name.startswith('CP05 residence walkway bracket'):
  a=o.matrix_world@Vector((0,0,-.5));b=o.matrix_world@Vector((0,0,.5))
  if a.z>b.z:a,b=b,a
  b.z+=walk_shift;o.location=(a+b)/2;o.scale.z=(b-a).length;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
bpy.data.objects['returning_resident'].location.z=MID+.007
for name in ['quiet_reader','CP05_overlook_bench']:bpy.data.objects[name].location.z=TOP+.004
for o in bpy.data.objects['CP05_overlook_bench'].children:
 if o.name.startswith('CP05 bench leg'):o.scale.z=.48
for oldpx,newpx in [((1009,159),(1029,157)),((1080,131),(1091,133)),((1217,157),(1215,160))]:
 p=xy(oldpx,TOP+.02);delta=xy(newpx,TOP+.02)-p
 for o in s.objects:
  if not o.parent and o.name.startswith(('CP05 terrace planter','CP05 terrace boundary planting')) and (o.location.xy-p.xy).length<.38:o.location+=delta
# Short staggered stone seams keep the retaining wall legible without tall bars.
for o in list(s.objects):
 if o.name.startswith('CP05 terrace stone joint'):bpy.data.objects.remove(o,do_unlink=True)
outline=[Vector(p) for p in t['upper_outline_world']]
for p,q in zip(outline[3:],outline[4:]+outline[:1]):
 length=(q-p).xy.length
 if length<.2:continue
 d=(q-p).normalized();normal=Vector((d.y,-d.x,0));angle=math.atan2(d.y,d.x)
 for row in range(4):
  count=max(1,round(length/.40));segment_size=length/count
  for i in range(count):
   u=(i+.5+(row%2)*.16)/count
   if u>.98:continue
   v=p.lerp(q,u)+normal*.008;v.z=BASE+.16+row*.28
   box('CP05 dressed paper stone',v,(segment_size*.94,.035,.25),terr[3 if (i+row)%3 else 2],(0,0,angle))

# Update existing design reservations to the new frontage and stair surfaces.
guides=bpy.data.collections['12_CP04_MOVEMENT_RESERVATIONS'];guides.name='12_CP05_MOVEMENT_RESERVATIONS';COL=guides
for o in list(guides.objects):
 if o.name.startswith('Stair clear tread'):bpy.data.objects.remove(o,do_unlink=True)
route_mat=bpy.data.materials['GUIDE ONLY | walking clearance cyan'];prev=json.loads((ROOT/'outputs/modeling-checkpoint-04/model-manifest.json').read_text());reserves=[r for r in prev['movement_reservations'] if not r['name'].startswith('Stair')]
def band(name,pts,width,replace=False):
 vs=[];fs=[]
 for p,q in zip(pts,pts[1:]):
  side=Vector((-(q-p).y,(q-p).x,0)).normalized()*width/2;k=len(vs);vs.extend([tuple(p-side),tuple(p+side),tuple(q+side),tuple(q-side)]);fs.append((k,k+1,k+2,k+3))
 me=bpy.data.meshes.new(name+' guide mesh');me.from_pydata(vs,[],fs);me.materials.append(route_mat);me.update()
 o=bpy.data.objects.get(name) if replace else None
 if o:o.data=me
 else:o=bpy.data.objects.new(name,me);COL.objects.link(o)
 o['guide_only']=True;o['no_new_decor']=True;o['reserved_width']=width
 return o
tea=bpy.data.objects['tea_house'];bpy.context.view_layer.update();market=[tea.matrix_world@Vector((x,-3.35,0)) for x in [-3.35,3.30]]+[xy((1082,321))]
for p in market:p.z=.695
band('Market frontage',market,1.12,True)
for r in reserves:
 if r['name']=='Market frontage':r['points_world']=[list(p) for p in market]
entry=[tea.matrix_world@Vector(p) for p in [(-3.65,-3.20,0),(-3.65,-.63,0),(-3.25,-.63,0)]]
for p in entry:p.z=.695
band('CP05 restaurant entry reservation',entry,.70)
reserves.append({'name':'CP05 restaurant entry reservation','width':.70,'points_world':[list(p) for p in entry],'purpose':'Entrance approach reserved for later detail; not a validated navigation route.'})
for root,prefix in [(lower,'Lower'),(upper,'Upper')]:
 for i in range(5):
  a=root.matrix_world@Vector((0,i*.2,(i+1)*rise+.025));b=root.matrix_world@Vector((0,(i+1)*.2,(i+1)*rise+.025));band('CP05 '+prefix+' stair clear tread '+str(i),[a,b],.86)
v=landing.location.copy();v.z=MID+.055;band('CP05 landing reservation',[v+Vector((-.3,0,0)),v+Vector((.3,0,0))],.90)
guides.hide_render=True;guides.hide_viewport=True;bpy.context.view_layer.update()

# Fixed-pose visibility and support samples, not simulated life or navigation.
dg=bpy.context.evaluated_depsgraph_get();vis=[];residents=[o for o in s.objects if o.get('entity_id') and any(c.name=='08_Residents_SCALE_PROXIES' for c in o.users_collection)];animals=[o for o in s.objects if o.get('entity_id') and any(c.name=='09_Animals_SCALE_PROXIES' for c in o.users_collection)]
for root in residents:
 row={'resident':root.name,'samples':{}}
 for label,z in [('head',1.08),('upper_body',.75)]:
  p=root.matrix_world@Vector((0,0,z));h,lo,no,fi,obj,m=s.ray_cast(dg,p-FWD*40,FWD,distance=41);a=obj
  while a and a.parent:a=a.parent
  row['samples'][label]={'unoccluded_center_ray':a==root,'first_hit':obj.name if obj else None,'pixel':pix(p)}
 vis.append(row)
supports=[]
support_meshes=[o for o in s.objects if o.type=='MESH' and o.name.startswith(('CP05 terrace paving','CP05 upper terrace stone layer','CP05 middle landing','CP05_lower_stair tread','CP05_upper_stair tread','CP05 top landing'))]
for name in ['quiet_reader','returning_resident','hill_windwheel']:
 o=bpy.data.objects[name];p=o.location.copy();hits=[]
 for surf in support_meshes:
  inv=surf.matrix_world.inverted();origin=inv@(p+Vector((0,0,.055)));direction=(inv.to_3x3()@Vector((0,0,-1))).normalized();hit,lo,no,fi=surf.ray_cast(origin,direction)
  if hit:
   point=surf.matrix_world@lo
   if p.z-2<point.z<=p.z+.055:hits.append((point.z,surf.name))
 hit=max(hits) if hits else None
 supports.append({'entity':name,'surface':hit[1] if hit else None,'root_minus_surface_z':p.z-hit[0] if hit else None,'method':'Ray against supporting terrain/stair meshes only, excluding actor geometry.'})
stair_samples=[]
for root in [lower,upper]:
 for i in range(5):
  for x in [-.36,0,.36]:
   p=root.matrix_world@Vector((x,(i+.5)*.2,(i+1)*rise));h,lo,no,fi,obj,m=s.ray_cast(dg,p+Vector((0,0,.07)),Vector((0,0,-1)),distance=.18)
   stair_samples.append({'flight':root.name,'step':i+1,'cross_offset':x,'first_hit':obj.name if obj else None,'surface_delta':lo.z-p.z if h else None,'at_tread_height':bool(h and abs(lo.z-p.z)<.035)})
manifest={'checkpoint':'CP05','source_checkpoint':'CP04','scope':'Broad-front core restaurant plus two-flight hillside terrace; stop for user review','camera':{'type':cam.data.type,'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'orthographic_scale':ORTHO,'elevation_degrees':math.degrees(math.asin(abs(FWD.z)))},'objects':len(s.objects),'resident_proxy_count':len(residents),'animal_proxy_count':len(animals),'static_visibility_samples':vis,'hill_support_samples':supports,'stair_surface_samples':stair_samples,'movement_reservations':reserves,'guide_collection':guides.name,'not_implemented':['final art and all decoration','rigged characters and animation visibility','navigation/collision simulation','web renderer','24/7 backend'],'limitations':'Samples check static scene points; no full-motion, whole-town collision or overall reference similarity guarantee.'}
(OUT/'model-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));rec['final_adjustments']=['Added stone support below upper flight','Restored house foundation footprint; side walk supported by brackets','Moved lamp off intermediate landing','Moved bench back for arrival clearance','Terrace planters moved inward','Restaurant and stair guide surfaces updated','Aligned final tread, middle landing and residence walk; small threshold remains at the residence floor'];(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
# Two actual close-up cameras; main camera remains untouched.
def detail_camera(name,pixelpoint,z,scale):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);cols['11_Cameras'].objects.link(o);d.type='ORTHO';d.ortho_scale=scale;o.rotation_euler=cam.rotation_euler;o.location=xy(pixelpoint,z)-FWD*30;return o
restaurant_cam=detail_camera('Camera_CP05_Restaurant',(773,238),1.4,10.4)
terrace_cam=detail_camera('Camera_CP05_Terrace',(1133,209),1.2,8.0)
plan=bpy.data.objects['Camera_Plan_CP04'];plan.name='Camera_Plan_CP05'
s['checkpoint']='CP05 | broad restaurant facade; five + five stairs with turning landing';s['review_status']='STOP for user review'
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.samples=96;s.cycles.use_denoising=True;s.render.filepath=str(OUT/'01-overview.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp05.blend'))
bpy.ops.render.render(write_still=True);print('CP05_MAIN_READY',flush=True)
s.camera=restaurant_cam;s.render.resolution_x=1500;s.render.resolution_y=1100;s.cycles.samples=80;s.render.filepath=str(OUT/'03-restaurant-detail.png');bpy.ops.render.render(write_still=True)
s.camera=terrace_cam;s.render.resolution_x=1300;s.render.resolution_y=1100;s.cycles.samples=64;s.render.filepath=str(OUT/'04-terrace-detail.png');bpy.ops.render.render(write_still=True)
s.camera=plan;s.render.resolution_x=1500;s.render.resolution_y=1000;s.cycles.samples=40
for o in s.objects:
 if o.name.startswith(('Paper crescent','Paper star','CP02 layered paper cloud','CP02 visible paper rain')):o.hide_render=True
s.render.filepath=str(OUT/'02-plan.png');bpy.ops.render.render(write_still=True)
guides.hide_render=False;guides.hide_viewport=False;bpy.context.view_layer.update();s.render.filepath=str(OUT/'05-reserved-space.png');bpy.ops.render.render(write_still=True)
print('CP05_ALL_RENDERS_READY',json.dumps({'heads':sum(v['samples']['head']['unoccluded_center_ray'] for v in vis),'torsos':sum(v['samples']['upper_body']['unoccluded_center_ray'] for v in vis),'tread_samples_passed':sum(v['at_tread_height'] for v in stair_samples),'tread_samples_total':len(stair_samples)}),flush=True)
