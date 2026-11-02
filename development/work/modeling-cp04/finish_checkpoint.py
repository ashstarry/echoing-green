import bpy,math,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-04';s=bpy.context.scene;cam=s.camera
W,H=1672,941;s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100
Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));UP=Q@Vector((0,1,0));FWD=Q@Vector((0,0,-1))
def xy(p,z=.61):
 o=cam.location+RIGHT*((p[0]/W-.5)*cam.data.ortho_scale)+UP*((.5-p[1]/H)*cam.data.ortho_scale/(W/H));return o+FWD*((z-o.z)/FWD.z)
def pix(p):
 q=world_to_camera_view(s,cam,p);return [q.x*W,(1-q.y)*H]
tea=bpy.data.objects['tea_house']
for o in tea.children:
 if o.name.startswith(('Awning folded stripe','Awning front')):o.location.z+=.24
 if o.name.startswith('Stall post'):o.location.z+=.12;o.scale.z*=1.12

# The reserved market approach follows the new facade. This remains a design guide.
guide=bpy.data.collections['12_CP03_MOVEMENT_RESERVATIONS'];guide.name='12_CP04_MOVEMENT_RESERVATIONS'
prev=json.loads((ROOT/'outputs/modeling-checkpoint-03/model-manifest.json').read_text())
reserves=prev['movement_reservations'];bpy.context.view_layer.update()
endpoints=[tea.matrix_world@Vector((x,-3.35,0)) for x in [-3.45,3.3]]
for p in endpoints:p.z=.695
endpoints.append(xy((1082,321),.695))
route=bpy.data.objects['Market frontage'];width=1.12;verts=[];faces=[]
for p,q in zip(endpoints,endpoints[1:]):
 side=Vector((-(q-p).y,(q-p).x,0)).normalized()*width/2;k=len(verts);verts.extend([tuple(p-side),tuple(p+side),tuple(q+side),tuple(q-side)]);faces.append((k,k+1,k+2,k+3))
mat=route.data.materials[0];me=bpy.data.meshes.new('CP04 market approach mesh');me.from_pydata(verts,[],faces);me.materials.append(mat);me.update();route.data=me
for r in reserves:
 if r['name']=='Market frontage':r['points_world']=[list(p) for p in endpoints]
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
def ray(p):
 hit,loc,n,fi,o,m=s.ray_cast(dg,p-FWD*40,FWD,distance=41);root=o
 while root and root.parent:root=root.parent
 return o,root
vis=[];residents=[o for o in s.objects if o.get('entity_id') and any(c.name=='08_Residents_SCALE_PROXIES' for c in o.users_collection)]
animals=[o for o in s.objects if o.get('entity_id') and any(c.name=='09_Animals_SCALE_PROXIES' for c in o.users_collection)]
for root in residents:
 row={'resident':root.name,'samples':{}}
 for label,z in [('head',1.08),('upper_body',.75)]:
  p=root.matrix_world@Vector((0,0,z));hit,ancestor=ray(p);row['samples'][label]={'unoccluded_center_ray':ancestor==root,'first_hit':hit.name if hit else None,'pixel':pix(p)}
 vis.append(row)
view=Vector((-FWD.x,-FWD.y,0)).normalized();facades=[]
for name,front,side in [('tea_house',(1.3,-1.40,2.78),(-2.70,-.63,2.78)),('west_home',(.70,-1.27,1.6),(-1.46,.58,1.54))]:
 root=bpy.data.objects[name];rot=root.rotation_euler.to_quaternion();row={'entity':name,'front_angle_to_camera_horizontal':math.degrees(math.acos((rot@Vector((0,-1,0))).dot(view))),'side_angle_to_camera_horizontal':math.degrees(math.acos((rot@Vector((-1,0,0))).dot(view))),'samples':{}}
 for label,p in [('front',front),('side',side)]:
  hit,ancestor=ray(root.matrix_world@Vector(p));row['samples'][label]={'first_hit':hit.name if hit else None,'target_building_visible_at_sample':ancestor==root}
 facades.append(row)
manifest={'checkpoint':'CP04','source_checkpoint':'CP03','scope':'Two-face architecture orientation and side-wall modeling; stop for user review','camera':{'type':cam.data.type,'elevation_degrees':math.degrees(math.asin(abs(FWD.z))),'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'orthographic_scale':cam.data.ortho_scale},'objects':len(s.objects),'resident_proxy_count':len(residents),'animal_proxy_count':len(animals),'static_visibility_samples':vis,'target_facade_samples':facades,'movement_reservations':reserves,'guide_collection':guide.name,'not_implemented':['final art quality','rigs and animation envelopes','navigation/collision simulation','browser renderer','24/7 backend'],'limitations':'Horizontal facade angles and fixed center rays are local diagnostics, not a whole-image fidelity score or full-motion visibility test.'}
(OUT/'model-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
rec=json.loads((OUT/'revision-record.json').read_text());rec['final_merchant_canopy_lift_local_z']=.24;rec['market_movement_guide_reoriented']=True
(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
# Unchanged-angle detail camera exposes the two faces in a single actual render.
d=bpy.data.cameras.new('CP04 architecture detail camera');detail=bpy.data.objects.new('Camera_CP04_ArchitectureDetail',d);bpy.data.collections['11_Cameras'].objects.link(detail);d.type='ORTHO';d.ortho_scale=16
detail.location=xy((620,260),1.6)-FWD*28;detail.rotation_euler=cam.rotation_euler
plan=bpy.data.objects['Camera_Plan_CP03'];plan.name='Camera_Plan_CP04';plan.data.ortho_scale=30.4
s['checkpoint']='CP04 | front and side at horizontal 45-degree view; camera unchanged from CP03'
s['review_status']='STOP: user review before continuing modeling or runtime work'
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
 for dev in prefs.devices:dev.use=dev.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.samples=96;s.cycles.use_denoising=True;s.render.filepath=str(OUT/'01-overview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp04.blend'));bpy.ops.render.render(write_still=True);print('CP04_MAIN_READY',flush=True)
s.camera=detail;s.render.resolution_x=1500;s.render.resolution_y=1000;s.cycles.samples=80;s.render.filepath=str(OUT/'03-architecture-detail.png');bpy.ops.render.render(write_still=True)
s.camera=plan;s.cycles.samples=40
for o in s.objects:
 if o.name.startswith(('Paper crescent','Paper star','CP02 layered paper cloud','CP02 visible paper rain')):o.hide_render=True
s.render.filepath=str(OUT/'02-plan.png');bpy.ops.render.render(write_still=True)
guide.hide_render=False;guide.hide_viewport=False;bpy.context.view_layer.update();s.render.filepath=str(OUT/'04-reserved-space.png');bpy.ops.render.render(write_still=True)
print('CP04_RENDERS_READY',json.dumps({'head_rays':sum(v['samples']['head']['unoccluded_center_ray'] for v in vis),'upper_body_rays':sum(v['samples']['upper_body']['unoccluded_center_ray'] for v in vis),'facade_samples':facades}),flush=True)
