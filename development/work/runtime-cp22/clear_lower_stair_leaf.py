import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path.cwd();A=R/'app/runtime-cp22/public/assets';reg=json.loads((A/'runtime-registry.json').read_text());e=next(e for e in reg['entities']if e['id']=='plant.cp07_garden_cluster_066');o=bpy.data.objects[e['blender_object']];before=list(o.matrix_world.translation);o.location+=Vector((-.28,.05,0));bpy.context.view_layer.update();e['position']=list(o.matrix_world.translation);points=[]
for child in o.children_recursive:
 if child.type in ['MESH','CURVE']:points.extend(child.matrix_world@Vector(v)for v in child.bound_box)
bounds=([min(p[k]for p in points)for k in range(3)],[max(p[k]for p in points)for k in range(3)])
nav=json.loads((A/'navigation.json').read_text());removed=[]
for key,i in list(nav['grid'].items()):
 p=nav['nodes'][i]
 if bounds[0][0]-.47<p[0]<bounds[1][0]+.47 and bounds[0][1]-.47<p[1]<bounds[1][1]+.47:
  del nav['grid'][key];removed.append(i)
(A/'navigation.json').write_text(json.dumps(nav,separators=(',',':')));(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));(R/'outputs/runtime-checkpoint-22/stair-leaf-clearance.json').write_text(json.dumps({'entity':e['id'],'before':before,'after':e['position'],'preserved_whole_composition':True,'new_bounds':bounds,'conservatively_reserved_existing_nav_nodes':removed},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp22/town-runtime.blend'));print('LEAF_CLEARANCE',before,e['position'],len(removed))
