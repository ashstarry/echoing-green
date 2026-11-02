import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path.cwd();A=R/'app/runtime-cp22/public/assets';reg=json.loads((A/'runtime-registry.json').read_text());s=bpy.context.scene;sockets=json.loads((A/'actor-sockets.json').read_text());count=0
for e in reg['entities']:
 if e['kind']!='resident' or e['id']in ['resident.cyclist','resident.upper_diner_0','resident.upper_diner_1']:continue
 root=bpy.data.objects[e['blender_object']]
 for side in ['left','right']:
  p=next((p for p in e['parts']if p['id']=='anim_arm_'+side),None)
  if not p:continue
  arm=bpy.data.objects[p['blender_object']];low=next((o for o in arm.children_recursive if o.name.startswith('Lower sleeve')),None);hand=next((o for o in arm.children_recursive if o.name.startswith('Hand')),None)
  if not low or not hand:continue
  # The existing beam's center is half way from the elbow to the hand.
  elbow=low.matrix_world.translation*2-hand.matrix_world.translation
  ctrl=bpy.data.objects.new(root.name+'__anim_elbow_'+side,None);s.collection.objects.link(ctrl);ctrl.matrix_world=root.matrix_world.copy();ctrl.matrix_world.translation=elbow;ctrl.parent=arm;ctrl.matrix_parent_inverse=arm.matrix_world.inverted();bpy.context.view_layer.update()
  for o in [low,hand]:
   mw=o.matrix_world.copy();o.parent=ctrl;o.matrix_parent_inverse=ctrl.matrix_world.inverted();o.matrix_world=mw
  # Existing hand-held things remain associated with the actual hand.
  for o in list(arm.children):
   if o==ctrl:continue
   if o.get('decision_entity_id')in ['book.terrace_reader_book','letter.postman_letter','watering_can.garden_can']:
    mw=o.matrix_world.copy();o.parent=ctrl;o.matrix_parent_inverse=ctrl.matrix_world.inverted();o.matrix_world=mw
  part='anim_elbow_'+side;ctrl['decision_part_id']=part;ctrl['decision_owner']=e['id'];e['parts'].append({'id':part,'blender_object':ctrl.name,'control':'rigid_hinge','axis':'X'});count+=1
  sockets[e['id']]['hands'][side]['part']='anim_elbow_'+side;sockets[e['id']]['hands'][side]['part_local']=list(ctrl.matrix_world.inverted()@hand.matrix_world.translation)
reg['parts_count']=sum(len(e['parts'])for e in reg['entities']);(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));(A/'actor-sockets.json').write_text(json.dumps(sockets,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp22/town-runtime.blend'));print('ELBOWS',count,'PARTS',reg['parts_count'])
