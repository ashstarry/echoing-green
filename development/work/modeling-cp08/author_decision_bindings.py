"""Authoring contract only: no provider call, state simulation or locomotion engine."""
exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
import re,hashlib
rec=json.loads((OUT/'revision-record.json').read_text());entities=[];used=set();bpy.context.view_layer.update()
def slug(n):return re.sub('[^a-z0-9_]+','_',n.lower()).strip('_')
def ancestors(o):
 a=[]
 while o:a.append(o);o=o.parent
 return a
def grouping(name,objects,pivot,parent=None):
 col=objects[0].users_collection[0] if objects else cols['01_Plaza'];root=bpy.data.objects.new(name,None);col.objects.link(root)
 if parent:
  root.parent=parent;root.matrix_parent_inverse=parent.matrix_world.inverted()
 root.matrix_basis=Matrix.Translation(pivot);bpy.context.view_layer.update()
 for o in objects:
  basis=o.matrix_basis.copy();factor=o.parent.matrix_world@o.matrix_parent_inverse if o.parent else Matrix.Identity(4);o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted()@factor;o.matrix_basis=basis
 bpy.context.view_layer.update();return root
def part(root,pid,objects,pivot,control,axis=None):
 p=grouping(root.name+'__'+pid,objects,pivot,root);p['decision_part_id']=pid;p['decision_owner']=root.get('decision_entity_id','');p['control_kind']=control
 if axis:p['control_axis']=axis
 return p
def register(root,kind,actions,label=None,mode='root_transform'):
 eid=kind+'.'+slug(root.name)
 assert eid not in used,eid
 used.add(eid);root['decision_entity_id']=eid;root['decision_kind']=kind;root['decision_actions']=json.dumps(actions);root['decision_status']='authoring_only_runtime_unimplemented';root['decision_actuation']=mode
 row={'id':eid,'label':label or root.name,'kind':kind,'blender_object':root.name,'position':list(root.matrix_world.translation),'actions':[{'id':a,'implementation':'declared; executor/animation not implemented'} for a in actions],'actuation':mode,'parts':[],'state':{},'anchors':[],'runtime_ready':False,'requires_animation_binding':kind in ['resident','animal','fish','bird']};entities.append(row);return row

# Residents remain separately identified, including a rider parented to a vehicle.
people=[o for o in s.objects if o.get('entity_id') and any(c.name=='08_Residents_SCALE_PROXIES' for c in o.users_collection) and any(c.name.startswith('Head') for c in o.children)]
for o in people:
 actions=['walk_to','wait','look_at','talk','sit','stand']
 if o.name=='musician':actions+=['play_guitar','stop_playing']
 if o.name=='cyclist':actions+=['ride','dismount']
 if 'gardener' in o.name:actions+=['water_plant','carry_pot']
 if o.name.startswith('vendor'):actions+=['serve','prepare_goods']
 row=register(o,'resident',actions);row['state']={'activity':'riding' if o.name=='cyclist' else ('seated' if any(c.name.startswith('Seated thigh') for c in o.children) else 'standing')};row['body_component_sources']=[c.name for c in o.children if c.type=='MESH'];row['motion_note']='Editable body pieces are retained in .blend. No skeleton or clip exists yet; final skinned export remains required.'
for o in [x for x in s.objects if x.get('entity_id') and any(c.name=='09_Animals_SCALE_PROXIES' for c in x.users_collection)]:
 kind='bird' if o.name.startswith('paper_bird') else 'animal';actions=['fly_to','perch','return_to_roost'] if kind=='bird' else (['swim_to','float','follow'] if o.name.startswith('duck') else ['walk_to','idle','follow','rest']);register(o,kind,actions)
for name in ['pond_fish_0','pond_fish_1']:register(bpy.data.objects[name],'fish',['swim_to','school','rest'])
for name in ['tram_car_front','tram_car_rear']:
 root=bpy.data.objects[name];row=register(root,'tram',['travel_route','stop_at_station','wait'],mode='root_along_rail_and_wheels');row['state']={'convoy':'town_tram','motion':'stopped'}
 for i,o in enumerate([x for x in root.children if x.name.startswith('Tram wheel')]):part(root,'wheel_%d'%i,[o],o.matrix_world.translation.copy(),'rotation','local Y')
row=register(bpy.data.objects['street_bicycle'],'bicycle',['ride_route','stop','park'],mode='root_and_wheels');row['state']={'rider':'resident.cyclist'}
for name in ['bicycle_wheel_front','bicycle_wheel_rear']:
 o=bpy.data.objects[name];o['decision_part_id']=name;o['decision_owner']='bicycle.street_bicycle';o['control_kind']='rotation';o['control_axis']='local Y'
register(bpy.data.objects['pond_boat'],'boat',['drift_to','moor','rock'],mode='root_on_water')
wind=bpy.data.objects['hill_windwheel'];register(wind,'windmill',['set_spin','stop'],mode='part_rotation');parts=[o for o in wind.children if o.name.startswith(('Folded wind vane','Wheel hub'))];part(wind,'rotor',parts,wind.matrix_world@Vector((0,-.12,2.75)),'rotation','local Y')
register(bpy.data.objects['station_entry_door'],'door',['open','close'],mode='hinge_rotation')
parked=bpy.data.objects.get('CP07 parked bicycle')
if parked:
 row=register(parked,'bicycle',['ride_route','stop','park'],mode='root_and_wheels');row['state']={'rider':None,'parked':True};row['wheel_binding_pending']=True
for parentname,prefixes,newname,kind,actions in [('musician',('CP07 guitar',),'musician_guitar','instrument',['carry','place','play']),('postman',('Red seal letter','Letter wax seal'),'postman_letter','letter',['carry','deliver','receive'])]:
 parent=bpy.data.objects[parentname];objects=[o for o in parent.children if o.name.startswith(prefixes)]
 if objects:
  pivot=objects[0].matrix_world.translation.copy();root=grouping(newname,objects,pivot,parent);row=register(root,kind,actions,mode='attached_prop');row['state']={'carrier':parent.get('decision_entity_id')};row['attachment_note']='Parent hierarchy exists; skeletal hand/socket binding remains to be authored.'

# Keep carried umbrella and kite assemblies individually addressable.
um=[o for o in s.objects if o.name.startswith(('CP02 paper umbrella','CP02 umbrella handle'))]
if um:
 pts=[o.matrix_world@Vector(v) for o in um for v in o.bound_box];pivot=Vector(((min(p.x for p in pts)+max(p.x for p in pts))/2,(min(p.y for p in pts)+max(p.y for p in pts))/2,max(p.z for p in pts)-.12));root=grouping('carried_umbrella',um,pivot,bpy.data.objects['water_companion']);row=register(root,'umbrella',['carry','tilt','lower'],mode='attached_root');row['state']={'carrier':'resident.water_companion'}
kiteobjs=[o for o in s.objects if o.name.startswith(('Red paper kite','Kite string','Kite ribbon')) and o.type in ['MESH','CURVE']]
if kiteobjs:
 body=bpy.data.objects['Red paper kite'];pts=[body.matrix_world@v.co for v in body.data.vertices];root=grouping('plaza_kite',kiteobjs,sum(pts,Vector())/len(pts));row=register(root,'kite',['raise','lower','sway'],mode='body_plus_deformable_tether');row['state']={'holder':'resident.kite_child'};row['tether_note']='Tether deformation and hand attachment require runtime/animation work; it is not a rigid free-flying object.'
cloud=bpy.data.objects.get('CP02_paper_cloud')
if cloud:
 register(cloud,'weather',['set_rain','stop_rain','drift'],mode='root_and_rain_visibility');rain=[o for o in s.objects if o.name.startswith('CP02 visible paper rain')];part(cloud,'rain',rain,cloud.matrix_world.translation.copy(),'visibility_and_particle_motion')

# Lights are independent logical objects. Static frames may remain batched inside each light,
# while emitted color/intensity is an entity-local state, never a global material mutation.
for index in range(20):
 prefix='CP02 street lantern '+str(index)+' ';group=[o for o in s.objects if o.name.startswith(prefix) and o.type in ['MESH','CURVE']]
 if not group:continue
 foot=next((o for o in group if 'foot' in o.name),group[0]);root=grouping('street_lantern_%02d'%index,group,foot.matrix_world.translation.copy());row=register(root,'light',['set_brightness','set_warmth','off'],mode='entity_material_and_light');row['state']={'on':True};row['material_override']='clone or instance material per logical entity in renderer, not shared-material mutation'
bulbs=[o for o in s.objects if o.type=='MESH' and 'lantern' in o.name.lower() and o.active_material and o.active_material.use_nodes and o.active_material.node_tree.nodes.get('Principled BSDF') and o.active_material.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value>0 and not any(a.get('decision_entity_id','').startswith('light.') for a in ancestors(o))]
for bulb in bulbs:
 parent=bulb.parent;p=bulb.matrix_world.translation.copy();group=[bulb]
 for o in list(parent.children) if parent else list(s.objects):
  if o==bulb or o.type not in ['MESH','CURVE'] or 'lantern' not in o.name.lower() or not any(x in o.name.lower() for x in ['ring','hanging','rib']):continue
  if (o.matrix_world.translation-p).length<.23:group.append(o)
 root=grouping('hanging_light_'+slug(bulb.name),group,p,parent);row=register(root,'light',['set_brightness','set_warmth','off'],mode='entity_material_and_light');row['material_override']='per-entity material instance required'

# Each composed plant/tree can react through a foliage pivot, without moving its pot or trunk.
plants=[o for o in s.objects if o.type=='EMPTY' and o.get('entity_id') and o.name.startswith(('CP07 garden cluster','garden_planter_','district_tree_','lantern_tree','pond_willow')) and o.name!='pond_willow_canopy']
for root in plants:
 kind='tree' if root.name.startswith(('district_tree','lantern_tree','pond_willow')) else 'plant';register(root,kind,['sway','settle','bloom_state'],mode='foliage_part_and_material')
 if root.name=='pond_willow':
  p=bpy.data.objects['pond_willow_canopy'];p['decision_part_id']='foliage';p['decision_owner']=root['decision_entity_id'];p['control_kind']='rotation';p['control_axis']='local X/Y'
 else:
  leafs=[o for o in root.children if o.type in ['MESH','CURVE'] and any(k in o.name.lower() for k in ['leaf','blossom','bloom','petal','flower stem','canopy'])]
  if leafs:part(root,'foliage',leafs,root.matrix_world@Vector((0,0,.25 if kind=='plant' else 1.3)),'rotation','local X/Y')
for o in [x for x in s.objects if x.type=='EMPTY' and x.get('entity_id') and ('bench' in x.name.lower() or x.name.startswith(('musician_stool','listener_seat','station_seat_','CP06 dining chair')))]:
 if o.get('decision_entity_id'):continue
 row=register(o,'seat',['reserve','release','occupy','vacate'],mode='occupancy_and_optional_root');row['state']={'occupied_by':o.get('occupied_by','resident.quiet_reader' if o.name=='CP05_overlook_bench' else None)}
register(bpy.data.objects['greenhouse_potting_table'],'workstation',['prepare','place_pot','clear'],mode='prop_state_and_interaction_target')

# Spatial targets are authored positions, with coverage explicitly separated from navmesh validation.
anchors=[]
def anchor(aid,p,role,verified=False):anchors.append({'id':aid,'position':list(p),'role':role,'static_local_route_checked':verified,'navigation_validated':False})
for key,pts in rec['routes'].items():
 for i in [0,len(pts)-1]:anchor(key+('_start' if i==0 else '_end'),Vector(pts[i]),key,True)
for name in ['musician','listener','quiet_reader','station_attendant','gardener','assistant_gardener','water_visitor','cyclist']:anchor(name+'_activity',bpy.data.objects[name].matrix_world.translation,'activity_origin')
for name in ['musician_stool','listener_seat','station_seat_A','station_seat_B','greenhouse_potting_table']:anchor(name+'_approach',bpy.data.objects[name].matrix_world@Vector((0,-.7,0)),'approach')
path_data={'existing_local_routes':rec['routes'],'rail_curve_objects':[o.name for o in s.objects if o.name.startswith('CP02 continuous rail')],'water_boundary':{'object':'CP02 pond','footprint_role':'swim/boat region, not a pedestrian floor'},'status':'Design targets and existing static local route samples. No navmesh, avoidance, schedules or crowd solver.'}
for row in entities:
 root=bpy.data.objects[row['blender_object']];row['position']=list(root.matrix_world.translation)
 row['parts']=[{'id':o['decision_part_id'],'blender_object':o.name,'control':o.get('control_kind'),'axis':o.get('control_axis'),'local_matrix':[list(r) for r in o.matrix_local]} for o in root.children_recursive if o.get('decision_part_id') and o.get('decision_owner')==row['id']]
 parent=next((a.get('decision_entity_id') for a in ancestors(root)[1:] if a.get('decision_entity_id')),None);row['parent_entity']=parent
 if parent:row['attachment_status']='actual Blender parent hierarchy retained'
 row['anchors']=[a['id'] for a in anchors if root.name in a['id']]
 root['decision_manifest']='decision-entities.json'
 for action in row['actions']:
  aid=action['id'];action['preconditions']='Executor must check current state, target eligibility and conflicts.'
  if aid in ['walk_to','fly_to','swim_to','drift_to','travel_route','ride_route','moor','stop_at_station']:action['parameters']={'target':'One ID selected from the currently eligible anchor/path candidates; never an unconstrained invented coordinate'}
  elif aid=='set_brightness':action['parameters']={'level':['off','low','medium','high']}
  elif aid=='set_warmth':action['parameters']={'palette':['warm','neutral','cool']}
  elif aid=='set_spin':action['parameters']={'speed':['stopped','slow','medium','fast']}
  elif aid=='set_rain':action['parameters']={'level':['dry','drizzle','rain']}
  elif aid=='bloom_state':action['parameters']={'phase':['closed','opening','open']}
  else:action['parameters']={'target':'Optional eligible entity/anchor ID supplied by the world-state candidate builder'}
  if aid in ['walk_to','ride','ride_route']:action['parameters']['pace']=['slow','normal']
registry={'schema_version':1,'purpose':'Authoring contract for later finite-action Decision -> validated local executor integration','provider_agnostic':True,'source_checkpoint':'CP08','api_called':False,'animation_or_simulation_implemented':False,'entity_count':len(entities),'entities':entities,'anchors':anchors,'paths':path_data,'rules':['Decision outputs stable entity IDs and finite action IDs.','Executor must validate preconditions, occupancy, reachability and conflicts before animation.','Render frame updates do not require a new Decision call.','Visual assets carry stable IDs; static batching must not swallow dynamic entity or part boundaries.','Declared actions are not working animation clips.','Movement must follow continuous validated routes; hiding or teleporting actors is not a substitute for passage clearance.','Unregistered scenic details are static decoration, not eligible action candidates. Any newly movable object must first gain an ID, binding and validated action.'],'unimplemented':['provider adapter for this town','state simulation','skeletons and clips','navmesh and crowd avoidance','runtime material/light control','browser FPS measurement']}
(OUT/'decision-entities.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2));s['decision_entity_schema']=1;s['decision_status']='IDs, hierarchy, control pivots and action declarations only; no Decision API integration executed'
rec['decision_authoring']={'entity_count':len(entities),'manifest':'decision-entities.json','status':'authoring contract only','api_calls':0};(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp08.blend'));print('CP08_DECISION_BINDINGS_SAVED',len(entities),flush=True)
