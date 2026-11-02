import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-07';s=bpy.context.scene
# A low decorative leaf overhung the first stair tread. Move its entire clump
# outward, preserving the established stairs and the intended walking surface.
o=bpy.data.objects.get('CP07 broad ground leaf.268');root=o.parent
stair=bpy.data.objects['CP05_lower_stair'];delta=stair.matrix_world.to_quaternion()@Vector((.42,0,0));root.location+=delta
bpy.context.view_layer.update();r=json.loads((OUT/'revision-record.json').read_text());r['final_clearance_fix']={'cluster':root.name,'delta':list(delta),'reason':'clear the right side of the first lower stair tread'};(OUT/'revision-record.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp07.blend'))
