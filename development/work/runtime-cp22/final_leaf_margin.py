import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path.cwd()
def run(model,A):
 reg=json.loads((A/'runtime-registry.json').read_text());e=next(e for e in reg['entities']if e['id']=='plant.cp07_garden_cluster_066');o=bpy.data.objects[e['blender_object']];before=list(o.matrix_world.translation);o.location.x-=.12;bpy.context.view_layer.update();e['position']=list(o.matrix_world.translation);points=[p.matrix_world@Vector(v)for p in o.children_recursive if p.type in ['MESH','CURVE']for v in p.bound_box];bounds=([min(v[k]for v in points)for k in range(3)],[max(v[k]for v in points)for k in range(3)]);(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(model));return {'before':before,'after':e['position'],'bounds':bounds}
a=run(R/'work/runtime-cp22/town-runtime.blend',R/'app/runtime-cp22/public/assets');A=R/'app/runtime-cp22/public/assets';nav=json.loads((A/'navigation.json').read_text());removed=[]
for key,i in list(nav['grid'].items()):
 p=nav['nodes'][i]
 if a['bounds'][0][0]-.47<p[0]<a['bounds'][1][0]+.47 and a['bounds'][0][1]-.47<p[1]<a['bounds'][1][1]+.47:del nav['grid'][key];removed.append(i)
assert not any(a['entry']and a['entry'][-1]in removed for a in nav['actors']);(A/'navigation.json').write_text(json.dumps(nav,separators=(',',':')))
b=R/'work/runtime-cp22/boarding/town-boarding.blend';bpy.ops.wm.open_mainfile(filepath=str(b));other=run(b,R/'work/runtime-cp22/boarding/assets');(R/'outputs/runtime-checkpoint-22/final-leaf-margin.json').write_text(json.dumps({'main':a,'boarding':other,'new_reserved_nodes':removed},indent=2));print('LEAF_MARGIN_DONE',a['after'],other['after'])
