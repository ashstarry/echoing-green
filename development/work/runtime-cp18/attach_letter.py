import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path.cwd();A=R/'app/runtime-cp18/public/assets';reg=json.loads((A/'runtime-registry.json').read_text());r=bpy.data.objects['postman'];letter=bpy.data.objects['postman_letter'];point=letter.matrix_world.translation;hands=[o for o in r.children_recursive if o.type=='MESH'and o.name.startswith('Hand')];hand=min(hands,key=lambda o:(o.matrix_world.translation-point).length);parent=hand.parent
while parent and not parent.get('decision_part_id'):parent=parent.parent
mw=letter.matrix_world.copy();letter.parent=parent;letter.matrix_world=mw;row=next(e for e in reg['entities']if e['id']=='letter.postman_letter');row['attachment_status']='Attached to carrying arm control; follows hand during gait';row['socket_part']=parent.get('decision_part_id');(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp18/town-runtime.blend'));print('LETTER_SOCKET',parent.name)
