import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/lighting-checkpoint-12';s=bpy.context.scene;main=s.camera;Q=main.rotation_euler.to_quaternion();right=Q@Vector((1,0,0));back=Vector((-right.y,right.x,0));forward=Q@Vector((0,0,-1))
s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.use_denoising=True;s.render.resolution_percentage=100
def render(cam,name,w,h,samples=64):
 s.camera=cam;s.render.resolution_x=w;s.render.resolution_y=h;s.cycles.samples=samples;s.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
def detail(name,focus,scale):
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.rotation_euler=main.rotation_euler;o.location=focus-forward*30;return o
render(main,'01-overview.png',1672,941,96)
focus=(bpy.data.objects['greenhouse'].matrix_world.translation+bpy.data.objects['pond_boat'].matrix_world.translation)/2+Vector((0,0,.85));render(detail('CP12 garden and water light',focus,8.8),'02-garden-water.png',1400,1100)
print('CP12_RENDERS_COMPLETE',flush=True)
