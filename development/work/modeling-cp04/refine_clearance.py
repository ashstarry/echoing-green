import bpy,math,json
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'work/modeling-cp04';OUT=ROOT/'outputs/modeling-checkpoint-04';s=bpy.context.scene;cam=s.camera
Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));UP=Q@Vector((0,1,0));FWD=Q@Vector((0,0,-1));W,H=1672,941
def xy(p,z=.61):
 o=cam.location+RIGHT*((p[0]/W-.5)*cam.data.ortho_scale)+UP*((.5-p[1]/H)*cam.data.ortho_scale/(W/H));return o+FWD*((z-o.z)/FWD.z)
tea=bpy.data.objects['tea_house'];old=tea.matrix_world.copy();anchor=Vector((0,-2.1,0));pivot=old@anchor
people=['vendor_bread','vendor_flower','vendor_lamp','customer_one','customer_two','customer_three'];locals_={n:old.inverted()@bpy.data.objects[n].location for n in people}
tea.scale.z=.80;tea.scale.y=.80;bpy.context.view_layer.update();tea.location+=pivot-tea.matrix_world@anchor;bpy.context.view_layer.update()
for n,p in locals_.items():bpy.data.objects[n].location=tea.matrix_world@p
# Fit door-height/roof proportions to the low foreground post-office reference.
bpy.data.objects['post_office'].scale.z*=.82
# Retain resident scale. Place the two affected actors on the open side approach.
bpy.data.objects['courier'].location=xy((586,402))
bpy.data.objects['customer_one'].location=xy((675,409))
record=json.loads((OUT/'revision-record.json').read_text());record['clearance_refinements']={'tea_scale_final':list(tea.scale),'post_office_height_factor_from_cp03':.82,'courier_ground_pixel':[586,402],'customer_one_ground_pixel':[675,409],'reason':'Keep the roof in the unchanged camera and open the visible west-home facade; moving proxies does not establish runtime navigation.'};(OUT/'revision-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='METAL';p.get_devices()
 for d in p.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.render.resolution_percentage=75;s.cycles.samples=48;s.render.filepath=str(WORK/'refined.png')
bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'refined.blend'));bpy.ops.render.render(write_still=True);print('CP04_REFINED_READY',flush=True)
