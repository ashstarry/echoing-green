import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-06';s=bpy.context.scene;main=s.camera
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='METAL';p.get_devices()
 for d in p.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.use_denoising=True;s.render.resolution_percentage=100
def render(camera,name,w,h,samples):
 s.camera=camera;s.render.resolution_x=w;s.render.resolution_y=h;s.cycles.samples=samples;s.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True);print(name+' READY',flush=True)
render(main,'01-overview.png',1672,941,96)
render(bpy.data.objects['Camera_CP06_SideStall'],'03-side-stall.png',1400,1100,80)
render(bpy.data.objects['Camera_CP06_Terrace'],'04-terrace.png',1400,1100,80)
# Four nearby positions of the same unrigged proxy show actual doorway occlusion.
# No actor visibility flag is switched. This is an inspection sequence, not walking animation.
data=json.loads((OUT/'circulation-check.json').read_text());points=data['routes']['dining_to_door']['samples'];first=next(i for i,p in enumerate(points) if p['visible_body_samples']>0);indices=[max(0,first-1),first,min(len(points)-1,first+1),len(points)-1]
proxy=bpy.data.objects['returning_resident'];saved_matrix=proxy.matrix_world.copy();fwd=main.rotation_euler.to_quaternion()@Vector((0,0,-1));focus=Vector(points[indices[1]]['foot'])+Vector((0,0,.70))
d=bpy.data.cameras.new('Door transition inspection');doorcam=bpy.data.objects.new('Door transition inspection',d);s.collection.objects.link(doorcam);d.type='ORTHO';d.ortho_scale=4.8;doorcam.rotation_euler=main.rotation_euler;doorcam.location=focus-fwd*30
(OUT/'door-sequence').mkdir(exist_ok=True);sequence=[]
for j,index in enumerate(indices):
 point=Vector(points[index]['foot']);nextp=Vector(points[min(index+1,len(points)-1)]['foot'])
 if (nextp-point).length<.001:nextp=Vector(json.loads((OUT/'revision-record.json').read_text())['routes']['gallery_treads'][0])
 direction=nextp-point;proxy.location=point;proxy.rotation_euler.z=math.atan2(direction.y,direction.x)+math.pi/2;bpy.context.view_layer.update();name='door-sequence/%02d.png'%(j+1);render(doorcam,name,900,700,40);sequence.append({'frame':j+1,'route_sample':index,'foot':list(point),'visible_body_samples':points[index]['visible_body_samples'],'file':name})
proxy.matrix_world=saved_matrix;bpy.context.view_layer.update();(OUT/'door-sequence/sequence.json').write_text(json.dumps({'type':'Four static nearby positions of the same unrigged proxy with full roof and unchanged visibility; not a locomotion animation.','normal_roof_preserved':True,'actor_hide_toggled':False,'frames':sequence},ensure_ascii=False,indent=2))
sky=[]
for o in s.objects:
 if o.name.startswith(('Paper crescent','Paper star','CP02 layered paper cloud','CP02 visible paper rain')):sky.append(o);o.hide_render=True
render(bpy.data.objects['Camera_Plan_CP06'],'02-plan.png',1500,1000,40)
guide=bpy.data.collections['12_CP06_CIRCULATION_AND_ACTION_ZONES'];guide.hide_render=False;guide.hide_viewport=False
tea=bpy.data.objects['tea_house']
hide=[]
for o in tea.children_recursive:
 if o.name.startswith(('tea_house roof','tea_house shingle','tea_house ridge','tea_house gable','CP02 tea dormer','CP02 dormer','CP04 tea west gable')):hide.append(o)
for o in hide:o.hide_render=True
bpy.context.view_layer.update()
render(bpy.data.objects['Camera_CP06_CirculationCutaway'],'05-circulation-cutaway.png',1600,1100,64)
# Preserve normal saved model: all changes here are inspection-only in memory.
print('CP06_RENDER_SET_COMPLETE',flush=True)
