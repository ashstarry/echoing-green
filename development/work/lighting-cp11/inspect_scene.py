import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'work/lighting-cp11';s=bpy.context.scene
data={'world':{'color':list(s.world.color),'nodes':[]},'view':{'transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma},'lights':[],'materials':[],'light_entities':[]}
for n in s.world.node_tree.nodes:
 row={'name':n.name,'type':n.bl_idname};row['inputs']={x.name:list(x.default_value)if hasattr(x.default_value,'__len__')else x.default_value for x in n.inputs if hasattr(x,'default_value')};data['world']['nodes'].append(row)
for o in s.objects:
 if o.type=='LIGHT':data['lights'].append({'name':o.name,'type':o.data.type,'power':o.data.energy,'color':list(o.data.color),'size':getattr(o.data,'size',None),'radius':getattr(o.data,'shadow_soft_size',None),'matrix':[list(r)for r in o.matrix_world],'parent':o.parent.name if o.parent else None,'props':[p.identifier for p in o.data.bl_rna.properties if any(k in p.identifier for k in ['shadow','normalize','spread'])]})
 if o.get('decision_kind')=='light':
  bulbs=[]
  for ch in o.children_recursive:
   m=ch.active_material if ch.type=='MESH'else None;p=m.node_tree.nodes.get('Principled BSDF')if m and m.use_nodes else None
   if p and p.inputs['Emission Strength'].default_value>0:bulbs.append({'name':ch.name,'position':list(ch.matrix_world.translation),'dimensions':list(ch.dimensions)})
  data['light_entities'].append({'name':o.name,'id':o['decision_entity_id'],'position':list(o.matrix_world.translation),'bulbs':bulbs})
for m in bpy.data.materials:
 p=m.node_tree.nodes.get('Principled BSDF')if m.use_nodes else None
 if p:data['materials'].append({'name':m.name,'color':list(p.inputs['Base Color'].default_value),'roughness':p.inputs['Roughness'].default_value,'emission':p.inputs['Emission Strength'].default_value,'emission_color':list(p.inputs['Emission Color'].default_value),'alpha':p.inputs['Alpha'].default_value,'transmission':p.inputs['Transmission Weight'].default_value})
(OUT/'scene-inspection.json').write_text(json.dumps(data,indent=2));print('INSPECTION_READY',flush=True)
