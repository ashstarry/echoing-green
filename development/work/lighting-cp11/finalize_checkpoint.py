import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'work/lighting-cp11';OUT=ROOT/'outputs/lighting-checkpoint-11';s=bpy.context.scene
exec(compile((WORK/'scene_signature.py').read_text(),'<signature>','exec'));current=json.loads(json.dumps(scene_signature(s)));baseline=json.loads((WORK/'baseline-scene-signature.json').read_text());assert current==baseline
s['checkpoint']='CP11 | local warm lighting on accepted CP10 geometry';s['review_status']='Lighting and material-response review; geometry unchanged; runtime unimplemented';s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100;s.cycles.samples=96;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.render.filepath=str(OUT/'01-overview.png')
reg=json.loads((ROOT/'outputs/modeling-checkpoint-10/decision-entities.json').read_text());reg['source_checkpoint']='CP11';reg['source_geometry_checkpoint']='CP10';ids={e['id']for e in reg['entities']}
lights=[]
for o in s.objects:
 if o.type!='LIGHT':continue
 owner=o.get('decision_owner');assert not owner or owner in ids,(o.name,owner)
 row={'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'matrix_world':[list(r)for r in o.matrix_world],'matrix_local':[list(r)for r in o.matrix_local],'parent':o.parent.name if o.parent else None,'decision_owner':owner,'role':o.get('lighting_role','environment or legacy art fill'),'active':o.data.energy>0}
 if o.data.type=='AREA':row.update({'shape':o.data.shape,'size':o.data.size,'size_y':o.data.size_y})
 if o.data.type=='POINT':row['radius']=o.data.shadow_soft_size
 lights.append(row)
for e in reg['entities']:e['lighting_bindings']=[l['name']for l in lights if l['decision_owner']==e['id']]
(OUT/'decision-entities.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2))
materials=[]
for m in bpy.data.materials:
 p=m.node_tree.nodes.get('Principled BSDF')if m.use_nodes else None
 if p:materials.append({'name':m.name,'base_color':list(p.inputs['Base Color'].default_value),'roughness':p.inputs['Roughness'].default_value,'emission_strength':p.inputs['Emission Strength'].default_value,'emission_color':list(p.inputs['Emission Color'].default_value),'alpha':p.inputs['Alpha'].default_value,'transmission':p.inputs['Transmission Weight'].default_value})
glows=[{'threshold':n.inputs['Threshold'].default_value,'strength':n.inputs['Strength'].default_value,'size':n.inputs['Size'].default_value}for n in s.compositing_node_group.nodes if n.bl_idname=='CompositorNodeGlare']
rig={'schema_version':1,'checkpoint':'CP11','coordinates':'Blender right-handed Z-up; convert with the GLB scene transform before any browser use','purpose':'Authoring light rig, not a tested browser-light conversion','source_geometry':'CP10','variant_selected':'D, built from C refinement of B','lights':lights,'active_light_count':sum(x['active']for x in lights),'materials':materials,'world_background_strength':s.world.node_tree.nodes['Background'].inputs['Strength'].default_value,'view_settings':{'transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma},'glow':glows,'glb_contains_lights':False,'baked_lighting':False,'runtime_implemented':False,'browser_fps_measured':False,'limits':'These Cycles energies/area sizes and compositor settings are not drop-in Three.js values. Geometry and material candidate export remain separate from runtime lighting.'}
(OUT/'lighting-rig.json').write_text(json.dumps(rig,indent=2));(OUT/'scene-signature.json').write_text(json.dumps(current,sort_keys=True));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp11.blend'));print('CP11_MASTER_SAVED',rig['active_light_count'],'active lights',flush=True)
