import bpy,json
from pathlib import Path
out={}
for name in ['child_runner','market_browser','customer_one','courier','musician','CP14_upper_diner_0','paper_bird_0','tea_house']:
 r=bpy.data.objects[name];out[name]={'matrix':[list(x)for x in r.matrix_world],'children':[{'name':o.name,'type':o.type,'loc':list(o.location),'scale':list(o.scale),'rot':list(o.rotation_euler),'dims':list(o.dimensions),'parent':o.parent.name if o.parent else None}for o in r.children_recursive if o.type=='MESH']}
Path('work/runtime-cp17/model-inspection.json').write_text(json.dumps(out,indent=2))
print('INSPECTED')
