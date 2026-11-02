import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path.cwd();A=R/'app/runtime-cp30/public/assets';moved=[]
placements={'CP07 garden cluster 066':[8.55,3.0],'CP07 garden cluster 1009':[8.5,3.65],'garden_planter_00':[8.85,3.25],'garden_planter_01':[8.95,3.8],'street_lantern_07':[8.15,3.25],'street_lantern_05':[4.70,2.05]}
for name,xy in placements.items():
 o=bpy.data.objects[name];before=o.matrix_world.translation.copy();m=o.matrix_world.copy();m.translation.x=xy[0];m.translation.y=xy[1];o.matrix_world=m;moved.append({'object':name,'before':list(before),'after':list(m.translation)})
# The small loose legacy pot is moved as a whole, with all its matching leaves.
for o in bpy.context.scene.objects:
 if o.name.startswith('CP02 street planter 10 '):m=o.matrix_world.copy();m.translation+=Vector((4.1,.9,0));o.matrix_world=m
reg=json.loads((A/'runtime-registry.json').read_text())
for e in reg['entities']:
 o=bpy.data.objects.get(e['blender_object'])
 if o:e['position']=list(o.matrix_world.translation)
(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));(R/'outputs/runtime-checkpoint-30/corridor-decor-moves.json').write_text(json.dumps(moved,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'outputs/runtime-checkpoint-30/town-cp30.blend'));print('CORRIDORS_OPENED',len(moved))
