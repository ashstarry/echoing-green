from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'work/lighting-cp12';OLD=ROOT/'work/lighting-cp11'
for name in ['export_web_asset.py','verify_glb.py','roundtrip_glb.py','audit_final.py','verify_light_bindings.py','check_review_files.py']:
 text=(OLD/name).read_text().replace('lighting-cp11','lighting-cp12').replace('lighting-checkpoint-11','lighting-checkpoint-12').replace('cp11','cp12').replace('CP11','CP12')
 if name=='roundtrip_glb.py':
  text=text.replace("for key,axis in [(('windmill.hill_windwheel','rotor'),'Y'),(('bicycle.street_bicycle','bicycle_wheel_front'),'Y')]:", "for key,axis in [(('windmill.hill_windwheel','rotor'),'Y'),(('bicycle.street_bicycle','bicycle_wheel_front'),'Y')]+[(k,'X') for k in parts if k[1] in ['wing_left','wing_right']]:")
  text=text.replace("'05-glb-roundtrip.png'", "'03-glb-inspection.png'")
 (W/name).write_text(text)
text=(OLD/'finalize_checkpoint.py').read_text().replace('lighting-cp11','lighting-cp12').replace('lighting-checkpoint-11','lighting-checkpoint-12').replace('cp11','cp12').replace('CP11','CP12')
text=text.replace(";baseline=json.loads((WORK/'baseline-scene-signature.json').read_text());assert current==baseline",'')
text=text.replace("ROOT/'outputs/modeling-checkpoint-10/decision-entities.json'","OUT/'decision-entities.json'")
text=text.replace("'CP12 | local warm lighting on accepted CP10 geometry'","'CP12 | readable rain, brighter environment and paper sky/water controls'")
text=text.replace("'Lighting and material-response review; geometry unchanged; runtime unimplemented'","'Lighting and two floating lanterns; original wing triangles split for control; runtime unimplemented'")
text=text.replace("'D, built from C refinement of B'","'C, after A/B local-fill trials'")
text=text.replace("'source_geometry':'CP10'","'source_geometry':'CP10 layout through CP11, two new water lanterns and unchanged bird shapes with split wing controls'")
text=text.replace("reg['source_geometry_checkpoint']='CP10'","reg['source_geometry_checkpoint']='CP10 layout; CP12 two new water lanterns'")
text=text.replace("lights=[]",'''# New action parameters are a finite authoring contract, not implemented behaviors.
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
lights=[]''')
(W/'finalize_checkpoint.py').write_text(text)
text=(ROOT/'work/modeling-cp10/check_full_contacts.py').read_text().replace("OUT=ROOT/'outputs/modeling-checkpoint-10'","OUT=ROOT/'outputs/lighting-checkpoint-12'").replace("'bicycle','boat','tram'","'bicycle','boat','tram','water_lantern'").replace("['boat','fish']","['boat','fish','water_lantern']")
text=text.replace("Rain particles excluded.","Rain particles excluded. Floating-lantern trays intersect the water surface intentionally, as do boat and water animals.")
(W/'check_full_contacts.py').write_text(text)
text=(OLD/'render_final.py').read_text().replace('lighting-checkpoint-11','lighting-checkpoint-12').replace('CP11','CP12')
start=text.index("focus=bpy.data.objects['plaza_ground']")
end=text.index("focus=(bpy.data.objects['greenhouse']")
text=text[:start]+text[end:]
text=text.replace('04-garden-water.png','02-garden-water.png')
(W/'render_final.py').write_text(text)
print('CP12 source preparation complete')
