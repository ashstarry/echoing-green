import bpy,json
from pathlib import Path
R=Path.cwd();reg=json.loads((R/'app/runtime-cp20/public/assets/runtime-registry.json').read_text())
for id in ['resident.kite_child','resident.child_parent','resident.garden_child','resident.cyclist']:
 e=next(e for e in reg['entities']if e['id']==id);r=bpy.data.objects[e['blender_object']];print('ACTOR',id,list(r.matrix_world.to_scale()),[(p['id'],p['blender_object'])for p in e['parts']]);print('MESHES',[(x.name,x.parent.name,list(x.location),list(x.scale))for x in r.children_recursive if x.type=='MESH'])
