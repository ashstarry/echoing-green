import bpy,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-08';s=bpy.context.scene;reg=json.loads((OUT/'decision-entities.json').read_text());changed=[]
for e in reg['entities']:
 owner=bpy.data.objects[e['blender_object']]
 for row in e['parts']:
  p=bpy.data.objects[row['blender_object']]
  if p.get('control_kind')!='rotation':continue
  saved={o.name:o.matrix_world.copy() for o in p.children};factors={o.name:p.matrix_world@o.matrix_parent_inverse for o in p.children};localpivot=owner.matrix_world.inverted()@p.matrix_world.translation;p.parent=owner;p.matrix_parent_inverse=Matrix.Identity(4);p.matrix_basis=Matrix.Translation(localpivot);bpy.context.view_layer.update()
  for name,factor in factors.items():bpy.data.objects[name].matrix_parent_inverse=p.matrix_world.inverted()@factor
  bpy.context.view_layer.update();err=max((max(abs(o.matrix_world[i][j]-saved[o.name][i][j]) for i in range(4) for j in range(4)) for o in p.children),default=0);assert err<1e-5,(p.name,err);row['local_matrix']=[list(r) for r in p.matrix_local];row['axis_space']='owning entity local coordinates';changed.append({'part':p.name,'max_world_child_matrix_change':err})
(OUT/'decision-entities.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));rec=json.loads((OUT/'revision-record.json').read_text());rec['control_axis_alignment']={'parts':changed,'render_geometry_unchanged_within':1e-5};(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp08.blend'));print('ALIGNED_CONTROL_AXES',len(changed))
