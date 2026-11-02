exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
p=bpy.data.objects['CP07 district fence post.027'];center=p.matrix_world.translation
for o in s.objects:
 if o.type=='MESH' and(o.matrix_world.translation-center).length<.12:print('POST_NEAR',o.name,list(o.matrix_world.translation),list(o.dimensions),o.parent.name if o.parent else None,flush=True)
for n in ['CP05 landing to residence link','CP05 residence side walk']:
 o=bpy.data.objects[n];vs=[o.matrix_world@v.co for v in o.data.vertices];print('DECK',n,[[min(p[i]for p in vs),max(p[i]for p in vs)]for i in range(3)],flush=True)
