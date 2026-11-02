import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-01'
s=bpy.context.scene
# Final presentation adjustment for CP01, not another modeling/detailing phase.
tea=bpy.data.objects.get('tea_house');tea.scale.z=.87
quiet=bpy.data.objects.get('quiet_home');quiet.scale=(.88,.88,.88);quiet.location.z=1.45
for ob in s.objects:
 if ob.name.startswith('Awning folded stripe'):
  ob.scale.y*=.76;ob.location.y+=.18
 if ob.name.startswith('Awning front'):ob.location.y+=.28
cam=bpy.data.objects['Camera_Main_CP01'];s.camera=cam
cam.location=(-6,-25,19.3);cam.rotation_euler=(Vector((0,0,1.7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=26.5
s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100
bpy.context.view_layer.update()
# Fit all major real geometry. Celestial paper cutouts are decorative hero-camera staging.
pts=[]
for o in s.objects:
 if o.type not in {'MESH','CURVE'} or o.hide_render or o.name.startswith(('Indigo studio floor','Paper crescent','Paper star')):continue
 pts += [o.matrix_world@Vector(c) for c in o.bound_box]
for step in range(3):
 uv=[world_to_camera_view(s,cam,p) for p in pts]
 xmin=min(p.x for p in uv);xmax=max(p.x for p in uv);ymin=min(p.y for p in uv);ymax=max(p.y for p in uv)
 right=cam.rotation_euler.to_quaternion()@Vector((1,0,0));up=cam.rotation_euler.to_quaternion()@Vector((0,1,0))
 cam.location+=right*((xmin+xmax)/2-.5)*cam.data.ortho_scale+up*((ymin+ymax)/2-.47)*cam.data.ortho_scale/(1672/941)
 cam.data.ortho_scale*=max((xmax-xmin)/.93,(ymax-ymin)/.82,1.0)
 bpy.context.view_layer.update()
# Place paper sky ornaments in the free top band; these remain actual extruded meshes.
right=cam.rotation_euler.to_quaternion()@Vector((1,0,0));up=cam.rotation_euler.to_quaternion()@Vector((0,1,0));fwd=cam.rotation_euler.to_quaternion()@Vector((0,0,-1))
def sky_position(u,v):return cam.location+fwd*22+right*((u-.5)*cam.data.ortho_scale)+up*((v-.5)*cam.data.ortho_scale/(1672/941))
moon=bpy.data.objects.get('Paper crescent');moon.location=sky_position(.88,.87);moon.rotation_euler=cam.rotation_euler
for i,(u,v) in enumerate([(.08,.70),(.18,.87),(.42,.93),(.69,.91),(.96,.72)]):
 o=bpy.data.objects.get('Paper star '+str(i));o.location=sky_position(u,v);o.rotation_euler=cam.rotation_euler
# Light quality and the figure silhouettes are still intentionally first-checkpoint work.
s.cycles.samples=96;s.cycles.use_denoising=True
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.render.filepath=str(OUT/'01-overview.png')
s['checkpoint']='CP01: inspectable spatial and architectural model. Stop for user review.'
s['user_scope']='Independent client-session town; NO always-on or offline simulation code. Future migration boundaries only.'
s['not_final']='Architecture layout/material block-in; people/animals are proportion proxies; no rigging, behavior, navigation, web rendering or browser-performance validation.'
bpy.context.view_layer.update()
roots=[o for o in s.objects if o.get('entity_id')]
manifest={'checkpoint':'CP01','blender_version':bpy.app.version_string,'source_script':'build_town.py + finish_checkpoint.py',
 'approved_reference':'../ecosystem-v3-lighting/borrowed-wind-town-soft-light.png',
 'objects':len(s.objects),'mesh_objects':sum(o.type=='MESH' for o in s.objects),
 'mesh_vertices_instance_sum':sum(len(o.data.vertices) for o in s.objects if o.type=='MESH'),
 'armatures':sum(o.type=='ARMATURE' for o in s.objects),
 'residents':20,'animal_proxies':7,'renderer':'Cycles / Metal','asset_stage':'spatial architecture and basic material checkpoint, not production-ready',
 'entities':[{'id':o.get('entity_id'),'location':list(o.location),'scale':list(o.scale),'stage':o.get('checkpoint_status'),'collection':o.users_collection[0].name} for o in roots],
 'camera':{'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'orthographic_scale':cam.data.ortho_scale},
 'reserved_boundaries':['stable root entity IDs','separate architecture, character, light and camera collections','visual assets only; no simulation or server code'],
 'limitations':['No final paper textures/baked browser materials','Scale-proxy figures/animals, no skeletons','Topology/object counts not optimized for web','No active social simulation, navigation or model API','Render is Blender, not a browser screenshot']}
(OUT/'model-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp01.blend'))
bpy.ops.render.render(write_still=True)
print('OVERVIEW_READY',flush=True)
s.camera=bpy.data.objects['Camera_Plan_CP01'];s.render.resolution_x=1400;s.render.resolution_y=1100;s.cycles.samples=32;s.render.filepath=str(OUT/'02-plan.png')
bpy.ops.render.render(write_still=True)
print('PLAN_READY',flush=True)
# Alternate view verifies the editable geometry; it is not a polished product camera.
s.camera=bpy.data.objects['Camera_Reverse_Proof'];s.render.resolution_x=1400;s.render.resolution_y=900;s.cycles.samples=32;s.render.filepath=str(OUT/'03-reverse-geometry.png')
for ob in s.objects:
 if ob.name.startswith(('Paper crescent','Paper star')):ob.hide_render=True
bpy.ops.render.render(write_still=True)
print('REVERSE_READY',flush=True)
print('STOP_AT_CP01',flush=True)
