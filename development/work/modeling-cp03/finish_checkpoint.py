import bpy, math, json, ast, random
from pathlib import Path
from mathutils import Vector
from contextlib import contextmanager
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-03'
s=bpy.context.scene;R=random.Random(2505);PI=math.pi;Z=.61;PARENT=None;assets=[]
cols={c.name:c for c in bpy.data.collections};COL=cols['00_Terrain']
templates={k:bpy.data.meshes['Shared '+k] for k in ['cube','sphere','ico','cyl']}
src=ast.parse((ROOT/'work/modeling-cp01/build_town.py').read_text())
allowed={'setmat','mesh','unit','primitive','box','cyl','ellipsoid','beam','path','ring'}
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allowed],type_ignores=[]),'<geometry helpers>','exec'))
cam=bpy.data.objects['Camera_Main_CP03_43deg'];s.camera=cam;W,H=1672,941
s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100
Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));UP=Q@Vector((0,1,0));FWD=Q@Vector((0,0,-1));ORTHO=cam.data.ortho_scale
def xy(pixel,z=Z):
 p=cam.location+RIGHT*((pixel[0]/W-.5)*ORTHO)+UP*((.5-pixel[1]/H)*ORTHO/(W/H));return p+FWD*((z-p.z)/FWD.z)
def pix(p):
 a=world_to_camera_view(s,cam,p);return [a.x*W,(1-a.y)*H]

# Keep the foreground station low enough to preserve the street behind it.
st=bpy.data.objects['station_main']
for o in st.children:
 if o.name.startswith(('CP02 station platform','CP02 platform bench','CP02 bench foot','CP02 station rear step')):continue
 o.location.z*=.90;o.scale.z*=.90
bpy.data.objects['small_wood_home'].scale.z*=.82
tea=bpy.data.objects['tea_house'];bpy.context.view_layer.update()
bpy.data.objects['customer_one'].location=tea.matrix_world@Vector((-2.20,-3.1,0))

# Preserve the accepted material/light direction. This round is spatial, not a relight.
reserved=bpy.data.collections.new('12_CP03_MOVEMENT_RESERVATIONS');s.collection.children.link(reserved);COL=reserved
def flatmat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Emission Color'].default_value=(*color,1);b.inputs['Emission Strength'].default_value=.5;b.inputs['Roughness'].default_value=1
 return m
route_mat=flatmat('GUIDE ONLY | walking clearance cyan',(.07,.66,.60))
act_mat=flatmat('GUIDE ONLY | action clearance amber',(.95,.52,.08))
reservations=[]
def band(name,pts,width,mat=route_mat):
 verts=[];faces=[]
 for p,q in zip(pts,pts[1:]):
  d=q-p; side=Vector((-d.y,d.x,0)).normalized()*width/2;k=len(verts)
  verts += [tuple(p-side),tuple(p+side),tuple(q+side),tuple(q-side)];faces.append((k,k+1,k+2,k+3))
 o=mesh(name,verts,faces,mat);o['guide_only']=True;o['reserved_width']=width;o['minimum_clear_height']=1.5;o['no_new_decor']=True
 reservations.append({'name':name,'width':width,'points_world':[list(p) for p in pts],'purpose':'Keep future detail out of walking surface; design reservation, not a navigable or collision-tested path.'})
 return o
for name,points,width in [
 ('West residential to market',[(397,536),(538,513),(580,437),(620,391)],1.00),
 ('Market frontage',[(620,391),(752,381),(978,345),(1082,321)],1.12),
 ('East plaza to hill',[(1008,595),(1055,488),(1087,381),(1123,299)],1.12),
 ('Garden approach',[(1090,417),(1180,423),(1284,418)],1.00),
 ('Station east approach',[(886,660),(937,616),(972,572)],1.05),
 ]:band(name,[xy(p,Z+.085) for p in points],width)
center=bpy.data.objects['plaza_ground'].location.copy();center.z=Z+.09
band('Plaza outer open circulation',[center+Vector((3.48*math.cos(a),3.48*math.sin(a),0)) for a in [i*2*PI/72 for i in range(73)]],.68)
stair=bpy.data.objects['CP03_hill_stair'];rr=json.loads((OUT/'revision-record.json').read_text());N=rr['stair']['steps'];t=rr['stair']['horizontal_tread'];h=rr['stair']['riser_height']
for i in range(N):
 a=stair.matrix_world@Vector((0,i*t,(i+1)*h+.025));b=stair.matrix_world@Vector((0,(i+1)*t,(i+1)*h+.025));band('Stair clear tread '+str(i),[a,b],.90)
for name,pixelpoint,radius in [('Post delivery interaction',(486,530),.58),('Plaza east interaction',(993,539),.58),('Market exchange',(971,357),.58)]:
 p=xy(pixelpoint,Z+.11);o=cyl(name,p,radius,.012,act_mat);o['guide_only']=True;o['no_new_decor']=True
 reservations.append({'name':name,'radius':radius,'center_world':list(p),'purpose':'Reserved interaction area; animation envelopes still need testing.'})
reserved.hide_render=True;reserved.hide_viewport=True

# Static visibility samples at head and upper body; these are not animated tests.
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();visibility=[]
residents=[o for o in s.objects if o.get('entity_id') and any(c.name=='08_Residents_SCALE_PROXIES' for c in o.users_collection)]
animals=[o for o in s.objects if o.get('entity_id') and any(c.name=='09_Animals_SCALE_PROXIES' for c in o.users_collection)]
for root in residents:
 row={'resident':root.name,'samples':{}}
 for label,local in [('head',(0,0,1.08)),('upper_body',(0,0,.75))]:
  p=root.matrix_world@Vector(local);hit,loc,n,face,obj,mat=s.ray_cast(deps,p-FWD*40,FWD,distance=41)
  ancestor=obj
  while ancestor and ancestor.parent:ancestor=ancestor.parent
  row['samples'][label]={'unoccluded_center_ray':ancestor==root,'first_hit':obj.name if obj else None,'pixel':pix(p)}
 visibility.append(row)
manifest={'checkpoint':'CP03','scope':'Real geometry revision, stopped for review; no runtime work','camera':{'type':cam.data.type,'elevation_degrees':math.degrees(math.asin(abs(FWD.z))),'orthographic_scale':ORTHO,'azimuth_degrees':12,'location':list(cam.location)},'objects':len(s.objects),'resident_proxy_count':len(residents),'animal_proxy_count':len(animals),'static_visibility_samples':visibility,'movement_reservations':reservations,'reservation_collection':'12_CP03_MOVEMENT_RESERVATIONS','reservation_status':'Hidden design guides for future detail placement; not navigation, automatic collision guarantees or a simulation.','not_implemented':['final architecture/vegetation/material detail','rigging and animation envelopes','navigation and social simulation','web renderer','24/7 backend']}
(OUT/'model-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
rr['additional_visibility_changes']=['Station upper geometry reduced 10% in height; platform unchanged.','Small foreground left house reduced 18% in height to reveal porch upper body.','One market proxy moved within frontage to clear the lantern-tree silhouette.']
(OUT/'revision-record.json').write_text(json.dumps(rr,ensure_ascii=False,indent=2))
# Camera-independent support diagnostic for the new hill actors, evaluated against modeled surfaces.
support=[]
for name in ['quiet_reader','returning_resident','hill_windwheel','quiet_home']:
 o=bpy.data.objects[name];p=o.matrix_world.translation.copy();start=p+Vector((0,0,.04));hit,loc,no,fi,ho,ma=s.ray_cast(deps,start,Vector((0,0,-1)),distance=3)
 support.append({'entity':name,'support_hit':ho.name if ho else None,'root_to_surface_delta':p.z-loc.z if hit else None})
(OUT/'hill-support-diagnostic.json').write_text(json.dumps(support,indent=2))
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.use_denoising=True;s.cycles.samples=96
plan=bpy.data.objects['Camera_Plan_CP02'];plan.name='Camera_Plan_CP03'
# A closer real-camera view lets the user inspect the newly built steps.
detail_data=bpy.data.cameras.new('CP03 hill detail camera');detail=bpy.data.objects.new('Camera_CP03_Hill_Detail',detail_data);cols['11_Cameras'].objects.link(detail)
detail_data.type='ORTHO';detail_data.ortho_scale=8.0
focus=xy((1153,224),1.1);detail.location=focus-FWD*28;detail.rotation_euler=cam.rotation_euler
s.render.filepath=str(OUT/'01-overview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp03.blend'))
bpy.ops.render.render(write_still=True);print('CP03_MAIN_READY',flush=True)
s.camera=detail;s.render.resolution_x=1300;s.render.resolution_y=1100;s.cycles.samples=64;s.render.filepath=str(OUT/'03-hill-detail.png');bpy.ops.render.render(write_still=True)
s.camera=plan;s.render.resolution_x=1500;s.render.resolution_y=1000;s.cycles.samples=40
sky=[]
for o in s.objects:
 if o.name.startswith(('Paper crescent','Paper star','CP02 layered paper cloud','CP02 visible paper rain')):sky.append(o);o.hide_render=True
s.render.filepath=str(OUT/'02-plan.png');bpy.ops.render.render(write_still=True)
reserved.hide_render=False;reserved.hide_viewport=False;bpy.context.view_layer.update();s.render.filepath=str(OUT/'04-reserved-space.png');bpy.ops.render.render(write_still=True)
print('CP03_FINAL_RENDERS_READY',json.dumps({'head':sum(x['samples']['head']['unoccluded_center_ray'] for x in visibility),'upper_body':sum(x['samples']['upper_body']['unoccluded_center_ray'] for x in visibility),'total':len(visibility)}),flush=True)
