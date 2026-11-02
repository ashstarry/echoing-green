exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
import re
reg=json.loads((OUT/'decision-entities.json').read_text());entities=reg['entities'];used={e['id'] for e in entities}
src=ast.parse((WORK/'author_decision_bindings.py').read_text());funcs={'slug','ancestors','grouping','register'};exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in funcs],type_ignores=[]),'<entity helpers>','exec'))
extra=[];bpy.context.view_layer.update()
for bulb in list(s.objects):
 if bulb.type!='MESH' or 'lantern' not in bulb.name.lower() or any(a.get('decision_entity_id','').startswith('light.') for a in ancestors(bulb)):continue
 m=bulb.active_material;p=m.node_tree.nodes.get('Principled BSDF') if m and m.use_nodes else None
 if not p or p.inputs['Emission Strength'].default_value<=0:continue
 parent=bulb.parent;point=bulb.matrix_world.translation.copy();root=grouping('hanging_light_'+slug(bulb.name),[bulb],point,parent);row=register(root,'light',['set_brightness','set_warmth','off'],mode='entity_material_and_light');row['state']={'on':True};row['material_override']='Per-entity material/light state; shared material must not be changed globally.';row['parent_entity']=next((a.get('decision_entity_id') for a in ancestors(root)[1:] if a.get('decision_entity_id')),None)
 for a in row['actions']:a['parameters']={'level':['off','low','medium','high']} if a['id']=='set_brightness' else ({'palette':['warm','neutral','cool']} if a['id']=='set_warmth' else {});a['preconditions']='Local executor validates current state.'
 root['decision_manifest']='decision-entities.json';extra.append(row['id'])
reg['entity_count']=len(entities);(OUT/'decision-entities.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));rec=json.loads((OUT/'revision-record.json').read_text());rec['decision_authoring']['entity_count']=len(entities);rec['remaining_lanterns_registered']=extra;(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp08.blend'));print('EXTRA_LIGHTS',len(extra),'TOTAL',len(entities),flush=True)
