import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'work/lighting-cp11';s=bpy.context.scene
exec(compile((WORK/'scene_signature.py').read_text(),'<signature>','exec'));before=scene_signature(s)
def tune(n,energy,color=None):
 o=bpy.data.objects[n];o.data.energy=energy
 if color:o.data.color=color
tune('Soft overhead blue hour',1000,(.59,.72,1))
tune('Quiet front paper fill',300,(.80,.85,1))
tune('CP09 warm town fill',85,(1,.72,.45))
tune('CP09 canopy warm key',35,(1,.70,.48))
tune('CP08 warm tree canopy bounce',75,(1,.41,.12))
tune('Warm lantern tree pool',170,(1,.47,.15));bpy.data.objects['Warm lantern tree pool'].data.size=3.6
for o in s.objects:
 if o.type=='LIGHT'and o.name.startswith('CP11 lamp spill | street_lantern'):o.data.energy=24;o.data.color=(1,.48,.17)
 if o.type=='LIGHT'and o.name.startswith('CP09 rear garden spill'):o.data.energy=8;o.location=(0,-.08,.52);o['decision_owner']=o.parent.get('decision_entity_id','');o['lighting_role']='Terrace lantern spill positioned outside the opaque paper shell'
for name,power in [('Shoji | transmitted honey',1.05),('Lantern | gentle amber',3.0),('CP05 shaded restaurant lantern paper',2.1)]:bpy.data.materials[name].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=power
# Extend the tree lantern's local glow across the shared music/listening zone.
owner=bpy.data.objects['hanging_light_tree_hanging_lantern_washi_005'];bulb=next(o for o in owner.children_recursive if o.type=='MESH'and o.active_material and o.active_material.name=='Lantern | gentle amber');p=bulb.matrix_world.translation+Vector((-.08,-.10,-.20));tree=bpy.data.objects['lantern_tree'];Q=s.camera.rotation_euler.to_quaternion();right=Q@Vector((1,0,0));back=Vector((-right.y,right.x,0));target=tree.matrix_world.translation-right*1.6-back*.65;target.z=.95
d=bpy.data.lights.new('CP11 shared music light','AREA');d.energy=30;d.color=(1,.54,.25);d.shape='DISK';d.size=1.8;o=bpy.data.objects.new(d.name,d);bpy.data.collections['10_Lighting'].objects.link(o);rot=(target-p).to_track_quat('-Z','Y');mw=Matrix.Translation(p)@rot.to_matrix().to_4x4();o.parent=owner;o.matrix_parent_inverse=owner.matrix_world.inverted();o.matrix_basis=mw;o['decision_owner']=owner['decision_entity_id'];o['lighting_role']='Soft extension of actual tree lantern over the fixed gathering area';o['cp11_new_light']=True
# Counter fill belongs to the nearest existing restaurant-lantern controller.
lamps=[o for o in s.objects if o.get('decision_kind')=='light'and 'restaurant_paper_lantern'in o.name]
for o in [x for x in s.objects if x.type=='LIGHT'and x.name.startswith('CP11 shop counter')]:
 owner=min(lamps,key=lambda r:(r.matrix_world.translation-o.matrix_world.translation).length);mw=o.matrix_world.copy();o.parent=owner;o.matrix_parent_inverse=owner.matrix_world.inverted();o.matrix_basis=mw;o['decision_owner']=owner['decision_entity_id']
bpy.context.view_layer.update();after=scene_signature(s);assert before==after
r=json.loads((WORK/'variant-B-record.json').read_text());r['variant']='C';r['refinement']='Readable blue-hour fill, warmer underside of tree flowers, shared music light, terrace light outside paper shell';r['geometry_camera_hierarchy_visibility_unchanged']=True;r['scene_signature']=after['digest'];r['active_lights']=sum(o.type=='LIGHT'and o.data.energy>0 for o in s.objects);r['new_light_objects']=[o.name for o in s.objects if o.type=='LIGHT'and o.get('cp11_new_light')];r['new_light_positions']={n:list(bpy.data.objects[n].matrix_world.translation)for n in r['new_light_objects']};(WORK/'variant-C-record.json').write_text(json.dumps(r,indent=2))
s['checkpoint']='CP11 lighting refinement C';s.render.resolution_x=1100;s.render.resolution_y=619;s.render.resolution_percentage=100;s.cycles.samples=32;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.render.filepath=str(WORK/'variant-C.png');bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'variant-C.blend'));bpy.ops.render.render(write_still=True);print('VARIANT_C_READY',flush=True)
