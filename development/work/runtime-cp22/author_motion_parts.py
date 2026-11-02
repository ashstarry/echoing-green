import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path.cwd();A=R/'app/runtime-cp22/public/assets';reg=json.loads((A/'runtime-registry.json').read_text());scene=bpy.context.scene
by={e['id']:e for e in reg['entities']}
def pivot(id,part,point,parent=None):
 e=by[id];root=bpy.data.objects[e['blender_object']];o=bpy.data.objects.new(root.name+'__'+part,None);scene.collection.objects.link(o);o.matrix_world=Matrix.Translation(Vector(point));o.parent=parent or root;o.matrix_parent_inverse=o.parent.matrix_world.inverted();o['decision_part_id']=part;o['decision_owner']=id;e['parts'].append({'id':part,'blender_object':o.name,'control':'rigid_hinge','axis':None});return o
def attach(o,parent):
 mw=o.matrix_world.copy();o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted();o.matrix_world=mw
# Real page rotation around the book spine; bind rest state remains visually unchanged.
e=by['book.terrace_reader_book'];book=bpy.data.objects[e['blender_object']];spine=book.matrix_world.translation.copy();spine.z+=.031
page=bpy.data.objects['CP19 book folded pages.001'];pg=pivot(e['id'],'turn_page',spine);attach(page,pg)
# A separately folded leaf is driven as part of the real book, not a screen overlay.
# The book follows the left supporting hand, preserving the current world pose.
arm=bpy.data.objects['quiet_reader__anim_arm_left'];attach(book,arm);e['socket_part']='anim_arm_left';e['parent_entity']='resident.quiet_reader'
# The umbrella's paper canopy folds along its vertical pole while the pole remains intact.
e=by['umbrella.carried_umbrella'];root=bpy.data.objects[e['blender_object']];fold=pivot(e['id'],'fold_canopy',root.matrix_world.translation);attach(bpy.data.objects['CP02 paper umbrella'],fold)
# The parked bicycle gains independent wheel boundaries; no magic motion is scheduled by default.
e=by['bicycle.cp07_parked_bicycle'];root=bpy.data.objects[e['blender_object']];centers=[]
for side,tire_name in enumerate(['CP07 bicycle tire','CP07 bicycle tire.001']):
 tire=bpy.data.objects[tire_name];points=[tire.matrix_world@Vector(v)for v in tire.bound_box];c=sum(points,Vector())/8;centers.append(c);wheel=pivot(e['id'],'wheel_'+str(side),c)
 for o in [x for x in root.children_recursive if x.type in ['MESH','CURVE'] and ('bicycle tire'in x.name or 'bicycle spoke'in x.name)]:
  if o==tire or ('spoke'in o.name and (o.matrix_world.translation-c).length<.40):attach(o,wheel)
# Every seated resident's existing shoes can tap independently (actual joint, no body disappearance).
for e in reg['entities']:
 if e['kind']!='resident' or any(p['id']=='anim_knee_left'for p in e['parts']) or 'upper_diner'in e['id'] or e['id']=='resident.cyclist':continue
 root=bpy.data.objects[e['blender_object']]
 shoes=sorted([o for o in root.children_recursive if o.name.startswith('Shoe')],key=lambda o:(root.matrix_world.inverted()@o.matrix_world.translation).x)
 for side,shoe in zip(['left','right'],shoes):
  c=shoe.matrix_world.translation.copy();c.z+=.05;part=pivot(e['id'],'tap_foot_'+side,c);attach(shoe,part)
# Record actual body-local hand tips for attached props and contact tests.
scene.view_layers.update() if hasattr(scene.view_layers,'update') else None
bpy.context.view_layer.update();sockets={}
for e in reg['entities']:
 if e['kind']!='resident':continue
 root=bpy.data.objects[e['blender_object']];row={'origin':list(root.matrix_world.translation),'yaw':root.matrix_world.to_euler().z,'scale':list(root.matrix_world.to_scale()),'hands':{}}
 for side in ['left','right']:
  p=next((p for p in e['parts']if p['id']=='anim_arm_'+side),None)
  if not p:continue
  arm=bpy.data.objects[p['blender_object']];hands=[o for o in arm.children_recursive if 'hand'in o.name.lower()]
  if hands:
   h=hands[0].matrix_world.translation;row['hands'][side]={'part_local':list(arm.matrix_world.inverted()@h),'root_local':list(root.matrix_world.inverted()@h),'world':list(h)}
 sockets[e['id']]=row
stair={}
for name in ['CP05_lower_stair','CP05_upper_stair','CP05_middle_landing']:
 o=bpy.data.objects[name];row={'matrix':[list(x)for x in o.matrix_world],'position':list(o.matrix_world.translation),'treads':[]}
 for child in o.children_recursive:
  if 'tread'in child.name or 'landing cap'in child.name or 'top landing'in child.name or 'bottom landing'in child.name:
   q=[child.matrix_world@Vector(v)for v in child.bound_box];row['treads'].append({'name':child.name,'center':list(sum(q,Vector())/8),'top':max(p.z for p in q)})
 stair[name]=row
(A/'actor-sockets.json').write_text(json.dumps(sockets,indent=2));(R/'work/runtime-cp22/stair-surfaces.json').write_text(json.dumps(stair,indent=2));reg['parts_count']=sum(len(e['parts'])for e in reg['entities']);(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp22/town-runtime.blend'));print('MOTION_PARTS_READY',reg['parts_count'])
