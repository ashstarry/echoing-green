import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'work/art-cp14';OUT=ROOT/'outputs/art-checkpoint-14';s=bpy.context.scene;tea=bpy.data.objects['tea_house'];rec=json.loads((OUT/'revision-record.json').read_text());col=bpy.data.collections['02_Teahouse_Market'];cube=bpy.data.meshes['Shared cube'];wood=bpy.data.materials['Cedar frame']
for o in s.objects:
 if o.name.startswith('CP14 pendant cord'):o.location.z+=.12;o.scale.z+=.24
roots=sorted([o for o in s.objects if o.name.startswith('hanging_light_cp05_restaurant_paper_lantern_paper')],key=lambda o:o.name)
for i,r in enumerate(roots[:5]):
 a=Vector((0,0,.53));b=Vector((0,.22,.53))if i<3 else Vector((.26,0,.53));ob=bpy.data.objects.new('CP14 pendant bracket',cube);col.objects.link(ob);ob.parent=r;ob.location=(a+b)*.5;ob.scale=(.018,.018,(b-a).length);ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
 for sl in ob.material_slots:sl.link='OBJECT';sl.material=wood
bpy.context.view_layer.update();exec(compile((ROOT/'work/art-cp13/scene_signature.py').read_text(),'<signature>','exec'));before=json.loads((ROOT/'outputs/art-checkpoint-13/scene-signature.json').read_text());after=json.loads(json.dumps(scene_signature(s)));rec['modified']=[n for n in before['objects']if n not in rec['removed']and before['objects'][n]!=after['objects'].get(n)];rec['added']=sorted(set(after['objects'])-set(before['objects']));(OUT/'revision-record.json').write_text(json.dumps(rec,indent=2))
s['checkpoint']='CP14 | open dining balcony and enveloping warm art light';s['review_status']='Awaiting user art review; no animation or runtime implemented';s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.samples=80;s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100;s.render.filepath=str(OUT/'01-overview.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp14.blend'))
# Preview with the unchanged main camera and the same restaurant detail framing as CP13.
main=s.camera;s.cycles.samples=28;s.render.resolution_x=1200;s.render.resolution_y=675;s.render.filepath=str(W/'final-draft-overview.png');bpy.ops.render.render(write_still=True)
f=main.rotation_euler.to_quaternion()@Vector((0,0,-1));d=bpy.data.cameras.new('CP14 final draft restaurant');d.type='ORTHO';d.ortho_scale=8.1;c=bpy.data.objects.new(d.name,d);s.collection.objects.link(c);c.rotation_euler=main.rotation_euler;c.location=tea.matrix_world@Vector((0,-1.05,2.02))-f*30;s.camera=c;s.render.resolution_x=1150;s.render.resolution_y=850;s.render.filepath=str(W/'final-draft-restaurant.png');bpy.ops.render.render(write_still=True);print('CP14_FINAL_DRAFT_READY',flush=True)
