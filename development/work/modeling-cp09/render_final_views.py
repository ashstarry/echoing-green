import bpy,math,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-09';s=bpy.context.scene;main=s.camera;old='--baseline' in sys.argv
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='METAL';p.get_devices()
 for d in p.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
if '--cpu' in sys.argv:s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6
s.cycles.use_denoising=True;s.render.resolution_percentage=100
def render(cam,name,w,h,samples=96):
 
 if '--repairs-only' in sys.argv and name not in ['01-overview.png','05-boat.png','06-terrace.png']:return
 s.camera=cam;s.render.resolution_x=w;s.render.resolution_y=h;s.cycles.samples=samples;s.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
def detail(name,focus,scale):
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.rotation_euler=main.rotation_euler;f=main.rotation_euler.to_quaternion()@Vector((0,0,-1));o.location=focus-f*30;return o

render(main,'01-overview.png',1672,941,128)
st=bpy.data.objects['station_main'];render(detail('CP09 station inspection',st.matrix_world.translation+Vector((0,0,.80)),8.8),'02-station.png',1500,950,96)
h=bpy.data.objects['west_home'];render(detail('CP09 west balcony inspection',h.matrix_world@Vector((0,-1.4,1.7)),5.8),'03-balcony.png',1400,1100,96)
b=bpy.data.objects['street_bicycle'];render(detail('CP09 bicycle inspection',b.matrix_world.translation+Vector((0,0,.70)),3.4),'04-bicycle.png',1200,1000,96)
b=bpy.data.objects['pond_boat'];render(detail('CP09 boat inspection',b.matrix_world.translation+Vector((0,0,.10)),4.2),'05-boat.png',1400,1000,96)
render(bpy.data.objects['Camera_CP06_Terrace'],'06-terrace.png',1400,1100,96)
r=main.rotation_euler.to_quaternion()@Vector((1,0,0));back=Vector((-r.y,r.x,0));render(detail('CP09 paper border inspection',r*(-4.6)+back*(-7.5)+Vector((0,0,.25)),7.8),'07-paper-border.png',1500,950,96)
render(detail('CP09 music plaza inspection',bpy.data.objects['plaza_ground'].matrix_world.translation+Vector((0,0,.70)),8.8),'08-plaza.png',1500,1050,96)
print('CP09_RENDER_SET_COMPLETE',flush=True)
