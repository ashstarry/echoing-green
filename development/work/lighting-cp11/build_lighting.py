import bpy,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'work/lighting-cp11';OUT=ROOT/'outputs/lighting-checkpoint-11';s=bpy.context.scene
exec(compile((WORK/'scene_signature.py').read_text(),'<signature>','exec'));before=scene_signature(s)
variant=sys.argv[sys.argv.index('--variant')+1]if '--variant'in sys.argv else'A';soft=variant=='B';light_col=bpy.data.collections['10_Lighting'];added=[]
Q=s.camera.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));BACK=Vector((-RIGHT.y,RIGHT.x,0));tree=bpy.data.objects['lantern_tree'];town_center=tree.matrix_world.translation.copy()
def tune(name,energy,color=None,size=None):
 o=bpy.data.objects.get(name)
 if not o:return
 o.data.energy=energy
 if color:o.data.color=color
 if size is not None and o.data.type=='AREA':o.data.size=size
def add_light(name,kind,p,power,color,radius=.25,target=None,size=1.0,parent=None,owner=None,role='local illumination'):
 d=bpy.data.lights.new(name,kind);d.energy=power;d.color=color
 if kind=='POINT':d.shadow_soft_size=radius
 if kind=='AREA':d.shape='DISK';d.size=size
 o=bpy.data.objects.new(name,d);light_col.objects.link(o);o.location=p
 if target is not None:o.rotation_euler=(Vector(target)-Vector(p)).to_track_quat('-Z','Y').to_euler()
 if parent:
  mw=Matrix.Translation(Vector(p))@o.rotation_euler.to_matrix().to_4x4();o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted();o.matrix_basis=mw
 if owner:o['decision_owner']=owner
 o['lighting_role']=role;o['cp11_new_light']=True;added.append(name);return o
# Broad lighting is quieter; actual lamps and activity zones carry the warm hierarchy.
tune('Soft overhead blue hour',820 if soft else 650,(.56,.69,1),12)
tune('Quiet front paper fill',340 if soft else 220,(.73,.81,1),10)
tune('CP09 warm town fill',90 if soft else 60,(1,.70,.42),7)
tune('CP09 canopy warm key',10,(1,.62,.32),2.5)
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.28 if soft else .24
tune('Warm lantern tree pool',160 if soft else 180,(1,.46,.12),3.1)
tune('CP08 warm tree canopy bounce',42,(1,.43,.13))
tune('Tea frontage warm bounce',65,(1,.54,.23),3)
tune('Station warm bounce',55,(1,.57,.27),3.2)
tune('Post office warm bounce',48,(1,.49,.16))
tune('Greenhouse soft interior',68,(1,.55,.22))
tune('CP08 greenhouse interior wash',50,(1,.58,.26),1.5)
for o in s.objects:
 if o.type=='LIGHT'and o.name.startswith(('CP07 local lantern pool','CP08 tree lantern spill')):o.data.energy=0;o['cp11_status']='Superseded by entity-attached source at actual lantern'
 if o.type=='LIGHT'and o.name.startswith('CP09 rear garden spill'):o.data.energy=5.5;o.data.color=(1,.48,.17)
# Emission and material response only; no vertex, object or actor moves.
for name,energy,color in [('Lantern | gentle amber',3.0 if soft else 3.4,(1,.43,.10)),('CP05 shaded restaurant lantern paper',2.4,(1,.34,.055)),('Shoji | transmitted honey',1.25,(1,.43,.12)),('Shoji | quiet window',.42,(1,.40,.10))]:
 p=bpy.data.materials[name].node_tree.nodes['Principled BSDF'];p.inputs['Emission Strength'].default_value=energy;p.inputs['Emission Color'].default_value=(*color,1)
for name in ['Cedar frame','Cut wood edges','Shoji walls | ivory','Washi | warm ivory','Washi | pale edge']:
 p=bpy.data.materials[name].node_tree.nodes['Principled BSDF'];p.inputs['Roughness'].default_value=.88
p=bpy.data.materials['Greenhouse paper panes'].node_tree.nodes['Principled BSDF'];p.inputs['Roughness'].default_value=.32;p.inputs['Transmission Weight'].default_value=.14;p.inputs['Alpha'].default_value=.18
p=bpy.data.materials['Layered paper water'].node_tree.nodes['Principled BSDF'];p.inputs['Roughness'].default_value=.35
p=bpy.data.materials['World backdrop | indigo'].node_tree.nodes['Principled BSDF'];p.inputs['Emission Strength'].default_value=.32;p.inputs['Emission Color'].default_value=(.045,.075,.17,1)
# Each new lamp source is attached to its existing logical lamp entity.
for root in [o for o in s.objects if o.get('decision_kind')=='light']:
 if root.name.startswith('terrace_garden_lantern'):continue
 bulbs=[]
 for child in root.children_recursive:
  m=child.active_material if child.type=='MESH'else None;p=m.node_tree.nodes.get('Principled BSDF')if m and m.use_nodes else None
  if p and p.inputs['Emission Strength'].default_value>0:bulbs.append(child)
 if not bulbs:continue
 bulb=max(bulbs,key=lambda o:o.dimensions.length);p=bulb.matrix_world.translation.copy();toward=town_center-p;toward.z=0
 if toward.length:toward.normalize()
 p+=toward*.08;p.z-=max(.17,bulb.dimensions.z*.62)
 if root.name.startswith('street_lantern'):power=18;radius=.24;role='Street / bridge / stair connection'
 elif 'tree_hanging'in root.name:power=11 if soft else 12;radius=.20;role='Shared lantern-tree gathering pool'
 elif 'restaurant'in root.name:power=3.3;radius=.14;role='Restaurant balcony lantern row'
 elif 'station'in root.name:power=6;radius=.18;role='Station waiting light'
 elif 'side'in root.name:power=5;radius=.20;role='Side-stall and corner activity'
 else:power=5;radius=.20;role='Quiet terrace accent'
 add_light('CP11 lamp spill | '+root.name,'POINT',p,power,(1,.45,.14),radius,parent=root,owner=root['decision_entity_id'],role=role)
# Counter-facing light comes from beneath the awning, toward the shared service area.
tea=bpy.data.objects['tea_house']
for i,x in enumerate([-1.8,0,1.8]):
 p=tea.matrix_world@Vector((x,-1.56,1.63));target=tea.matrix_world@Vector((x,-2.9,.60));add_light('CP11 shop counter '+str(i),'AREA',p,34 if soft else 40,(1,.53,.20),target=target,size=1.15,parent=tea,role='Shared vendor and customer activity area')
# Window light is authored under each moving vehicle, with its existing Decision owner.
for name in ['tram_car_front','tram_car_rear']:
 car=bpy.data.objects[name];p=car.matrix_world@Vector((0,-.60,.91));target=car.matrix_world@Vector((0,-1.8,-.15));o=add_light('CP11 carriage window spill | '+name,'AREA',p,17,(1,.47,.12),target=target,size=2.4,parent=car,owner=car['decision_entity_id'],role='Window spill follows vehicle transform; no motion implemented');o.data.shape='RECTANGLE';o.data.size_y=.32
# A slightly stronger but localized glow, with no full-frame blur.
for node in s.compositing_node_group.nodes:
 if node.bl_idname=='CompositorNodeGlare':node.inputs['Threshold'].default_value=2.2;node.inputs['Strength'].default_value=.14;node.inputs['Size'].default_value=.30
bpy.context.view_layer.update();after=scene_signature(s);assert before==after,'Non-light scene/camera/visibility changed'
record={'variant':variant,'scope':'Lighting and surface-response only; fixed CP10 geometry and poses','source_model':str(ROOT/'outputs/modeling-checkpoint-10/borrowed-wind-town-cp10.blend'),'source_sha256':hashlib.sha256((ROOT/'outputs/modeling-checkpoint-10/borrowed-wind-town-cp10.blend').read_bytes()).hexdigest(),'geometry_camera_hierarchy_visibility_unchanged':True,'scene_signature':after['digest'],'new_light_objects':added,'new_light_positions':{n:list(bpy.data.objects[n].matrix_world.translation)for n in added},'active_lights':sum(o.type=='LIGHT'and o.data.energy>0 for o in s.objects),'browser_runtime_or_bake_implemented':False,'normal_roof_preserved':True}
(WORK/('variant-'+variant+'-record.json')).write_text(json.dumps(record,indent=2));(WORK/'baseline-scene-signature.json').write_text(json.dumps(before,sort_keys=True))
s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=619;s.render.resolution_percentage=100;s.cycles.samples=32;s.render.filepath=str(WORK/('variant-'+variant+'.png'));s['checkpoint']='CP11 lighting study '+variant;bpy.ops.wm.save_as_mainfile(filepath=str(WORK/('variant-'+variant+'.blend')));bpy.ops.render.render(write_still=True);print('LIGHTING_VARIANT_READY',variant,flush=True)
