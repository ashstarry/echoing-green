import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path.cwd();scene=bpy.context.scene;center=Vector((11.72,1.66,0));selected=[]
for o in scene.objects:
 if o.type not in ['MESH','CURVE']or not o.name.startswith('CP02 restrained flower bed'):continue
 points=[o.matrix_world@Vector(v)for v in o.bound_box];c=sum(points,Vector())/8
 if math.hypot(c.x-center.x,c.y-center.y)<.67:selected.append(o)
assert selected,'No complete flower group found';rows=[]
for o in selected:
 before=o.matrix_world.copy();after=before.copy();after.translation+=Vector((-.22,-.04,0));o.matrix_world=after;rows.append({'name':o.name,'parent':o.parent.name if o.parent else None,'before':list(before.translation),'after':list(after.translation)})
bpy.context.view_layer.update();(R/'outputs/runtime-checkpoint-22/final-rail-flower-adjustment.json').write_text(json.dumps({'translation':[-.22,-.04,0],'objects':rows,'count_preserved':len(rows),'source':'Complete local legacy flower composition selected by shared prefix and spatial cluster, with all petals/leaves retained.'},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp22/town-runtime.blend'));print('MOVED_FLOWER_COMPONENTS',len(rows),[o.name for o in selected])
