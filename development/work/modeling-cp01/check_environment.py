import bpy, json
data={'blender':bpy.app.version_string,'engines':[e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]}
try:
 p=bpy.context.preferences.addons['cycles'].preferences
 p.get_devices()
 data['compute_types']=[e.identifier for e in p.bl_rna.properties['compute_device_type'].enum_items]
 data['devices']=[{'name':d.name,'type':d.type} for d in p.devices]
 try:
  p.compute_device_type='METAL';p.get_devices()
  data['metal_devices']=[{'name':d.name,'type':d.type} for d in p.devices]
 except Exception as e:data['metal_error']=str(e)
except Exception as e:data['cycles_error']=str(e)
print('ENV_CHECK '+json.dumps(data))
