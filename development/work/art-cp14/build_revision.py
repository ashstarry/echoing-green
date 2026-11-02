import bpy,json,math,ast,copy
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'work/art-cp14';OUT=ROOT/'outputs/art-checkpoint-14';s=bpy.context.scene;tea=bpy.data.objects['tea_house'];col=bpy.data.collections['02_Teahouse_Market'];lightcol=bpy.data.collections['10_Lighting'];peoplecol=bpy.data.collections['08_Residents_SCALE_PROXIES'];changes={'removed':[],'modified':[],'added':[]};initial=set(s.objects.keys());reg=json.loads((ROOT/'outputs/art-checkpoint-13/decision-entities.json').read_text());old_ids={e['id']for e in reg['entities']}
exec(compile((ROOT/'work/art-cp13/scene_signature.py').read_text(),'<signature>','exec'));before=scene_signature(s)
src=ast.parse((ROOT/'work/art-cp13/build_revision.py').read_text());exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef)and n.name in ['mat','mesh','box','lathe','beam','erase','area']],type_ignores=[]),'<helpers>','exec'))
cube=bpy.data.meshes['Shared cube'];wood=bpy.data.materials['Cedar frame'];edge=bpy.data.materials['Cut wood edges'];ivory=bpy.data.materials['CP13 tea ceramic'];jade=bpy.data.materials['CP13 tea ceramic jade'];gold=bpy.data.materials['CP13 gilded paper edge'];skin=mat('CP14 warm paper skin',(.68,.42,.25));hair=mat('CP14 charcoal folded hair',(.035,.045,.055));coatA=mat('CP14 diner sage coat',(.22,.35,.29));coatB=mat('CP14 diner berry coat',(.40,.10,.095));pants=bpy.data.materials['CP13 indigo textile'];shoe=mat('CP14 paper shoes',(.055,.038,.028));eye=mat('CP14 ink eyes',(.018,.014,.012));fabric=mat('CP14 soft chair cushion',(.49,.28,.12));paperlight=mat('CP14 ribbed lantern warm washi',(.64,.26,.055),.92,(1,.34,.045))
def empty(name,parent,position=(0,0,0),yaw=0,collection=col):
 o=bpy.data.objects.new(name,None);collection.objects.link(o);o.parent=parent;o.location=position;o.rotation_euler.z=yaw;return o
def sphere(name,p,scale,m,parent):
 data=bpy.data.meshes['Shared sphere'];o=bpy.data.objects.new(name,data);peoplecol.objects.link(o);o.parent=parent;o.location=p;o.scale=scale
 for slot in o.material_slots:slot.link='OBJECT';slot.material=m
 return o
def row(eid,kind,obj,label,actions):
 obj['decision_entity_id']=eid;obj['decision_kind']=kind;obj['decision_status']='authoring_only_runtime_unimplemented';obj['decision_actions']=json.dumps(actions)
 return {'id':eid,'kind':kind,'blender_object':obj.name,'label':label,'position':list(obj.matrix_world.translation),'parent_entity':None,'parts':[],'actions':[{'id':a,'implementation':'declared; animation/state executor unimplemented','preconditions':'Check current state, target occupancy and spatial constraints'}for a in actions],'anchors':[],'runtime_ready':False}
# Give seated bodies enough real floor in front of the roof, while keeping the main camera/full roof.
floor=bpy.data.objects['Tea balcony floor'];floor.location.y=-1.62;floor.scale.y=1.11
for o in list(tea.children):
 if o.name.startswith(('Balcony baluster','Balcony long rail')):o.location.y-=.36
 if o.name.startswith(('CP05 balcony flower','CP05 balcony foliage','CP07 balcony flower','CP07 balcony bloom')):o.location.y-=.53
 if o.name.startswith(('CP13 folded balcony cloth','CP13 tea-leaf cloth crest')):o.location.y-=.36
 if o.name.startswith(('CP13 balcony tea ledge','CP13 ledge bracket','CP13 shallow tea saucer','CP13 small tea cup','CP13 tea pot','CP13 rolled bamboo blind','CP13 indigo short noren','CP13 restaurant indigo sign','CP13 sign brass dot')):erase(o)
# Keep the side screens at the outer edge of each bay, clear of the two rearward exits.
for o in tea.children:
 if o.name.startswith(('CP13 stacked upper shoji','CP13 folded screen border','CP13 folded screen lattice')):o.location.x+=-.34 if o.location.x<0 else .34
# Reshape the 11 old light identities into five slim paper pendants and six discreet underside glows.
lamproots=sorted([o for o in s.objects if o.name.startswith('hanging_light_cp05_restaurant_paper_lantern_paper')],key=lambda o:o.name);assert len(lamproots)==11
lamp_positions=[(-2.57,-1.69,3.38),(-.18,-1.72,3.42),(2.53,-1.72,3.35),(-2.90,-.65,3.25),(-2.90,.62,3.35)];light_changes=[]
for i,root in enumerate(lamproots):
 light=next((c for c in root.children if c.type=='LIGHT'),None)
 for ch in list(root.children):
  if ch.type!='LIGHT':erase(ch)
 root.parent=tea;root.matrix_parent_inverse=Matrix.Identity(4);root.matrix_basis=Matrix.Identity(4);root.location=lamp_positions[i]if i<5 else(-2.10+(i-5)*.84,-2.04,2.16)
 if i<5:
  lathe('CP14 narrow folded paper pendant',[(.07,-.25),(.11,-.20),(.115,-.04),(.09,.04),(.055,.06)],8,paperlight,root)
  for z,r in [(-.25,.071),(.05,.06)]:lathe('CP14 pendant dark collar',[(r,z),(r,z+.025)],8,wood,root)
  beam('CP14 pendant cord',(0,0,.075),(0,0,.29),.009,wood,root)
  for k in range(8):
   a=k*math.tau/8;beam('CP14 pendant paper rib',(.071*math.cos(a),.071*math.sin(a),-.24),(.11*math.cos(a),.11*math.sin(a),-.04),.004,gold,root)
  label='Slim folded pendant '+str(i)
  if light:light.parent=root;light.matrix_parent_inverse=Matrix.Identity(4);light.matrix_basis=Matrix.Identity(4);light.location=(0,-.10,-.32);light.data.energy=3.2;light.data.color=(1,.43,.09);light.data.shadow_soft_size=.18
 else:
  box('CP14 recessed amber paper light',(0,0,0),(.24,.08,.055),paperlight,root)
  label='Concealed balcony warm glow '+str(i-5)
  if light:light.parent=root;light.matrix_parent_inverse=Matrix.Identity(4);light.matrix_basis=Matrix.Identity(4);light.location=(0,-.08,-.09);light.data.energy=2.1;light.data.color=(1,.43,.09);light.data.shadow_soft_size=.23
 e=next(e for e in reg['entities']if e['id']==root['decision_entity_id']);e['label']=label;e['authoring_note']='Existing light ID retained; redesigned placement/form. Runtime per-instance material control remains unimplemented.';light_changes.append({'id':e['id'],'style':'slim_pendant'if i<5 else'concealed_glow','tea_local_position':list(root.location)})
# Reuse the two existing chair identities. Tables become two authoring workstations.
room=bpy.data.objects['CP06_upper_dining_layout']
for o in list(room.children):
 if o.name.startswith(('CP06 dining table','CP06 dining cup')):erase(o)
seat_specs=[(-1.95,-1.60,math.pi/2),(.35,-1.60,math.pi/2)];tables=[];diners=[]
for i,(x,y,yaw)in enumerate(seat_specs):
 chair=bpy.data.objects['CP06 dining chair '+str(i)]
 for ch in list(chair.children):erase(ch)
 chair.parent=tea;chair.matrix_parent_inverse=Matrix.Identity(4);chair.matrix_basis=Matrix.Identity(4);chair.location=(x,y,2.255);chair.rotation_euler.z=yaw
 box('CP14 chair seat',(0,0,.53),(.49,.44,.065),edge,chair,bevel=.008)
 for dx in [-.19,.19]:
  for dy in [-.16,.16]:box('CP14 chair leg',(dx,dy,.25),(.045,.045,.50),wood,chair)
 for z in [.72,.88]:box('CP14 chair back slat',(0,.20,z),(.49,.045,.08),edge,chair)
 tx=x+.79;table=empty('CP14_upper_dining_table_'+str(i),tea,(tx,y,2.255));tables.append(table)
 box('CP14 dining table top',(0,0,.80),(.68,.54,.065),edge,table,bevel=.009)
 for dx in [-.25,.25]:
  for dy in [-.235,.235]:box('CP14 dining table leg',(dx,dy,.385),(.045,.045,.77),wood,table)
 lathe('CP14 dinner plate',[(.12,0),(.15,.015),(.12,.03)],12,ivory,table,(0,0,.835))
 for dx,dy in [(-.04,0),(.05,.015)]:sphere('CP14 small rice bun',(dx,dy,.905),(.045,.04,.035),ivory,table)
 for dy in [-.16,.16]:lathe('CP14 dinner tea cup',[(.038,0),(.048,.07),(.038,.071),(.030,.014)],12,jade,table,(.15,dy,.835))
 e=row('workstation.upper_dining_table_'+str(i),'workstation',table,'Upper dining tea table '+str(i),['serve_tea','clear_table']);e['constraints']=['Keep the rear route and chair exit zone clear'];reg['entities'].append(e)
 guest=empty('CP14_upper_diner_'+str(i),tea,(x,y,2.255),yaw,peoplecol);diners.append(guest);coat=coatA if i==0 else coatB
 # Local forward is -Y. Seat contact is deliberate with a .004-unit clearance.
 box('CP14 diner pelvis',(0,0,.635),(.29,.23,.13),pants,guest,bevel=.018)
 for side in [-1,1]:
  box('Seated thigh CP14',(side*.10,-.135,.622),(.13,.33,.11),pants,guest,bevel=.012)
  beam('CP14 diner shin',(side*.10,-.30,.60),(side*.10,-.32,.13),.105,pants,guest)
  box('Shoe CP14',(side*.10,-.39,.058),(.13,.25,.11),shoe,guest,bevel=.008)
 # Simple tapered coat, with separate head and shaped sleeves; still an unrigged proxy.
 vs=[(-.16,-.13,.67),(.16,-.13,.67),(.16,.12,.67),(-.16,.12,.67),(-.19,-.11,.96),(.19,-.11,.96),(.19,.09,.96),(-.19,.09,.96)];body=mesh('CP14 folded diner coat',vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],[coat],guest,peoplecol)
 sphere('CP14 diner neck',(0,-.01,.985),(.065,.065,.065),skin,guest);sphere('Head CP14',(0,-.025,1.105),(.145,.135,.145),skin,guest);sphere('CP14 diner folded hair',(0,.006,1.18),(.15,.13,.085),hair,guest)
 for side in [-1,1]:
  beam('CP14 diner upper sleeve',(side*.18,-.01,.91),(side*.22,-.23,.84),.105,coat,guest)
  beam('CP14 diner lower sleeve',(side*.22,-.23,.84),(side*.16,-.49,.90),.085,coat,guest)
  sphere('CP14 diner hand',(side*.16,-.535,.90),(.055,.065,.045),skin,guest)
  sphere('CP14 diner eye',(side*.045,-.155,1.12),(.009,.006,.012),eye,guest)
 # Differing collars give the two small silhouettes clear identities.
 box('CP14 diner scarf',(0,-.14,.91),(.09,.018,.18),ivory if i==0 else gold,guest)
 e=row('resident.upper_diner_'+str(i),'resident',guest,'Upper dining guest '+str(i),['dine','drink_tea','stand_up','walk_to','look_at','sit_down']);e['state']={'activity':'seated_dining','seat_id':chair['decision_entity_id'],'table_id':table['decision_entity_id']};e['requires_animation_binding']=True;e['constraints']=['Stand/turn in the reserved chair exit zone before entering the rear aisle','Respect seating occupancy and door/gallery yielding'];reg['entities'].append(e)
 next(e for e in reg['entities']if e['id']==chair['decision_entity_id'])['state']={'occupied_by':guest['decision_entity_id']}
# Replace the old front aisle with a rearward route; retain the exterior network unchanged.
bpy.context.view_layer.update();oldroutes=copy.deepcopy(json.loads((ROOT/'outputs/modeling-checkpoint-10/revision-record.json').read_text())['routes']);local=lambda p:list(tea.matrix_world@Vector(p));routes={k:v for k,v in oldroutes.items()if k not in ['dining_to_door','seat_to_aisle_left','seat_to_aisle_right']}
routes['dining_to_door']=[local((x,.20,2.255))for x in [-1.95,-.80,.35,1.50,2.35]]+[local((2.9,0,2.255)),local((3.18,0,2.255)),oldroutes['dining_to_door'][-1]]
for i,(x,y,yaw)in enumerate(seat_specs):routes['seat_to_aisle_'+('left'if i==0 else'right')]=[local((x,y,2.255)),local((x,-.95,2.255)),local((x,.20,2.255))]
# Art-directed interconnected warm pools; visible paper colors remain saturated.
for name,power in [('CP09 warm town fill',260),('Quiet front paper fill',430),('Warm lantern tree pool',205),('CP08 warm tree canopy bounce',103),('CP09 canopy warm key',46),('CP13 warm west street',54),('CP13 warm garden path',45),('CP13 warm station forecourt',34)]:
 o=bpy.data.objects.get(name)
 if o:o.data.energy=power
bpy.data.objects['Quiet front paper fill'].data.color=(.84,.83,.91);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.36
bg=bpy.data.materials['World backdrop | indigo'].node_tree.nodes['Principled BSDF'];bg.inputs['Emission Color'].default_value=(.04,.085,.21,1);bg.inputs['Emission Strength'].default_value=.46
for i in range(2):
 o=bpy.data.objects['CP13 dining nook amber '+str(i)];p=tea.matrix_world@Vector((seat_specs[i][0],-2.75,3.45));target=tea.matrix_world@Vector((seat_specs[i][0],-1.5,3.05));mw=Matrix.Translation(p)@(target-p).to_track_quat('-Z','Y').to_matrix().to_4x4();o.parent=tea;o.matrix_parent_inverse=tea.matrix_world.inverted();o.matrix_basis=mw;o.data.energy=15;o.data.size=1.7;o.data.color=(1,.49,.16)
for n in s.compositing_node_group.nodes:
 if n.bl_idname=='CompositorNodeGlare':n.inputs['Threshold'].default_value=1.05;n.inputs['Strength'].default_value=.22;n.inputs['Size'].default_value=.25
for me in bpy.data.meshes:
 if not me.users or not me.polygons or me.uv_layers:continue
 uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  axes=[j for j in range(3)if j!=max(range(3),key=lambda j:abs(p.normal[j]))]
  for li in p.loop_indices:v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
bpy.context.view_layer.update()
for e in reg['entities']:
 o=bpy.data.objects[e['blender_object']];e['position']=list(o.matrix_world.translation);e['lighting_bindings']=[l.name for l in s.objects if l.type=='LIGHT'and l.get('decision_owner')==e['id']]
reg['source_checkpoint']='CP14';reg['entity_count']=len(reg['entities']);reg['parts_count']=sum(len(e['parts'])for e in reg['entities']);reg['cp14_new_entity_ids']=sorted({e['id']for e in reg['entities']}-old_ids);(OUT/'decision-entities.json').write_text(json.dumps(reg,indent=2))
after=scene_signature(s);changes['modified']=[name for name in before['objects']if name not in changes['removed']and before['objects'][name]!=after['objects'].get(name)];changes['added']=sorted(set(s.objects.keys())-initial);changes['scope']='Restaurant upper lights and real dining guests, shallow balcony expansion, revised indoor exits, connected warmer art lighting; main camera and complete roof retained.';changes['lamp_recomposition']=light_changes;changes['balcony_depth']={'before':.75,'after':1.11,'units':'tea-house local units, not meters or net walkable area'};changes['routes']=routes;changes['diner_specs']=[{'actor':o.name,'seat':bpy.data.objects['CP06 dining chair '+str(i)].name,'table':tables[i].name,'tea_local_position':list(o.location)}for i,o in enumerate(diners)];changes['runtime_implemented']=False;(OUT/'revision-record.json').write_text(json.dumps(changes,indent=2))
s['checkpoint']='CP14 warm social balcony';s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.use_denoising=True;s.cycles.samples=28;s.render.resolution_x=1200;s.render.resolution_y=675;s.render.resolution_percentage=100;bpy.ops.wm.save_as_mainfile(filepath=str(W/'draft.blend'));s.render.filepath=str(W/'draft-overview.png');bpy.ops.render.render(write_still=True)
main=s.camera;f=main.rotation_euler.to_quaternion()@Vector((0,0,-1));d=bpy.data.cameras.new('CP14 dining draft');d.type='ORTHO';d.ortho_scale=8.1;c=bpy.data.objects.new(d.name,d);s.collection.objects.link(c);c.rotation_euler=main.rotation_euler;c.location=tea.matrix_world@Vector((0,-1.05,2.02))-f*30;s.camera=c;s.render.resolution_x=1150;s.render.resolution_y=850;s.render.filepath=str(W/'draft-restaurant.png');bpy.ops.render.render(write_still=True);print('CP14_DRAFT_READY',flush=True)
