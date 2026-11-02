import bpy,json
from pathlib import Path
R=Path.cwd();A=R/'app/runtime-cp18/public/assets';act=json.loads((A/'motion-activities.json').read_text());reg=json.loads((A/'runtime-registry.json').read_text());e=next(e for e in reg['entities']if e['id']=='fish.pond_fish_1');o=bpy.data.objects[e['blender_object']];m=o.matrix_world.copy();m.translation.z-=.035;o.matrix_world=m
for p in act['clips'][e['id']]['samples']:p[2]-=.035
(A/'motion-activities.json').write_text(json.dumps(act,separators=(',',':')));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp18/town-runtime.blend'));print('FISH_DEPTH',o.matrix_world.translation.z)
