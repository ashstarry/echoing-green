import bpy, math, random, json, sys, time
from pathlib import Path
from mathutils import Vector
from contextlib import contextmanager

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/modeling-checkpoint-01'
OUT.mkdir(exist_ok=True)
R=random.Random(241026)
PI=math.pi
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials):bpy.data.materials.remove(d)
scene=bpy.context.scene
scene.name='Borrowed Wind Town | CP01'
cols={}
for key in ['00_Terrain','01_Plaza','02_Teahouse_Market','03_Post_Residential','04_Station_Tram','05_Water_Garden','06_Hillside','07_Paper_Foliage','08_Residents_SCALE_PROXIES','09_Animals_SCALE_PROXIES','10_Lighting','11_Cameras']:
 c=bpy.data.collections.new(key);scene.collection.children.link(c);cols[key]=c
COL=cols['00_Terrain'];PARENT=None;templates={};assets=[]

def material(name,color,rough=.8,metal=0,emission=0,paper=False,alpha=1):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,alpha)
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 if alpha<1:p.inputs['Alpha'].default_value=alpha;p.inputs['Transmission Weight'].default_value=.08
 if paper:
  n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=95;n.inputs['Detail'].default_value=2;n.inputs['Roughness'].default_value=.6
  b=m.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.12;b.inputs['Distance'].default_value=.018
  m.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
 m['cp_material_note']='Blender paper shader; web texture bake/adapter pending' if paper else 'Base material'
 return m

ivory=material('Washi | warm ivory',(0.72,.63,.45),paper=True)
cream=material('Washi | pale edge',(0.88,.79,.59),paper=True)
walls=material('Shoji walls | ivory',(0.77,.64,.42),paper=True)
navy=material('Roof paper | indigo',(.034,.065,.16),paper=True)
navy2=material('Roof paper | slate',(.064,.10,.21),paper=True)
navy3=material('Roof paper | faded',(.085,.13,.24),paper=True)
wood=material('Cedar frame',(.24,.11,.045),paper=True)
woodlight=material('Cut wood edges',(.49,.28,.11),paper=True)
dark=material('Ink dark',(.018,.025,.045))
amber=material('Lantern | gentle amber',(1,.43,.10),emission=1.8,paper=True)
windowmat=material('Shoji | transmitted honey',(1,.55,.19),emission=.9,paper=True)
windowdim=material('Shoji | quiet window',(.49,.33,.17),emission=.22,paper=True)
glass=material('Greenhouse paper panes',(.44,.58,.54),rough=.48,alpha=.20)
red=material('Vermilion lacquer paper',(.42,.027,.024),paper=True)
gold=material('Aged brass',(.45,.25,.075),rough=.45,metal=.55)
railmat=material('Rail | warm iron',(.19,.15,.12),rough=.45,metal=.65)
pink=material('Sakura paper | blush',(.76,.36,.39),paper=True)
pinklight=material('Sakura paper | pale',(.91,.64,.59),paper=True)
pinkdark=material('Sakura paper | muted',(.45,.19,.25),paper=True)
sage=material('Paper foliage | gray sage',(.24,.31,.26),paper=True)
blueleaf=material('Paper foliage | blue slate',(.085,.16,.21),paper=True)
leafcream=material('Paper foliage | cream',(.55,.56,.40),paper=True)
green=material('Greenhouse leaves',(.13,.25,.13),paper=True)
water=material('Layered paper water',(.035,.105,.19),rough=.48,paper=True)
waterline=material('Cut ripple | soft blue',(.18,.31,.42),rough=.7)
skin=material('Paper doll | skin',(.66,.40,.25),paper=True)
orange=material('Fox paper',(.64,.16,.035),paper=True)
white=material('Warm white paper',(.81,.77,.63),paper=True)
coatmats=[material('Resident coat '+str(i),c,paper=True) for i,c in enumerate([(.045,.12,.25),(.48,.07,.045),(.25,.32,.24),(.52,.31,.09),(.16,.21,.27),(.48,.30,.28)])]
terr=[material('Paper land layer '+str(i),c,paper=True) for i,c in enumerate([(.035,.064,.14),(.065,.10,.19),(.12,.17,.25),(.27,.30,.33),(.54,.52,.44)])]
ground=material('World backdrop | indigo',(.025,.055,.13),paper=True,emission=.24)

def relink(obj):
 for c in list(obj.users_collection):c.objects.unlink(obj)
 COL.objects.link(obj)
 if PARENT:obj.parent=PARENT
 return obj
def setmat(obj,m):
 if not obj.data.materials:obj.data.materials.append(m)
 obj.material_slots[0].link='OBJECT';obj.material_slots[0].material=m
 return obj
def mesh(name,verts,faces,m):
 me=bpy.data.meshes.new(name+' mesh');me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);COL.objects.link(ob)
 if PARENT:ob.parent=PARENT
 if m:me.materials.append(m)
 return ob
def unit(kind):
 if kind in templates:return templates[kind]
 if kind=='cube':bpy.ops.mesh.primitive_cube_add(size=1)
 elif kind=='sphere':bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1)
 elif kind=='ico':bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1)
 elif kind=='cyl':bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=1,depth=1)
 ob=bpy.context.object;me=ob.data;me.name='Shared '+kind;bpy.data.objects.remove(ob,do_unlink=True)
 templates[kind]=me;return me
def primitive(name,kind,p,scale,m,rot=(0,0,0),smooth=False):
 ob=bpy.data.objects.new(name,unit(kind));COL.objects.link(ob);ob.location=p;ob.scale=scale;ob.rotation_euler=rot
 if PARENT:ob.parent=PARENT
 setmat(ob,m)
 if smooth:
  for f in ob.data.polygons:f.use_smooth=True
 return ob
def box(name,p,size,m,rot=(0,0,0)):return primitive(name,'cube',p,size,m,rot)
def cyl(name,p,r,h,m):return primitive(name,'cyl',p,(r,r,h),m)
def ellipsoid(name,p,s,m):return primitive(name,'sphere',p,s,m,smooth=True)
def ico(name,p,s,m):return primitive(name,'ico',p,s,m)
def beam(name,a,b,r,m):
 a=Vector(a);b=Vector(b);ob=cyl(name,(a+b)/2,r,(b-a).length,m);ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return ob
def taper(name,a,b,r1,r2,m,n=10):
 a=Vector(a);b=Vector(b);L=(b-a).length
 verts=[(r*math.cos(2*PI*i/n),r*math.sin(2*PI*i/n),z) for z,r in [(-L/2,r1),(L/2,r2)] for i in range(n)]
 faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 ob=mesh(name,verts,faces,m);ob.location=(a+b)/2;ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return ob
def path(name,pts,r,m,closed=False):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2
 s=cu.splines.new('POLY');s.points.add(len(pts)-1)
 for q,p in zip(s.points,pts):q.co=(*p,1)
 s.use_cyclic_u=closed
 ob=bpy.data.objects.new(name,cu);COL.objects.link(ob);cu.materials.append(m)
 if PARENT:ob.parent=PARENT
 return ob
def ring(name,p,r,t,m,n=48):
 return path(name,[(p[0]+r*math.cos(2*PI*i/n),p[1]+r*math.sin(2*PI*i/n),p[2]) for i in range(n)],t,m,True)
def asset(name,p=(0,0,0),yaw=0,quality='modeled prototype'):
 ob=bpy.data.objects.new(name,None);COL.objects.link(ob);ob.location=p;ob.rotation_euler.z=yaw
 ob['entity_id']=name;ob['checkpoint_status']=quality;assets.append({'id':name,'position':list(p),'quality':quality,'collection':COL.name})
 return ob
@contextmanager
def under(parent):
 global PARENT
 old=PARENT;PARENT=parent
 yield
 PARENT=old
def ellipse_solid(name,rx,ry,z,depth,m,n=96,jitter=.02,cx=0,cy=0):
 rs=[1+R.uniform(-jitter,jitter) for i in range(n)]
 vs=[(cx+rx*rs[i]*math.cos(2*PI*i/n),cy+ry*rs[i]*math.sin(2*PI*i/n),zz) for zz in [z-depth,z] for i in range(n)]
 fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,vs,fs,m)

print('BUILD terrain',flush=True)
for i,(rx,ry,z) in enumerate([(11.8,8.25,-.08),(11.7,8.15,.10),(11.55,8.02,.28),(11.42,7.92,.43),(11.30,7.80,.59)]):
 ellipse_solid('Island paper layer '+str(i),rx,ry,z,.19,terr[i],jitter=.014)
Z=.61
box('Indigo studio floor',(0,0,-.54),(200,200,.10),ground)
# Low hillside, one connected foundation rather than isolated floating stages.
for i in range(3):ellipse_solid('Quiet hill terrace '+str(i),3.1-i*.37,2.0-i*.25,Z+.15+i*.30,.32,terr[3 if i<2 else 4],cx=4.5,cy=4.9,jitter=.03,n=30)

COL=cols['01_Plaza']
# Annular paving as one mesh per ring; visible paper joints, walkable continuous top.
for j in range(9):
 r0=.74+j*.34;r1=r0+.322;n=max(16,int(2*PI*(r0+r1)/2/.40));vs=[];fs=[]
 for i in range(n):
  a=2*PI*i/n+.01/(r0+.1);b=2*PI*(i+1)/n-.01/(r0+.1);k=len(vs)
  vs.extend([(-.7+r*math.cos(t),-.25+r*math.sin(t),z) for z in [Z+.005,Z+.045] for r,t in [(r0,a),(r1,a),(r1,b),(r0,b)]])
  fs.extend([tuple(k+q for q in f) for f in [(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
 mesh('Plaza ring '+str(j),vs,fs,ivory if j%3 else cream)
# Broad walkway strips between the districts.
def paving_strip(name,x,y,w,d):
 colsN=max(1,int(w/.43));rows=max(1,int(d/.40));vs=[];fs=[]
 for j in range(rows):
  for i in range(colsN):
   xx=x-w/2+(i+.5)*w/colsN;yy=y-d/2+(j+.5)*d/rows;ww=w/colsN-.018;dd=d/rows-.018;k=len(vs)
   vs.extend([(xx+a*ww/2,yy+b*dd/2,Z+.02) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]])
   fs.append((k,k+1,k+2,k+3))
 mesh(name,vs,fs,ivory)
for args in [('Market approach',-.8,2.9,7.4,1.25),('Station approach',-2.4,-3.95,5.0,1.7),('Post street',-5.6,-.6,3.0,5.6),('Water path',4.0,-2.8,2.0,4.0)]:paving_strip(*args)

def window(name,x,y,z,w,h,side='front',dim=False):
 # Front windows live on y- plane. Side windows are separate rotated subassemblies.
 ob=box(name+' paper pane',(x,y,z),(w,.045,h),windowdim if dim else windowmat)
 for xx in [x-w/2,x+w/2]:box(name+' jamb',(xx,y-.035,z),(.055,.07,h+.1),wood)
 for zz in [z-h/2,z+h/2]:box(name+' sill',(x,y-.04,zz),(w+.11,.095,.055),wood)
 for q in [-.25,0,.25]:box(name+' lattice',(x+q*w,y-.04,z),(.024,.05,h),woodlight)
 box(name+' middle',(x,y-.045,z),(w,.055,.025),woodlight)
def roof(name,w,d,eave,rise,axis='x'):
 # ridge along local x; roof strip geometry is genuinely sloped.
 roofroot=asset(name+' roof')
 roofroot.parent=PARENT
 if axis=='y':roofroot.rotation_euler.z=PI/2;w,d=d,w
 with under(roofroot):
  vv=[(-w/2,-d/2,eave),(w/2,-d/2,eave),(w/2,0,eave+rise),(-w/2,0,eave+rise),(-w/2,d/2,eave),(w/2,d/2,eave)]
  mesh(name+' roof underlay',vv,[(0,1,2,3),(3,2,5,4)],navy)
  rows=max(3,int(math.hypot(d/2,rise)/.23));nc=max(3,int(w/.35));ang=math.atan2(rise,d/2);sl=math.hypot(d/2,rise)
  for side in [-1,1]:
   for row in range(rows):
    u=(row+.5)/rows
    for c in range(nc):
     x=-w/2+(c+.5)*w/nc;y=side*(d/2)*(1-u);z=eave+rise*u+.028
     box(name+' shingle',(x,y,z),(w/nc-.014,sl/rows+.035,.035),R.choice([navy,navy,navy2,navy3]),(-side*ang,0,0))
  beam(name+' ridge',(-w/2-.05,0,eave+rise+.07),(w/2+.05,0,eave+rise+.07),.055,navy2)
  for x in [-w/2,w/2]:
   mesh(name+' gable',[(x,-d/2,eave),(x,d/2,eave),(x,0,eave+rise)],[(0,1,2)],walls)
   beam(name+' gable trim',(x,-d/2,eave),(x,0,eave+rise),.065,wood)
   beam(name+' gable trim',(x,d/2,eave),(x,0,eave+rise),.065,wood)
def house(name,x,y,w,d,h,base=Z,axis='x',floors=1):
 root=asset(name,(x,y,base))
 with under(root):
  box(name+' foundation',(0,0,.12),(w+.24,d+.24,.24),terr[3])
  box(name+' paper body',(0,0,h/2+.2),(w,d,h),walls)
  for xx in [-w/2,w/2]:
   for yy in [-d/2,d/2]:box(name+' timber',(xx,yy,h/2+.2),(.10,.10,h+.15),wood)
  for f in range(floors):
   zz=.2+(f+.5)*h/floors
   for i in [-1,1]:window(name+' front window',i*w*.26,-d/2-.04,zz,w*.31,h/floors*.60)
   box(name+' story beam',(0,-d/2-.065,.2+f*h/floors),(w,.11,.09),wood)
  box(name+' front lintel',(0,-d/2-.07,h+.16),(w,.14,.11),wood)
  side=asset(name+' east windows',(w/2+.025,0,0),PI/2)
  side.parent=root
  with under(side):
   for f in range(floors):window(name+' side',0,0,.2+(f+.5)*h/floors,d*.60,h/floors*.57)
  roof(name,w+.45,d+.50,h+.22,.80 if h<3 else 1.0,axis)
  for j in range(3):box(name+' porch step',(0,-d/2-.24-j*.16,.15-j*.045),(w*.75,.42,.10),ivory)
 return root

def lantern(name,p,scale=1,parent=None):
 x,y,z=p;r=.115*scale;h=.26*scale
 ellipsoid(name+' washi',p,(r,r,h*.58),amber)
 for zz in [z-h*.48,z+h*.48]:cyl(name+' ring',(x,y,zz),r*.70,.028*scale,wood)
 beam(name+' hanging',(x,y,z+h*.5),(x,y,z+h*.5+.16*scale),.008*scale,wood)
def pointlight(name,p,power,color=(1,.47,.18),radius=.5):
 d=bpy.data.lights.new(name,'POINT');d.energy=power;d.color=color;d.shadow_soft_size=radius
 o=bpy.data.objects.new(name,d);COL.objects.link(o);o.location=p
 if PARENT:o.parent=PARENT
 return o
def lamppost(name,x,y,z=Z):
 cyl(name+' foot',(x,y,z+.06),.14,.12,woodlight)
 beam(name+' shaft',(x,y,z+.1),(x,y,z+1.2),.036,wood)
 box(name+' glow',(x,y,z+1.32),(.18,.18,.28),amber)
 for dx in [-.10,.10]:
  for dy in [-.10,.10]:beam(name+' frame',(x+dx,y+dy,z+1.15),(x+dx*.7,y+dy*.7,z+1.49),.012,wood)
 taper(name+' cap',(x,y,z+1.48),(x,y,z+1.65),.16,.025,wood,4)

print('BUILD architecture',flush=True)
COL=cols['02_Teahouse_Market']
tea=house('tea_house',.4,4.0,5.3,2.7,3.45,floors=2)
with under(tea):
 box('Tea balcony floor',(0,-1.62,1.91),(5.55,.75,.13),woodlight)
 for xx in [-2.6,-1.75,-.9,0,.9,1.75,2.6]:beam('Balcony baluster',(xx,-1.95,1.98),(xx,-1.95,2.58),.04,wood)
 for zz in [2.12,2.58]:beam('Balcony long rail',(-2.7,-1.95,zz),(2.7,-1.95,zz),.045,wood)
 for i in range(11):lantern('Tea lantern',(-2.35+i*.47,-1.62,3.10),.85)
 for sx in [-1.8,0,1.8]:
  box('Stall counter',(sx,-2.10,.66),(1.58,.55,.18),woodlight)
  box('Stall front',(sx,-2.15,.35),(1.53,.13,.58),wood)
  for xx in [sx-.8,sx+.8]:beam('Stall post',(xx,-2.12,0),(xx,-2.12,1.75),.038,wood)
  for j in range(5):box('Awning folded stripe',(sx-.64+j*.32,-1.83,1.72),(.32,1.05,.045),cream if j%2==0 else navy2,(.19,0,0))
  beam('Awning front', (sx-.82,-2.35,1.62),(sx+.82,-2.35,1.62),.035,wood)
  for j in range(4):ellipsoid('Bread / market goods',(sx-.5+j*.32,-2.14,.84),(.13,.10,.075),cream)

COL=cols['03_Post_Residential']
post=house('post_office',-6.1,.15,2.7,2.35,2.05,axis='y')
with under(post):
 box('Postal vermilion sign',(0,-1.21,2.0),(.72,.07,.29),red)
 for zz in [2.07,1.98]:box('Postal mark bar',(0,-1.26,zz),(.22,.025,.025),cream)
 box('Postal mark stem',(0,-1.26,1.94),(.025,.025,.12),cream)
 # Discrete door and windows, model revisions can later add interiors.
 box('Post door',(0,-1.22,.80),(.48,.055,1.34),wood)
 window('Door shoji',0,-1.26,1.04,.38,.72)
 cyl('Postbox pedestal',(-1.75,-1.0,.07),.19,.14,terr[3])
 cyl('Postbox red body',(-1.75,-1.0,.62),.20,1.0,red)
 cyl('Postbox top',(-1.75,-1.0,1.16),.24,.10,red)
 box('Postbox slot',(-1.75,-1.202,.91),(.23,.025,.035),dark)
 box('Postbox letter panel',(-1.75,-1.206,.69),(.15,.02,.12),cream)
house('west_home',-7.15,3.3,2.8,2.45,2.45,axis='y')
house('small_wood_home',-8.4,.1,1.75,1.8,1.80,axis='x')
# Round paper civic lookout echoes the approved reference's left silhouette.
look=asset('paper_observatory',(-4.75,4.75,Z))
with under(look):
 cyl('Lookout tower',(0,0,1.70),.95,3.4,walls)
 for z in [1.1,2.4]:window('Tower window',0,-.96,z,.44,.62)
 verts=[];faces=[];n=32;nr=8
 for j in range(nr+1):
  t=(PI/2)*j/nr
  for i in range(n):verts.append((1.03*math.cos(t)*math.cos(i*2*PI/n),1.03*math.cos(t)*math.sin(i*2*PI/n),3.4+1.02*math.sin(t)))
 for j in range(nr):
  for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 mesh('Paper dome',verts,faces,navy2)
 for i in range(12):
  a=2*PI*i/12;path('Dome seam',[(1.04*math.cos(t)*math.cos(a),1.04*math.cos(t)*math.sin(a),3.4+1.03*math.sin(t)) for t in [j*PI/20 for j in range(11)]],.014,woodlight)
 ring('Dome eave',(0,0,3.4),1.08,.035,woodlight)
 beam('Dome finial',(0,0,4.4),(0,0,4.7),.025,gold)

COL=cols['06_Hillside']
house('quiet_home',4.75,5.2,2.8,2.25,2.0,base=1.65,axis='y')
for i in range(9):box('Hill stair',(3.0,3.1+i*.22,Z+.055+i*.11),(1.0,.27,.15),ivory)
wind=asset('hill_windwheel',(7.1,4.8,1.5))
with under(wind):
 beam('Wind pole',(0,0,0),(0,0,2.8),.07,wood)
 cyl('Wind base',(0,0,.08),.19,.16,woodlight)
 for i in range(6):
  a=i*PI/3+.1
  vs=[(0,-.07,2.75),(.15*math.cos(a+.6),-.08,2.75+.15*math.sin(a+.6)),(.84*math.cos(a+.38),-.10,2.75+.84*math.sin(a+.38)),(.56*math.cos(a-.08),-.04,2.75+.56*math.sin(a-.08))]
  mesh('Folded wind vane',vs,[(0,1,2),(0,2,3)],cream)
 ellipsoid('Wheel hub',(0,-.12,2.75),(.11,.05,.11),gold)

COL=cols['04_Station_Tram']
station=house('station_main',-2.8,-5.15,4.8,1.35,1.5,axis='x')
with under(station):
 # Broad timber canopy extending over visible platform.
 for xx in [-2.65,-1.5,0,1.5,2.65]:beam('Canopy post',(xx,-1.38,0),(xx,-1.38,1.68),.065,wood)
 box('Station platform',(0,-1.08,.04),(5.9,1.5,.08),ivory)
 for j in range(17):box('Station canopy tile',(-2.72+j*.34,-1.02,1.87),(.35,1.4,.055),navy2,(.12,0,0))
 for xx in [-1.8,-.7,.6,1.8]:lantern('Station warm lamp',(xx,-.82,1.49),.7)
 for xx in [-1.6,1.25]:
  box('Station bench seat',(xx,-1.02,.43),(1.0,.35,.07),woodlight)
  for dx in [-.4,.4]:box('Bench foot',(xx+dx,-1.02,.22),(.06,.25,.43),wood)
# Elliptic continuous track with normal offsets and individual sleepers.
rx,ry=10.45,7.13
def railpoint(t,off=0):
 x=rx*math.cos(t);y=ry*math.sin(t);n=Vector((math.cos(t)/rx,math.sin(t)/ry,0)).normalized();return (x+n.x*off,y+n.y*off,Z+.13)
for off in [-.34,.34]:path('Continuous rail', [railpoint(i*2*PI/200,off) for i in range(200)],.035,railmat,True)
for i in range(170):
 t=i*2*PI/170;p=railpoint(t);a=math.atan2(ry*math.cos(t),-rx*math.sin(t))
 box('Railway sleeper',(p[0],p[1],Z+.07),(.15,1.0,.095),woodlight,(0,0,a))
def tram_car(name,t):
 p=railpoint(t);a=math.atan2(ry*math.cos(t),-rx*math.sin(t));root=asset(name,(p[0],p[1],Z+.20),a)
 with under(root):
  box('Tram chassis',(0,0,.23),(2.75,1.0,.17),dark)
  box('Tram burgundy body',(0,0,.79),(2.66,.95,1.0),red)
  box('Tram indigo roof',(0,0,1.34),(2.84,1.09,.16),navy)
  for sy in [-1,1]:
   for i in range(7):
    x=-1.1+i*.36
    box('Tram glowing window',(x,sy*.481,.91),(.27,.022,.43),windowmat if i%3 else windowdim)
    for z in [.66,1.15]:box('Tram window trim',(x,sy*.50,z),(.30,.025,.025),gold)
   box('Tram belt line',(0,sy*.50,.55),(2.60,.035,.025),gold)
  for x in [-1.06,1.06]:
   for sy in [-1,1]:
    ob=cyl('Tram wheel',(x,sy*.47,.10),.19,.10,dark);ob.rotation_euler.x=PI/2
  for x in [-.75,.55]:box('Roof vent',(x,0,1.46),(.36,.32,.08),navy2)
  box('Tram end window',(1.341,0,.90),(.025,.58,.43),windowmat)
  box('Tram bumper',(1.41,0,.30),(.12,.55,.09),dark)
 return root
tram_car('tram_car_front',-1.30);tram_car('tram_car_rear',-1.59)

print('BUILD garden',flush=True)
COL=cols['05_Water_Garden']
ellipse_solid('Pond paper surface',2.85,2.25,Z+.025,.07,water,n=70,cx=6.1,cy=-.35,jitter=.018)
for i in range(7):
 x=R.uniform(4.5,7.7);y=R.uniform(-1.75,.8)
 ring('Water ripple',(x,y,Z+.04),R.uniform(.16,.39),.009,waterline,n=32)
greenhouse=asset('greenhouse',(6.0,3.05,Z+.13))
with under(greenhouse):
 w,d,h=2.9,2.5,1.75
 box('Greenhouse footing',(0,0,.08),(w+.18,d+.18,.16),terr[3])
 for xx in [-w/2,-w/4,0,w/4,w/2]:
  for yy in [-d/2,d/2]:beam('Glasshouse upright',(xx,yy,.15),(xx,yy,h),.035,woodlight)
 for yy in [-d/2,-d/4,0,d/4,d/2]:
  for xx in [-w/2,w/2]:beam('Glasshouse side',(xx,yy,.15),(xx,yy,h),.035,woodlight)
 for yy in [-d/2,d/2]:
  box('Greenhouse paper glass',(0,yy,h/2),(w,.015,h-.15),glass)
  for zz in [.35,1.05,h]:beam('Greenhouse crossbar',(-w/2,yy,zz),(w/2,yy,zz),.028,woodlight)
 for xx in [-w/2,w/2]:box('Greenhouse side glass',(xx,0,h/2),(.015,d,h-.15),glass)
 for yy in [-d/2,-d/4,0,d/4,d/2]:
  beam('Greenhouse rafter',(-w/2,yy,h),(0,yy,h+.8),.035,woodlight)
  beam('Greenhouse rafter',(0,yy,h+.8),(w/2,yy,h),.035,woodlight)
 mesh('Greenhouse roof glazing',[(-w/2,-d/2,h),(-w/2,d/2,h),(0,d/2,h+.8),(0,-d/2,h+.8),(w/2,d/2,h),(w/2,-d/2,h)],[(0,1,2,3),(3,2,4,5)],glass)
 beam('Greenhouse ridge',(0,-d/2,h+.8),(0,d/2,h+.8),.04,woodlight)
 pointlight('Greenhouse soft interior',(0,0,1.15),45,(1,.62,.28),1.0)
 for xx in [-.85,0,.85]:box('Plant bench',(xx,0,.49),(.55,1.7,.07),woodlight)
# Arched bridge crosses pond with distinct walkable planks.
for i in range(22):
 u=i/21;x=3.75+4.6*u;z=Z+.17+.42*math.sin(PI*u)
 box('Bridge deck plank',(x,.47,z),(.23,1.0,.09),woodlight,(0,-.42*PI/4.6*math.cos(PI*u),0))
for sy in [-.08,1.02]:
 pts=[]
 for i in range(11):
  u=i/10;x=3.75+4.6*u;z=Z+.2+.42*math.sin(PI*u)
  beam('Bridge post',(x,sy,z),(x,sy,z+.64),.035,wood)
  pts.append((x,sy,z+.66))
 path('Bridge handrail',pts,.04,woodlight)
# Boat with separate shallow hull, seats and mooring rope.
boat=asset('pond_boat',(5.05,-1.05,Z+.10),-.28)
with under(boat):
 vs=[(-.75,0,0),(-.48,-.3,0),(.48,-.3,0),(.75,0,0),(.48,.3,0),(-.48,.3,0),(-.58,0,-.18),(-.37,-.18,-.18),(.37,-.18,-.18),(.58,0,-.18),(.37,.18,-.18),(-.37,.18,-.18)]
 mesh('Folded boat hull',vs,[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]+[(6,7,8,9,10,11)],woodlight)
 path('Boat gunwale',vs[:6],.03,wood,True)
 for xx in [-.3,.28]:box('Boat bench',(xx,0,-.015),(.16,.55,.035),wood)

COL=cols['07_Paper_Foliage']
leafverts=[(0,-.50,0),(.22,-.10,0),(.22,.22,.025),(0,.56,.05),(-.22,.22,.025),(-.22,-.10,0),(0,.05,.065)]
leaffaces=[(0,1,6),(1,2,6),(2,3,6),(3,4,6),(4,5,6),(5,0,6)]
leafmesh=bpy.data.meshes.new('Shared folded leaf');leafmesh.from_pydata(leafverts,[],leaffaces);leafmesh.update();leafmesh.materials.append(sage)
def leaf(name,p,scale,m,rot):
 ob=bpy.data.objects.new(name,leafmesh);COL.objects.link(ob);ob.location=p;ob.scale=scale;ob.rotation_euler=rot
 if PARENT:ob.parent=PARENT
 setmat(ob,m);return ob
def flower(name,p,scale,m):
 x,y,z=p
 for i in range(5):
  a=i*2*PI/5
  ob=ellipsoid(name+' petal',(x+math.cos(a)*scale*.35,y+math.sin(a)*scale*.35,z),(.31*scale,.18*scale,.028*scale),m)
  ob.rotation_euler.z=a
 ellipsoid(name+' center',(x,y,z+.023*scale),(.08*scale,.08*scale,.04*scale),gold)
def plant(name,x,y,z=Z,scale=1,m=None,pot=True):
 m=m or R.choice([sage,blueleaf,leafcream])
 if pot:
  taper(name+' paper pot',(x,y,z),(x,y,z+.26*scale),.15*scale,.20*scale,R.choice([terr[3],woodlight,navy2]));z+=.24*scale
 for i in range(5):
  a=i*2*PI/5+R.random()*.3
  leaf(name+' leaf',(x+.10*scale*math.cos(a),y+.10*scale*math.sin(a),z+.22*scale),(.33*scale,.65*scale,.6*scale),m,(R.uniform(.3,.8),R.uniform(-.4,.4),a))
 if R.random()<.55:flower(name+' bloom',(x,y,z+.51*scale),.30*scale,R.choice([pinklight,cream,leafcream]))
def tree(name,x,y,z,height=2.5,crown=1.2,pink_tree=False):
 root=asset(name,(x,y,z))
 with under(root):
  taper(name+' trunk',(0,0,0),(0,0,height*.72),.15,.055,wood)
  for i in range(9):
   a=i*2.4;r=crown*R.uniform(.5,.8);tip=(r*math.cos(a),r*math.sin(a),height*R.uniform(.65,.92))
   taper(name+' branch',(0,0,height*.35),tip,.055,.014,wood)
  for i in range(95 if pink_tree else 55):
   a=R.uniform(0,2*PI);u=R.uniform(-1,1);s=math.sqrt(1-u*u);rad=R.uniform(.65,1)
   p=(crown*rad*s*math.cos(a),crown*.8*rad*s*math.sin(a),height*.78+crown*.55*u)
   if pink_tree:flower(name+' cut blossom',p,R.uniform(.32,.48),R.choice([pink,pink,pinklight,pinkdark]))
   else:leaf(name+' crown leaf',p,(.55,.82,.65),R.choice([sage,blueleaf,leafcream]),(R.uniform(-1.0,1),R.uniform(-.8,.8),a))
 return root
main=tree('lantern_tree',-.7,-.25,Z+.16,2.7,1.8,True)
with under(main):
 for i in range(9):
  a=i*2*PI/9;r=1.30
  lantern('Tree hanging lantern',(r*math.cos(a),r*.75*math.sin(a),1.85+R.uniform(-.14,.12)),1.0)
# Circular segmented bench, accessible from all main paths.
COL=cols['01_Plaza']
ring('Tree planter rim',(-.7,-.25,Z+.18),.78,.10,woodlight)
for i in range(12):
 a=i*2*PI/12;r=1.28
 box('Circular bench segment',(-.7+r*math.cos(a),-.25+r*math.sin(a),Z+.47),(.60,.29,.07),woodlight,(0,0,a+PI/2))
 for da in [-.18,.18]:
  aa=a+da;box('Bench leg',(-.7+r*math.cos(aa),-.25+r*math.sin(aa),Z+.25),(.06,.09,.44),wood)
COL=cols['07_Paper_Foliage']
for i,(x,y,h,s) in enumerate([(-8.8,4.3,2.6,1.05),(-6.9,5.6,2.1,.9),(-3.5,5.8,2.1,.85),(2.5,6.2,2.5,1.0),(6.8,6.0,2.5,.95),(8.7,3.7,2.5,1.05),(-8.5,-2.9,1.8,.7)]):tree('district_tree_'+str(i),x,y,Z,h,s,i in [2,4])
for i in range(70):
 t=i*2*PI/70
 if -2.0<t-2*PI<-1.0:continue
 x=9.6*math.cos(t);y=6.35*math.sin(t)
 plant('Perimeter paper planting',x,y,Z,R.uniform(.55,.9),pot=False)
for x,y in [(-7.6,-1.3),(-7.1,-1.35),(-4.7,-1.4),(-4.9,1.5),(-3.6,2.4),(-2.8,2.4),(2.2,2.2),(3.0,2.3),(4.5,2.1),(7.6,2.0),(7.7,3.8),(8.4,-2.0),(4.2,-2.6),(-5.1,-4.3)]:plant('Street planter',x,y,scale=R.uniform(.65,.9))
# Greenhouse plants are visible through modeled panes.
for x in [5.15,6.0,6.85]:
 for y in [2.45,3.1,3.7]:plant('Greenhouse plant',x,y,Z+.7,.55,green)
for i in range(10):
 x=R.uniform(4.8,7.6);y=R.uniform(-2.2,-.5)
 cyl('Water lily leaf',(x,y,Z+.065),R.uniform(.11,.2),.015,sage)
 if i%3==0:flower('Water lily',(x,y,Z+.09),.25,pinklight)

COL=cols['08_Residents_SCALE_PROXIES']
def person(name,x,y,yaw=0,coat=0,z=Z,pose='stand',hat=True):
 root=asset(name,(x,y,z),yaw,'scale / silhouette proxy; not rigged')
 with under(root):
  c=coatmats[coat%len(coatmats)]
  if pose=='sit':
   hip=.43;torso=.70;head=1.05
   for sx in [-.10,.10]:
    beam('Seated thigh',(sx,0,hip),(sx,-.23,.43),.07,navy)
    beam('Seated shin',(sx,-.23,.43),(sx,-.24,.10),.055,navy)
    box('Shoe',(sx,-.30,.07),(.13,.25,.10),dark)
  else:
   hip=.48;torso=.72;head=1.08
   for sx in [-.10,.10]:
    beam('Trouser leg',(sx,0,.50),(sx,-.02,.12),.07,navy)
    box('Shoe',(sx,-.075,.07),(.14,.25,.10),dark)
  taper('Coat body',(0,0,hip-.05),(0,0,.91),.22,.17,c,8)
  cyl('Neck',(0,0,.98),.055,.12,skin)
  ellipsoid('Head',(0,-.01,head),(.145,.135,.18),skin)
  ellipsoid('Hair cap',(0,.012,head+.075),(.15,.135,.115),dark)
  ellipsoid('Nose',(0,-.142,head-.01),(.035,.038,.035),skin)
  for sx in [-.055,.055]:ellipsoid('Eye',(sx,-.133,head+.025),(.012,.009,.013),dark)
  for s in [-1,1]:
   elbow=(s*.25,-.03,.65);hand=(s*.24,-.12,.49) if pose!='sit' else (s*.18,-.22,.53)
   beam('Upper sleeve',(s*.15,0,.86),elbow,.07,c);beam('Lower sleeve',elbow,hand,.055,c);ellipsoid('Hand',hand,(.05,.048,.06),skin)
  box('Coat front fold',(0,-.174,.72),(.02,.016,.32),woodlight)
  if hat:
   cyl('Paper cap crown',(0,0,head+.17),.16,.075,c)
   ellipsoid('Cap brim',(0,-.10,head+.14),(.20,.17,.025),c)
 return root
people=[('postman',-5.0,-1.7,.25,0,'stand'),('elder',-8.0,-.9,-.2,5,'sit'),('porch_resident',-6.9,2.0,.2,2,'stand'),('vendor_bread',-.8,2.0,0,3,'stand'),('vendor_lamp',1.0,2.0,0,0,'stand'),('customer_one',-2.6,1.25,PI,1,'stand'),('customer_two',.6,1.05,PI,4,'stand'),('courier',-3.5,1.1,1.3,3,'stand'),('musician',-2.2,-1.0,-.3,0,'sit'),('listener',-.5,-1.8,2.7,5,'sit'),('child_listener',-1.3,-1.65,2.5,0,'stand'),('kite_child',1.6,-1.5,0,1,'stand'),('child_parent',2.25,-1.9,.5,0,'stand'),('gardener',7.65,2.0,.3,2,'stand'),('water_visitor',8.3,-.7,2.0,1,'stand'),('station_attendant',-4.1,-6.15,-.2,0,'stand'),('station_traveler',-2.8,-6.18,.3,1,'stand'),('waiting_passenger',-1.45,-6.2,0,4,'sit'),('quiet_reader',6.25,4.9,-.4,3,'sit'),('returning_resident',3.15,4.05,2.0,1,'stand')]
for n,x,y,a,c,pose in people:
 if n.startswith('vendor_') or n.startswith('customer_'):x+=1.2
 if n.startswith('station_') or n=='waiting_passenger':y-=.25
 z=Z if y<3.5 else (1.65 if y>4.5 else 1.0)
 ob=person(n,x,y,a,c,z,pose)
 if 'child' in n:ob.scale=(.78,.78,.78)
 if n=='postman':
  with under(ob):box('Red seal letter',(.17,-.23,.67),(.26,.025,.17),cream,(.1,.15,.1));ellipsoid('Letter wax seal',(.17,-.248,.67),(.032,.009,.032),red)
# Kite: real folded mesh, line connects to child's approximate hand.
kite=mesh('Red paper kite',[(-.30,0,0),(0,0,.45),(.30,0,0),(0,0,-.35),(0,-.04,0)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],red)
kite.location=(2.0,-.8,3.25);kite.rotation_euler.z=.3
path('Kite string',[(1.75,-1.6,Z+.65),(1.9,-1.15,1.9),(2,-.8,3.0)],.005,cream)
path('Kite ribbon',[(2,-.8,2.90),(2.4,-.7,2.72),(2.65,-.85,2.78),(2.9,-.75,2.56)],.025,red)

COL=cols['09_Animals_SCALE_PROXIES']
def fox(name,x,y,z=Z):
 root=asset(name,(x,y,z),.35,'animal silhouette proxy; not rigged')
 with under(root):
  ico('Fox body',(0,0,.29),(.38,.16,.23),orange)
  ico('Fox neck',(-.22,0,.43),(.17,.13,.22),orange)
  ico('Fox head',(-.35,0,.54),(.22,.13,.16),orange)
  taper('Fox muzzle',(-.40,-.01,.52),(-.62,-.01,.48),.10,.025,cream,5)
  for yy in [-.09,.09]:
   mesh('Fox folded ear',[(-.38,yy,.62),(-.25,yy,.62),(-.31,yy,.82),(-.31,yy+.035,.66)],[(0,1,2),(0,2,3),(1,3,2)],orange)
   for xx in [-.18,.22]:beam('Fox leg',(xx,yy,.25),(xx+.02,yy,.04),.04,dark)
  taper('Fox tail',(.22,0,.32),(.65,.09,.49),.14,.07,orange,6)
  taper('Fox white tail',(.65,.09,.49),(.78,.1,.58),.07,.015,cream,6)
  ellipsoid('Fox eye',(-.41,-.12,.57),(.018,.012,.018),dark)
fox('garden_fox',4.45,1.8)
for i,(x,y) in enumerate([(6.3,-1.4),(7.15,-1.45)]):
 ob=asset('duck_'+str(i),(x,y,Z+.08),.3,'animal silhouette proxy; not rigged')
 with under(ob):
  ellipsoid('Duck body',(0,0,.12),(.24,.13,.13),white);ellipsoid('Duck neck',(-.12,0,.25),(.07,.07,.14),white);ellipsoid('Duck head',(-.15,0,.35),(.09,.075,.08),white);box('Duck bill',(-.26,0,.34),(.13,.08,.035),orange)
cat=asset('doorstep_cat',(-7.7,-1.65,Z),0,'animal silhouette proxy; not rigged')
with under(cat):
 ico('Cat body',(0,0,.18),(.23,.12,.16),blueleaf);ellipsoid('Cat head',(-.15,0,.36),(.12,.105,.12),blueleaf)
 for yy in [-.07,.07]:mesh('Cat ear',[(-.22,yy,.42),(-.10,yy,.42),(-.16,yy,.56)],[(0,1,2)],blueleaf)
 path('Cat tail',[(.15,0,.19),(.30,0,.3),(.3,0,.5)],.035,blueleaf)
for i,p in enumerate([(-6.1,3.6,5.3),(3.5,4.3,5.6),(7.4,1.3,4.3)]):
 ob=asset('paper_bird_'+str(i),p,.3+i*.7,'folded mesh proxy; flight rig pending')
 with under(ob):
  mesh('Bird folded body',[(-.25,0,0),(.22,0,.04),(0,-.08,-.10),(0,.08,-.10),(0,0,.12)],[(0,1,2),(0,3,1),(0,4,3),(0,2,4),(1,3,4),(1,4,2)],cream)
  mesh('Bird paper wings',[(0,0,0),(-.14,-.6,.24),(.2,-.18,.1),(-.14,.6,.24),(.2,.18,.1)],[(0,1,2),(0,4,3)],white)

print('BUILD finish',flush=True)
COL=cols['01_Plaza']
for x,y in [(-4.2,-2.5),(-5.9,1.8),(-3.0,2.4),(1.9,2.1),(3.2,-1.9),(4.2,1.2),(8.1,1.9),(8.4,-2.4),(-5.5,-4.2),(.9,-4.7),(4.2,4.8)]:lamppost('Street lantern',x,y)
# Perimeter rails are intermittent and do not block district pathways.
for start,end in [(.08,.85),(1.1,2.75),(3.0,3.8),(5.40,6.15)]:
 pts=[]
 for j in range(max(3,int((end-start)*14))):
  t=start+(end-start)*j/max(2,int((end-start)*14)-1);x=9.7*math.cos(t);y=6.3*math.sin(t)
  beam('Paper fence post',(x,y,Z),(x,y,Z+.55),.036,woodlight);pts.append((x,y,Z+.46))
 path('Paper fence rail',pts,.025,woodlight)

COL=cols['05_Water_Garden']
# Cloud is cut-paper lobes in vertical planes, not a painted sky image.
cloudmat=material('Cloud | softly filled paper',(.20,.26,.37),paper=True,emission=.12)
for layer in range(3):
 for i in range(6):
  x=8.6+(i-2.5)*.31;y=2.9+layer*.06;z=4.0+.35*math.sin(i*.9)+layer*.03
  ob=cyl('Rain cloud paper lobe',(x,y,z),.42,.035,cloudmat);ob.rotation_euler.x=PI/2
for i in range(25):
 x=7.8+R.random()*1.6;y=2.7+R.random()*.35
 beam('Rain silver thread',(x,y,3.7),(x,y,Z+.06),.005,waterline)
for i in range(3):ring('Rain ripple',(8.25,1.9,Z+.05+i*.004),.20+i*.17,.012,waterline)

COL=cols['10_Lighting']
def area(name,p,aim,power,color,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size
 ob=bpy.data.objects.new(name,d);COL.objects.link(ob);ob.location=p;ob.rotation_euler=(Vector(aim)-Vector(p)).to_track_quat('-Z','Y').to_euler();return ob
area('Soft overhead blue hour',(-3,-4,13),(0,0,0),1050,(.66,.77,1.0),12)
area('Quiet front paper fill',(2,-11,7),(0,0,1),420,(.62,.73,1.0),10)
area('Warm lantern tree pool',(-.7,-.25,2.50),(-.7,-.25,.6),100,(1,.55,.24),3.3)
area('Tea frontage warm bounce',(.4,2.25,2.7),(.4,.5,.7),105,(1,.54,.23),3.0)
area('Station warm bounce',(-2.8,-5.6,2.1),(-2.8,-6.4,.5),105,(1,.56,.25),3.5)
pointlight('Post office warm bounce',(-6.1,-1.4,1.6),45,(1,.56,.25),.7)
world=bpy.data.worlds.new('Indigo evening ambience');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.22,.38,1);world.node_tree.nodes['Background'].inputs[1].default_value=.24;scene.world=world

COL=cols['11_Cameras']
def camera(name,p,target,ortho):
 data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);COL.objects.link(ob);ob.location=p;ob.rotation_euler=(Vector(target)-Vector(p)).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=ortho;data.lens=45;data.clip_end=200;return ob
cam=camera('Camera_Main_CP01',(-6,-25,19.3),(0,0,1.35),26.0);scene.camera=cam
camera('Camera_Plan_CP01',(0,0,35),(0,0,0),26)
camera('Camera_Reverse_Proof',(-15,23,22),(0,0,1),29.2)

# Celestial details are actual thin paper meshes, oriented to the hero camera.
COL=cols['07_Paper_Foliage']
from mathutils.geometry import tessellate_polygon
def paper_shape(name,outline,pos,mat):
    poly=[Vector((x,y,0)) for x,y in outline]
    triangles=tessellate_polygon([poly])
    verts=[tuple(v) for v in poly];faces=[tuple(v if isinstance(v,int) else min(range(len(poly)),key=lambda j:(poly[j]-v).length) for v in tri) for tri in triangles]
    ob=mesh(name,verts,faces,mat);ob.location=pos;ob.rotation_euler=cam.rotation_euler
    mod=ob.modifiers.new('Visible paper thickness','SOLIDIFY');mod.thickness=.045
    return ob
moonmat=material('Moon washi glow',(1,.62,.23),paper=True,emission=.7)
outer=[(.70*math.cos(a),.70*math.sin(a)) for a in [math.radians(58)+i*math.radians(244)/40 for i in range(41)]]
# The inner curve joins the two tips, opening to screen right.
inner=[(.34+.56*math.cos(a),.56*math.sin(a)) for a in [math.radians(-99)-i*math.radians(162)/32 for i in range(33)]]
paper_shape('Paper crescent',outer+inner,(8.3,4.0,6.2),moonmat)
for i,(x,y,z) in enumerate([(-9,3.5,4.8),(-7,5.3,6),(-1.7,7.0,5.8),(3.0,6.5,5.3),(9.5,1.0,5.5)]):
    r=.11 if i%2 else .15
    outline=[((r if j%2==0 else r*.42)*math.cos(PI/2+j*PI/5),(r if j%2==0 else r*.42)*math.sin(PI/2+j*PI/5)) for j in range(10)]
    paper_shape('Paper star '+str(i),outline,(x,y,z),moonmat)

scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.cycles.max_bounces=6;scene.cycles.transparent_max_bounces=12
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 gpu=False
 for d in pref.devices:d.use=(d.type=='METAL');gpu=gpu or d.use
 scene.cycles.device='GPU' if gpu else 'CPU'
 print('RENDER_DEVICE',scene.cycles.device,[(d.name,d.type,d.use) for d in pref.devices],flush=True)
except Exception as e:scene.cycles.device='CPU';print('CPU fallback',str(e),flush=True)
scene.render.resolution_x=1672;scene.render.resolution_y=941;scene.render.resolution_percentage=65
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.15;scene.view_settings.gamma=1
scene.render.filepath=str(OUT/'overview-draft.png')
scene['checkpoint']='CP01 | full-town spatial/material prototype'
scene['approved_reference']='outputs/ecosystem-v3-lighting/borrowed-wind-town-soft-light.png'
scene['limitations']='No rigged residents, animation system, navigation, web renderer or 24/7 code. Figure and animal proxies only. Blender procedural materials need web baking/adaptation.'
# Save reference within the project as a camera background for optional manual alignment; it does not render.
try:
 im=bpy.data.images.load(str(ROOT/scene['approved_reference']),check_existing=True);im.pack()
 bg=cam.data.background_images.new();bg.image=im;bg.alpha=.25;cam.data.show_background_images=False
except Exception as e:print('Reference load note',e)
for s in bpy.data.screens:
 for a in s.areas:
  if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA'
stats={'checkpoint':'CP01','assets':assets,'objects':len(scene.objects),'mesh_objects':sum(o.type=='MESH' for o in scene.objects),'mesh_vertices':sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'),'blender_version':bpy.app.version_string,'resident_count':len(people),'reference':scene['approved_reference'],'render_device':scene.cycles.device,'not_implemented':['character rigging','continuous simulation','web runtime','24/7 backend']}
(OUT/'model-manifest.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp01.blend'))
print('SAVED',len(scene.objects),'objects',flush=True)
bpy.ops.render.render(write_still=True)
print('CP01_DRAFT_RENDER_DONE',flush=True)
