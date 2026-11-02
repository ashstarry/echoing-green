import bpy,json,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/art-checkpoint-16';s=bpy.context.scene;main=s.camera;FWD=main.rotation_euler.to_quaternion()@Vector((0,0,-1));tea=bpy.data.objects['tea_house'];s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=5;s.cycles.use_denoising=True;s.render.resolution_percentage=100
group=int(sys.argv[sys.argv.index('--group')+1]) if '--group' in sys.argv else None
def render(cam,name,w,h,samples=64):
 if group is not None and (0 if name=='01-overview.png' else 1 if name=='02-restaurant.png' else 2)!=group:return
 s.camera=cam;s.render.resolution_x=w;s.render.resolution_y=h;s.cycles.samples=samples;s.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
def detail(name,p,scale):
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.rotation_euler=main.rotation_euler;o.location=p-FWD*30;return o
render(main,'01-overview.png',1672,941,80)
render(detail('CP16 upper dining view',tea.matrix_world@Vector((0,-1.05,2.02)),8.1),'02-restaurant.png',1400,1035)
render(detail('CP16 central tea cabinet',tea.matrix_world@Vector((-.15,-1.65,2.96)),2.8),'03-tea-cabinet.png',900,780,48)
print('CP16_RENDERS_COMPLETE',flush=True)
