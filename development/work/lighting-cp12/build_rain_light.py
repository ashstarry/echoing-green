import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'work/lighting-cp12';s=bpy.context.scene
exec(compile((WORK/'scene_signature.py').read_text(),'<signature>','exec'));before=scene_signature(s)
variant=sys.argv[sys.argv.index('--variant')+1]if '--variant'in sys.argv else'A';strong=variant=='B';col=bpy.data.collections['10_Lighting']
def area(name,p,target,power,color,size,owner,role):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size
 if hasattr(d,'spread'):d.spread=math.radians(105)
 o=bpy.data.objects.new(name,d);col.objects.link(o);mw=Matrix.Translation(Vector(p))@(Vector(target)-Vector(p)).to_track_quat('-Z','Y').to_matrix().to_4x4();o.parent=owner;o.matrix_parent_inverse=owner.matrix_world.inverted();o.matrix_basis=mw;o['decision_owner']=owner['decision_entity_id'];o['lighting_role']=role;o['cp12_new_light']=True;return o
cloud=bpy.data.objects['CP02_paper_cloud'];lamp=bpy.data.objects['street_lantern_09']
area('CP12 rain-sky soft fill',(8.8,-1.0,5.8),(8.9,-1.3,.85),185 if strong else 130,(.62,.77,1),4.0,cloud,'Local overcast skylight: umbrella top, bridge and water remain readable')
area('CP12 bridge lamp reflected fill',(9.4,-3.0,2.30),(9.95,-.68,1.78),65 if strong else 45,(1,.72,.48),2.2,lamp,'Soft reflected lantern light from the pond-side bank into the fixed bridge area; not actor-following')
o=bpy.data.objects['CP11 lamp spill | street_lantern_09'];o.data.energy=32;o.data.shadow_soft_size=.30
o=bpy.data.objects['CP11 lamp spill | street_lantern_08'];o.data.energy=28;o.data.shadow_soft_size=.30
# Separate the paper rain from the ripple material without changing rain geometry.
base=bpy.data.materials['Cut ripple | soft blue'];rain=base.copy();rain.name='CP12 rain thread | silver blue';p=rain.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.34,.46,.60,1);p.inputs['Roughness'].default_value=.58;p.inputs['Emission Color'].default_value=(.28,.42,.60,1);p.inputs['Emission Strength'].default_value=.035;rain.diffuse_color=(.34,.46,.60,1)
rain_objects=[]
for o in s.objects:
 if o.type in ['MESH','CURVE']and o.name.startswith('CP02 visible paper rain'):
  o.material_slots[0].link='OBJECT';o.material_slots[0].material=rain;rain_objects.append(o.name)
p=base.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.23,.36,.49,1);p.inputs['Roughness'].default_value=.65;base.diffuse_color=(.23,.36,.49,1)
bpy.context.view_layer.update();after=scene_signature(s);assert before==after
r={'checkpoint':'CP12','variant':variant,'source':'CP11','geometry_camera_hierarchy_visibility_unchanged':True,'scene_signature':after['digest'],'new_lights':[{'name':o.name,'position':list(o.matrix_world.translation),'energy':o.data.energy,'owner':o.get('decision_owner')}for o in s.objects if o.type=='LIGHT'and o.get('cp12_new_light')],'modified_existing_lights':['CP11 lamp spill | street_lantern_08','CP11 lamp spill | street_lantern_09'],'rain_material_objects':rain_objects,'global_exposure_changed':False,'rain_motion_implemented':False};(WORK/('variant-'+variant+'-record.json')).write_text(json.dumps(r,indent=2));(WORK/'baseline-scene-signature.json').write_text(json.dumps(before,sort_keys=True))
s['checkpoint']='CP12 local rainy bridge lighting '+variant;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100;bpy.ops.wm.save_as_mainfile(filepath=str(WORK/('variant-'+variant+'.blend')))
main=s.camera;focus=(bpy.data.objects['greenhouse'].matrix_world.translation+bpy.data.objects['pond_boat'].matrix_world.translation)/2+Vector((0,0,.85));d=bpy.data.cameras.new('CP12 draft detail');d.type='ORTHO';d.ortho_scale=8.8;c=bpy.data.objects.new(d.name,d);s.collection.objects.link(c);c.rotation_euler=main.rotation_euler;c.location=focus-(main.rotation_euler.to_quaternion()@Vector((0,0,-1)))*30;s.camera=c;s.render.resolution_x=1000;s.render.resolution_y=786;s.render.filepath=str(WORK/('variant-'+variant+'.png'));bpy.ops.render.render(write_still=True);print('CP12_DRAFT_READY',variant,flush=True)
