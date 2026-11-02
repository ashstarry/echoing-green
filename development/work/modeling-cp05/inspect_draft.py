import bpy,math,json
from mathutils import Vector
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'work/modeling-cp05';s=bpy.context.scene;cam=s.camera;Q=cam.rotation_euler.to_quaternion();FWD=Q@Vector((0,0,-1));RIGHT=Q@Vector((1,0,0));UP=Q@Vector((0,1,0));W,H=1672,941
def xy(p,z=.61):
 o=cam.location+RIGHT*((p[0]/W-.5)*cam.data.ortho_scale)+UP*((.5-p[1]/H)*cam.data.ortho_scale/(W/H));return o+FWD*((z-o.z)/FWD.z)
dg=bpy.context.evaluated_depsgraph_get();rows=[]
for root in s.objects:
 if not root.get('entity_id') or not any(c.name=='08_Residents_SCALE_PROXIES' for c in root.users_collection):continue
 row={'resident':root.name,'samples':{}}
 for label,z in [('head',1.08),('upper_body',.75)]:
  p=root.matrix_world@Vector((0,0,z));h,lo,no,fi,obj,m=s.ray_cast(dg,p-FWD*40,FWD,distance=41);a=obj
  while a and a.parent:a=a.parent
  row['samples'][label]={'clear':a==root,'first_hit':obj.name if obj else None}
 rows.append(row)
support=[]
for name in ['quiet_reader','returning_resident','hill_windwheel']:
 o=bpy.data.objects[name];p=o.location.copy();h,lo,no,fi,obj,m=s.ray_cast(dg,p+Vector((0,0,.05)),Vector((0,0,-1)),distance=2)
 support.append({'entity':name,'hit':obj.name if obj else None,'root_minus_surface_z':p.z-lo.z if h else None})
(WORK/'inspection.json').write_text(json.dumps({'residents':rows,'support':support},indent=2));print(json.dumps({'blocked':[r for r in rows if not all(v['clear'] for v in r['samples'].values())],'support':support},indent=2),flush=True)
d=bpy.data.cameras.new('CP05 draft terrace camera');o=bpy.data.objects.new('CP05 draft terrace camera',d);s.collection.objects.link(o);d.type='ORTHO';d.ortho_scale=8.0;o.rotation_euler=cam.rotation_euler;o.location=xy((1130,208),1.2)-FWD*30;s.camera=o
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='METAL';p.get_devices()
 for dev in p.devices:dev.use=dev.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.samples=48;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath=str(WORK/'terrace-draft.png');bpy.ops.render.render(write_still=True)
