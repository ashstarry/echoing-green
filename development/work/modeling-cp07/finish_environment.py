import bpy,math,json,ast,random,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
from contextlib import contextmanager
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-07';WORK=ROOT/'work/modeling-cp07';s=bpy.context.scene;cam=s.camera;PI=math.pi;Z=.61;R=random.Random(71251);PARENT=None;assets=[]
cols={c.name:c for c in bpy.data.collections};COL=cols['07_Paper_Foliage'];templates={k:bpy.data.meshes['Shared '+k] for k in ['cube','sphere','ico','cyl']}
src=ast.parse((ROOT/'work/modeling-cp02/refine_and_present.py').read_text());node=next(n for n in src.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='aliases' for t in n.targets));exec(compile(ast.Module(body=[node],type_ignores=[]),'<aliases>','exec'))
for k,n in aliases.items():globals()[k]=bpy.data.materials[n]
src=ast.parse((ROOT/'work/modeling-cp01/build_town.py').read_text());allow={'setmat','mesh','unit','primitive','box','cyl','ellipsoid','ico','beam','taper','path','ring','asset','under','window','lantern','leaf'};exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allow],type_ignores=[]),'<helpers>','exec'))
leafmesh=bpy.data.meshes['Shared folded leaf'];flower_mesh=bpy.data.meshes['CP07 shared five-petal paper flower | 106 triangles'];terr=[bpy.data.materials['Paper land layer '+str(i)] for i in range(5)]
blue2=bpy.data.materials['CP07 foliage | deep blue'];sage2=bpy.data.materials['CP07 foliage | dusk sage'];paleleaf=bpy.data.materials['CP07 foliage | pale folded edge']
Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));BACK=Vector((-RIGHT.y,RIGHT.x,0));FWD=Q@Vector((0,0,-1));UP=Q@Vector((0,1,0))
rec=json.loads((OUT/'revision-record.json').read_text());segments=[(Vector(a),Vector(b),.65 if k=='stall_approach' else .72) for k,pts in rec['routes'].items() for a,b in zip(pts,pts[1:])]
def rb(r,b,z=Z):
 p=RIGHT*r+BACK*b;p.z=z;return p
def protected(p,radius=.3):
 for a,b,w in segments:
  d=Vector((b.x-a.x,b.y-a.y,0));q=Vector((p.x-a.x,p.y-a.y,0));t=max(0,min(1,q.dot(d)/max(1e-8,d.length_squared)))
  if (q-d*t).length<w+radius and abs(p.z-(a.z+t*(b.z-a.z)))<1.8:return True
 return False
def erase(o):
 for n in [c.name for c in o.children]:
  c=bpy.data.objects.get(n)
  if c:erase(c)
 bpy.data.objects.remove(o,do_unlink=True)
def bloom(name,p,scale,mat,parent=None):
 o=bpy.data.objects.new(name,flower_mesh);COL.objects.link(o);o.location=p;o.scale=(scale,scale,scale);o.rotation_euler=(R.uniform(-.35,.35),R.uniform(-.3,.3),R.uniform(0,2*PI));o.parent=parent or PARENT;o.material_slots[0].link='OBJECT';o.material_slots[0].material=mat;return o
land=bpy.data.objects['Island paper layer 4']
def ground_at(p):
 inv=land.matrix_world.inverted();hit,loc,n,i=land.ray_cast(inv@Vector((p.x,p.y,3)),(inv.to_3x3()@Vector((0,0,-1))).normalized())
 return (land.matrix_world@loc).z if hit else None

# A lobed, folded card silhouette rather than inflated foliage or dense spheres.
edge=[(0,0),(.07,.16),(.24,.13),(.29,.21),(.13,.31),(.32,.34),(.34,.45),(.13,.49),(.29,.59),(.27,.69),(.10,.68),(.19,.82),(.13,.89),(0,1.02)]
outline=edge+[(-x,z) for x,z in reversed(edge[1:-1])]
verts=[(x,0,z) for x,z in outline]+[(0,-.045,.48)];faces=[(len(outline),i,(i+1)%len(outline)) for i in range(len(outline))]
sprigmesh=bpy.data.meshes.new('CP07 shared lobed folded paper sprig');sprigmesh.from_pydata(verts,[],faces);sprigmesh.materials.append(blueleaf);sprigmesh.update()
def sprig(name,p,scale,mat,yaw=0,lean=0):
 o=bpy.data.objects.new(name,sprigmesh);COL.objects.link(o);o.location=p;o.scale=(scale,scale,scale);o.rotation_euler=(lean,R.uniform(-.28,.28),yaw);o.parent=PARENT;setmat(o,mat);return o
clumps=0
def garden(p,scale=1,pot=False,flowers=True):
 global clumps
 if protected(p,.38*scale):return
 root=asset('CP07 garden cluster %03d'%clumps,p);clumps+=1
 with under(root):
  zz=0
  if pot:
   taper('CP07 folded paper planter',(0,0,0),(0,0,.26*scale),.18*scale,.24*scale,R.choice([navy2,woodlight,terr[3]]),8);cyl('CP07 planter dark soil',(0,0,.26*scale),.215*scale,.025,wood);zz=.26*scale
  for j in range(5):
   a=j*2.4;ss=scale*R.uniform(.54,.92);sprig('CP07 garden lobed leaf',(math.cos(a)*.12*scale,math.sin(a)*.12*scale,zz),ss,R.choice([blueleaf,blue2,blue2,sage2,paleleaf]),R.uniform(-1,1)+.2,R.uniform(-.28,.28))
  for j in range(4):
   a=j*2.1;leaf('CP07 broad ground leaf',(.13*scale*math.cos(a),.13*scale*math.sin(a),zz+.15*scale),(.85*scale,.95*scale,.6*scale),R.choice([blueleaf,sage2,blue2]),(.35,.1,a))
  if flowers:
   for j in range(R.randint(3,6)):
    x,y=R.uniform(-.31,.31)*scale,R.uniform(-.21,.21)*scale;h=R.uniform(.38,.66)*scale+zz
    beam('CP07 flower paper stem',(x*.7,y*.7,zz),(x,y,h),.008*scale,sage2);bloom('CP07 garden full blossom',(x,y,h),R.uniform(.24,.38)*scale,R.choice([pink,pinklight,cream,cream,navy3]))
 return root

# Replace the draft's scattered tiny border garnish with composed clusters.
for n in [o.name for o in s.objects if o.name.startswith(('CP07 folded border leaf','CP07 border blossom','CP07 cut-paper cliff facet'))]:erase(bpy.data.objects[n])
for i in range(105):
 a=2*PI*i/105;ry=9.1 if math.sin(a)>0 else 7.2;p=rb(12.65*math.cos(a),-.75+ry*math.sin(a));z=ground_at(p)
 if z is not None:
  p.z=z+.02;garden(p,R.uniform(.78,1.16),flowers=i%5!=0)
# Layered planting beds frame buildings; the street and performance plaza stay open.
for r,b,ss in [(-10.8,2.0,1),(-10.4,-.7,1),(-9.5,-2.2,.8),(-8.6,-2.65,.9),(-7.6,-2.6,.85),(-6.8,-2.7,.8),(-5.85,-2.7,.75),(-9.5,3.4,.8),(-8.4,4.3,.9),(-6.8,5.5,.9),(-5.9,4.8,.8),(-4.4,3.35,.7),(-4.6,3.9,.9),(-3.9,4.2,.8),(3.75,3.0,.8),(4.45,3.4,.8),(4.8,2.7,1),(5.2,1.8,.85),(5.8,1.2,.8),(6.0,.3,.7),(5.65,-.7,.65),(5.6,-3.8,.85),(6.5,-4.2,.9),(8.2,-4.0,1),(9.4,-3.5,.8),(10.45,-1.0,.8),(11,2.5,.8),(10.7,3.7,1),(10.2,4.6,1.0),(8.65,5.5,.9),(7.7,6.3,.9),(-3.9,-3.0,.65)]:
 garden(rb(r,b),ss,pot=R.random()<.28)
# Background paper hedges add silhouette behind the accepted architecture.
for r,b,z in [(-10,5.6,Z),(-9,6.2,Z),(-8,6.9,Z),(-7,7.3,Z),(-6,7.65,Z),(-5,7.85,Z),(-4,8.1,Z),(-3,8.3,Z),(-1.8,8.4,Z),(0,8.5,Z),(1.8,8.1,1.4),(3.2,7.8,1.85),(4.0,7.8,1.85),(6.7,7.0,1.85),(7.6,6.8,1.4),(8.8,5.8,Z),(10.1,5.1,Z)]:
 p=rb(r,b,z)
 if not protected(p,.35):
  for j in range(4):sprig('CP07 backdrop cut-paper grove',p+RIGHT*R.uniform(-.35,.35)+BACK*R.uniform(-.1,.1),R.uniform(1.55,2.45),R.choice([blueleaf,blue2,sage2]),R.uniform(-.8,.8)+.2,.05)

# Less geometric-looking tree crowns, still all flat cut-paper geometry.
for rootname in ['district_tree_0','district_tree_1','district_tree_3','district_tree_5','district_tree_6']:
 root=bpy.data.objects.get(rootname)
 if not root:continue
 leaves=[o for o in root.children if 'crown leaf' in o.name]
 for i,o in enumerate(leaves):
  p=o.location.copy();mat=o.active_material;erase(o)
  with under(root):sprig('CP07 tree crown lobed paper',p-Vector((0,0,.28)),R.uniform(.55,.82),mat,.2+R.uniform(-1.1,1.1),R.uniform(-.3,.3))
# Fix the known side-counter clearance defect.
o=bpy.data.objects.get('CP02 restrained flower bed leaf.282')
if o:o.location+=RIGHT*.35+BACK*.20

# Lift the lowest blossoms away from the focal lanterns, giving the canopy air.
main=bpy.data.objects['lantern_tree']
for o in main.children:
 if any(k in o.name for k in ['blossom','petal']):
  if o.location.z<1.8:o.location.z=1.8+(o.location.z-1.1)*.35
  if o.name.startswith('CP07 layered'):o.scale*=1.3
with under(main):
 for i in range(85):
  a=R.random()*2*PI;rr=R.uniform(.35,1.55);p=Vector((rr*math.cos(a),rr*.75*math.sin(a),2.05+R.uniform(-.1,.7)))
  bloom('CP07 canopy blossom',p,R.uniform(.28,.42),R.choice([pink,pink,pinklight,pinkdark]))
 for i in range(10):
  a=i*2.4;taper('CP07 tree root flare',(0,0,.12),(.40*math.cos(a),.40*math.sin(a),.02),.05,.018,wood,6)
 # Rib lines help the lanterns read as crafted paper forms at the default camera.
 for ob in [o for o in main.children if 'Tree hanging lantern washi' in o.name]:
  x,y,z=ob.location;r=.12;h=.15
  for k in range(6):
   a=k*PI/3;pts=[(x+math.cos(a)*r*math.sin(t),y+math.sin(a)*r*math.sin(t),z+h*math.cos(t)) for t in [j*PI/8 for j in range(9)]];path('CP07 lantern folded rib',pts,.0035,woodlight)
bpy.data.objects['Warm lantern tree pool'].data.energy=125
amber.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=1.1

# Simple railings and coping stones describe district boundaries without filling streets.
COL=cols['03_Post_Residential']
def fence(points,z=Z):
 for a,b in zip(points,points[1:]):
  a=rb(*a,z);b=rb(*b,z);d=b-a;n=max(1,round(d.length/.62))
  for j in range(n+1):
   p=a+d*j/n
   if protected(p,.10):continue
   box('CP07 district fence post',p+Vector((0,0,.32)),(.085,.085,.64),woodlight)
  for h in [.23,.51]:
   if not protected((a+b)/2,.15):beam('CP07 district fence rail',a+Vector((0,0,h)),b+Vector((0,0,h)),.026,woodlight)
fence([(-10.5,-1.7),(-9.5,-2.3),(-8.3,-2.8),(-6.5,-3.15)])
fence([(-11,3.7),(-9.9,4.7),(-8.6,5.7),(-7.0,6.3),(-5.5,6.9)])
fence([(5.6,-3.95),(6.8,-4.25),(8.4,-4.25),(9.5,-3.7)])
fence([(10.5,2.7),(10.5,4.1),(9.8,5.0)])

# Baskets, crates and folded paper flowers enrich the storefront edges.
def crate(name,p,parent=None,size=.4):
 root=asset(name,p);root.parent=parent
 with under(root):
  box(name+' floor',(0,0,.025),(size,size*.72,.05),woodlight)
  for z in [.09,.21,.33]:
   for y in [-size*.36,size*.36]:box(name+' slat',(0,y,z),(size,.035,.08),woodlight)
   for x in [-size*.5,size*.5]:box(name+' end',(x,0,z),(.035,size*.72,.08),woodlight)
  for x in [-size*.43,size*.43]:
   for y in [-size*.29,size*.29]:box(name+' corner',(x,y,.18),(.04,.04,.35),wood)
 return root
def bicycle(p,yaw):
 root=asset('CP07 parked bicycle',p,yaw)
 with under(root):
  for x in [-.45,.45]:
   pts=[(x+.29*math.cos(i*2*PI/28),0,.30+.29*math.sin(i*2*PI/28)) for i in range(28)];path('CP07 bicycle tire',pts,.024,dark,True)
   for j in range(8):a=j*PI/4;beam('CP07 bicycle spoke',(x,0,.3),(x+.27*math.cos(a),0,.3+.27*math.sin(a)),.005,woodlight)
  for a,b in [((-.45,0,.3),(-.15,0,.65)),((-.15,0,.65),(.03,0,.3)),((.03,0,.3),(-.45,0,.3)),((-.15,0,.65),(.32,0,.64)),((.32,0,.64),(.03,0,.3)),((.32,0,.64),(.45,0,.3)),((.32,0,.64),(.28,0,.85))]:beam('CP07 bicycle frame',a,b,.018,dark)
  box('CP07 bicycle saddle',(-.15,0,.70),(.22,.12,.045),wood);beam('CP07 bicycle handlebar',(.28,-.16,.85),(.28,.16,.85),.017,dark)
  taper('CP07 bicycle paper basket',(.44,0,.61),(.44,0,.83),.12,.19,woodlight,8)
 return root
post=bpy.data.objects['post_office'];bpy.context.view_layer.update()
bikepos=post.matrix_world@Vector((1.6,-1.3,0));bicycle(bikepos,post.rotation_euler.z-.2)
for rootname,coords in [('post_office',[(-1.65,-1.15,.05),(1.4,.5,.02)]),('tea_house',[(2.95,-1.3,.0),(-2.85,.45,0)]),('station_main',[(-3.55,-.15,.02),(3.45,-.10,.02)])]:
 root=bpy.data.objects[rootname]
 for i,p in enumerate(coords):
  world=root.matrix_world@Vector(p)
  if not protected(world,.35):
   c=crate('CP07 store crate '+rootname+str(i),p,root,.38)
   with under(c):
    for j in range(5):ico('CP07 basket produce',(R.uniform(-.12,.12),R.uniform(-.08,.08),.36),(.07,.06,.06),R.choice([orange,red,green]))
tea=bpy.data.objects['tea_house'];COL=cols['02_Teahouse_Market']
with under(tea):
 # Three menu tablets and low shelves remain inside counter footprints.
 for xx in [-1.8,0,1.8]:
  box('CP07 menu tablet',(xx,-1.37,1.41),(.23,.045,.38),woodlight)
  for j in range(3):box('CP07 menu ink',(xx,-1.399,1.49-j*.065),(.12,.005,.014),dark)
  for yy in [-1.92,-1.78]:
   for j in range(3):
    x=xx-.25+j*.22;cyl('CP07 ceramic serving bowl',(x,yy,.96),.085,.045,cream);cyl('CP07 dish content',(x,yy,.987),.065,.008,R.choice([orange,green,wood]))
 # Paper curtains hang beside the facade, never across the upper side door.
 for xx in [-1.8,0,1.8]:
  for j in [-1,1]:box('CP07 short indigo noren',(xx+j*.2,-1.46,1.81),(.36,.025,.35),navy2)
 # Front balcony small planters stay against the rail.
 for xx in [-2.25,-.75,.75,2.25]:
  box('CP07 balcony flower box',(xx,-1.70,2.42),(.36,.18,.15),woodlight)
  for j in range(3):bloom('CP07 balcony bloom',(xx+(j-1)*.12,-1.70,2.65),.20,R.choice([pink,cream,pinklight]))

COL=cols['04_Station_Tram'];station=bpy.data.objects['station_main']
with under(station):
 for xx in [-3.4,-2.25,-1.0,0,1,2.3,3.4]:lantern('CP07 station warm lantern',(xx,-.78,1.45),.90)
 for xx in [-2.6,2.65]:
  box('CP07 station timetable',(xx,.10,.98),(.30,.035,.5),woodlight)
  for j in range(5):box('CP07 timetable ink',(xx,.078,1.14-j*.075),(.18,.005,.015),dark)
for rootname in ['tram_car_front','tram_car_rear']:
 root=bpy.data.objects[rootname]
 with under(root):
  for xx in [-.8,0,.8]:
   box('CP07 tram roof vent',(xx,0,1.51),(.23,.27,.075),dark)
  for yy in [-.52,.52]:
   for xx in [-1.12,1.12]:box('CP07 tram gold corner',(xx,yy,.77),(.024,.025,.87),gold)
   box('CP07 tram lower lining',(0,yy,.43),(2.6,.024,.023),gold)

COL=cols['05_Water_Garden'];gh=bpy.data.objects['greenhouse']
with under(gh):
 for x in [-1.02,1.02]:
  box('CP07 greenhouse side shelf',(x,0,.52),(.40,1.7,.05),woodlight)
  for y in [-.67,-.22,.25,.68]:
   taper('CP07 greenhouse pot',(x,y,.55),(x,y,.78),.12,.17,woodlight,8)
   for j in range(3):sprig('CP07 greenhouse paper plant',(x+(j-1)*.06,y,.76),.43,R.choice([green,sage2,blueleaf]),j*1.5,.2)
   bloom('CP07 greenhouse flowering pot',(x,y,1.16),.23,R.choice([pinklight,cream]))
 # A folded watering can and unobstructed center aisle.
 cyl('CP07 watering can',(-.68,-.85,.24),.16,.28,navy3);taper('CP07 watering spout',(-.55,-.9,.26),(-.34,-.95,.43),.045,.02,navy3,8)
 path('CP07 watering handle',[(-.80,-.84,.34),(-.93,-.84,.40),(-.99,-.84,.24),(-.80,-.84,.14)],.018,navy3)
# Pond edge stones/lilies and reeds; preserve boat and ducks in open water.
pond=bpy.data.objects['CP02 pond'];pc=Vector((pond.location.x,pond.location.y,Z+.02))
for i in range(22):
 a=2*PI*i/22
 if .25<a<2.8:continue
 p=pc+RIGHT*(2.85*math.cos(a))+BACK*(1.83*math.sin(a));ico('CP07 folded pond bank',p,(R.uniform(.24,.41),R.uniform(.22,.34),R.uniform(.15,.25)),R.choice([terr[2],terr[3],navy3]))
for i in range(11):
 a=3.1+i*.27;p=pc+RIGHT*(2.45*math.cos(a))+BACK*(1.48*math.sin(a));cyl('CP07 pond lily pad',p+Vector((0,0,.035)),R.uniform(.14,.25),.015,sage2)
 if i%2==0:bloom('CP07 pond full lily',p+Vector((0,0,.07)),.3,pinklight)
for r,b in [(5.3,-2.0),(5.6,-2.8),(9.9,-2.7),(10.5,-2.1)]:garden(rb(r,b),.85,flowers=False)

# A tiled dome and a small wind ornament give the observatory the reference's craft.
COL=cols['03_Post_Residential'];ob=bpy.data.objects['paper_observatory']
with under(ob):
 for zz,rr in [(2.82,.86),(3.0,.77),(3.18,.61),(3.32,.38)]:ring('CP07 observatory dome band',(0,0,zz),rr,.013,navy3,36)
 # All these details are low-poly silhouettes, not subdivision surfaces.
 beam('CP07 observatory finial',(0,0,3.42),(0,0,3.77),.026,gold)
 for sign in [-1,1]:path('CP07 finial curl',[(0,0,3.65),(sign*.14,0,3.68),(sign*.18,0,3.77),(sign*.12,0,3.82)],.023,gold)

# UVs on the new paper meshes; reuse the two shared normal maps.
for me in bpy.data.meshes:
 if not me.users or not me.polygons or me.uv_layers:continue
 uv=me.uv_layers.new(name='UVMap')
 for poly in me.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(poly.normal[i]))]
  for li in poly.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]*2,p[axes[1]]*2)
for o in s.objects:
 if o.type=='CURVE':o.data.bevel_resolution=min(o.data.bevel_resolution,1)
rec['finish_environment']={'composed_garden_clusters':clumps,'new_shared_sprig_triangles':len(faces),'bicycle':1,'paper_style':'folded cards, shared leaf and blossom geometry, no subdivision','roof_policy':'complete normal view; inspection cutaway only'}
(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.context.view_layer.update()
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.samples=64;s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100;s.render.filepath=str(WORK/'environment-finish.png');bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'environment-finish.blend'));bpy.ops.render.render(write_still=True);print('ENVIRONMENT_FINISH_READY',clumps,flush=True)
