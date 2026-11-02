import bpy,json,math,ast
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'work/art-cp16';OUT=ROOT/'outputs/art-checkpoint-16';s=bpy.context.scene;tea=bpy.data.objects['tea_house'];col=bpy.data.collections['02_Teahouse_Market'];reg=json.loads((ROOT/'outputs/art-checkpoint-15/decision-entities.json').read_text());changes={'removed':[],'modified':[],'added':[]};initial=set(s.objects.keys())
exec(compile((ROOT/'work/art-cp15/scene_signature.py').read_text(),'<signature>','exec'));before=scene_signature(s)
src=ast.parse((ROOT/'work/art-cp13/build_revision.py').read_text());exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef)and n.name in ['mat','mesh','box','lathe','beam']],type_ignores=[]),'<helpers>','exec'))
cube=bpy.data.meshes['Shared cube'];wood=bpy.data.materials['Cedar frame'];edge=bpy.data.materials['Cut wood edges'];ivory=bpy.data.materials['CP13 tea ceramic'];jade=bpy.data.materials['CP13 tea ceramic jade'];linen=bpy.data.materials['Washi | pale edge'];indigo=bpy.data.materials['CP13 indigo textile'];basketmat=mat('CP16 folded basket paper',(.38,.23,.10));D=.12
# Return halfway from CP14's raised roof toward CP13; floor, table/actor and awning positions stay.
for o in list(tea.children):
 if o.name=='tea_house roof'or o.name.startswith('CP02 tea dormer'):o.location.z-=D
 if o.name in ['tea_house front lintel','CP06 upper exit header']:o.location.z-=D
 if o.name.startswith(('tea_house timber','CP06 upper exit door frame')):o.location.z-=D/2;o.scale.z-=D
room=bpy.data.objects['CP06_upper_dining_layout']
for o in room.children:
 if o.name.startswith(('CP06 upper back wall','CP06 upper west wall','CP06 upper east door jamb wall','CP06 upper front timber')):o.location.z-=D/2;o.scale.z-=D
# Keep the orange visible bulbs/light sources in place; shorten only their attachment cords.
for o in s.objects:
 if o.name.startswith('CP14 pendant cord'):o.location.z-=D/2;o.scale.z-=D
 if o.name.startswith('CP14 pendant bracket'):o.location.z-=D
# Lower the curtain top with the roof while retaining the hem's world height and seated readability.
curtain=bpy.data.objects['CP15_upper_noren'];curtain.location.z-=D
for node in curtain.children:
 if not node.get('decision_part_id'):continue
 meshes=[o for o in node.children_recursive if o.type=='MESH'];height=-min(v.co.z for o in meshes for v in o.data.vertices);factor=(height-D)/height
 for o in meshes:
  o.data=o.data.copy()
  for v in o.data.vertices:v.co.z*=factor
  o.data.update()
for name in ['CP15_restaurant_wind_chime','CP15_restaurant_crane_mobile']:bpy.data.objects[name].location.z-=D
# Fill the gap with a small fixed tea-service cabinet, without shifting either dining arrangement.
cab=bpy.data.objects.new('CP16_upper_tea_cabinet',None);col.objects.link(cab);cab.parent=tea;cab.location=(-.15,-1.78,2.255);cab['art_role']='Static central tea-service dressing; not an action candidate'
box('CP16 tea cabinet top',(0,0,.675),(.76,.43,.055),edge,cab,bevel=.007)
box('CP16 tea cabinet lower shelf',(0,0,.19),(.65,.34,.04),edge,cab,bevel=.004)
box('CP16 tea cabinet rear',(0,.16,.42),(.65,.035,.46),wood,cab)
for x in [-.325,.325]:
 box('CP16 tea cabinet side',(x,0,.42),(.035,.36,.46),wood,cab)
 for y in [-.145,.145]:box('CP16 tea cabinet foot',(x,y,.095),(.045,.045,.182),wood,cab,bevel=.003)
# Open slatted lower doors, a folded basket and dishes give the cabinet depth at close range.
for x in [-.275,-.165,-.055,.055,.165,.275]:box('CP16 cabinet fine slat',(x,-.175,.40),(.024,.022,.37),edge,cab)
lathe('CP16 paper basket',[(.085,.211),(.11,.24),(.115,.36),(.10,.38),(.10,.36),(.095,.25)],10,basketmat,cab,(-.12,0,0))
for z in [.26,.31,.36]:lathe('CP16 basket narrow band',[(.116,z),(.116,z+.012)],10,edge,cab,(-.12,0,0))
for z in [.23,.265,.30]:lathe('CP16 stacked lower saucer',[(.08,z),(.092,z+.008),(.08,z+.018)],12,ivory,cab,(.14,0,0))
# The upper tray bridges the empty space below the middle light without becoming another light source.
box('CP16 dark serving tray',(0,.015,.715),(.60,.32,.025),wood,cab,bevel=.005)
lathe('CP16 central tea pot',[(.045,0),(.085,.035),(.073,.105),(.043,.14)],12,jade,cab,(.12,.035,.73))
lathe('CP16 central tea lid',[(.05,0),(.051,.012),(.018,.025)],12,ivory,cab,(.12,.035,.87))
beam('CP16 teapot spout',(.17,.035,.79),(.28,.035,.86),.027,jade,cab)
for z in [.73,.79]:lathe('CP16 central stacked cup',[(.035,0),(.045,.055),(.035,.057),(.028,.01)],12,ivory,cab,(-.21,.05,z))
for j in range(3):box('CP16 folded tea linen',(-.13,-.095,.745+j*.018),(.24,.14,.018),linen,cab,bevel=.002)
box('CP16 linen indigo tie',(-.13,-.095,.794),(.035,.145,.006),indigo,cab)
box('CP16 small tea card',(.28,.10,.82),(.105,.025,.16),edge,cab,bevel=.003)
mesh('CP16 tea card leaf',[(.28,.084,.875),(.25,.083,.835),(.28,.080,.805),(.31,.083,.835)],[(0,1,2),(0,2,3)],[linen],cab)
bpy.context.view_layer.update()
for me in bpy.data.meshes:
 if not me.users or not me.polygons or me.uv_layers or not me.name.startswith('CP16'):continue
 uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  axes=[j for j in range(3)if j!=max(range(3),key=lambda j:abs(p.normal[j]))]
  for li in p.loop_indices:v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
for e in reg['entities']:
 e['position']=list(bpy.data.objects[e['blender_object']].matrix_world.translation)
 for p in e['parts']:p['local_matrix']=[list(r)for r in bpy.data.objects[p['blender_object']].matrix_local]
reg['source_checkpoint']='CP16';reg['static_decoration_note']='Central tea-service cabinet is fixed scenic dressing. Register identities/constraints before making its vessels individually movable.';(OUT/'decision-entities.json').write_text(json.dumps(reg,indent=2))
after=scene_signature(s);changes['modified']=[n for n in before['objects']if before['objects'][n]!=after['objects'].get(n)];changes['added']=sorted(set(s.objects.keys())-initial);changes['scope']='Restaurant upper roof/header/support height reduced by .12 tea-local Z; curtains compressed to keep their hem height, hanging ornaments follow roof; central static tea cabinet fills the gap. Existing actors, tables, awnings, camera and light-source settings preserved.';changes['height_reduction_local']=D;changes['height_reduction_world']=D*.86;changes['cabinet']={'root':cab.name,'tea_local_position':list(cab.location),'top_width':.76,'top_depth':.43,'static_decor':True};changes['diner_contract']='Two CP15 goals retained: behind_noren and dining_seat; no new semantic actions or animation.';(OUT/'revision-record.json').write_text(json.dumps(changes,indent=2))
s['checkpoint']='CP16 | slightly lower upper story and central tea cabinet';s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.use_denoising=True;s.cycles.samples=28;s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100;bpy.ops.wm.save_as_mainfile(filepath=str(W/'draft.blend'))
main=s.camera;f=main.rotation_euler.to_quaternion()@Vector((0,0,-1));d=bpy.data.cameras.new('CP16 restaurant draft');d.type='ORTHO';d.ortho_scale=8.1;c=bpy.data.objects.new(d.name,d);s.collection.objects.link(c);c.rotation_euler=main.rotation_euler;c.location=tea.matrix_world@Vector((0,-1.05,2.02))-f*30;s.camera=c;s.render.resolution_x=1150;s.render.resolution_y=850;s.render.filepath=str(W/'draft-restaurant.png');bpy.ops.render.render(write_still=True);print('CP16_DRAFT_READY',flush=True)
