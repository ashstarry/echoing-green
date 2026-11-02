exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
dg=bpy.context.evaluated_depsgraph_get();p=Vector((4.27,5.84,1.45))
for o in s.objects:
 if o.type!='MESH' or o.hide_render or any(c.hide_render or c.name.startswith('12_') for c in o.users_collection):continue
 bb=[o.matrix_world@Vector(v)for v in o.bound_box]
 if not(min(q.x for q in bb)<p.x<max(q.x for q in bb)and min(q.y for q in bb)<p.y<max(q.y for q in bb)):continue
 ev=o.evaluated_get(dg);inv=ev.matrix_world.inverted();h,loc,n,fi=ev.ray_cast(inv@p,(inv.to_3x3()@Vector((0,0,-1))).normalized())
 if h:
  q=ev.matrix_world@loc
  if 1.18<q.z<1.40:print('FLOOR_HIT',o.name,list(q),o.parent.name if o.parent else None,[m.material.name if m.material else None for m in o.material_slots],flush=True)
