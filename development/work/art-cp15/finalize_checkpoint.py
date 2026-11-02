import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/art-checkpoint-15';s=bpy.context.scene;reg=json.loads((OUT/'decision-entities.json').read_text());rec=json.loads((OUT/'revision-record.json').read_text());col=bpy.data.collections['02_Teahouse_Market'];cube=bpy.data.meshes['Shared cube'];hem=bpy.data.materials['CP15 warm paper hem']
def beam(name,parent,a,b,w):
 a,b=Vector(a),Vector(b);o=bpy.data.objects.new(name,cube);col.objects.link(o);o.parent=parent;o.location=(a+b)*.5;o.scale=(w,w,(b-a).length);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
 for sl in o.material_slots:sl.link='OBJECT';sl.material=hem
 return o
# Close the tiny attachment gaps in the hanging strings.
o=bpy.data.objects['CP15 chime thread'];o.location.z=-.0225;o.scale.z=.045
beam('CP15 chime upper connector',bpy.data.objects['CP15_restaurant_wind_chime__pendulum'],(0,0,0),(0,0,-.02),.004)
o=bpy.data.objects['CP15 crane mobile suspension'];o.location.z=-.0425;o.scale.z=.085
beam('CP15 crane mobile crossbar',bpy.data.objects['CP15_restaurant_crane_mobile__mobile'],(-.065,0,-.04),(.065,0,-.04),.007)
bpy.context.view_layer.update()
for e in reg['entities']:
 e['position']=list(bpy.data.objects[e['blender_object']].matrix_world.translation)
 if e['id'].startswith('seat.cp06_dining_chair_'):
  for a in e['actions']:a['exposed_to_decision']=False;a['internal_transition_only']=True
 for p in e['parts']:p['local_matrix']=[list(r)for r in bpy.data.objects[p['blender_object']].matrix_local]
reg['interaction_contract_scope']='Two upper diners only; other town entities retain their broader authoring action contracts.'
(OUT/'decision-entities.json').write_text(json.dumps(reg,indent=2));exec(compile((ROOT/'work/art-cp14/scene_signature.py').read_text(),'<signature>','exec'));before=json.loads((ROOT/'outputs/art-checkpoint-14/scene-signature.json').read_text());after=json.loads(json.dumps(scene_signature(s)));rec['added']=sorted(set(after['objects'])-set(before['objects']));rec['modified']=[n for n in before['objects']if before['objects'][n]!=after['objects'].get(n)];(OUT/'revision-record.json').write_text(json.dumps(rec,indent=2))
s['checkpoint']='CP15 | striped awnings, upper noren and two ornaments';s['review_status']='Awaiting user art review; upper diner behavior declared as two endpoints; no animation/runtime';s.cycles.samples=80;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=5;s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100;s.render.filepath=str(OUT/'01-overview.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp15.blend'));print('CP15_MASTER_SAVED')
