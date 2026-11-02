import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path.cwd();reg=json.loads((R/'app/runtime-cp22/public/assets/runtime-registry.json').read_text());out={}
for e in reg['entities']:
 if not e['id'].startswith('resident.upper_diner_'):continue
 root=bpy.data.objects[e['blender_object']];inv=root.matrix_world.inverted();row=[]
 for o in root.children_recursive:
  if o.type=='MESH' and any(t in o.name for t in ['sleeve','hand','Head','eye','hair']):
   row.append({'name':o.name,'part':o.parent.get('decision_part_id'),'matrix':[list(x)for x in inv@o.matrix_world],'center':list(inv@o.matrix_world.translation)})
 out[e['id']]=row
(R/'work/runtime-cp22/diner-components.json').write_text(json.dumps(out,indent=2));print(json.dumps({id:[{'name':r['name'],'part':r['part'],'center':r['center']}for r in rows]for id,rows in out.items()},indent=2))
