import bpy,json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-07';old=bpy.context.scene;new=bpy.data.scenes.new('GLB roundtrip inspection');bpy.context.window.scene=new
new.world=old.world.copy();new.view_settings.view_transform=old.view_settings.view_transform;new.view_settings.look=old.view_settings.look;new.view_settings.exposure=old.view_settings.exposure;new.view_settings.gamma=old.view_settings.gamma
for o in old.objects:
 if o.type=='LIGHT' or o==old.camera or o.name=='Indigo studio floor':
  n=o.copy();n.data=o.data.copy();new.collection.objects.link(n);n.parent=None;n.matrix_world=o.matrix_world
  if o==old.camera:new.camera=n
bpy.ops.import_scene.gltf(filepath=str(OUT/'borrowed-wind-town-cp07-web.glb'))
meshes=[o for o in new.objects if o.type=='MESH' and o.name!='Indigo studio floor.001'];triangles=0
for o in meshes:o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
bad=[o.name for o in new.objects if not all(math.isfinite(v) for row in o.matrix_world for v in row)]
expected=json.loads((OUT/'web-asset-validation.json').read_text());assert triangles==expected['triangles'],(triangles,expected['triangles'])
record={'decoder_import_succeeded':True,'triangles_including_imported_meshes':triangles,'finite_transforms':not bad,'new_meshes':len(meshes),'glb_sha256':hashlib.sha256((OUT/'borrowed-wind-town-cp07-web.glb').read_bytes()).hexdigest(),'source_model_sha256':hashlib.sha256((OUT/'borrowed-wind-town-cp07.blend').read_bytes()).hexdigest(),'render_lighting':'Copied from Blender master for material/geometry inspection; not included in GLB and not a browser screenshot','browser_test':False}
(OUT/'glb-roundtrip-check.json').write_text(json.dumps(record,indent=2));assert not bad
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='METAL';p.get_devices()
 for d in p.devices:d.use=d.type=='METAL'
 new.cycles.device='GPU'
except Exception:new.cycles.device='CPU'
new.render.engine='CYCLES';new.cycles.samples=64;new.cycles.use_denoising=True;new.render.resolution_x=1672;new.render.resolution_y=941;new.render.resolution_percentage=100;new.render.filepath=str(OUT/'07-glb-roundtrip.png');bpy.ops.render.render(write_still=True);print('GLB_ROUNDTRIP_COMPLETE',json.dumps(record),flush=True)
