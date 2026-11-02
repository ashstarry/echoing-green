import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path.cwd();A=R/'app/runtime-cp22/public/assets';reg=json.loads((A/'runtime-registry.json').read_text());by={e['id']:e for e in reg['entities']};scene=bpy.context.scene
for i in range(2):
 table=bpy.data.objects['CP14_upper_dining_table_'+str(i)];sign=1 if i==0 else-1
 for kind,p in [('cup',(-.25,sign*.20,.835)),('food',(-.24,sign*.05,.835))]:
  e=by[f'{kind}.upper_table_{i}'];root=bpy.data.objects[e['blender_object']];m=root.matrix_world.copy();m.translation=table.matrix_world@Vector(p);root.matrix_world=m;e['position']=list(m.translation)
  if kind=='food':
   me=bpy.data.meshes.new('CP22 folded snack paper');me.from_pydata([(-.065,-.06,0),(.065,-.06,0),(.065,.06,0),(-.065,.06,0)],[],[(0,1,2,3)]);me.materials.append(bpy.data.materials['Washi | warm ivory']);o=bpy.data.objects.new('CP22 snack paper wrapper',me);scene.collection.objects.link(o);o.parent=root;o.location.z=.001
(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp22/town-runtime.blend'));print('TABLE_REACH_REFINED')
