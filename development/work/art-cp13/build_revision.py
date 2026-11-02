import bpy,math,json,random
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'work/art-cp13';OUT=ROOT/'outputs/art-checkpoint-13';s=bpy.context.scene;reg=json.loads((ROOT/'outputs/lighting-checkpoint-12/decision-entities.json').read_text());old_ids={e['id']for e in reg['entities']};changes={'removed':[],'modified':[],'added':[]};initial=set(s.objects.keys());R=random.Random(1301)
tea=bpy.data.objects['tea_house'];col=bpy.data.collections['02_Teahouse_Market'];watercol=bpy.data.collections['05_Water_Garden'];skycol=bpy.data.collections['09_Animals_SCALE_PROXIES'];lightcol=bpy.data.collections['10_Lighting']
def mat(name,color,emission=0,emitcolor=None,source='Washi | pale edge'):
 m=bpy.data.materials[source].copy();m.name=name;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.87;p.inputs['Emission Color'].default_value=(*(emitcolor or color),1);p.inputs['Emission Strength'].default_value=emission;return m
wood=bpy.data.materials['Cedar frame'];edge=bpy.data.materials['Cut wood edges'];paper=bpy.data.materials['Washi | pale edge'];blue=mat('CP13 indigo textile',(.055,.12,.19));rust=mat('CP13 russet textile',(.35,.085,.035));ivory=mat('CP13 tea ceramic',(.75,.66,.45));jade=mat('CP13 tea ceramic jade',(.15,.28,.23));gold=mat('CP13 gilded paper edge',(.55,.28,.07),.15);birdpaper=mat('CP13 bird folded ivory',(.83,.75,.58),.10);birdshade=mat('CP13 bird fold shadow',(.30,.39,.43),.025)
def mesh(name,verts,faces,mats,parent=None,collection=None):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);(collection or col).objects.link(o)
 if parent:o.parent=parent
 for m in mats:me.materials.append(m)
 return o
cube=bpy.data.meshes['Shared cube']
def box(name,p,scale,m,parent=tea,bevel=0):
 o=bpy.data.objects.new(name,cube);col.objects.link(o);o.parent=parent;o.location=p;o.scale=scale
 for slot in o.material_slots:slot.link='OBJECT';slot.material=m
 if bevel:
  o.data=o.data.copy();o.data.transform(Matrix.Diagonal((*scale,1)));o.scale=(1,1,1);mod=o.modifiers.new('Paper edge bevel','BEVEL');mod.width=bevel;mod.segments=1
 return o
def lathe(name,profile,n,m,parent,position=(0,0,0),collection=None):
 vs=[(r*math.cos(j*math.tau/n),r*math.sin(j*math.tau/n),z)for r,z in profile for j in range(n)];fs=[]
 for k in range(len(profile)-1):
  for j in range(n):a=k*n+j;b=k*n+(j+1)%n;fs.append((a,b,b+n,a+n))
 fs.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+j for j in range(n))]);o=mesh(name,vs,fs,[m],parent,collection);o.location=position;return o
def beam(name,a,b,width,m,parent=tea):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)*.5,(width,width,(b-a).length),m,parent);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def erase(o):
 for ch in list(o.children):erase(ch)
 changes['removed'].append(o.name);bpy.data.objects.remove(o,do_unlink=True)
def area(name,pos,target,power,color,size,parent=None,owner=None):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);lightcol.objects.link(o);mw=Matrix.Translation(Vector(pos))@(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_matrix().to_4x4()
 if parent:o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted();o.matrix_basis=mw
 else:o.matrix_world=mw
 if owner:o['decision_owner']=owner
 o['lighting_role']='Art-directed soft amber bounce; source placement is intentionally stylized';return o
# Keep visible light surfaces saturated; scene readability comes from separate soft pools.
for name,strength,color in [('CP05 shaded restaurant lantern paper',.80,(1,.24,.025)),('Lantern | gentle amber',1.45,(1,.30,.035)),('Shoji | transmitted honey',.60,(1,.29,.035)),('Shoji | quiet window',.22,(1,.29,.035))]:
 p=bpy.data.materials[name].node_tree.nodes['Principled BSDF'];p.inputs['Emission Strength'].default_value=strength;p.inputs['Emission Color'].default_value=(*color,1)
for name,power,color in [('Soft overhead blue hour',1175,(.59,.72,1)),('Quiet front paper fill',390,(.80,.85,1)),('CP09 warm town fill',190,(1,.60,.27)),('CP12 bridge lamp reflected fill',22,(1,.46,.16))]:
 o=bpy.data.objects[name];o.data.energy=power;o.data.color=color
for o in s.objects:
 if o.type=='LIGHT'and o.name.startswith(('CP11 lamp spill','CP11 shop counter','CP11 carriage window')):o.data.color=(1,.36,.07)
area('CP13 warm west street',(-6.7,-2.7,3.8),(-5.6,-1.4,.7),38,(1,.44,.11),3.0)
area('CP13 warm garden path',(6.1,.4,3.6),(6.3,.1,.7),30,(1,.46,.12),2.7)
area('CP13 warm station forecourt',(-1.5,-5,3.5),(-1.5,-3.9,.7),22,(1,.45,.11),2.8)
# Turn the two upper luminous screens into actual open dining bays; keep roof and aisle.
removedscreens=[]
for o in list(tea.children):
 if o.name.startswith(('tea_house front window paper pane','tea_house front window lattice','tea_house front window middle')) and o.location.z>2.1:
  removedscreens.append(o.name);erase(o)
for side,x in enumerate([-1.378,1.378]):
 # Stacked screen at the side; most of each opening remains visibly open.
 sx=x+(-.68 if side==0 else .68)
 box('CP13 stacked upper shoji',(sx,-1.40,2.78),(.23,.055,1.00),bpy.data.materials['Shoji | quiet window'])
 for dx in [-.11,.11]:box('CP13 folded screen border',(sx+dx,-1.445,2.78),(.025,.025,1.03),wood)
 for z in [2.46,2.78,3.08]:box('CP13 folded screen lattice',(sx,-1.446,z),(.24,.025,.023),edge)
 # Low front-facing serving ledge, outside the protected y=-.6 aisle envelope.
 box('CP13 balcony tea ledge',(x,-1.48,2.94),(.86,.22,.055),edge,bevel=.007)
 for dx in [-.34,.34]:beam('CP13 ledge bracket',(x+dx,-1.35,2.65),(x+dx,-1.51,2.90),.035,wood)
 for dx in [-.24,.24]:
  lathe('CP13 shallow tea saucer',[(.085,0),(.10,.012),(.082,.021)],12,ivory,tea,(x+dx,-1.49,2.973))
  lathe('CP13 small tea cup',[(.041,0),(.049,.065),(.039,.066),(.032,.012)],12,jade,tea,(x+dx,-1.49,2.994))
 lathe('CP13 tea pot',[(.045,0),(.084,.035),(.070,.10),(.045,.12)],12,jade,tea,(x,-1.48,2.973))
 lathe('CP13 tea pot lid',[(.052,0),(.052,.012),(.022,.025),(.014,.035)],12,ivory,tea,(x,-1.48,3.095))
 beam('CP13 tea pot spout',(x+.05,-1.48,3.03),(x+.14,-1.48,3.085),.025,jade)
 # A folded textile and bamboo blind break the long row without blocking movement.
 box('CP13 rolled bamboo blind',(x,-1.43,3.36),(1.33,.10,.085),edge)
 for j in range(3):box('CP13 indigo short noren',(x-.34+j*.34,-1.45,3.24),(.315,.025,.18),blue if side==0 else rust)
 area('CP13 dining nook amber '+str(side),tea.matrix_world@Vector((x,-.25,3.43)),tea.matrix_world@Vector((x,-1.35,2.75)),10,(1,.40,.075),1.0,tea)
 # Real back-wall shelf and pottery create interior depth even when partly roof-occluded.
 box('CP13 upper ceramic shelf',(x,1.17,3.13),(.82,.20,.055),wood)
 for dx in [-.28,0,.28]:lathe('CP13 upper jar',[(.055,0),(.078,.08),(.06,.17),(.035,.20)],10,jade if dx else ivory,tea,(x+dx,1.14,3.16))
# A small indigo shop banner in the central bay, suspended clear of the aisle.
box('CP13 restaurant indigo sign',(0,-1.43,3.13),(.65,.04,.25),blue)
for x in [-.19,0,.19]:
 lathe('CP13 sign brass dot',[(.027,0),(.027,.012)],8,gold,tea,(x,-1.465,3.13)).rotation_euler.x=math.pi/2
# Rebuild square water lanterns as folded lotus vessels with a warm faceted heart.
petal=mat('CP13 lotus paper blush',(.76,.30,.16),.12,(1,.24,.035));petalshade=mat('CP13 lotus paper underside',(.35,.085,.045));petaledge=mat('CP13 lotus fold edge',(.88,.48,.22),.16,(1,.32,.05))
for i,root in enumerate([bpy.data.objects['CP12_floating_paper_lantern_'+str(i)]for i in range(2)]):
 for o in list(root.children):
  if o.type!='LIGHT':erase(o)
 m=bpy.data.materials['CP12 glowing water-lantern paper '+str(i)];p=m.node_tree.nodes['Principled BSDF'];p.inputs['Emission Color'].default_value=(1,.26,.025,1);p.inputs['Emission Strength'].default_value=1.5;p.inputs['Base Color'].default_value=(.93,.44,.13,1)
 lathe('CP13 lotus floating wooden saucer',[(.12,-.016),(.17,.003),(.18,.02),(.14,.035)],12,edge,root,collection=watercol)
 for k in range(8):
  a=k*math.tau/8;vs=[(.065,-.043,.025),(.16,-.075,.06),(.245,0,.17),(.16,.075,.06),(.065,.043,.025),(.145,0,.13)];fs=[(0,1,5),(1,2,5),(2,3,5),(3,4,5),(4,0,5)];o=mesh('CP13 folded lotus petal',vs,fs,[petal,petalshade,petaledge],root,watercol);o.rotation_euler.z=a;o.modifiers.new('Thin paper edge','SOLIDIFY').thickness=.006
  for poly in o.data.polygons:poly.material_index=2 if poly.index in [0,3]else 0
 lathe('CP13 faceted paper lantern heart',[(.065,.04),(.10,.09),(.105,.17),(.075,.25),(.055,.26),(.055,.245),(.085,.165),(.08,.10),(.055,.055)],8,m,root,collection=watercol)
 lathe('CP13 lantern golden collar',[(.076,.247),(.076,.258),(.058,.264)],8,gold,root,collection=watercol)
 for k in range(8):
  a=k*math.tau/8;v=[(.101*math.cos(a),.101*math.sin(a),.085),(.107*math.cos(a),.107*math.sin(a),.17),(.076*math.cos(a),.076*math.sin(a),.25)];curve=bpy.data.curves.new('CP13 lantern fine ribs','CURVE');curve.dimensions='3D';curve.bevel_depth=.0025;curve.bevel_resolution=0;sp=curve.splines.new('POLY');sp.points.add(2)
  for pnt,co in zip(sp.points,v):pnt.co=(*co,1)
  curve.materials.append(gold);o=bpy.data.objects.new('CP13 lantern fine ribs',curve);watercol.objects.link(o);o.parent=root
 light=next(o for o in root.children if o.type=='LIGHT');light.location=(0,-.22,.15);light.data.energy=1.7;light.data.color=(1,.34,.05)
 row=next(e for e in reg['entities']if e['id']==root['decision_entity_id']);row['brightness_levels']['medium']=1.5;row['label']='Folded lotus water lantern '+str(i);row['geometry_note']='Eight folded paper petals, faceted glowing heart, fine ribs and floating dish; same logical identity. Static contact and nearby rail clearance must be rechecked.'
# A bird now has a volumetric folded hull, pointed beak, forked tail and ridged paper wings.
for root in [bpy.data.objects['paper_bird_'+str(i)]for i in range(3)]:
 for o in list(root.children):
  if o.type=='MESH':erase(o)
 body=mesh('CP13 folded bird body',[(-.30,0,.03),(.21,0,.07),(0,-.09,-.06),(0,.09,-.06),(-.08,0,.16),(.30,0,.13)],[(0,2,4),(0,4,3),(0,3,2),(1,4,2),(1,3,4),(1,2,3),(1,5,4)],[birdpaper,birdshade],root,skycol)
 for p in body.data.polygons:p.material_index=1 if p.index in [1,2]else 0
 for sign in [-1,1]:
  o=mesh('CP13 swallow fork tail',[(-.19,0,.02),(-.48,sign*.16,.02),(-.36,sign*.02,-.015),(-.29,sign*.065,.075)],[(0,1,3),(1,2,3),(2,0,3)],[birdpaper,birdshade],root,skycol);o.modifiers.new('Tail paper thickness','SOLIDIFY').thickness=.012
 for pid,sign in [('wing_left',-1),('wing_right',1)]:
  node=bpy.data.objects[root.name+'__'+pid]
  for o in list(node.children):erase(o)
  vs=[(-.08,0,.08),(-.25,sign*.68,.33),(.16,sign*.47,.21),(.23,sign*.16,.07),(-.025,sign*.29,.24)];o=mesh('CP13 folded wing '+root.name+' '+pid,vs,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],[birdpaper,birdshade],node,skycol)
  for p in o.data.polygons:p.material_index=1 if p.index in [0,3]else 0
  o.modifiers.new('Wing paper thickness','SOLIDIFY').thickness=.012
 next(e for e in reg['entities']if e['id']==root['decision_entity_id'])['motion_note']='Volumetric folded body and ridged wing meshes with left/right pivots retained. Current model only; flight and flap animations unimplemented.'
# Embossed stars with independent glowing faces, darker folded faces, real thickness.
for i in range(5):
 o=bpy.data.objects['Paper star '+str(i)];outline=[tuple(v.co)for v in o.data.vertices];m=bpy.data.materials['CP12 star paper '+str(i)];p=m.node_tree.nodes['Principled BSDF'];p.inputs['Emission Strength'].default_value=1.05;p.inputs['Emission Color'].default_value=(1,.43,.10,1);shade=mat('CP13 star folded shadow '+str(i),(.70,.30,.07),.36,(1,.31,.05));r=max(Vector(v).length for v in outline);vs=[(x,y,.006)for x,y,z in outline]+[(0,0,r*.42),(0,0,-r*.20)];fs=[]
 for k in range(10):fs.append((k,(k+1)%10,10));fs.append(((k+1)%10,k,11))
 me=bpy.data.meshes.new('CP13 embossed star '+str(i));me.from_pydata(vs,[],fs);me.materials.append(m);me.materials.append(shade);me.update();o.data=me;o.modifiers.clear()
 for p in me.polygons:p.material_index=0 if p.index%4==0 else 1
 row=next(e for e in reg['entities']if e['id']==o['decision_entity_id']);row['material_bindings']=[m.name,shade.name];row['brightness_levels']['medium']=1.05;row['material_relative_strengths']=[1,.36/1.05];changes['modified'].append(o.name)
# Layered crescent, actual folded surface with a shallow raised ridge and warm edge.
o=bpy.data.objects['Paper crescent'];m=bpy.data.materials['Moon washi glow'];m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=.65;m.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value=(1,.45,.10,1);moonshade=mat('CP13 crescent paper folds',(.77,.37,.10),.42,(1,.37,.07));moonedges=mat('CP13 crescent cut edge',(.45,.18,.035),.18);vs=[];N=32
for i in range(N+1):
 t=i/N;a=math.radians(58+244*t);b=math.radians(99+162*t);outer=Vector((.70*math.cos(a),.70*math.sin(a),0));inner=Vector((.34+.56*math.cos(b),.56*math.sin(b),0))
 for u in [0,.48,1]:p=outer.lerp(inner,u);p.z=.025+(.055 if u==.48 else 0)*math.sin(math.pi*t);vs.append(tuple(p))
fs=[]
for i in range(N):
 for j in range(2):a=i*3+j;fs.extend([(a,a+3,a+1),(a+1,a+3,a+4)])
me=bpy.data.meshes.new('CP13 creased crescent face');me.from_pydata(vs,[],fs);me.materials.append(m);me.materials.append(moonshade);me.materials.append(moonedges);me.update();o.data=me;o.modifiers.clear();mod=o.modifiers.new('Layered crescent depth','SOLIDIFY');mod.thickness=.065;mod.material_offset=2;mod.material_offset_rim=2
for p in me.polygons:p.material_index=1 if p.index%7 in [0,1,4]else 0
eid='moon.paper_crescent';o['decision_entity_id']=eid;o['decision_kind']='celestial';o['decision_status']='authoring_only_runtime_unimplemented';reg['entities'].append({'id':eid,'label':'Layered paper crescent','kind':'celestial','blender_object':o.name,'position':list(o.matrix_world.translation),'parent_entity':None,'parts':[],'actions':[{'id':'set_brightness','parameters':{'level':{'enum':['low','medium','high']}},'implementation':'declared only; no executor'}],'state':{'brightness':'medium'},'material_bindings':[m.name,moonshade.name,moonedges.name],'anchors':[],'runtime_ready':False});changes['modified'].append(o.name)
# Keep all authoring identities and parts. New static ceramics/textiles are not action candidates.
bpy.context.view_layer.update()
for me in bpy.data.meshes:
 if not me.users or not me.polygons or me.uv_layers:continue
 uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  axes=[j for j in range(3)if j!=max(range(3),key=lambda j:abs(p.normal[j]))]
  for li in p.loop_indices:v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*2,v[axes[1]]*2)
for e in reg['entities']:
 obj=bpy.data.objects[e['blender_object']];e['position']=list(obj.matrix_world.translation)
 e['lighting_bindings']=[l.name for l in s.objects if l.type=='LIGHT'and l.get('decision_owner')==e['id']]
reg['source_checkpoint']='CP13';reg['entity_count']=len(reg['entities']);reg['parts_count']=sum(len(e['parts'])for e in reg['entities']);reg['cp13_new_entity_ids']=sorted({e['id']for e in reg['entities']}-old_ids);(OUT/'decision-entities.json').write_text(json.dumps(reg,indent=2))
changes['added']=sorted(set(s.objects.keys())-initial);changes['scope']='Warm saturated visible lights with stylized bounce pools; open upper dining bays, real tea service and textiles; lotus lamps; volumetric birds; embossed stars and layered crescent';changes['open_upper_screens']=removedscreens;changes['new_entity_ids']=reg['cp13_new_entity_ids'];changes['runtime_implemented']=False;(OUT/'revision-record.json').write_text(json.dumps(changes,indent=2))
s['checkpoint']='CP13 art-directed amber, upper dining details and folded sky/water objects';s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.samples=28;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=675;s.render.resolution_percentage=100;bpy.ops.wm.save_as_mainfile(filepath=str(W/'draft.blend'));s.render.filepath=str(W/'draft-overview.png');bpy.ops.render.render(write_still=True)
main=s.camera;d=bpy.data.cameras.new('CP13 restaurant draft');d.type='ORTHO';d.ortho_scale=8.1;c=bpy.data.objects.new(d.name,d);s.collection.objects.link(c);c.rotation_euler=main.rotation_euler;f=main.rotation_euler.to_quaternion()@Vector((0,0,-1));c.location=tea.matrix_world@Vector((0,-1.05,2.02))-f*30;s.camera=c;s.render.resolution_x=1150;s.render.resolution_y=850;s.render.filepath=str(W/'draft-restaurant.png');bpy.ops.render.render(write_still=True);print('CP13_DRAFT_READY',flush=True)
