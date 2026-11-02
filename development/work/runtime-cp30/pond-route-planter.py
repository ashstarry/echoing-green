import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path.cwd();A=R/'app/runtime-cp30/public/assets';o=bpy.data.objects['garden_planter_08'];old=o.matrix_world.translation.copy();m=o.matrix_world.copy();m.translation.x=5.05;m.translation.y=-3.0;o.matrix_world=m
reg=json.loads((A/'runtime-registry.json').read_text())
for e in reg['entities']:
 if e['blender_object']==o.name:e['position']=list(o.matrix_world.translation)
(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));(R/'outputs/runtime-checkpoint-30/pond-planter-move.json').write_text(json.dumps({'object':o.name,'before':list(old),'after':list(o.matrix_world.translation)},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'outputs/runtime-checkpoint-30/town-cp30.blend'));print('PLANTER_MOVED',list(old),list(o.matrix_world.translation))
