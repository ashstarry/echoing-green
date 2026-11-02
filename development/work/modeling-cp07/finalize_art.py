import bpy,math,json,ast,random
from pathlib import Path
from mathutils import Vector
from contextlib import contextmanager
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-07';WORK=ROOT/'work/modeling-cp07';s=bpy.context.scene;cam=s.camera;PI=math.pi;Z=.61;R=random.Random(71427);PARENT=None;assets=[]
cols={c.name:c for c in bpy.data.collections};COL=cols['07_Paper_Foliage'];templates={k:bpy.data.meshes['Shared '+k] for k in ['cube','sphere','ico','cyl']}
src=ast.parse((ROOT/'work/modeling-cp02/refine_and_present.py').read_text());node=next(n for n in src.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='aliases' for t in n.targets));exec(compile(ast.Module(body=[node],type_ignores=[]),'<aliases>','exec'))
for k,n in aliases.items():globals()[k]=bpy.data.materials[n]
src=ast.parse((ROOT/'work/modeling-cp01/build_town.py').read_text());allow={'setmat','mesh','unit','primitive','box','cyl','ellipsoid','ico','beam','taper','path','ring','asset','under','window','lantern','leaf'};exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allow],type_ignores=[]),'<helpers>','exec'))
leafmesh=bpy.data.meshes['Shared folded leaf'];flower_mesh=bpy.data.meshes['CP07 shared five-petal paper flower | 106 triangles'];sprigmesh=bpy.data.meshes['CP07 shared lobed folded paper sprig'];terr=[bpy.data.materials['Paper land layer '+str(i)] for i in range(5)]
blue2=bpy.data.materials['CP07 foliage | deep blue'];sage2=bpy.data.materials['CP07 foliage | dusk sage'];paleleaf=bpy.data.materials['CP07 foliage | pale folded edge'];Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));BACK=Vector((-RIGHT.y,RIGHT.x,0));FWD=Q@Vector((0,0,-1));UP=Q@Vector((0,1,0));rec=json.loads((OUT/'revision-record.json').read_text());segments=[(Vector(a),Vector(b),.65 if k=='stall_approach' else .72) for k,pts in rec['routes'].items() for a,b in zip(pts,pts[1:])]
src=ast.parse((WORK/'finish_environment.py').read_text());allow={'rb','protected','erase','bloom','sprig','garden','ground_at'};exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allow],type_ignores=[]),'<helpers>','exec'));clumps=2000;land=bpy.data.objects['Island paper layer 4']
# Ground every new rear sapling on real existing terrain. No floating set dressing.
ground_meshes=[o for o in cols['00_Terrain'].objects if o.type=='MESH' and o.name!='Indigo studio floor']
support=[]
for root in [o for o in s.objects if o.name.startswith('CP07 rear paper sapling')]:
 p=root.location.copy();best=None
 for ground in ground_meshes:
  inv=ground.matrix_world.inverted();h,loc,n,i=ground.ray_cast(inv@Vector((p.x,p.y,10)),(inv.to_3x3()@Vector((0,0,-1))).normalized())
  if h:
   z=(ground.matrix_world@loc).z
   if best is None or z>best:best=z
 if best is None:
  support.append({'name':root.name,'removed_no_ground':True});erase(root);continue
 root.location.z=best+.015;root.scale*=.85;support.append({'name':root.name,'z':root.location.z,'grounded':True})
 with under(root):
  for o in list(root.children):
   if 'little botanical sprig' in o.name:o.scale*=1.65
# A restrained fabric tone and rounded paper valance on the market awnings.
COL=cols['02_Teahouse_Market'];tea=bpy.data.objects['tea_house'];cloth=navy2.copy();cloth.name='CP07 awning paper | muted blue';cloth.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.15,.21,.29,1);cloth.diffuse_color=(.15,.21,.29,1)
for o in tea.children:
 if o.name.startswith('Awning folded stripe'):
  m=o.active_material
  if m.name.startswith('Roof'):setmat(o,cloth);m=cloth
  x=o.location.x;y=-2.075;zz=2.10
  with under(tea):
   verts=[(x-.16,y,zz+.035),(x+.16,y,zz+.035),(x+.16,y,zz-.045),(x+.10,y-.015,zz-.10),(x,y-.025,zz-.12),(x-.10,y-.015,zz-.10),(x-.16,y,zz-.045)]
   mesh('CP07 rounded awning paper hem',verts,[(0,i,i+1) for i in range(1,len(verts)-1)],m)
for me in bpy.data.meshes:
 if not me.users or not me.polygons or me.uv_layers:continue
 uv=me.uv_layers.new(name='UVMap')
 for poly in me.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(poly.normal[i]))]
  for li in poly.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]*2,p[axes[1]]*2)
for o in s.objects:
 if o.type=='CURVE':o.data.bevel_resolution=min(o.data.bevel_resolution,1)
rec['rear_sapling_support']=support;rec['normal_view_complete_roof']=True
s['checkpoint']='CP07 | cut-paper environment detail pass';s['runtime_status']='Editable art assets. Character rigs, real-time light calibration, simulation and performance benchmark not implemented.'
(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.context.view_layer.update()
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.samples=128;s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100;s.render.filepath=str(OUT/'01-overview.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp07.blend'));bpy.ops.render.render(write_still=True);print('CP07_FINAL_ART_READY',flush=True)
