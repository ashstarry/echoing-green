import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path.cwd();A=R/'app/runtime-cp20/public/assets';nav=json.loads((A/'navigation.json').read_text());reg=json.loads((A/'runtime-registry.json').read_text());space=json.loads((A/'activity-spaces.json').read_text());rows=[]
for id,p in [('resident.garden_child',(3.84,.24)),('resident.kite_child',(2.08,-.56)),('resident.child_parent',(3.2,-1.36))]:
 a=next(a for a in nav['actors']if a['id']==id);e=next(e for e in reg['entities']if e['id']==id);o=bpy.data.objects[e['blender_object']];old=o.matrix_world.translation.copy();n=min(range(len(nav['nodes'])),key=lambda i:(nav['nodes'][i][0]-p[0])**2+(nav['nodes'][i][1]-p[1])**2);q=nav['nodes'][n];pos=Vector((q[0],q[1],q[2]-.02*a['scale'][2]+.006));o.matrix_world.translation=pos;a['position']=list(pos);a['entry']=[n];a['nearest']=[n];e['position']=list(pos);space['residents'][id]['position']=list(pos)
 if id=='resident.kite_child':bpy.data.objects['plaza_kite'].location+=pos-old
 rows.append({'id':id,'before':list(old),'after':list(pos),'distance':(pos-old).length})
bpy.context.view_layer.update()
for e in reg['entities']:e['position']=list(bpy.data.objects[e['blender_object']].matrix_world.translation)
for name,data in [('navigation.json',nav),('runtime-registry.json',reg),('activity-spaces.json',space)]:(A/name).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
(R/'outputs/runtime-checkpoint-20/family-start-spacing.json').write_text(json.dumps(rows,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp20/town-runtime.blend'));print(rows)
