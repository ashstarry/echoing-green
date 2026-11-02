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
 s.camera=cam;s.render.resolution_x=w;s.render.resolution_y=h;s.cycles.samples=samples;s.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
def detail(name,focus,scale):
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.rotation_euler=main.rotation_euler;f=main.rotation_euler.to_quaternion()@Vector((0,0,-1));o.location=focus-f*30;return o
plaza=detail('CP09 social plaza inspection',bpy.data.objects['plaza_ground'].matrix_world.translation+Vector((0,0,.65)),8.8)

render(main,'01-draft.png',1672,941,64)
render(detail('Station body inspection',bpy.data.objects['station_main'].matrix_world.translation+Vector((0,0,.80)),8.8),'02-station-draft.png',1500,950,64)
home=bpy.data.objects['west_home'];render(detail('West balcony body inspection',home.matrix_world@Vector((0,-1.4,1.7)),5.4),'03-balcony-draft.png',1300,1050,64)
bike=bpy.data.objects['street_bicycle'];render(detail('Bicycle body inspection',bike.matrix_world.translation+Vector((0,0,.65)),3.2),'04-bicycle-draft.png',1200,1000,64)
