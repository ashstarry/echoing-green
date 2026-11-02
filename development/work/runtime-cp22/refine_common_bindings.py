import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path.cwd()
def refine(model,A):
 reg=json.loads((A/'runtime-registry.json').read_text());by={e['id']:e for e in reg['entities']};scene=bpy.context.scene
 e=by['plant.garden_planter_00'];plant=bpy.data.objects[e['blender_object']];before=list(plant.matrix_world.translation);plant.location+=Vector((.18,-.30,0));bpy.context.view_layer.update();e['position']=list(plant.matrix_world.translation)
 # Keep each complete arm together around its actual shoulder, including baked grip meshes.
 root=bpy.data.objects['cyclist'];inv=root.matrix_world.inverted();allmesh=[o for o in root.children_recursive if o.type=='MESH'];groups={side:{}for side in ['left','right']}
 for o in allmesh:
  if not any(s in o.name for s in ['CP09 cyclist forearm','CP09 cyclist upper sleeve','CP09 open grip hand']):continue
  points=[o.matrix_world@Vector(v)for v in o.bound_box];center=sum(points,Vector())/8;side='left'if(inv@center).x<0 else'right';kind='hand'if'grip'in o.name else'lower'if'forearm'in o.name else'upper';groups[side][kind]=(o,center)
 saved={o:o.matrix_world.copy()for g in groups.values()for o,c in g.values()};gaps={}
 for side,g in groups.items():
  hand=g['hand'][1];elbow=g['lower'][1]*2-hand;shoulder=g['upper'][1]*2-elbow;ctrl=bpy.data.objects['cyclist__anim_arm_'+side];m=root.matrix_world.copy();m.translation=shoulder;ctrl.matrix_world=m;bpy.context.view_layer.update()
  for o,c in g.values():o.parent=ctrl;o.matrix_parent_inverse=ctrl.matrix_world.inverted();o.matrix_world=saved[o]
  gaps[side]={'shoulder':list(shoulder),'hand':list(hand),'members':[o.name for o,c in g.values()]}
 (A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(model));return {'plant_before':before,'plant_after':e['position'],'cyclist_bindings':gaps}
main=refine(R/'work/runtime-cp22/town-runtime.blend',R/'app/runtime-cp22/public/assets')
A=R/'app/runtime-cp22/public/assets';nav=json.loads((A/'navigation.json').read_text());removed=[]
for key,i in list(nav['grid'].items()):
 p=nav['nodes'][i]
 if 2.5823<p[0]<4.5519 and 2.3111<p[1]<4.1976:del nav['grid'][key];removed.append(i)
assert not any(a['entry'] and a['entry'][-1]in removed for a in nav['actors']), 'Would block an actor entry'
(A/'navigation.json').write_text(json.dumps(nav,separators=(',',':')))
branch=R/'work/runtime-cp22/boarding/town-boarding.blend';bpy.ops.wm.open_mainfile(filepath=str(branch));other=refine(branch,R/'work/runtime-cp22/boarding/assets');(R/'outputs/runtime-checkpoint-22/common-binding-refinement.json').write_text(json.dumps({'main':main,'candidate':other,'new_reserved_nav_nodes':removed},indent=2));print('COMMON_BINDINGS_READY',len(removed))
