import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/art-checkpoint-14';s=bpy.context.scene;reg=json.loads((OUT/'decision-entities.json').read_text());rec=json.loads((OUT/'revision-record.json').read_text())
root=bpy.data.objects['hanging_light_cp05_restaurant_paper_lantern_paper'];root.location.z+=.16
for o in root.children:
 if o.name.startswith('CP14 pendant cord'):o.location.z-=.08;o.scale.z-=.16
 if o.name.startswith('CP14 pendant bracket'):o.location.z-=.16
for i,side in [(0,-1),(1,1)]:
 guest=bpy.data.objects['CP14_upper_diner_'+str(i)]
 for o in guest.children:
  if (1 if o.location.x>0 else -1)!=side:continue
  if o.name.startswith('CP14 diner upper sleeve'):a,b=Vector((side*.18,-.01,.91)),Vector((side*.22,-.06,.78))
  elif o.name.startswith('CP14 diner lower sleeve'):a,b=Vector((side*.22,-.06,.78)),Vector((side*.18,-.12,.73))
  elif o.name.startswith('CP14 diner hand'):o.location=(side*.18,-.12,.73);continue
  else:continue
  o.location=(a+b)*.5;o.scale.z=(b-a).length;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
bpy.context.view_layer.update()
for e in reg['entities']:e['position']=list(bpy.data.objects[e['blender_object']].matrix_world.translation)
rec['final_pose_note']='One arm rests nearer the lap for each diner. The left pendant is raised 0.16 local units, with its cord shortened, to clear the fully pulled chair back.'
exec(compile((ROOT/'work/art-cp13/scene_signature.py').read_text(),'<signature>','exec'));before=json.loads((ROOT/'outputs/art-checkpoint-13/scene-signature.json').read_text());after=json.loads(json.dumps(scene_signature(s)));rec['modified']=[n for n in before['objects']if n not in rec['removed']and before['objects'][n]!=after['objects'].get(n)];rec['added']=sorted(set(after['objects'])-set(before['objects']));(OUT/'decision-entities.json').write_text(json.dumps(reg,indent=2));(OUT/'revision-record.json').write_text(json.dumps(rec,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp14.blend'));print('CP14_POSE_FINAL')
