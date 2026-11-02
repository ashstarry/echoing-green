import bpy,math,json,ast,random,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
from contextlib import contextmanager
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-07';WORK=ROOT/'work/modeling-cp07';s=bpy.context.scene;cam=s.camera;PI=math.pi;Z=.61;R=random.Random(2707);PARENT=None;assets=[]
cols={c.name:c for c in bpy.data.collections};COL=cols['07_Paper_Foliage'];templates={k:bpy.data.meshes['Shared '+k] for k in ['cube','sphere','ico','cyl']}
src=ast.parse((ROOT/'work/modeling-cp02/refine_and_present.py').read_text());node=next(n for n in src.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='aliases' for t in n.targets));exec(compile(ast.Module(body=[node],type_ignores=[]),'<aliases>','exec'))
for k,n in aliases.items():globals()[k]=bpy.data.materials[n]
src=ast.parse((ROOT/'work/modeling-cp01/build_town.py').read_text());allow={'setmat','mesh','unit','primitive','box','cyl','ellipsoid','ico','beam','taper','path','ring','asset','under','window','lantern','leaf'};exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allow],type_ignores=[]),'<helpers>','exec'))
leafmesh=bpy.data.meshes['Shared folded leaf'];terr=[bpy.data.materials['Paper land layer '+str(i)] for i in range(5)]
rec=json.loads((ROOT/'outputs/modeling-checkpoint-06/revision-record.json').read_text());rec['source_checkpoint']='CP06';rec['checkpoint']='CP07';rec['art_stage']='Approved spatial layout retained; reference-directed paper craft finish'
Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));BACK=Vector((-RIGHT.y,RIGHT.x,0));FWD=Q@Vector((0,0,-1));UP=Q@Vector((0,1,0));cam.name='Camera_Main_CP07_43deg'
def rb(r,b,z=Z):
 p=RIGHT*r+BACK*b;p.z=z;return p
def xy(p,z=Z):
 v=cam.location+RIGHT*((p[0]/1672-.5)*cam.data.ortho_scale)+UP*((.5-p[1]/941)*cam.data.ortho_scale/(1672/941));return v+FWD*((z-v.z)/FWD.z)
def erase(o):
 for c in list(o.children):erase(c)
 bpy.data.objects.remove(o,do_unlink=True)
def variant(base,name,color):
 m=base.copy();m.name=name;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);m.diffuse_color=(*color,1);return m
blue2=variant(blueleaf,'CP07 foliage | deep blue',(.045,.105,.16));sage2=variant(sage,'CP07 foliage | dusk sage',(.22,.32,.31));paleleaf=variant(leafcream,'CP07 foliage | pale folded edge',(.50,.55,.48))
stone2=variant(ivory,'CP07 paving | warm limestone',(.64,.57,.44));stone3=variant(ivory,'CP07 paving | muted rose',(.65,.56,.47));wood2=variant(woodlight,'CP07 cedar | warm slat',(.42,.235,.095));tramroof=variant(red,'CP07 tram roof | oxblood',(.22,.024,.025))

# Replace expensive round blossom petals with thin folded paper cards.
outline=[(-1,0),(-.80,-.48),(-.18,-.92),(.58,-.80),(1,-.30),(.91,0),(1,.30),(.58,.80),(-.18,.92),(-.80,.48)]
vs=[(x,y,0) for x,y in outline]+[(0,0,.75),(0,0,-.10)];faces=[]
for i in range(10):faces.extend([(10,i,(i+1)%10),(11,(i+1)%10,i)])
petal=bpy.data.meshes.new('CP07 shared folded paper petal | 20 triangles');petal.from_pydata(vs,[],faces);petal.update()
counts={'replaced_round_petals':0,'replaced_centers':0,'added_flower_objects':0,'added_foliage_clumps':0,'beveled_objects':0}
for o in list(s.objects):
 if o.type=='MESH' and 'petal' in o.name and o.data.name.startswith('Shared sphere'):
  mat=o.active_material;o.data=petal;setmat(o,mat);counts['replaced_round_petals']+=1
 if o.type=='MESH' and ('bloom center' in o.name or 'blossom center' in o.name or 'lily center' in o.name):
  mat=o.active_material;o.data=templates['ico'];o.scale*=.68;setmat(o,mat);counts['replaced_centers']+=1

# A whole low-poly blossom shares geometry across the town.
fvs=[];ffs=[];fmi=[]
for k in range(5):
 a=k*2*PI/5;rot=Matrix.Rotation(a,3,'Z');base=Vector((.35*math.cos(a),.35*math.sin(a),0));offset=len(fvs)
 for v in vs:fvs.append(tuple(base+rot@Vector((v[0]*.31,v[1]*.18,v[2]*.028))))
 for face in faces:ffs.append(tuple(offset+j for j in face));fmi.append(0)
offset=len(fvs);fvs.extend([(0,0,.03)]+[(.07*math.cos(i*PI/3),.07*math.sin(i*PI/3),.02) for i in range(6)])
for i in range(6):ffs.append((offset,offset+1+i,offset+1+(i+1)%6));fmi.append(1)
flower_mesh=bpy.data.meshes.new('CP07 shared five-petal paper flower | 106 triangles');flower_mesh.from_pydata(fvs,[],ffs);flower_mesh.materials.append(pink);flower_mesh.materials.append(gold);flower_mesh.update()
for p,i in zip(flower_mesh.polygons,fmi):p.material_index=i
def blossom(name,p,scale,mat,parent=None):
 o=bpy.data.objects.new(name,flower_mesh);COL.objects.link(o);o.location=p;o.scale=(scale,scale,scale);o.rotation_euler=(R.uniform(-.18,.18),R.uniform(-.18,.18),R.random()*2*PI)
 if parent:o.parent=parent
 o.material_slots[0].link='OBJECT';o.material_slots[0].material=mat;counts['added_flower_objects']+=1;return o
for name in ['lantern_tree','district_tree_2']:
 tree=bpy.data.objects[name];centers=[o.location.copy() for o in tree.children if 'blossom center' in o.name]
 for p in centers:
  for j in range(2):blossom('CP07 layered blossom',p+Vector((R.uniform(-.20,.20),R.uniform(-.20,.20),R.uniform(-.12,.14))),R.uniform(.16,.27),R.choice([pink,pinklight,pinkdark]),tree)

# Low-cost folded leaves and small edge flowers enrich the ecosystem without
# consuming walking surfaces. Corridors use the accepted route data as exclusions.
segments=[(Vector(a),Vector(b),.65 if k=='stall_approach' else .72) for k,pts in rec['routes'].items() for a,b in zip(pts,pts[1:])]
def protected(p,radius=.3):
 for a,b,w in segments:
  d=Vector((b.x-a.x,b.y-a.y,0));q=Vector((p.x-a.x,p.y-a.y,0));t=max(0,min(1,q.dot(d)/max(1e-8,d.length_squared)))
  if (q-d*t).length<w+radius and abs(p.z-(a.z+t*(b.z-a.z)))<1.7:return True
 return False
def shrub(p,scale=1,flowers=True):
 if protected(p,.18*scale):return
 for k in range(7):
  a=k*2.399+R.uniform(-.2,.2);q=p+Vector((math.cos(a)*.12*scale,math.sin(a)*.12*scale,R.uniform(.12,.30)*scale));leaf('CP07 folded border leaf',q,(.24*scale,.43*scale,.46*scale),R.choice([blueleaf,blue2,sage2,paleleaf]),(R.uniform(.25,.9),R.uniform(-.5,.5),a))
 if flowers:
  for j in range(2):blossom('CP07 border blossom',p+Vector((R.uniform(-.14,.14)*scale,R.uniform(-.14,.14)*scale,R.uniform(.28,.42)*scale)),R.uniform(.12,.20)*scale,R.choice([pinklight,cream,paleleaf]))
 counts['added_foliage_clumps']+=1
land=bpy.data.objects['Island paper layer 4']
def ground_at(p):
 inv=land.matrix_world.inverted();hit,loc,n,i=land.ray_cast(inv@Vector((p.x,p.y,3)),(inv.to_3x3()@Vector((0,0,-1))).normalized())
 return (land.matrix_world@loc).z if hit else None
for i in range(175):
 a=2*PI*i/175;ry=9.1 if math.sin(a)>0 else 7.2;p=rb(12.65*math.cos(a),-.75+ry*math.sin(a));z=ground_at(p)
 if z is not None:p.z=z+.025;shrub(p,R.uniform(.65,1.03),i%3!=0)
# Clusters by building edges and the pond; leave the main plaza readable.
pixels=[(159,509),(203,524),(284,537),(355,569),(432,534),(536,410),(571,346),(1015,336),(1080,405),(1122,475),(1092,548),(1107,594),(1184,633),(1265,650),(1393,633),(1490,590),(1527,533),(1494,415),(1393,414),(1204,410),(1015,205),(489,294)]
for pp in pixels:
 p=xy(pp)
 for j in range(3):shrub(p+Vector((R.uniform(-.28,.28),R.uniform(-.28,.28),.01)),R.uniform(.6,.92),True)

# Paper-rock facets along the outer base, avoiding the upper movement surfaces.
COL=cols['00_Terrain']
for i in range(82):
 a=PI+PI*i/81;p=rb(12.95*math.cos(a),-.85+7.40*math.sin(a),.24);z=ground_at(p)
 if z is None:continue
 ob=ico('CP07 cut-paper cliff facet',p,(R.uniform(.25,.48),R.uniform(.18,.32),R.uniform(.20,.36)),R.choice([terr[2],terr[3],terr[4]]));ob.rotation_euler.z=a

# Refine the bench as a modest two-seat form; keep its right end clear of the roof.
COL=cols['06_Hillside'];bench=bpy.data.objects['CP05_overlook_bench'];bench.location=rb(5.54,6.71,1.871);bench.rotation_euler.z=math.radians(9)
for o in bench.children:
 if 'slat' in o.name:o.scale.x=1.55
 elif 'leg' in o.name or 'upright' in o.name:o.location.x=math.copysign(.64,o.location.x)
reader=bpy.data.objects['quiet_reader'];reader.location=bench.location;reader.rotation_euler.z=bench.rotation_euler.z
wind=bpy.data.objects['hill_windwheel'];wind.location=rb(6.55,5.95,1.872)
bpy.data.objects['district_tree_3'].location=rb(8.5,4.0,Z)
prefix='CP02 street lantern 13 ';old=bpy.data.objects[prefix+'foot'].location-Vector((0,0,.06));dest=rb(7.1,5.7,Z)
for o in s.objects:
 if o.name.startswith(prefix):o.location+=dest-old
rec['routes']['terrace_main']=[list(rb(r,b,1.872)) for r,b in [(3,5.55),(3.3,6.35),(4.25,6.5),(4.5,6.15),(5.35,5.85),(5.65,5.85)]]
lantern('CP07 fence hanging lantern',rb(4.60,6.95,2.55),.75)

# Human-scale architecture accents; paper craft, not high-subdivision detail.
COL=cols['03_Post_Residential'];home=bpy.data.objects['west_home']
with under(home):
 beam('CP07 laundry cord',(.05,-1.96,2.22),(1.2,-1.96,2.22),.009,wood)
 for i,m in enumerate([cream,navy2,red]):
  xx=.23+i*.35;mesh('CP07 folded balcony cloth',[(xx-.13,-1.95,2.2),(xx+.13,-1.95,2.2),(xx+.12,-2.0,1.69),(xx,-2.025,1.72),(xx-.12,-2,1.69)],[(0,1,3),(1,2,3),(0,3,4)],m)
 for xx in [-.9]:box('CP07 home chimney',(xx,.45,3.0),(.22,.28,.65),ivory)
COL=cols['02_Teahouse_Market'];tea=bpy.data.objects['tea_house']
for o in list(tea.children):
 if o.name.startswith('Bread / market goods') and o.location.x>-.65:
  p=o.location.copy();erase(o)
  with under(tea):
   if p.x<.8:
    for j in range(3):ico('CP07 market fruit',p+Vector((R.uniform(-.06,.06),R.uniform(-.05,.05),.02)),(.055,.052,.06),R.choice([red,orange,green]))
   else:
    cyl('CP07 tea cup',p+Vector((0,0,.025)),.075,.10,cream);cyl('CP07 tea surface',p+Vector((0,0,.078)),.060,.008,wood)
# Simple aprons and collars make roles readable while keeping figures unrigged.
COL=cols['08_Residents_SCALE_PROXIES']
for root in [o for o in s.objects if o.get('entity_id') and any(c.name==COL.name for c in o.users_collection)]:
 with under(root):
  for sign in [-1,1]:mesh('CP07 folded collar',[(0,-.18,.91),(sign*.13,-.16,.87),(sign*.08,-.21,.75)],[(0,1,2)],cream)
  if root.name.startswith('vendor') or root.name=='gardener':mesh('CP07 paper apron',[(-.18,-.21,.79),(.18,-.21,.79),(.19,-.23,.39),(0,-.26,.41),(-.19,-.23,.39)],[(0,1,3),(1,2,3),(0,3,4)],white)
# A reusable guitar prop, not a fixed animation sequence.
mus=bpy.data.objects['musician']
with under(mus):
 ob=ellipsoid('CP07 guitar paper body',(.10,-.31,.62),(.26,.045,.20),woodlight);box('CP07 guitar neck',(.37,-.31,.78),(.43,.055,.07),wood,(0,.0,.35));cyl('CP07 guitar sound hole',(.10,-.359,.65),.065,.012,dark).rotation_euler.x=PI/2
 for i in range(3):beam('CP07 guitar string',(-.08,-.37,.57+i*.018),(.57,-.37,.83+i*.018),.003,cream)

COL=cols['04_Station_Tram']
for rootname in ['tram_car_front','tram_car_rear']:
 root=bpy.data.objects[rootname]
 for o in root.children:
  if o.name.startswith('Tram indigo roof'):setmat(o,tramroof)
 with under(root):
  for sign in [-1,1]:
   box('CP07 tram cream pinstripe',(0,sign*.505,1.19),(2.60,.018,.018),cream)
  for yy in [-.31,.31]:
   o=cyl('CP07 tram headlight',(1.415,yy,.60),.070,.035,amber);o.rotation_euler.y=PI/2
  box('CP07 tram destination plate',(1.425,0,1.19),(.025,.38,.12),woodlight)

COL=cols['05_Water_Garden']
for o in s.objects:
 if o.name.startswith('CP02 bridge deck'):
  o.scale.x*=.92;setmat(o,R.choice([woodlight,wood2]))
pond=bpy.data.objects['CP02 pond'];center=Vector((pond.location.x,pond.location.y,Z+.055))
for i in range(23):
 xx=R.uniform(-2.5,2.5);yy=R.uniform(-1.65,1.65)
 if (xx/2.8)**2+(yy/1.9)**2>1:continue
 p=center+RIGHT*xx+BACK*yy
 pts=[tuple(p+RIGHT*(j*.09)+BACK*(.018*math.sin(j*.7))) for j in range(R.randint(4,10))];path('CP07 paper water glint',pts,.006,waterline)

# Small real bevels on reusable boxes; no subdivision or bevels on every petal.
bevel_cache={}
for o in list(s.objects):
 if o.type!='MESH' or o.data.name!='Shared cube':continue
 if any(c.name.startswith('08_') or c.name.startswith('12_') for c in o.users_collection):continue
 dims=tuple(round(abs(v),4) for v in o.scale)
 if min(dims)<.025 or max(dims)>10:continue
 width=min(.016,min(dims)*.13);segments=1
 key=(dims,round(width,4))
 if key not in bevel_cache:
  me=bpy.data.meshes.new('CP07 shared beveled box '+str(len(bevel_cache)));bm=bmesh.new();bmesh.ops.create_cube(bm,size=1)
  bmesh.ops.transform(bm,matrix=Matrix.Diagonal(Vector((*dims,1))),verts=bm.verts)
  bmesh.ops.bevel(bm,geom=list(bm.edges),offset=width,segments=segments,affect='EDGES');bm.to_mesh(me);bm.free();me.update();bevel_cache[key]=me
 mat=o.active_material;o.data=bevel_cache[key];o.scale=(1,1,1);setmat(o,mat);counts['beveled_objects']+=1
# Give the street tiles a paper-cut edge below their original walking height.
paving=bpy.data.objects['CP02 open street paving'];paving.data=paving.data.copy();bm=bmesh.new();bm.from_mesh(paving.data)
ret=bmesh.ops.extrude_discrete_faces(bm,faces=list(bm.faces));bmesh.ops.translate(bm,verts=list({v for f in ret['faces'] for v in f.verts}),vec=(0,0,-.018))
bmesh.ops.bevel(bm,geom=list(bm.edges),offset=.004,segments=1,affect='EDGES');bm.to_mesh(paving.data);bm.free();paving.data.update()
for mat in [stone2,stone3]:paving.data.materials.append(mat)
for p in paving.data.polygons:p.material_index=R.choices([0,1,2],[7,2,1])[0]

# Deterministic UVs for code-built meshes, and two shared ImageGen-derived normal maps.
normal_paper=bpy.data.images.load(str(OUT/'textures/washi-normal.png'),check_existing=True);normal_paper.colorspace_settings.name='Non-Color';normal_paper.pack()
normal_wood=bpy.data.images.load(str(OUT/'textures/cedar-normal.png'),check_existing=True);normal_wood.colorspace_settings.name='Non-Color';normal_wood.pack()
for me in list(bpy.data.meshes):
 if me.users==0 or not me.polygons:continue
 uv=me.uv_layers.active or me.uv_layers.new(name='UVMap')
 for poly in me.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(poly.normal[i]))]
  for li in poly.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]*2,p[axes[1]]*2)
for m in bpy.data.materials:
 if not m.use_nodes or m.name.startswith('GUIDE'):continue
 p=m.node_tree.nodes.get('Principled BSDF')
 if not p:continue
 if m.name.startswith(('Ink dark','Rail','Aged brass','Moon','Cloud')):continue
 for link in list(m.node_tree.links):
  if link.to_node==p and link.to_socket==p.inputs['Normal']:m.node_tree.links.remove(link)
 tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=normal_wood if any(k in m.name.lower() for k in ['wood','cedar']) else normal_paper;tex.extension='REPEAT';n=m.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.30 if tex.image==normal_wood else .26;m.node_tree.links.new(tex.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],p.inputs['Normal']);p.inputs['Roughness'].default_value=.84
 m['material_source']='ImageGen height -> Cycles tangent normal; shared 1024 texture; base tint retained'
for m in [windowmat,windowdim]:
 p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.85,.38,.085,1);p.inputs['Emission Color'].default_value=(1,.38,.075,1);p.inputs['Emission Strength'].default_value=.50 if m==windowmat else .17
for o in s.objects:
 if o.type=='CURVE':o.data.bevel_resolution=min(o.data.bevel_resolution,1)

# Restore the reference's warm center and quieter cool edges.
bpy.data.objects['Soft overhead blue hour'].data.energy=1050
bpy.data.objects['Quiet front paper fill'].data.energy=380
bpy.data.objects['Warm lantern tree pool'].data.energy=200
bpy.data.objects['Tea frontage warm bounce'].data.energy=115
bpy.data.objects['Station warm bounce'].data.energy=100
s.world.node_tree.nodes['Background'].inputs[1].default_value=.24
COL=cols['10_Lighting']
for i in [0,2,3,4,5,8,9,10,12]:
 o=bpy.data.objects.get('CP02 street lantern '+str(i)+' glow')
 if o:
  d=bpy.data.lights.new('CP07 local lantern pool '+str(i),'POINT');d.energy=9;d.color=(1,.42,.13);d.shadow_soft_size=.45;lamp=bpy.data.objects.new(d.name,d);COL.objects.link(lamp);lamp.location=o.matrix_world.translation+Vector((0,0,-.20))
s.view_settings.exposure=.0;s['checkpoint']='CP07 | reference-led cut-paper finish and resource-conscious mesh detail';s['not_web_performance_claim']='Actual FPS not measured; optimized GLB is a separate staging export.'
rec['art_changes']=counts;rec['bench']={'length_before':1.07,'length_after':1.55,'center_rb':[5.54,6.71],'yaw':9};rec['material_pipeline']='Built-in ImageGen grayscale sources, Cycles tangent normal bake, shared 1024 maps';(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
bpy.context.view_layer.update()
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.samples=64;s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=85;s.render.filepath=str(WORK/'art-draft.png');bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'art-draft.blend'));bpy.ops.render.render(write_still=True);print('CP07_ART_DRAFT_READY',json.dumps(counts),flush=True)
