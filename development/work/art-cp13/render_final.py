import bpy,json,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/art-checkpoint-13';s=bpy.context.scene;main=s.camera;FWD=main.rotation_euler.to_quaternion()@Vector((0,0,-1));tea=bpy.data.objects['tea_house'];s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=3;s.cycles.use_denoising=True;s.render.resolution_percentage=100
group=int(sys.argv[sys.argv.index('--group')+1]) if '--group' in sys.argv else None
def render(cam,name,w,h,samples=64):
 if group is not None and (0 if name=='01-overview.png' else 1 if name=='02-restaurant.png' else 2)!=group:return
 s.camera=cam;s.render.resolution_x=w;s.render.resolution_y=h;s.cycles.samples=samples;s.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
def detail(name,p,scale):
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.rotation_euler=main.rotation_euler;o.location=p-FWD*30;return o
render(main,'01-overview.png',1672,941,80)
render(detail('CP13 upper dining view',tea.matrix_world@Vector((0,-1.05,2.02)),8.1),'02-restaurant.png',1400,1035)
focus=(bpy.data.objects['greenhouse'].matrix_world.translation+bpy.data.objects['pond_boat'].matrix_world.translation)/2+Vector((0,0,.85));render(detail('CP13 lotus and rain bridge',focus,8.8),'03-garden-water.png',1400,1100)
render(detail('CP13 folded moon',bpy.data.objects['Paper crescent'].matrix_world.translation,1.85),'04a-moon-detail.png',680,680,48)
render(detail('CP13 folded bird',bpy.data.objects['paper_bird_0'].matrix_world.translation,1.25),'04b-bird-detail.png',680,680,48)
render(detail('CP13 embossed star',bpy.data.objects['Paper star 0'].matrix_world.translation,.44),'04c-star-detail.png',680,680,48)
render(detail('CP13 lotus lamp',bpy.data.objects['CP12_floating_paper_lantern_0'].matrix_world.translation+Vector((0,0,.12)),.85),'04d-lantern-detail.png',680,680,48)
print('CP13_RENDERS_COMPLETE',flush=True)
