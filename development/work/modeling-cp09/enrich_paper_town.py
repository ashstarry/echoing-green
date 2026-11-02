exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
import re
rec=json.loads((OUT/'revision-record.json').read_text());bpy.context.view_layer.update()
def slug(n):return re.sub('[^a-z0-9_]+','_',n.lower()).strip('_')
def tag(root,kind,actions):
 root['decision_entity_id']=kind+'.'+slug(root.name);root['decision_kind']=kind;root['decision_actions']=json.dumps(actions);root['decision_status']='authoring_only_runtime_unimplemented';root['movable']=True
def move(o,d):
 f=o.parent.matrix_world@o.matrix_parent_inverse if o.parent else Matrix.Identity(4);o.location+=f.to_3x3().inverted()@Vector(d)
def geometry_children_delete(root):
 for name in [o.name for o in root.children_recursive if o.type in ['MESH','CURVE']]:
  o=bpy.data.objects.get(name)
  if o:bpy.data.objects.remove(o,do_unlink=True)
def foliage_node(root):
 p=next((o for o in root.children if o.get('decision_part_id')=='foliage'),None)
 if p is None:p=asset(root.name+'__foliage');p.parent=root
 p.matrix_parent_inverse=Matrix.Identity(4);p.matrix_basis=Matrix.Identity(4);p['decision_part_id']='foliage';p['decision_owner']=root['decision_entity_id'];p['control_kind']='rotation';p['control_axis']='local X/Y';return p

blue=variant(blueleaf,'CP09 broad foliage | deep teal',(.10,.20,.25));sage2=variant(sage,'CP09 broad foliage | sage',(.31,.40,.32));ivleaf=variant(leafcream,'CP09 broad foliage | pale sage',(.57,.61,.43));peach=variant(pinklight,'CP09 blossom | warm blush',(.86,.49,.43));creamflower=variant(cream,'CP09 blossom | buttercream',(.88,.73,.43))
outline=[(0,-.52),(.18,-.40),(.29,-.17),(.26,.12),(.15,.37),(0,.54),(-.15,.37),(-.26,.12),(-.29,-.17),(-.18,-.40)];v=[(x,y,0) for x,y in outline]+[(0,.02,.065)];f=[(10,i,(i+1)%10) for i in range(10)];broad=bpy.data.meshes.new('CP09 shared broad folded leaf');broad.from_pydata(v,[],f);broad.materials.append(blue);broad.update()
def leaf_card(name,p,scale,mat,rot):
 o=bpy.data.objects.new(name,broad);COL.objects.link(o);o.location=p;o.scale=scale;o.rotation_euler=rot;o.parent=PARENT;setmat(o,mat);return o
# Reference-like exterior groups: broad low foliage plus a few full-size flowers, not tiny sprinkles.
outer_ids=rec['outer_planting']['clusters_kept'];COL=cols['07_Paper_Foliage'];outer_stats=[]
for i,name in enumerate(outer_ids):
 root=bpy.data.objects.get(name)
 if not root:continue
 geometry_children_delete(root);p=root.matrix_world.translation.copy();rr=p.dot(RIGHT);bb=p.dot(BACK);normal=(RIGHT*(rr/144)+BACK*((bb+.65)/(6.3*6.3))).normalized();move(root,normal*.24);root.scale=(1,1,1);root.rotation_euler.z=math.atan2(normal.y,normal.x)-PI/2;fol=foliage_node(root)
 with under(fol):
  for j in range(14):
   x=R.uniform(-.65,.65);y=R.uniform(-.035,.11);z=R.uniform(.16,.28);leaf_card('CP09 exterior broad paper leaf',(x,y,z),(R.uniform(.62,.85),R.uniform(.70,1.05),1),R.choice([blue,blue,blueleaf,sage2,ivleaf]),(R.uniform(.35,.75),R.uniform(-.15,.15),PI/2+R.uniform(-.22,.22)))
  for j in range(3 if i%3 else 4):
   x=R.uniform(-.48,.48);y=.12+R.uniform(0,.08);h=R.uniform(.40,.64);beam('CP09 exterior flower stalk',(x*.9,y,.03),(x,y,h),.009,sage2);bloom('CP09 exterior full flower',(x,y,h),R.uniform(.35,.48),R.choice([creamflower,cream,peach]),fol)
 outer_stats.append(root.name)
# Replace the scattered flat star-shaped cap experiment with a few grounded faceted paper rocks.
for name in [o.name for o in s.objects if o.name.startswith(('CP08 layered rim cap','CP07 layered bank paper face'))]:erase(bpy.data.objects[name])
COL=cols['00_Terrain']
for i in range(18):
 a=PI+PI*(i+.28)/18;p=rb(12.72*math.cos(a),-1.1+7.15*math.sin(a),.33);ob=ico('CP09 layered perimeter rock',p,(R.uniform(.55,.85),R.uniform(.26,.43),R.uniform(.25,.34)),R.choice([terr[3],terr[4]]));ob.rotation_euler.z=a+.2

# New pink-flowering rear garden has actual raised support behind the terrace rail.
COL=cols['06_Hillside'];bank=asset('CP09_rear_flower_bank',rb(4.75,7.42,Z),math.atan2(RIGHT.y,RIGHT.x))
with under(bank):
 box('CP09 rear bank paper foundation',(0,0,.59),(4.35,.65,1.18),terr[3]);box('CP09 rear garden soil',(0,0,1.20),(4.28,.61,.06),sage2)
COL=cols['07_Paper_Foliage'];new_trees=[]
for i,(r,b,h) in enumerate([(3.20,7.42,1.55),(4.28,7.48,1.72),(6.40,7.42,1.48)]):
 tree=asset('terrace_sakura_'+str(i),rb(r,b,1.84));tag(tree,'tree',['sway','settle','bloom_state']);new_trees.append(tree.name)
 with under(tree):
  taper('CP09 rear sakura trunk',(0,0,0),(.06,0,h*.78),.085,.028,woodlight,7)
  fol=foliage_node(tree)
  with under(fol):
   for j in range(7):
    a=j*2.399;rad=R.uniform(.35,.61);tip=Vector((rad*math.cos(a),rad*.68*math.sin(a),h*R.uniform(.68,.94)));taper('CP09 sakura branch',(0,0,h*.38),tip,.026,.009,woodlight,6)
    for k in range(5):
     q=tip+Vector((R.uniform(-.20,.20),R.uniform(-.15,.15),R.uniform(-.10,.16)));bloom('CP09 rear pink blossom',q,R.uniform(.29,.40),R.choice([pink,pinklight,peach,peach]),fol)
   for j in range(8):bloom('CP09 crown pink blossom',(R.uniform(-.35,.35),R.uniform(-.25,.25),h*R.uniform(.72,.92)),R.uniform(.29,.40),R.choice([pink,peach]),fol)

# Small lanterns along the rear garden reinforce the reference's inhabited night silhouette.
COL=cols['06_Hillside'];new_lights=[]
for i,r in enumerate([3.0,3.85,4.8,5.75,6.7]):
 root=asset('terrace_garden_lantern_'+str(i),rb(r,7.12,1.87));tag(root,'light',['set_brightness','set_warmth','off']);new_lights.append(root.name)
 with under(root):
  beam('CP09 garden lantern post',(0,0,0),(0,0,.80),.027,woodlight);lantern('CP09 warm garden lantern',(0,0,.74),.95)
  data=bpy.data.lights.new('CP09 rear garden spill '+str(i),'POINT');data.energy=7;data.color=(1,.45,.12);data.shadow_soft_size=.35;o=bpy.data.objects.new(data.name,data);COL.objects.link(o);o.parent=root;o.location=(0,0,.63)

# Dress the central planted seat, and give the focal lanterns more visual weight.
COL=cols['01_Plaza'];plaza=bpy.data.objects['plaza_ground'];tree=bpy.data.objects['lantern_tree']
with under(plaza):
 for i in range(30):
  a=i*2.4;r=R.uniform(.27,.76);leaf_card('CP09 planted tree groundcover',(r*math.cos(a),r*math.sin(a),.31),(.28,.40,.30),R.choice([sage,blue,sage2]),(.30,.1,a))
with under(tree):
 for i in range(6):
  a=i*PI/3;taper('CP09 natural root flare',(0,0,.28),(.45*math.cos(a),.45*math.sin(a),.16),.06,.018,wood,6)
for root in s.objects:
 if root.get('decision_kind')=='light' and root.name.startswith('hanging_light_tree_hanging'):root.scale*=1.22
 if root.get('decision_kind')=='light' and ('restaurant' in root.name or 'ribbed' in root.name):root.scale*=1.12

# More crafted storefront detail remains against the buildings and below counters.
COL=cols['02_Teahouse_Market'];tea=bpy.data.objects['tea_house']
with under(tea):
 for sx in [-1.8,0,1.8]:
  for j in range(7):box('CP09 stall fascia slat',(sx-.66+j*.22,-2.23,.35),(.17,.035,.48),woodlight)
  box('CP09 stall framed menu',(sx+.52,-2.26,.46),(.24,.018,.27),cream)
  for j in range(3):box('CP09 menu brush line',(sx+.52,-2.273,.54-j*.065),(.14,.008,.014),wood)
  for j in range(3):
   cyl('CP09 stacked ceramic plate',(sx-.4,-2.1,.94+j*.018),.12,.018,cream)
COL=cols['04_Station_Tram'];station=bpy.data.objects['station_main']
with under(station):
 for x in [-3.70,3.65]:
  box('CP09 station parcel',(x,.40,.35),(.32,.27,.32),woodlight);box('CP09 parcel strap',(x,.40,.518),(.045,.28,.012),cream)
 # A compact timetable hangs on the rear, away from waiting heads.
 box('CP09 station noticeboard',(0,.60,1.16),(.46,.045,.58),woodlight)
 for i in range(5):box('CP09 station timetable line',(0,.57,1.34-i*.085),(.30,.01,.018),dark)

# Warm, bright music-box lighting, while preserving readable blue-filled shadows.
bpy.data.objects['Soft overhead blue hour'].data.energy=1100
fill=bpy.data.objects['Quiet front paper fill'];fill.data.energy=600;fill.data.color=(1,.79,.53)
for n,power in [('Warm lantern tree pool',130),('CP08 warm tree canopy bounce',100),('Tea frontage warm bounce',185),('Station warm bounce',150),('Post office warm bounce',80),('Greenhouse soft interior',85),('CP08 greenhouse interior wash',65)]:
 if bpy.data.objects.get(n):bpy.data.objects[n].data.energy=power
for o in s.objects:
 if o.type=='LIGHT' and o.name.startswith('CP07 local lantern pool'):o.data.energy=24;o.data.color=(1,.43,.10);o.data.shadow_soft_size=.50
COL=cols['10_Lighting']
for name,p,power,size in [('CP09 warm town fill',(-7,-5,7),420,7),('CP09 canopy warm key',tuple(tree.matrix_world.translation+Vector((-1,-1,3.7))),55,2.5)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=(1,.69,.35);o=bpy.data.objects.new(name,data);COL.objects.link(o);o.location=p;target=tree.matrix_world.translation+Vector((0,0,1.5));o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
s.world.node_tree.nodes['Background'].inputs[1].default_value=.34
bg=bpy.data.materials['World backdrop | indigo'].node_tree.nodes['Principled BSDF'];bg.inputs['Base Color'].default_value=(.035,.065,.16,1);bg.inputs['Emission Color'].default_value=(.035,.065,.16,1);bg.inputs['Emission Strength'].default_value=.28

for me in bpy.data.meshes:
 if not me.users or not me.polygons or me.uv_layers:continue
 uv=me.uv_layers.new(name='UVMap')
 for poly in me.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(poly.normal[i]))]
  for li in poly.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]*2,p[axes[1]]*2)
for o in s.objects:
 if o.type=='CURVE':o.data.bevel_resolution=min(o.data.bevel_resolution,1)
rec['art_revision']={'outer_groups_rebuilt':outer_stats,'outer_design':'Wide low folded-leaf masses, three or four larger flowers per group, intervals of paper rock','new_rear_sakura':new_trees,'new_garden_lanterns':new_lights,'rear_bank_supported':True,'lighting':'Warmer broad fill, stronger local amber pools, pink terrace planting and canopy key; not a browser lighting claim'};bpy.context.view_layer.update();(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.samples=80;s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100;s.render.filepath=str(WORK/'art-rich.png');bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'art-rich.blend'));bpy.ops.render.render(write_still=True);print('CP09_ART_RICH_READY',flush=True)
