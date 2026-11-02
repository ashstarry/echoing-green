import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path.cwd();o=bpy.data.objects['CP02 restrained flower bed leaf.012'];m=o.matrix_world.copy();m.translation+=Vector((.26,.08,0));o.matrix_world=m;bpy.ops.wm.save_as_mainfile(filepath=str(r/'work/runtime-cp18/town-runtime.blend'));(r/'outputs/runtime-checkpoint-18/last-rail-leaf-adjustment.json').write_text(json.dumps({'object':o.name,'translation':[.26,.08,0],'purpose':'Clear actual steered wheel envelope; retain the leaf component.'},indent=2))
