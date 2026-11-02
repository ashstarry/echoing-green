import bpy,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-04';s=bpy.context.scene;cam=s.camera
if os.environ.get('TOWN_RENDER_CPU')=='1':s.cycles.device='CPU'
else:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='METAL';p.get_devices()
 for d in p.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
s.cycles.samples=96;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.resolution_x=1672;s.render.resolution_y=941;s.render.filepath=str(OUT/'01-overview.png');bpy.ops.render.render(write_still=True);print('CP04_MAIN_READY',flush=True)
s.camera=bpy.data.objects['Camera_CP04_ArchitectureDetail'];s.render.resolution_x=1500;s.render.resolution_y=1000;s.cycles.samples=80;s.render.filepath=str(OUT/'03-architecture-detail.png');bpy.ops.render.render(write_still=True);print('CP04_DETAIL_READY',flush=True)
s.camera=bpy.data.objects['Camera_Plan_CP04'];s.cycles.samples=40
for o in s.objects:
 if o.name.startswith(('Paper crescent','Paper star','CP02 layered paper cloud','CP02 visible paper rain')):o.hide_render=True
s.render.filepath=str(OUT/'02-plan.png');bpy.ops.render.render(write_still=True)
guide=bpy.data.collections['12_CP04_MOVEMENT_RESERVATIONS'];guide.hide_render=False;guide.hide_viewport=False;bpy.context.view_layer.update();s.render.filepath=str(OUT/'04-reserved-space.png');bpy.ops.render.render(write_still=True)
print('CP04_ALL_RENDERS_READY',flush=True)
