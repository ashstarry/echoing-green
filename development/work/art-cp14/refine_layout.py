import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'work/art-cp14';OUT=ROOT/'outputs/art-checkpoint-14';s=bpy.context.scene;tea=bpy.data.objects['tea_house'];rec=json.loads((OUT/'revision-record.json').read_text());reg=json.loads((OUT/'decision-entities.json').read_text())
for o in list(s.objects):
 if o.name.startswith('CP05 restaurant paper lantern '):rec['removed'].append(o.name);bpy.data.objects.remove(o,do_unlink=True)
for i in range(2):
 for name in ['CP14_upper_diner_'+str(i),'CP06 dining chair '+str(i),'CP14_upper_dining_table_'+str(i)]:bpy.data.objects[name].location.y=-1.80
 guest=bpy.data.objects['CP14_upper_diner_'+str(i)];guest['entity_id']=guest.name;rec['diner_specs'][i]['tea_local_position']=list(guest.location)
for o in s.objects:
 if o.type=='LIGHT'and o.parent and o.parent.name.startswith('hanging_light_cp05_restaurant'):
  i=next(i for i,r in enumerate(rec['lamp_recomposition'])if r['id']==o.parent.get('decision_entity_id'))
  o.data.energy=1.8 if i<5 else .35;o.data.shadow_soft_size=.23 if i<5 else .38
p=bpy.data.materials['CP14 ribbed lantern warm washi'].node_tree.nodes['Principled BSDF'];p.inputs['Emission Strength'].default_value=.75;p.inputs['Emission Color'].default_value=(1,.29,.03,1)
bpy.context.view_layer.update();inv=tea.matrix_world.inverted();info=[]
for o in tea.children:
 if o.name.startswith('Awning'):
  v=[inv@o.matrix_world@Vector(c)for c in o.bound_box];info.append({'name':o.name,'bounds':[[min(p[j]for p in v),max(p[j]for p in v)]for j in range(3)]})
(W/'awning-bounds.json').write_text(json.dumps(info,indent=2))
# Entry/exit anchors are a separate action-space contract, not the seated pose itself.
local=lambda p:list(tea.matrix_world@Vector(p));rec['chair_exit_actions']=[]
for i,x in enumerate([-1.95,.35]):
 key='seat_to_aisle_'+('left'if i==0 else'right');rec['routes'][key]=[local((x+.20,-1.80,2.255)),local((x+.20,-.84,2.255)),local((x+.20,.20,2.255))]
 rec['chair_exit_actions'].append({'actor':'CP14_upper_diner_'+str(i),'chair':'CP06 dining chair '+str(i),'chair_pullback_tea_local':[-.20,0,0],'standing_tea_local':[x+.20,-1.80,2.255],'note':'Chair and seated actor first pull back; stand ahead of the seat and exit rearward. Key placements need verification; transitions/animation not implemented.'})
for e in reg['entities']:e['position']=list(bpy.data.objects[e['blender_object']].matrix_world.translation)
(OUT/'decision-entities.json').write_text(json.dumps(reg,indent=2));(OUT/'revision-record.json').write_text(json.dumps(rec,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(W/'refined.blend'));print('CP14_REFINED_LAYOUT')
