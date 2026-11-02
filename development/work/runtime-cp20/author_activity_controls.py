import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path.cwd();A=R/'app/runtime-cp20/public/assets';reg=json.loads((A/'runtime-registry.json').read_text());s=bpy.context.scene
# Refit a single folded leaf tip away from the longer bicycle sweep; retain the composition.
o=bpy.data.objects['CP02 restrained flower bed leaf.096'];o.location.y-=.20
# The raised kite hand and forearm now belong to the same real shoulder control as the sleeve.
arm=bpy.data.objects['kite_child__anim_arm_left']
for name in ['CP09 kite holding hand','CP09 kite raised forearm']:
 o=bpy.data.objects[name];mw=o.matrix_world.copy();o.parent=arm;o.matrix_world=mw
# Dedicated foot-down controls. Normalize nothing in the visible meshes; preserve the bind pose.
e=next(e for e in reg['entities']if e['id']=='resident.cyclist');root=bpy.data.objects[e['blender_object']];inv=root.matrix_world.inverted();C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)));CI=C.inverted();out={}
def limb(a,b,w):
 a,b=Vector(a),Vector(b);return Matrix.Translation((a+b)*.5)@(b-a).to_track_quat('Z','Y').to_matrix().to_4x4()@Matrix.Diagonal((w,w,(b-a).length,1))
for name,key in [('CP09 cyclist thigh.001','stop_thigh'),('CP09 cyclist shin.001','stop_shin'),('CP09 cyclist shoe.001','stop_shoe')]:
 o=bpy.data.objects[name];old=inv@o.matrix_world;target=old.copy();hip=(.11,.02,.46);knee=(.36,-.24,.08);ankle=(.41,-.08,-.385)
 if key=='stop_thigh':target=limb(hip,knee,.062)
 elif key=='stop_shin':target=limb(knee,ankle,.049)
 else:target.translation=Vector((.41,-.10,-.385))
 ctrl=bpy.data.objects.new('cyclist__'+key,None);s.collection.objects.link(ctrl);ctrl.parent=root;ctrl.matrix_basis=Matrix.Identity(4);ctrl['decision_part_id']=key;ctrl['decision_owner']=e['id'];bpy.context.view_layer.update();mw=o.matrix_world.copy();o.parent=ctrl;o.matrix_world=mw;e['parts'].append({'id':key,'blender_object':ctrl.name,'control':'affine_pose_channel','axis':None});dm=C@(target@old.inverted())@CI;out[key]=[dm[r][col]for col in range(4)for r in range(4)]
(A/'cycle-stop-pose.json').write_text(json.dumps(out));reg['parts_count']=sum(len(e['parts'])for e in reg['entities']);(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp20/town-runtime.blend'));print('ACTIVITY_CONTROLS_READY')
