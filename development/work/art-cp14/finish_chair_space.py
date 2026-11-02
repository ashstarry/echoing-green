import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/art-checkpoint-14';s=bpy.context.scene;tea=bpy.data.objects['tea_house'];rec=json.loads((OUT/'revision-record.json').read_text());reg=json.loads((OUT/'decision-entities.json').read_text());col=bpy.data.collections['02_Teahouse_Market']
for o in tea.children:
 if o.name.startswith(('CP05 balcony flower','CP05 balcony foliage')):o.location.y-=.23
for x in [-2.29,2.29]:
 for a,b in [((x,-2.16,2.86),(x,-2.16,2.31)),((x,-2.16,2.31),(x,-2.29,2.31))]:
  a,b=Vector(a),Vector(b);o=bpy.data.objects.new('CP14 balcony planter bracket',bpy.data.meshes['Shared cube']);col.objects.link(o);o.parent=tea;o.location=(a+b)*.5;o.scale=(.025,.025,(b-a).length);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
  for slot in o.material_slots:slot.link='OBJECT';slot.material=bpy.data.materials['Cedar frame']
for action in rec['chair_exit_actions']:action['chair_pullback_tea_local']=[-.30,0,0]
for e in reg['entities']:
 if e['id'].startswith('seat.cp06_dining_chair_'):
  e['actuation_note']='Authoring pullback before rising: tea-house local X -0.30; no motion executor.'
  for a in e['actions']:
   if a['id']=='pull_back':a['parameters']['distance_local']['enum']=[.30]
rec['chair_space_refinement']='End planters moved outside the railing with brackets; chair pullback increased to 0.30 tea-local X so the actual standing turn clears seat edges.'
bpy.context.view_layer.update();exec(compile((ROOT/'work/art-cp13/scene_signature.py').read_text(),'<signature>','exec'));before=json.loads((ROOT/'outputs/art-checkpoint-13/scene-signature.json').read_text());after=json.loads(json.dumps(scene_signature(s)));rec['modified']=[n for n in before['objects']if n not in rec['removed']and before['objects'][n]!=after['objects'].get(n)];rec['added']=sorted(set(after['objects'])-set(before['objects']));(OUT/'revision-record.json').write_text(json.dumps(rec,indent=2));(OUT/'decision-entities.json').write_text(json.dumps(reg,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp14.blend'));print('CP14_CHAIR_SPACE_FINAL')
