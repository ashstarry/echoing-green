import bpy,math,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-08';s=bpy.context.scene;main=s.camera;old='--baseline' in sys.argv
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='METAL';p.get_devices()
 for d in p.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
if '--cpu' in sys.argv:s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6
s.cycles.use_denoising=True;s.render.resolution_percentage=100
def render(cam,name,w,h,samples=96):
 s.camera=cam;s.render.resolution_x=w;s.render.resolution_y=h;s.cycles.samples=samples;s.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
def detail(name,focus,scale):
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.rotation_euler=main.rotation_euler;f=main.rotation_euler.to_quaternion()@Vector((0,0,-1));o.location=focus-f*30;return o
plaza=detail('CP08 social plaza inspection',bpy.data.objects['plaza_ground'].matrix_world.translation+Vector((0,0,.65)),8.8)
if old:render(plaza,'reference/cp07-plaza.png',1500,1050,64)
elif '--hero-only' in sys.argv:render(main,'01-overview.png',1672,941,128)
else:
 render(main,'01-overview.png',1672,941,128)
 render(plaza,'02-plaza.png',1500,1050)
 gh=bpy.data.objects['greenhouse'];render(detail('CP08 garden and water inspection',gh.matrix_world.translation+Vector((0,-1.8,.45)),9.6),'03-garden-water.png',1500,1150)
 st=bpy.data.objects['station_main'];render(detail('CP08 station inspection',st.matrix_world.translation+Vector((0,0,.65)),9.6),'04-station.png',1500,900)
 render(bpy.data.objects['Camera_CP06_Terrace'],'05-terrace.png',1400,1050,80)
 for o in s.objects:
  if o.name.startswith(('Paper crescent','Paper star','CP02 layered paper cloud','CP02 visible paper rain')):o.hide_render=True
 render(bpy.data.objects['Camera_Plan_CP06'],'06-plan.png',1500,1000,48)
print('CP08_RENDER_REVIEW_COMPLETE',flush=True)
