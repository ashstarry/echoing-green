import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path.cwd();A=R/'app/runtime-cp19/public/assets';reg=json.loads((A/'runtime-registry.json').read_text());nav=json.loads((A/'navigation.json').read_text());spaces=json.loads((A/'activity-spaces.json').read_text());rows=json.loads((R/'work/runtime-cp19/mobile-starts.json').read_text())
for row in rows:
 e=next(e for e in reg['entities']if e['id']==row['id']);o=bpy.data.objects[e['blender_object']];m=o.matrix_world.copy();m.translation=Vector(row['point']);o.matrix_world=m;bpy.context.view_layer.update();a=next(a for a in nav['actors']if a['id']==row['id']);a['position']=row['point'];a['entry']=[row['node']];a['nearest']=[row['node']];spaces['residents'][row['id']].update({'position':row['point'],'covered':spaces['nodes'][row['node']]['covered'],'umbrellaClear':spaces['nodes'][row['node']]['umbrellaClear']})
for e in reg['entities']:e['position']=list(bpy.data.objects[e['blender_object']].matrix_world.translation)
(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));(A/'navigation.json').write_text(json.dumps(nav,separators=(',',':')));(A/'activity-spaces.json').write_text(json.dumps(spaces,separators=(',',':')));(R/'outputs/runtime-checkpoint-19/mobile-start-adjustments.json').write_text(json.dumps(rows,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp19/town-runtime.blend'));print('MOBILE_STARTS_PLACED')
