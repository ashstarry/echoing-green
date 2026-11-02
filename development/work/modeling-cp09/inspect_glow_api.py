import bpy,json
n=bpy.data.node_groups.new('Inspect','CompositorNodeTree').nodes.new('CompositorNodeGlare')
r={'properties':[(p.identifier,p.type) for p in n.bl_rna.properties],'inputs':[]}
for x in n.inputs:
 d={'name':x.name,'idname':x.bl_idname}
 try:d['default']=str(x.default_value)
 except Exception:pass
 try:d['enums']=[e.identifier for e in x.bl_rna.properties['default_value'].enum_items]
 except Exception:pass
 r['inputs'].append(d)
print(json.dumps(r,indent=2))
