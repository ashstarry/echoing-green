import bpy,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-07';s=bpy.context.scene;main=s.camera
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='METAL';p.get_devices()
 for d in p.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.use_denoising=True;s.render.resolution_percentage=100
def render(camera,name,w,h,samples=96):
 s.camera=camera;s.render.resolution_x=w;s.render.resolution_y=h;s.cycles.samples=samples;s.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True);print(name+' READY',flush=True)
def detail(name,focus,scale):
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.rotation_euler=main.rotation_euler;f=main.rotation_euler.to_quaternion()@Vector((0,0,-1));o.location=focus-f*30;return o
render(main,'01-overview.png',1672,941,128)
tea=bpy.data.objects['tea_house'];render(detail('CP07 restaurant inspection',tea.matrix_world@Vector((-.35,-.9,1.7)),8.0),'02-restaurant.png',1600,1150)
render(bpy.data.objects['Camera_CP06_Terrace'],'03-terrace.png',1500,1100)
gh=bpy.data.objects['greenhouse'];render(detail('CP07 water garden inspection',gh.matrix_world@Vector((0,-1.5,.6)),7.7),'04-water-garden.png',1500,1150)
post=bpy.data.objects['post_office'];render(detail('CP07 paper neighborhood inspection',post.matrix_world@Vector((-.2,-.3,.9)),6.4),'05-paper-neighborhood.png',1500,1100)
for o in s.objects:
 if o.name.startswith(('Paper crescent','Paper star','CP02 layered paper cloud','CP02 visible paper rain')):o.hide_render=True
render(bpy.data.objects['Camera_Plan_CP06'],'06-plan.png',1500,1000,48)
print('CP07_RENDERS_COMPLETE',flush=True)
