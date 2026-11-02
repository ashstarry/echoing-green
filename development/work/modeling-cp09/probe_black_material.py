exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
for name in ['CP07 district fence post.027','CP07 district fence post.026','small_wood_home paper body']:
 o=bpy.data.objects[name];print('MAT_PROBE',name,'mesh',o.data.name,'polys',[(p.material_index,p.use_smooth)for p in o.data.polygons],'slots',[(x.link,x.material.name if x.material else None)for x in o.material_slots],'uv',o.data.uv_layers.active.name if o.data.uv_layers.active else None,flush=True)
 for slot in o.material_slots:
  m=slot.material
  if not m:continue
  print('NODES',m.name,[(n.name,n.bl_idname)for n in m.node_tree.nodes],[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in m.node_tree.links],flush=True)
