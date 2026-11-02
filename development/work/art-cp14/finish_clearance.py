import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'work/art-cp14';OUT=ROOT/'outputs/art-checkpoint-14';s=bpy.context.scene;tea=bpy.data.objects['tea_house'];rec=json.loads((OUT/'revision-record.json').read_text());reg=json.loads((OUT/'decision-entities.json').read_text())
# Keep a complete roof but give a standing guest appropriate headroom at the front openings.
for o in list(tea.children):
 if o.name=='tea_house roof'or o.name.startswith('CP02 tea dormer'):o.location.z+=.24
 if o.name=='tea_house front lintel':o.location.z+=.24
 if o.name.startswith(('tea_house timber','CP06 upper front timber','CP06 upper exit door frame')):
  o.location.z+=.12;o.scale.z+=.24
 if o.name=='CP06 upper exit header':o.location.z+=.24
 if o.name.startswith('Awning'):o.location.z-=.19
 if o.name.startswith(('tea_house front window jamb','tea_house front window sill'))and o.location.z>2.1:
  rec['removed'].append(o.name);bpy.data.objects.remove(o,do_unlink=True)
room=bpy.data.objects['CP06_upper_dining_layout']
for o in room.children:
 if o.name.startswith(('CP06 upper back wall','CP06 upper west wall','CP06 upper east door jamb wall','CP06 upper front timber')):o.location.z+=.12;o.scale.z+=.24
# Separate the right exit from the structural central post; both guests remain in clear window bays.
for name in ['CP14_upper_diner_1','CP06 dining chair 1','CP14_upper_dining_table_1']:bpy.data.objects[name].location.x+=.50
bpy.context.view_layer.update();local=lambda p:list(tea.matrix_world@Vector(p))
for i,x in enumerate([-1.95,.85]):
 key='seat_to_aisle_'+('left'if i==0 else'right');rec['routes'][key]=[local((x+.15,-1.80,2.255)),local((x+.15,-.84,2.255)),local((x+.15,.20,2.255))];rec['chair_exit_actions'][i]['standing_tea_local']=[x+.15,-1.80,2.255];rec['diner_specs'][i]['tea_local_position']=list(bpy.data.objects['CP14_upper_diner_'+str(i)].location)
 rec['chair_exit_actions'][i]['standing_proxy_height_world']=1.303
rec['headroom_revision']={'roof_and_dormer_lift_local':.24,'world_vertical_change':.24*.86,'full_roof_retained':True,'front_windows_converted_to_open_bays':True,'awning_shift_local':-.19,'reason':'Allow full-height guest standing/turning under the eave and remove overlapping awning tops below the expanded balcony floor.'}
exec(compile((ROOT/'work/art-cp13/scene_signature.py').read_text(),'<signature>','exec'));before=json.loads((ROOT/'outputs/art-checkpoint-13/scene-signature.json').read_text());after=json.loads(json.dumps(scene_signature(s)));rec['modified']=[n for n in before['objects']if n not in rec['removed']and before['objects'][n]!=after['objects'].get(n)];rec['added']=sorted(set(after['objects'])-set(before['objects']));rec['removed']=sorted(set(rec['removed']))
for e in reg['entities']:
 o=bpy.data.objects[e['blender_object']];e['position']=list(o.matrix_world.translation)
 if e['id'].startswith('seat.cp06_dining_chair_'):
  e['actuation_note']='Authoring pullback before rising: tea-house local X -0.20; no motion executor.'
  e['actions'].append({'id':'pull_back','parameters':{'distance_local':{'enum':[.20]}},'implementation':'declared; validate occupied guest movement together'})
 if e['id'].startswith('resident.upper_diner_'):
  i=int(e['id'][-1]);e['anchors']=[{'id':'standing_exit','position':rec['routes']['seat_to_aisle_'+('left'if i==0 else'right')][0]}]
(OUT/'revision-record.json').write_text(json.dumps(rec,indent=2));(OUT/'decision-entities.json').write_text(json.dumps(reg,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(W/'ready.blend'));print('CP14_CLEARANCE_READY',flush=True)
