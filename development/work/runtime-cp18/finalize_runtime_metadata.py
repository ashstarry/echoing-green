import bpy,json
from pathlib import Path
R=Path.cwd();A=R/'app/runtime-cp18/public/assets';O=R/'outputs/runtime-checkpoint-18';reg=json.loads((A/'runtime-registry.json').read_text());nav=json.loads((A/'navigation.json').read_text());act=json.loads((A/'motion-activities.json').read_text());walking={a['id']for a in nav['actors']if a['entry']};records=[]
for e in reg['entities']:
 id=e['id'];kind=e['kind'];modes=[]
 if id in walking:modes=['navigate_safe_ground','yield','idle_turn']
 elif id.startswith('resident.upper_diner_'):modes=['retreat_behind_curtain','come_out_to_dine']
 elif kind=='resident':modes=['idle_turn']+(['strum']if id=='resident.musician'else['work_gesture']if 'vendor_'in id else['greet_arrival']if id in ['resident.station_attendant','resident.station_traveler']else[])
 if id in act['clips']:modes+=[act['clips'][id]['motion']+'_bounded_route','decelerate_and_resume']
 if kind=='tram':modes=['travel_actual_rail','decelerate_at_station','dwell','depart']
 if kind=='windmill':modes=['wind_driven_rotation']
 if kind in ['plant','tree']and any(p['id']=='foliage'for p in e['parts']):modes=['bounded_wind_sway']
 if kind=='curtain':modes=['bounded_sway']+(['fold_for_upper_diners']if id=='curtain.restaurant_upper_noren'else[])
 if kind=='hanging_ornament':modes=['bounded_sway']
 if kind=='boat':modes=['moored_bob','bounded_oar_rock']
 if kind=='water_lantern':modes=['vertical_float','warm_glow']
 if kind=='kite':modes=['tethered_wind_sway']
 if kind=='weather':modes=['cloud_sway','paper_rain','paper_snow']
 if kind in ['light','star','moon']:modes=['global_warm_light_response']+(['twinkle']if kind=='star'else[])
 if id=='letter.postman_letter':modes=['follow_carrying_hand']
 e['runtime_binding_status']='partial'if modes else'static_or_not_yet_executable';e['executable_modes']=modes;e['runtime_contract_note']='Only modes listed here and choices in runtime-capabilities.json are executable. Original authoring action declarations are not blanket promises.';e['position']=list(bpy.data.objects[e['blender_object']].matrix_world.translation);records.append({'id':id,'kind':kind,'modes':modes,'declared_actions':[x['id']for x in e['actions']]})
reg['parts_count']=sum(len(e['parts'])for e in reg['entities']);(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));effects=[{'id':'effect.festival_fireworks','decision':'festival','implementation':'Finite red/gold festival on GPU; separate color-preserving effect pass and reflected town light.'},{'id':'effect.paper_rain','decision':'weather','implementation':'100 model-supported paper rain instances.'},{'id':'effect.paper_snow','decision':'weather','implementation':'160 model-supported folded snow instances.'}];(A/'runtime-effects.json').write_text(json.dumps(effects,ensure_ascii=False,indent=2));(O/'runtime-capabilities.json').write_text(json.dumps({'checkpoint':'CP18','entities':len(reg['entities']),'parts':reg['parts_count'],'walking_residents':len(walking),'resident_models':sum(e['kind']=='resident'for e in reg['entities']),'route_movers':len(act['clips']),'upper_diners':2,'nav_cells':len(nav['nodes']),'bindings':records,'runtime_effects':effects,'limits':['No stair or arbitrary indoor navigation.','Birds can fly/hover, but cannot land or return to nests.','Cyclist coasts with rolling wheels; a pedal cycle and dismount are not implemented.','Boat is moored; there is no free sailing or passenger boarding.','Only webpage-open independent sessions; no offline computation.','Browser lighting remains a realtime translation of accepted CP16, not pixel-identical.']},ensure_ascii=False,indent=2));print('CAPABILITIES',len(walking),len(act['clips']),reg['parts_count'])
