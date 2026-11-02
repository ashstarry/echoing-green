import bpy,json,math,ast,copy
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'work/art-cp15';OUT=ROOT/'outputs/art-checkpoint-15';s=bpy.context.scene;tea=bpy.data.objects['tea_house'];col=bpy.data.collections['02_Teahouse_Market'];changes={'removed':[],'modified':[],'added':[]};initial=set(s.objects.keys());reg=json.loads((ROOT/'outputs/art-checkpoint-14/decision-entities.json').read_text());old_ids={e['id']for e in reg['entities']}
exec(compile((ROOT/'work/art-cp14/scene_signature.py').read_text(),'<signature>','exec'));before=scene_signature(s)
src=ast.parse((ROOT/'work/art-cp13/build_revision.py').read_text());exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef)and n.name in ['mat','mesh','box','lathe','beam']],type_ignores=[]),'<helpers>','exec'))
cube=bpy.data.meshes['Shared cube'];wood=bpy.data.materials['Cedar frame'];edge=bpy.data.materials['Cut wood edges'];ivory=bpy.data.materials['Washi | pale edge'];gold=bpy.data.materials['CP13 gilded paper edge'];indigo=mat('CP15 noren indigo',(.055,.12,.20));indigo_shade=mat('CP15 noren folded blue',(.038,.085,.145));hem=mat('CP15 warm paper hem',(.66,.58,.41));celadon=mat('CP15 celadon paper chime',(.21,.38,.34));crane_paper=mat('CP15 ivory crane paper',(.82,.72,.54));crane_blush=mat('CP15 coral crane paper',(.62,.29,.18))
def empty(name,parent,p=(0,0,0)):
 o=bpy.data.objects.new(name,None);col.objects.link(o);o.parent=parent;o.location=p;return o
def declare(eid,kind,o,label,actions):
 o['decision_entity_id']=eid;o['decision_kind']=kind;o['decision_actions']=json.dumps(actions);o['decision_status']='authoring_only_runtime_unimplemented'
 return {'id':eid,'kind':kind,'label':label,'blender_object':o.name,'position':list(o.matrix_world.translation),'parent_entity':None,'parts':[],'actions':[{'id':a,'implementation':'declared only; executor/animation unimplemented'}for a in actions],'anchors':[],'runtime_ready':False}
def part(root,pid,p=(0,0,0)):
 n=empty(root.name+'__'+pid,root,p);n['decision_part_id']=pid;n['decision_owner']=root['decision_entity_id'];n['control_kind']='rotation';n['control_axis']='local X';n['authoring_rotation_limit_degrees']=8;return n
def partrow(n):return {'id':n['decision_part_id'],'blender_object':n.name,'control':'rotation','axis':'local X','local_matrix':[list(r)for r in n.matrix_local],'authoring_angle_limit_degrees':8}
# Make the retained blue/cream awnings project visibly beyond CP14's deeper balcony.
awnings=[]
for o in tea.children:
 if o.name.startswith('Awning'):o.location.y-=.45;awnings.append(o.name)
# Seven split, creased noren panels screen the empty upper room. They are behind the diners.
curtain=empty('CP15_upper_noren',tea,(0,-1.23,3.86));entry=declare('curtain.restaurant_upper_noren','curtain',curtain,'Upper dining indigo noren',['sway','settle']);panels=[]
segments=[(-2.54,-1.90),(-1.87,-1.23),(-1.20,-.55),(-.48,.48),(.55,1.20),(1.23,1.87),(1.90,2.54)]
for i,(a,b)in enumerate(segments):
 width=b-a;length=.86 if i==3 else 1.03+(.025 if i%2 else 0);node=part(curtain,'panel_%02d'%i,((a+b)/2,0,0));panels.append(node);vs=[]
 for j in range(5):
  x=-width/2+j*width/4;y=.018 if j%2 else -.009;vs.extend([(x,y,0),(x,y-.006,-length)])
 fs=[(2*j,2*j+1,2*j+3,2*j+2)for j in range(4)];o=mesh('CP15 folded noren panel',vs,fs,[indigo,indigo_shade],node);o.modifiers.new('Paper cloth edge','SOLIDIFY').thickness=.007
 for poly in o.data.polygons:poly.material_index=poly.index%2
 # A narrow warm hem follows the actual folds, not a flat overlay.
 v=[]
 for j in range(5):
  x=-width/2+j*width/4;y=(.018 if j%2 else -.009)-.008;v.extend([(x,y,-length+.025),(x,y,-length+.045)])
 mesh('CP15 noren hem',v,[(2*j,2*j+1,2*j+3,2*j+2)for j in range(4)],[hem],node)
 if i in [1,5]:
  vs=[(0,-.027,-.55),(-.085,-.027,-.66),(0,-.035,-.75),(.085,-.027,-.66),(0,-.052,-.66)];mesh('CP15 tea leaf crest',vs,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],[ivory],node)
beam('CP15 noren hanging rod',(-2.61,0,.02),(2.61,0,.02),.025,wood,curtain)
for x in [-2.57,-.52,.52,2.57]:beam('CP15 noren rod bracket',(x,-.17,.02),(x,0,.02),.018,wood,curtain)
entry['parts']=[partrow(n)for n in panels];entry['state']={'pose':'resting'};entry['collision_policy']='Flexible portal screen. A future pre-authored enter/exit transition handles the curtain and occlusion; current closed geometry is not a proven rigid walking corridor.';reg['entities'].append(entry)
# Ornament one: a small faceted paper/ceramic-style wind bell with a paper wish strip.
chime=empty('CP15_restaurant_wind_chime',tea,(-1.02,-1.64,3.87));entry=declare('ornament.restaurant_wind_chime','hanging_ornament',chime,'Celadon wind bell and paper strip',['sway','settle']);pend=part(chime,'pendulum',(0,0,-.045));beam('CP15 chime hanging hook',(0,0,0),(0,.22,0),.012,wood,chime);beam('CP15 chime thread',(0,0,0),(0,0,-.035),.004,hem,chime)
profile=[(.023,-.02),(.066,-.045),(.095,-.10),(.105,-.16),(.093,-.16),(.083,-.10),(.056,-.05),(.023,-.03)];lathe('CP15 folded wind bell',profile,10,celadon,pend)
lathe('CP15 wind bell paper rim',[(.105,-.16),(.106,-.15),(.096,-.147)],10,hem,pend);beam('CP15 clapper thread',(0,0,-.03),(0,0,-.19),.003,wood,pend)
lathe('CP15 bell wooden clapper',[(.012,-.14),(.023,-.16),(.012,-.18)],8,wood,pend)
vs=[(-.04,-.004,-.20),(.04,-.004,-.20),(-.037,-.013,-.49),(.037,-.013,-.49),(0,-.026,-.35)];mesh('CP15 wind bell wish paper',vs,[(0,1,4),(1,3,4),(3,2,4),(2,0,4)],[ivory],pend).modifiers.new('Paper strip thickness','SOLIDIFY').thickness=.004
mesh('CP15 wish paper simple leaf',[(0,-.030,-.29),(-.016,-.032,-.34),(0,-.034,-.38),(.016,-.032,-.34)],[(0,1,2),(0,2,3)],[indigo],pend)
entry['parts']=[partrow(pend)];entry['state']={'pose':'still'};reg['entities'].append(entry)
# Ornament two: a small suspended pair of real folded cranes, not a light.
mobile=empty('CP15_restaurant_crane_mobile',tea,(1.94,-1.57,3.87));entry=declare('ornament.restaurant_paper_cranes','hanging_ornament',mobile,'Pair of hanging paper cranes',['sway','settle']);swing=part(mobile,'mobile',(0,0,-.045));beam('CP15 crane mobile hook',(0,0,0),(0,.20,0),.012,wood,mobile);beam('CP15 crane mobile suspension',(0,0,0),(0,0,-.07),.004,hem,mobile)
for i,(x,z,material)in enumerate([(-.055,-.21,crane_paper),(.065,-.43,crane_blush)]):
 bird=empty('CP15 hanging crane '+str(i),swing,(x,0,z));bird.rotation_euler.z=.28 if i==0 else -.35
 vs=[(-.075,0,0),(.07,0,.02),(0,-.037,-.035),(0,.037,-.035),(0,0,.045)];mesh('CP15 crane folded body',vs,[(0,2,4),(0,4,3),(0,3,2),(1,4,2),(1,3,4),(1,2,3)],[material],bird)
 for sign in [-1,1]:
  o=mesh('CP15 crane folded wing',[(-.03,0,.025),(-.035,sign*.16,.12),(.06,sign*.07,.025),(0,sign*.065,.075)],[(0,1,3),(1,2,3),(2,0,3)],[material],bird);o.modifiers.new('Folded paper edge','SOLIDIFY').thickness=.003
 o=mesh('CP15 crane neck and beak',[(.04,-.012,.02),(.04,.012,.02),(.10,0,.14),(.155,0,.105),(.092,0,.10)],[(0,1,2),(0,2,4),(1,4,2),(2,3,4)],[material],bird);o.modifiers.new('Paper neck thickness','SOLIDIFY').thickness=.003
 mesh('CP15 crane pointed tail',[(-.05,-.015,.02),(-.05,.015,.02),(-.15,0,.12),(-.085,0,.065)],[(0,2,3),(1,3,2)],[material],bird)
 beam('CP15 crane fine string',(x,0,-.04),(x,0,z+.045),.003,hem,swing)
entry['parts']=[partrow(swing)];entry['state']={'pose':'still'};reg['entities'].append(entry)
# Latest user steering: each upper diner exposes only two semantic goals.
bpy.context.view_layer.update();diner_contract=[]
for i in range(2):
 obj=bpy.data.objects['CP14_upper_diner_'+str(i)];e=next(e for e in reg['entities']if e['id']==obj['decision_entity_id']);seat=list(obj.matrix_world.translation);hidden=list(tea.matrix_world@Vector((obj.location.x+.15,-.45,2.255)))
 e['actions']=[{'id':'retreat_behind_curtain','target_anchor':'behind_noren','implementation':'declared only; short transition and portal visibility unimplemented'},{'id':'come_out_to_dine','target_anchor':'dining_seat','implementation':'declared only; short transition to the seat unimplemented'}]
 e['anchors']=[{'id':'dining_seat','position':seat},{'id':'behind_noren','position':hidden}];e['state']['activity']='dining';e['goal_states']=['behind_noren','dining'];e['interaction_note']='User-selected two-endpoint behavior. Internal walk/sit and curtain passage are a short local transition, not additional semantic decisions. Visual presence can end in the curtained occlusion region; full indoor life is not required.';obj['decision_actions']=json.dumps([a['id']for a in e['actions']]);diner_contract.append({'entity':e['id'],'anchors':e['anchors'],'goal_states':e['goal_states']})
for me in bpy.data.meshes:
 if not me.users or not me.polygons or me.uv_layers or not me.name.startswith('CP15'):continue
 uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  axes=[j for j in range(3)if j!=max(range(3),key=lambda j:abs(p.normal[j]))]
  for li in p.loop_indices:v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
bpy.context.view_layer.update()
for e in reg['entities']:e['position']=list(bpy.data.objects[e['blender_object']].matrix_world.translation)
reg['source_checkpoint']='CP15';reg['entity_count']=len(reg['entities']);reg['parts_count']=sum(len(e['parts'])for e in reg['entities']);reg['cp15_new_entity_ids']=sorted({e['id']for e in reg['entities']}-old_ids);(OUT/'decision-entities.json').write_text(json.dumps(reg,indent=2))
after=scene_signature(s);changes['modified']=[n for n in before['objects']if before['objects'][n]!=after['objects'].get(n)];changes['added']=sorted(set(s.objects.keys())-initial);changes['scope']='Retained blue/white awnings shifted .45 local Y toward viewer; added upper noren and two non-luminous ornaments; upper diners now have two semantic goals. CP14 lighting, roof height, camera, people positions and furniture kept.';changes['awning_objects']=awnings;changes['noren_panels']=len(panels);changes['new_entities']=reg['cp15_new_entity_ids'];changes['diner_interaction_contract']=diner_contract;changes['runtime_implemented']=False;(OUT/'revision-record.json').write_text(json.dumps(changes,indent=2))
s['checkpoint']='CP15 | restored striped awnings, noren and two ornaments';s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.samples=28;s.cycles.use_denoising=True;s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100;bpy.ops.wm.save_as_mainfile(filepath=str(W/'draft.blend'))
main=s.camera;f=main.rotation_euler.to_quaternion()@Vector((0,0,-1));d=bpy.data.cameras.new('CP15 restaurant draft');d.type='ORTHO';d.ortho_scale=8.1;c=bpy.data.objects.new(d.name,d);s.collection.objects.link(c);c.rotation_euler=main.rotation_euler;c.location=tea.matrix_world@Vector((0,-1.05,2.02))-f*30;s.camera=c;s.render.resolution_x=1150;s.render.resolution_y=850;s.render.filepath=str(W/'draft-restaurant.png');bpy.ops.render.render(write_still=True);print('CP15_DRAFT_READY',flush=True)
