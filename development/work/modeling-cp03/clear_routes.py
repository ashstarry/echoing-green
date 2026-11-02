import bpy,math,json,bmesh
from mathutils import Vector
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-03';s=bpy.context.scene;cam=s.camera
Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));UP=Q@Vector((0,1,0));FWD=Q@Vector((0,0,-1));BACK=Vector((-RIGHT.y,RIGHT.x,0));W,H=1672,941;Z=.61
def xy(pixel,z=Z):
 p=cam.location+RIGHT*((pixel[0]/W-.5)*cam.data.ortho_scale)+UP*((.5-pixel[1]/H)*cam.data.ortho_scale/(W/H));return p+FWD*((z-p.z)/FWD.z)
def pix(p):
 q=world_to_camera_view(s,cam,p);return [q.x*W,(1-q.y)*H]
manifest=json.loads((OUT/'model-manifest.json').read_text());record=json.loads((OUT/'revision-record.json').read_text())
stair=bpy.data.objects['CP03_hill_stair'];inv=stair.matrix_world.inverted();L=record['stair']['horizontal_tread']*8
# A coplanar landing overlapped the concave platform surface. Lift its top slightly,
# and triangulate the slab's real mesh to remove the dark overlapping-surface seam.
bpy.data.objects['CP03 upper stair landing'].location.z+=.018
for o in s.objects:
 if o.name.startswith(('CP03 upper terrace layer','CP03 residence terrace layer')):
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
segments=[]
for r in manifest['movement_reservations']:
 if 'points_world' in r and not r['name'].startswith('Stair'):
  for p,q in zip(r['points_world'],r['points_world'][1:]):segments.append((Vector(p),Vector(q),r['width']))
def distance2d(p,a,b):
 v=Vector((b.x-a.x,b.y-a.y,0));d=Vector((p.x-a.x,p.y-a.y,0));t=max(0,min(1,d.dot(v)/max(1e-8,v.length_squared)));return (d-v*t).length
removed=[]
for o in list(s.objects):
 if o.parent or not o.name.startswith(('CP02 restrained flower bed','CP02 edge planting','CP02 street planter','Street planter','Perimeter paper planting')):continue
 p=o.matrix_world.translation;local=inv@p
 on_stair=abs(local.x)<.95 and -.75<local.y<L+.50
 in_route=any(distance2d(p,a,b)<w/2+.22 for a,b,w in segments)
 if on_stair or in_route:removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
lamp_moves=[]
for i,pixelpoint,z in [(3,(548,527),Z),(5,(1093,451),Z),(6,(1155,427),Z),(7,(1124,367),Z),(12,(1087,282),Z),(13,(1037,175),1.65)]:
 prefix='CP02 street lantern '+str(i)+' ';foot=bpy.data.objects[prefix+'foot'];old=foot.location-Vector((0,0,.06));new=xy(pixelpoint,z);delta=new-old
 for o in s.objects:
  if o.name.startswith(prefix):o.location+=delta
 lamp_moves.append({'lamp_index':i,'new_ground_pixel':pixelpoint,'new_ground_z':z})
# The rear rail originally ran through the new hill approach. Route that half
# behind the terrace, preserving the entire foreground arc and the two cars.
rails=[o for o in s.objects if o.name.startswith('CP02 continuous rail')]
pts=[Vector(p.co[:3]) for p in rails[0].data.splines[0].points];center=sum(pts,Vector())/len(pts)
def reroute(p):
 v=p-center;back=v.dot(BACK)
 return p+BACK*(max(0,back)*.33)
for o in rails:
 for sp in o.data.splines:
  for p in sp.points:
   q=reroute(Vector(p.co[:3]));p.co=(*q,1)
for o in s.objects:
 if o.name.startswith('CP02 sleeper'):
  old=o.location.copy();o.location=reroute(old)
  if (old-center).dot(BACK)>0:
   d=o.rotation_euler.to_quaternion()@Vector((1,0,0));d=d+BACK*(d.dot(BACK)*.33);o.rotation_euler.z=math.atan2(d.y,d.x)
for o in s.objects:
 if o.name.startswith('Island paper layer'):
  for v in o.data.vertices:
   if v.co.y>0:v.co.y*=1.15
# Keep sky ornaments inside the frame after lowering the camera.
for o in s.objects:
 if o.name.startswith('Paper star'):
  q=pix(o.matrix_world.translation)
  if q[1]<28:o.location-=UP*((28-q[1])*cam.data.ortho_scale/W)
record['route_cleanup']={'removed_loose_plant_components':len(removed),'moved_lamps':lamp_moves,'upper_landing_surface_separation':.018,'rear_rail_depth_factor':1.33,'rear_ground_extension_factor':1.15,'front_rail_and_trams_unchanged':True}
(OUT/'revision-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();visibility=[]
for root in s.objects:
 if not root.get('entity_id') or not any(c.name=='08_Residents_SCALE_PROXIES' for c in root.users_collection):continue
 row={'resident':root.name,'samples':{}}
 for label,local in [('head',(0,0,1.08)),('upper_body',(0,0,.75))]:
  p=root.matrix_world@Vector(local);hit,loc,n,face,o,ma=s.ray_cast(deps,p-FWD*40,FWD,distance=41);ancestor=o
  while ancestor and ancestor.parent:ancestor=ancestor.parent
  row['samples'][label]={'unoccluded_center_ray':ancestor==root,'first_hit':o.name if o else None,'pixel':pix(p)}
 visibility.append(row)
manifest['static_visibility_samples']=visibility;manifest['objects']=len(s.objects);manifest['existing_loose_decor_cleared_from_routes']=True
(OUT/'model-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='METAL';p.get_devices()
 for d in p.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.samples=96;s.render.resolution_percentage=100;s.render.filepath=str(OUT/'01-overview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp03.blend'))
s.camera=bpy.data.objects['Camera_CP03_Hill_Detail'];s.render.resolution_x=1300;s.render.resolution_y=1100;s.cycles.samples=64;s.render.filepath=str(OUT/'03-hill-detail.png');bpy.ops.render.render(write_still=True);print('CP03_CLEAN_HILL_READY',flush=True)
s.camera=cam;s.render.resolution_x=W;s.render.resolution_y=H;s.cycles.samples=96;s.render.filepath=str(OUT/'01-overview.png');bpy.ops.render.render(write_still=True);print('CP03_CLEAN_MAIN_READY',flush=True)
s.camera=bpy.data.objects['Camera_Plan_CP03'];s.render.resolution_x=1500;s.render.resolution_y=1000;s.cycles.samples=40
for o in s.objects:
 if o.name.startswith(('Paper crescent','Paper star','CP02 layered paper cloud','CP02 visible paper rain')):o.hide_render=True
s.render.filepath=str(OUT/'02-plan.png');bpy.ops.render.render(write_still=True)
guides=bpy.data.collections['12_CP03_MOVEMENT_RESERVATIONS'];guides.hide_render=False;guides.hide_viewport=False;bpy.context.view_layer.update()
s.render.filepath=str(OUT/'04-reserved-space.png');bpy.ops.render.render(write_still=True)
print('CP03_CLEANUP_DONE',json.dumps({'removed_loose_plant_components':len(removed),'head_rays':sum(x['samples']['head']['unoccluded_center_ray'] for x in visibility),'upper_body_rays':sum(x['samples']['upper_body']['unoccluded_center_ray'] for x in visibility)}),flush=True)
