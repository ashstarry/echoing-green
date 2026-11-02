import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'work/lighting-cp12';OUT=ROOT/'outputs/lighting-checkpoint-12';s=bpy.context.scene
exec(compile((WORK/'scene_signature.py').read_text(),'<signature>','exec'));current=json.loads(json.dumps(scene_signature(s)))
s['checkpoint']='CP12 | readable rain, brighter environment and paper sky/water controls';s['review_status']='Lighting and two floating lanterns; original wing triangles split for control; runtime unimplemented';s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100;s.cycles.samples=96;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.render.filepath=str(OUT/'01-overview.png')
reg=json.loads((OUT/'decision-entities.json').read_text());reg['source_checkpoint']='CP12';reg['source_geometry_checkpoint']='CP10 layout; CP12 two new water lanterns';ids={e['id']for e in reg['entities']}
# New action parameters are a finite authoring contract, not implemented behaviors.
for e in reg['entities']:
 if e['kind'] in ['star','water_lantern']:
  for a in e['actions']:
   if a['id']=='set_brightness':a['parameters']={'level':{'enum':['off','low','medium','high']}}
   if a['id']=='twinkle':a['parameters']={'pattern':{'enum':['slow_breathe','sparse_twinkle','steady']}}
   if a['id']=='drift_to':a['parameters']={'target':{'enum':['own_initial_anchor']} };a['availability']='disabled until validated water routes and collision executor exist'
  if e['kind']=='water_lantern':e['anchors']=[{'id':'own_initial_anchor','position':e['position'],'scope':'Current verified placement only, not a validated route'}]
 if e['kind']=='bird':
  for a in e['actions']:
   if a['id']=='flap':a['parameters']={'style':{'enum':['gentle','active']}};a['availability']='disabled until animation and clearance verified'
 e['position']=list(bpy.data.objects[e['blender_object']].matrix_world.translation)
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
rig={'schema_version':1,'checkpoint':'CP12','coordinates':'Blender right-handed Z-up; convert with the GLB scene transform before any browser use','purpose':'Authoring light rig, not a tested browser-light conversion','source_geometry':'CP10 layout through CP11, two new water lanterns and unchanged bird shapes with split wing controls','variant_selected':'C, after A/B local-fill trials','lights':lights,'active_light_count':sum(x['active']for x in lights),'materials':materials,'world_background_strength':s.world.node_tree.nodes['Background'].inputs['Strength'].default_value,'view_settings':{'transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma},'glow':glows,'glb_contains_lights':False,'baked_lighting':False,'runtime_implemented':False,'browser_fps_measured':False,'limits':'These Cycles energies/area sizes and compositor settings are not drop-in Three.js values. Geometry and material candidate export remain separate from runtime lighting.'}
(OUT/'lighting-rig.json').write_text(json.dumps(rig,indent=2));(OUT/'scene-signature.json').write_text(json.dumps(current,sort_keys=True));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp12.blend'));print('CP12_MASTER_SAVED',rig['active_light_count'],'active lights',flush=True)
