exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
for frame,names in [('station_main',['station_entry_door','CP08 station door panel','CP08 station platform','CP08 ticket window sill.002','CP08 ticket window sill.003']),('street_bicycle',['CP09 cycle main tube.002','CP08 cycle tire.001']),('hill_windwheel',['Wheel hub','Wind pole','hill_windwheel__rotor'])]:
 f=bpy.data.objects[frame].matrix_world.inverted()
 for name in names:
  o=bpy.data.objects[name];v=[f@o.matrix_world@Vector(p) for p in o.bound_box];print(name,'local-origin',list(f@o.matrix_world.translation),'bounds',[[min(p[i]for p in v),max(p[i]for p in v)]for i in range(3)],'parent',o.parent.name if o.parent else None,'matrix_basis',[list(r)for r in o.matrix_basis],flush=True)
