import bpy,json
from pathlib import Path
R=Path.cwd();r=json.loads((R/'app/runtime-cp20/public/assets/runtime-registry.json').read_text());print('KITE',next(e for e in r['entities']if e['id']=='kite.plaza_kite'))
for o in bpy.context.scene.objects:
 if 'kite' in o.name.lower()and not('child' in o.name.lower()):print(o.name,'parent',o.parent.name if o.parent else None,'pos',list(o.matrix_world.translation),'dims',list(o.dimensions),dict(o.items()))
