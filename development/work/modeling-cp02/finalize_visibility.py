import bpy,math,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-02';s=bpy.context.scene;W,H=1672,941
cam=bpy.data.objects['Camera_Main_CP02_45deg'];s.camera=cam
s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100
# Preserve the main camera and all building anchors. Extend rear paper contours to support the rear arc.
for o in s.objects:
 if o.name.startswith('Island paper layer'):
  for v in o.data.vertices:
   if v.co.y>0:v.co.y*=1.15
tea=bpy.data.objects['tea_house']
for o in tea.children:
 if o.name.startswith(('Tea balcony floor','Balcony baluster','Balcony long rail')):
  o.location.z+=.28;o.location.y+=.18
 if o.name.startswith(('Awning folded stripe','Awning front')):o.location.z+=.24
 if o.name.startswith('Stall post'):
  o.scale.z*=1.13;o.location.z+=.11
# Proxy poses follow real usable surfaces, not frozen pixels in a concept illustration.
for name,loc in {'vendor_bread':(-1.65,-1.77,0),'vendor_flower':(.0,-1.77,0),'vendor_lamp':(1.65,-1.77,0),'customer_one':(-1.5,-2.97,0),'customer_two':(.50,-3.00,0),'customer_three':(2.4,-3.00,0)}.items():
 bpy.data.objects[name].location=tea.matrix_world@Vector(loc)
bpy.context.view_layer.update()
Q=cam.rotation_euler.to_quaternion();FWD=Q@Vector((0,0,-1))
def px(p):
 a=world_to_camera_view(s,cam,p);return [a.x*W,(1-a.y)*H]
align=json.loads((OUT/'landmark-alignment.json').read_text())
for a in align['landmarks']:
 o=bpy.data.objects.get(a['entity'])
 if o:
  a['render_pixel']=px(o.matrix_world@Vector(a['anchor_local']));a['error_pixels']=math.dist(a['reference_pixel'],a['render_pixel'])
  if a['entity'].startswith(('vendor_','customer_')):a['note']='Scale proxy moved to the actual stall/walking surface for visible actions; not a fixed-pose image match.'
(OUT/'landmark-alignment.json').write_text(json.dumps(align,ensure_ascii=False,indent=2))
deps=bpy.context.evaluated_depsgraph_get();visibility=[]
for o in s.objects:
 if not o.get('entity_id') or not any(c.name=='08_Residents_SCALE_PROXIES' for c in o.users_collection):continue
 head=next((h for h in o.children if h.name.startswith('Head')),None)
 if not head:continue
 p=head.matrix_world.translation;hit,loc,n,fi,ho,ma=s.ray_cast(deps,p-FWD*40,FWD,distance=50)
 ancestor=ho
 while ancestor and ancestor.parent:ancestor=ancestor.parent
 visibility.append({'resident':o.name,'head_first_hit':ho.name if ho else None,'unoccluded_head_center_ray':ancestor==o,'pixel':px(p)})
manifest=json.loads((OUT/'model-manifest.json').read_text());manifest['head_visibility_sampling']=visibility;manifest['rear_terrain_support_extended']=True
manifest['notes']='Fixed 45-degree orthographic camera; building anchor positions remain. Resident proxies are placed for visibility, not frozen to the reference poses. Head rays and manual landmarks do not constitute a navigation system or overall fidelity score.'
(OUT/'model-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
plan=bpy.data.objects.get('Camera_Plan_CP01') or bpy.data.objects.get('Camera_Plan_CP02');plan.name='Camera_Plan_CP02'
land=next(o for o in s.objects if o.name=='Island paper layer 4');center=Vector((land.location.x,land.location.y+.35,0))
plan.location=center+Vector((0,0,36));plan.rotation_euler=(center-plan.location).to_track_quat('-Z','Y').to_euler();plan.data.ortho_scale=29.3
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='METAL';p.get_devices()
 for d in p.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.samples=96;s.render.filepath=str(OUT/'01-overview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp02.blend'))
bpy.ops.render.render(write_still=True);print('CP02_MAIN_FINAL',flush=True)
s.camera=plan;s.render.resolution_x=1500;s.render.resolution_y=1000;s.cycles.samples=40
for o in s.objects:
 if o.name.startswith(('Paper crescent','Paper star','CP02 layered paper cloud','CP02 visible paper rain')):o.hide_render=True
s.render.filepath=str(OUT/'02-plan.png');bpy.ops.render.render(write_still=True)
print('CP02_DONE_STOP',json.dumps({'head_rays_visible':sum(v['unoccluded_head_center_ray'] for v in visibility),'head_rays_total':len(visibility)}),flush=True)
