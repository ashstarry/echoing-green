import bpy,math,json,ast,random
from pathlib import Path
from mathutils import Vector,Matrix
from contextlib import contextmanager
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-07';WORK=ROOT/'work/modeling-cp07';s=bpy.context.scene;cam=s.camera;PI=math.pi;Z=.61;R=random.Random(71327);PARENT=None;assets=[]
cols={c.name:c for c in bpy.data.collections};COL=cols['07_Paper_Foliage'];templates={k:bpy.data.meshes['Shared '+k] for k in ['cube','sphere','ico','cyl']}
src=ast.parse((ROOT/'work/modeling-cp02/refine_and_present.py').read_text());node=next(n for n in src.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='aliases' for t in n.targets));exec(compile(ast.Module(body=[node],type_ignores=[]),'<aliases>','exec'))
for k,n in aliases.items():globals()[k]=bpy.data.materials[n]
src=ast.parse((ROOT/'work/modeling-cp01/build_town.py').read_text());allow={'setmat','mesh','unit','primitive','box','cyl','ellipsoid','ico','beam','taper','path','ring','asset','under','window','lantern','leaf'};exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allow],type_ignores=[]),'<helpers>','exec'))
leafmesh=bpy.data.meshes['Shared folded leaf'];flower_mesh=bpy.data.meshes['CP07 shared five-petal paper flower | 106 triangles'];sprigmesh=bpy.data.meshes['CP07 shared lobed folded paper sprig'];terr=[bpy.data.materials['Paper land layer '+str(i)] for i in range(5)]
blue2=bpy.data.materials['CP07 foliage | deep blue'];sage2=bpy.data.materials['CP07 foliage | dusk sage'];paleleaf=bpy.data.materials['CP07 foliage | pale folded edge']
Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));BACK=Vector((-RIGHT.y,RIGHT.x,0));FWD=Q@Vector((0,0,-1));UP=Q@Vector((0,1,0));rec=json.loads((OUT/'revision-record.json').read_text());segments=[(Vector(a),Vector(b),.65 if k=='stall_approach' else .72) for k,pts in rec['routes'].items() for a,b in zip(pts,pts[1:])]
src=ast.parse((WORK/'finish_environment.py').read_text());allow={'rb','protected','erase','bloom','sprig','garden','ground_at'};exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allow],type_ignores=[]),'<garden helpers>','exec'));clumps=1000;land=bpy.data.objects['Island paper layer 4']
for n in [o.name for o in s.objects if o.name.startswith('CP07 backdrop cut-paper grove')]:erase(bpy.data.objects[n])
# Layered botanical silhouettes made of small paper leaves and slender stems.
for i,(r,b,z) in enumerate([(-10.2,5.5,Z),(-9.3,6.15,Z),(-8.3,6.7,Z),(-7.2,7.2,Z),(-6.2,7.65,Z),(-5.1,7.9,Z),(-4.05,8.1,Z),(-3.0,8.35,Z),(-1.9,8.35,Z),(0,8.5,Z),(1.5,8.1,1.25),(3.25,7.9,1.85),(4.4,7.8,1.85),(6.6,7.15,1.85),(7.8,6.7,1.4),(8.9,5.8,Z),(10.1,5.1,Z)]):
 p=rb(r,b,z)
 if protected(p,.35):continue
 root=asset('CP07 rear paper sapling %02d'%i,p,R.uniform(-.35,.35)+.2)
 with under(root):
  h=R.uniform(1.35,1.9);taper('CP07 sapling folded trunk',(0,0,0),(0,0,h),.055,.018,woodlight,6)
  for j in range(7):
   sign=(-1)**j;zz=.35+j*h/9;end=Vector((sign*R.uniform(.26,.42),R.uniform(-.12,.14),zz+.36));beam('CP07 sapling twig',(0,0,zz),end,.014,woodlight)
   for k in range(3):
    pp=end+Vector((R.uniform(-.10,.10),R.uniform(-.08,.08),k*.15));sprig('CP07 little botanical sprig',pp,.31,R.choice([blueleaf,blue2,sage2,paleleaf]),R.uniform(-.55,.55)+.2,.1)
   if i in [4,10,12,13]:bloom('CP07 rear sakura cluster',end+Vector((0,0,.20)),.36,R.choice([pink,pinklight,pinkdark]))
# Give the central lanterns a clear hanging band beneath the canopy.
main=bpy.data.objects['lantern_tree']
for o in main.children:
 if any(k in o.name for k in ['blossom','petal']):o.location.z=2.20+(o.location.z-1.80)*.72
 if 'Tree hanging lantern' in o.name or 'CP07 lantern folded rib' in o.name:o.location.z-=.16
bpy.data.objects['Warm lantern tree pool'].data.energy=155
# The whole flower layer now forms a raised open crown; small leaves soften its rim.
with under(main):
 for i in range(28):
  a=i*2.399;p=(1.3*math.cos(a),.95*math.sin(a),2.15+R.random()*.4);leaf('CP07 canopy underside paper leaf',p,(.35,.5,.4),R.choice([sage2,blueleaf,pinkdark]),(.25,.15,a))

# Correct dome bands to the actual modeled hemisphere, with a decorative finial above it.
for n in [o.name for o in s.objects if o.name.startswith(('CP07 observatory dome band','CP07 observatory finial','CP07 finial curl'))]:erase(bpy.data.objects[n])
COL=cols['03_Post_Residential'];ob=bpy.data.objects['paper_observatory']
with under(ob):
 for ang in [.2,.4,.6,.8,1.0,1.2]:ring('CP07 dome paper latitude',(0,0,3.4+1.03*math.sin(ang)),1.047*math.cos(ang),.012,navy3,40)
 for sign in [-1,1]:path('CP07 dome finial curl',[(0,0,4.66),(sign*.14,0,4.69),(sign*.18,0,4.78),(sign*.12,0,4.83)],.025,gold)

# More flowers at architectural edges, with a deliberately varied rhythm.
COL=cols['07_Paper_Foliage']
for r,b,ss in [(-8.8,-1.7,.72),(-7.8,-1.9,.65),(-7.0,-2.1,.75),(-6.0,-2.05,.65),(-6.0,3.7,.8),(-5.8,4.3,.75),(-4.5,4.0,.75),(4.55,4.25,.8),(5.3,3.5,.7),(5.4,2.9,.85),(6.1,1.35,.7),(9.8,2.0,.8),(10.0,3.25,.85),(6.8,-3.75,.8)]:garden(rb(r,b),ss,pot=True)
# Window sill pots remain within the facade rather than obstructing the roadway.
COL=cols['03_Post_Residential']
for name,width,depth in [('post_office',2.8,1.8),('west_home',3.1,2.4)]:
 root=bpy.data.objects[name]
 with under(root):
  for xx in [-width*.34,width*.34]:
   taper('CP07 doorstep pot',(xx,-depth*.5-.10,.04),(xx,-depth*.5-.10,.25),.13,.19,navy2,8)
   for j in range(3):bloom('CP07 doorstep bloom',(xx+(j-1)*.09,-depth*.5-.1,.49+j*.025),.25,R.choice([pink,cream,pinklight]))

# Paired paper pillows and book make the longer bench feel intentional.
COL=cols['06_Hillside'];bench=bpy.data.objects['CP05_overlook_bench']
with under(bench):
 box('CP07 folded bench cushion',(-.45,0,.51),(.30,.28,.035),navy3)
 box('CP07 bench closed book',(-.46,.02,.55),(.21,.16,.035),red,(0,0,.12))
 box('CP07 bench book paper edge',(-.46,.02,.557),(.20,.15,.02),cream,(0,0,.12))
# A few hand-cut stones break the perfect horizontal base bands without granular noise.
COL=cols['00_Terrain']
for i in range(27):
 a=PI+PI*i/26;p=rb(12.7*math.cos(a),-.80+7.35*math.sin(a),.29)
 if ground_at(p) is not None:
  o=ico('CP07 layered bank paper face',p,(R.uniform(.42,.72),R.uniform(.30,.45),R.uniform(.22,.32)),R.choice([terr[2],terr[3],terr[4]]));o.rotation_euler.z=a
for me in bpy.data.meshes:
 if not me.users or not me.polygons or me.uv_layers:continue
 uv=me.uv_layers.new(name='UVMap')
 for poly in me.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(poly.normal[i]))]
  for li in poly.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]*2,p[axes[1]]*2)
for o in s.objects:
 if o.type=='CURVE':o.data.bevel_resolution=min(o.data.bevel_resolution,1)
rec['polish']={'rear_grove':'slender branched card silhouettes, scaled to subordinate architecture','lantern_tree':'raised canopy with visible hanging lantern band','added_potted_clusters':clumps-1000,'dome':'bands match actual hemisphere'}
(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.context.view_layer.update()
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.samples=80;s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100;s.render.filepath=str(WORK/'polished.png');bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'polished.blend'));bpy.ops.render.render(write_still=True);print('CP07_POLISHED_READY',flush=True)
