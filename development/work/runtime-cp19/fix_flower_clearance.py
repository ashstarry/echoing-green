import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path.cwd();center=Vector((3.395785,-3.87670,.88795));rows=[]
# Move the complete small legacy flower composition together, clear of the bicycle's rear tyre.
for o in bpy.context.scene.objects:
 if o.name.startswith('CP02 restrained flower bed') and (o.matrix_world.translation-center).length<.48:
  old=list(o.matrix_world.translation);o.location.y-=.18;rows.append({'name':o.name,'before':old,'after':list(o.matrix_world.translation)})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp19/town-runtime.blend'))
(R/'outputs/runtime-checkpoint-19/flower-clearance-adjustment.json').write_text(json.dumps(rows,indent=2));print('SHIFTED',len(rows),[r['name']for r in rows])
