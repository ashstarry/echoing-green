import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path.cwd();A=R/'app/runtime-cp30/public/assets';reg=json.loads((A/'runtime-registry.json').read_text());seats=['resident.quiet_reader','resident.listener','resident.elder','resident.waiting_passenger','resident.waiting_passenger_2'];meta={}
for e in reg['entities']:
 if e['id']not in seats:continue
 root=bpy.data.objects[e['blender_object']];allchildren=list(root.children_recursive)
 def joint(key,point,parent):
  o=bpy.data.objects.new('CP30_'+root.name+'__'+key,None);bpy.context.scene.collection.objects.link(o);o.matrix_world=root.matrix_world@Matrix.Translation(Vector(point));mw=o.matrix_world.copy();o.parent=parent;o.matrix_world=mw;o['decision_part_id']=key;o['decision_owner']=e['id'];e['parts'].append({'id':key,'blender_object':o.name,'control':'rigid_hinge','axis':'X'});return o
 def attach(o,parent):
  mw=o.matrix_world.copy();o.parent=parent;o.matrix_world=mw
 for side,sgn in [('left',-1),('right',1)]:
  x=sgn*.1;hip=joint('event_hip_'+side,[x,0,.43],root);knee=joint('event_knee_'+side,[x,-.235,.43],hip);ankle=joint('event_ankle_'+side,[x,-.235,.10],knee)
  for o in allchildren:
   if o.type!='MESH':continue
   if not any(k in o.name for k in ['Seated thigh','Seated shin','Shoe']):continue
   local=root.matrix_world.inverted()@o.matrix_world.translation
   if local.x*sgn<0:continue
   attach(o,hip if 'thigh'in o.name else knee if 'shin'in o.name else ankle)
 meta[e['id']]={'hip':.43,'upper':.235,'lower':.33,'ankle':.10,'standingRise':.235,'seatedFootForward':.235}
(A/'seated-rigs.json').write_text(json.dumps(meta,indent=2));reg['parts_count']=sum(len(e['parts'])for e in reg['entities']);(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'outputs/runtime-checkpoint-30/town-cp30.blend'));print('NEW_SEATED_HINGES',len(meta)*6,flush=True)
