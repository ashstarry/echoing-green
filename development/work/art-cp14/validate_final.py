import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'work/art-cp14';OUT=ROOT/'outputs/art-checkpoint-14';s=bpy.context.scene
exec(compile((W/'scene_signature.py').read_text(),'<signature>','exec'));current=json.loads(json.dumps(scene_signature(s)));before=json.loads((ROOT/'outputs/art-checkpoint-13/scene-signature.json').read_text());rev=json.loads((OUT/'revision-record.json').read_text());removed=set(rev['removed']);modified=set(rev['modified']);unexpected=[]
for name,row in before['objects'].items():
 if name in removed or name in modified:continue
 if row!=current['objects'].get(name):unexpected.append(name)
def in_restaurant(name):
 seen=set()
 while name and name not in seen:
  if name=='tea_house' or name.startswith('hanging_light_cp05_restaurant'):return True
  seen.add(name);name=before['objects'].get(name,{}).get('parent')
 return False
assert all(in_restaurant(n) for n in modified|removed),[n for n in modified|removed if not in_restaurant(n)]
missing=sorted(set(before['objects'])-set(current['objects'])-removed);extra=sorted(set(current['objects'])-set(before['objects'])-set(rev['added']));reg=json.loads((OUT/'decision-entities.json').read_text());oldreg=json.loads((ROOT/'outputs/art-checkpoint-13/decision-entities.json').read_text());ids={o['decision_entity_id']for o in s.objects if o.get('decision_entity_id')};parts={(o['decision_owner'],o['decision_part_id'])for o in s.objects if o.get('decision_part_id')};assert {e['id']for e in oldreg['entities']}<=ids;assert ids=={e['id']for e in reg['entities']}and len(ids)==196 and len(parts)==82
proof=[]
for o in [o for o in s.objects if o.get('decision_part_id')in ['wing_left','wing_right']]:
 meshes=[m for m in o.children_recursive if m.type=='MESH'];saved=o.matrix_basis.copy();beforepoints=[m.matrix_world@v.co for m in meshes for v in m.data.vertices];o.matrix_basis=saved@Matrix.Rotation(.35,4,'X');bpy.context.view_layer.update();afterpoints=[m.matrix_world@v.co for m in meshes for v in m.data.vertices];o.matrix_basis=saved;bpy.context.view_layer.update();restored=[m.matrix_world@v.co for m in meshes for v in m.data.vertices];motion=max((a-b).length for a,b in zip(beforepoints,afterpoints));error=max((a-b).length for a,b in zip(beforepoints,restored));proof.append({'part':o.name,'movement':motion,'restore_error':error,'passed':motion>.02 and error<1e-5})
binding_rows=[e for e in reg['entities']if e['kind']in ['star','water_lantern','celestial']];mats={name:bpy.data.materials[name]for e in binding_rows for name in e.get('material_bindings',[])};saved={n:m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value for n,m in mats.items()};emissionproof=[]
for e in binding_rows:
 own=set(e['material_bindings'])
 for n in own:mats[n].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=0
 okay=all(m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value==saved[n]for n,m in mats.items()if n not in own)
 for n in own:mats[n].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=saved[n]
 emissionproof.append({'entity':e['id'],'other_entities_unchanged':okay,'controlled_materials':len(own)})
assert all(p['passed']for p in proof)and all(p['other_entities_unchanged']for p in emissionproof)
(OUT/'sky-control-check.json').write_text(json.dumps({'passed':True,'wing_controls':proof,'independent_emission':emissionproof,'scope':'Actual rotations/material edits and restore. No full flap sweeps, flight, animation or runtime executor.'},indent=2))
prior={}
for i in range(1,14):
 folder='outputs/modeling-checkpoint-%02d'%i if i<=10 else ('outputs/lighting-checkpoint-%02d'%i if i<=12 else 'outputs/art-checkpoint-13');p=ROOT/folder;name='borrowed-wind-town-cp%02d.blend'%i;manifest=json.loads((p/'file-manifest.json').read_text());prior['CP%02d'%i]=hashlib.sha256((p/name).read_bytes()).hexdigest()==manifest[name]['sha256']
rec={'passed':not unexpected and not missing and not extra and current['camera']==before['camera']and current['collections']==before['collections']and all(prior.values()),'camera_unchanged':current['camera']==before['camera'],'unexpected_modified_objects':unexpected,'unexpected_missing_objects':missing,'unexpected_added_objects':extra,'authorized_removed_count':len(removed),'authorized_modified_objects':sorted(modified),'old_entity_ids_preserved':True,'entities':len(ids),'parts':len(parts),'previous_models_unchanged':prior,'source_model_sha256':hashlib.sha256((OUT/'borrowed-wind-town-cp14.blend').read_bytes()).hexdigest(),'scope':'Existing geometry/transforms outside the restaurant upper dining/awning/roof assembly preserved; new diners, tables and recomposed old light identities. New local routes/actions checked separately, no runtime guarantee.','runtime_implemented':False,'browser_fps_measured':False};(OUT/'validation.json').write_text(json.dumps(rec,indent=2));(OUT/'scene-signature.json').write_text(json.dumps(current,sort_keys=True));print(json.dumps(rec,indent=2));assert rec['passed']
# Record the actual art rig independently of a renderer implementation.
lights=[]
for o in s.objects:
 if o.type=='LIGHT':lights.append({'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'matrix_world':[list(r)for r in o.matrix_world],'parent':o.parent.name if o.parent else None,'decision_owner':o.get('decision_owner'),'role':o.get('lighting_role','inherited art lighting'),'active':o.data.energy>0,'size':o.data.size if o.data.type=='AREA'else o.data.shadow_soft_size})
materials=[]
for m in bpy.data.materials:
 p=m.node_tree.nodes.get('Principled BSDF')if m.use_nodes else None
 if p:materials.append({'name':m.name,'base_color':list(p.inputs['Base Color'].default_value),'emission_color':list(p.inputs['Emission Color'].default_value),'emission_strength':p.inputs['Emission Strength'].default_value,'roughness':p.inputs['Roughness'].default_value})
(OUT/'lighting-rig.json').write_text(json.dumps({'checkpoint':'CP14','lights':lights,'active_light_count':sum(x['active']for x in lights),'materials':materials,'coordinates':'Blender Z-up','art_directed_bounce':True,'browser_lighting_implemented':False,'runtime_implemented':False,'note':'Surface color/emission intentionally separated from soft spatial fill. Not a drop-in Three.js lighting conversion.'},indent=2))
