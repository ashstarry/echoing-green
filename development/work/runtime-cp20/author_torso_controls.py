import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path.cwd();A=R/'app/runtime-cp20/public/assets';reg=json.loads((A/'runtime-registry.json').read_text());s=bpy.context.scene
bpy.data.objects['CP02 restrained flower bed leaf.095'].location.y-=.23
for id in ['resident.gardener','resident.assistant_gardener','resident.water_visitor','resident.water_companion','resident.quiet_reader']:
 e=next(e for e in reg['entities']if e['id']==id);root=bpy.data.objects[e['blender_object']];children=list(root.children);ctrl=bpy.data.objects.new(root.name+'__anim_torso',None);s.collection.objects.link(ctrl);ctrl.parent=root;ctrl.location=(0,0,.54);ctrl['decision_part_id']='anim_torso';ctrl['decision_owner']=id;bpy.context.view_layer.update()
 for o in children:
  if o.get('decision_part_id','').startswith(('anim_head','anim_arm'))or o.name.startswith(('Coat body','Coat front fold','Neck')):
   mw=o.matrix_world.copy();o.parent=ctrl;o.matrix_world=mw
 e['parts'].append({'id':'anim_torso','blender_object':ctrl.name,'control':'rigid_hinge','axis':'X'})
reg['parts_count']=sum(len(e['parts'])for e in reg['entities']);(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp20/town-runtime.blend'));print('TORSOS_READY')
