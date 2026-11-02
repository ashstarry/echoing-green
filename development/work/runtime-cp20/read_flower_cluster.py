import bpy,json
from pathlib import Path
rows=[]
for o in bpy.context.scene.objects:
 p=o.matrix_world.translation
 if o.name.startswith('CP02 restrained flower bed')and 2.7<p.x<4.2 and -4.5<p.y<-3.3:rows.append({'name':o.name,'position':list(p)})
Path('work/runtime-cp20/flower-cluster-source.json').write_text(json.dumps(rows));print('CLUSTER',len(rows))
