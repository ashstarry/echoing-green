import bpy
from mathutils import Vector
o=bpy.data.objects['CP02 restrained flower bed bloom petal.057'];print('FLOWER',o.name,o.parent.name if o.parent else None,list(o.matrix_world.translation));p=o.parent;print('PARENT',p.name if p else None,list(p.matrix_world.translation)if p else None);print('SIBLINGS',[(x.name,list(x.matrix_world.translation))for x in p.children]if p else [])
