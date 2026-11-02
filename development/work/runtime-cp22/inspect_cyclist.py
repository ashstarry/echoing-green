import bpy,json
from pathlib import Path
R=Path.cwd();r=bpy.data.objects['cyclist'];print('ROOT',list(r.matrix_world.translation),list(r.matrix_world.to_euler()))
for o in r.children_recursive:
 if o.type=='MESH'and any(t in o.name.lower()for t in ['arm','sleeve','hand']):print(o.name,'PARENT',o.parent.name,'CENTER',list(o.matrix_world.translation))
