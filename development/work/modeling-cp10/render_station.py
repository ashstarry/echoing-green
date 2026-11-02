import bpy,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-10';WORK=ROOT/'work/modeling-cp10';s=bpy.context.scene;main=s.camera;draft='--draft'in sys.argv
s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.use_denoising=True;s.render.resolution_percentage=100
def render(cam,name,w,h,samples):
 s.camera=cam;s.render.resolution_x=w;s.render.resolution_y=h;s.cycles.samples=samples;s.render.filepath=str((WORK if draft else OUT)/name);bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
def detail(name,focus,scale):
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.rotation_euler=main.rotation_euler;o.location=focus-(main.rotation_euler.to_quaternion()@Vector((0,0,-1)))*30;return o
st=bpy.data.objects['station_main'];c=detail('CP10 station same-angle detail',st.matrix_world.translation+Vector((0,0,.80)),8.8)
if draft:
 if '--overview'in sys.argv:render(main,'overview-draft.png',1100,619,24)
 else:render(c,'station-draft.png',1000,634,24)
else:
 render(c,'02-station.png',1500,950,64)
 render(main,'01-overview.png',1672,941,64)
 # True orthographic top inspection: roof is hidden only for this diagnostic frame.
 q=main.rotation_euler.to_quaternion();right=q@Vector((1,0,0));back=Vector((-right.y,right.x,0));focus=st.matrix_world.translation+back*(-.20);c=detail('CP10 plan inspection',focus,10.2);c.location=focus+Vector((0,0,30));c.rotation_euler=(0,0,__import__('math').atan2(right.y,right.x));s.camera=c
 for o in st.children_recursive:
  if any(k in o.name.lower()for k in ['roof','shingle','ridge','gable']):o.hide_render=True
 render(c,'03-plan-inspection.png',1500,950,48)
print('CP10_RENDER_COMPLETE',flush=True)
