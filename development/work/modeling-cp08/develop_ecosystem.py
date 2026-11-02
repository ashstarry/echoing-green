exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
rec=json.loads((OUT/'revision-record.json').read_text());segments=[(Vector(a),Vector(b),.65 if k=='stall_approach' else .72) for k,pts in rec['routes'].items() for a,b in zip(pts,pts[1:])]
def protected(p,radius=.3):
 for a,b,w in segments:
  d=Vector((b.x-a.x,b.y-a.y,0));q=Vector((p.x-a.x,p.y-a.y,0));t=max(0,min(1,q.dot(d)/max(1e-8,d.length_squared)))
  if (q-d*t).length<w+radius and abs(p.z-(a.z+t*(b.z-a.z)))<1.7:return True
 return False
def plant(name,p,sc=1,pot=True,color=None):
 if protected(p,.35*sc):return
 root=asset(name,p);root['entity_kind']='plant';root['decision_role']='environment_state';root['movable']=True
 with under(root):
  z=0
  if pot:taper(name+' folded planter',(0,0,0),(0,0,.25*sc),.15*sc,.22*sc,R.choice([navy2,woodlight,terr[3]]),8);z=.24*sc
  for j in range(8):
   a=j*2.399;leaf(name+' paper leaf',(.14*sc*math.cos(a),.14*sc*math.sin(a),z+.20*sc),(.65*sc,1.05*sc,.65*sc),R.choice([sage,blueleaf,leafcream]),(R.uniform(.25,.75),R.uniform(-.3,.3),a))
  for j in range(5):
   x,y=R.uniform(-.24,.24)*sc,R.uniform(-.17,.17)*sc;h=z+R.uniform(.40,.74)*sc;beam(name+' flower stem',(x*.5,y*.5,z),(x,y,h),.008*sc,sage);bloom(name+' blossom',(x,y,h),R.uniform(.25,.37)*sc,color or R.choice([pink,pinklight,cream]),root)
 return root

# Relocate the whole waterside assembly, including bridge occupants and weather props.
# This creates a readable garden forecourt between the glasshouse and the pond.
COL=cols['05_Water_Garden'];delta=RIGHT*(-.22)+BACK*(-1.05);water_roots=[]
for o in list(COL.objects):
 if o.parent is None and o.name!='greenhouse':o.location+=delta;water_roots.append(o.name)
for name in ['duck_0','duck_1','water_visitor','water_companion']:bpy.data.objects[name].location+=delta
rec['water_move']={'delta':list(delta),'root_objects':water_roots,'occupants':['duck_0','duck_1','water_visitor','water_companion']}
bpy.context.view_layer.update()

# Continuous street paving is rebuilt against the current pond and plaza footprints.
COL=cols['01_Plaza'];erase(bpy.data.objects['CP02 open street paving']);pond=bpy.data.objects['CP02 pond'];pc=Vector((pond.location.x,pond.location.y,Z));center=bpy.data.objects['plaza_ground'].location;railcenter=rb(0,-.52,Z)
rose=bpy.data.materials.get('CP08 plaza | dusty rose') or variant(ivory,'CP08 plaza | dusty rose',(.64,.51,.40))
stones=[bpy.data.materials['CP08 plaza | warm limestone'],bpy.data.materials['CP08 plaza | light edge'],rose];verts=[];faces=[];mi=[]
for j in range(-25,26):
 for i in range(-43,44):
  u=i*.29+(j%2)*.145;v=j*.30
  if (u/11.55)**2+(v/6.35)**2>1:continue
  p=railcenter+RIGHT*u+BACK*v;p.z=Z+.018;d=p-pc
  if (d.dot(RIGHT)/3.14)**2+(d.dot(BACK)/2.24)**2<1:continue
  if (Vector((p.x-center.x,p.y-center.y,0))).length<4.34:continue
  k=len(verts);verts.extend([tuple(p+RIGHT*x+BACK*y+Vector((0,0,z))) for z in [-.022,0] for x,y in [(-.136,-.141),(.136,-.141),(.136,.141),(-.136,.141)]])
  faces.extend([tuple(k+x for x in f) for f in [(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]);idx=R.choices([0,1,2],[8,3,1])[0];mi.extend([idx]*5)
o=mesh('CP08 continuous street paving',verts,faces,None)
for m in stones:o.data.materials.append(m)
for p,m in zip(o.data.polygons,mi):p.material_index=m

# The garden's details are grouped against the facade and banks, not in the through lane.
COL=cols['07_Paper_Foliage'];pots=[]
for i,(xx,yy,sc) in enumerate([(1087,355,.9),(1114,369,.72),(1147,385,.9),(1183,420,.75),(1200,433,.65),(1249,425,.75),(1356,432,.8),(1400,459,.95),(1080,583,1),(1092,623,.8),(1466,657,.85),(1510,606,.85),(546,410,.8),(555,460,.75),(543,507,.8),(333,480,.8),(287,483,.7),(206,444,.6)]):
  ob=plant('garden_planter_%02d'%i,xy((xx,yy)),sc,True)
  if ob:pots.append(ob.name)
# Flower boxes on low retaining walls tie the district edges together.
COL=cols['03_Post_Residential']
def low_border(name,a,b,rail=True):
 a,b=xy(a),xy(b);mid=(a+b)/2;d=b-a;angle=math.atan2(d.y,d.x);root=asset(name,mid,angle)
 with under(root):
  box(name+' paper wall',(0,0,.16),(d.length,.22,.30),terr[3])
  box(name+' warm stone cap',(0,0,.33),(d.length+.06,.28,.06),cream)
  if rail:
   n=max(2,round(d.length/.55))
   for j in range(n+1):box(name+' wood post',(-d.length/2+j*d.length/n,0,.61),(.06,.06,.58),woodlight)
   for h in [.55,.79]:beam(name+' cross rail',(-d.length/2,0,h),(d.length/2,0,h),.022,woodlight)
 return root
low_border('CP08 left district boundary',(525,424),(541,451));low_border('CP08 left district boundary south',(542,489),(548,523))
COL=cols['05_Water_Garden'];low_border('CP08 garden low retaining wall',(1052,366),(1130,395))

# A compact potting table, terracotta pots and tools give the greenhouse an inhabited edge.
gh=bpy.data.objects['greenhouse'];glass.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.65,.48,.22,1);glass.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value=.11;glass.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.36
table=asset('greenhouse_potting_table',xy((1372,420)),math.radians(-12));table['entity_kind']='workstation';table['movable']=True
with under(table):
 box('CP08 potting tabletop',(0,0,.62),(.85,.44,.055),woodlight)
 for x in [-.33,.33]:
  for y in [-.15,.15]:box('CP08 potting table legs',(x,y,.31),(.065,.065,.62),wood)
 for x in [-.25,0,.25]:taper('CP08 spare clay pot',(x,0,.65),(x,0,.84),.07,.11,orange,8)
 box('CP08 seed packet',(.20,-.15,.69),(.16,.08,.07),cream,(.25,0,.1))

# The willow uses a pivoted canopy and inexpensive folded strips, retaining room at the bridge.
COL=cols['07_Paper_Foliage'];willow=asset('pond_willow',xy((1452,510)));willow['entity_kind']='tree';willow['movable']=True
with under(willow):
 taper('CP08 willow trunk',(0,0,0),(.12,0,1.62),.10,.045,wood,7)
 crown=asset('pond_willow_canopy',(0,0,1.55));crown.parent=willow;crown['movable_part']=True;crown['pivot_role']='wind_sway'
 with under(crown):
  for j in range(14):
   a=j*2.399;rr=R.uniform(.65,1.05);pts=[(0,0,0),(rr*.45*math.cos(a),rr*.45*math.sin(a),.22),(rr*math.cos(a),rr*math.sin(a),-.13),(rr*math.cos(a),rr*math.sin(a),-.85)]
   path('CP08 willow curved paper stem',pts,.014,woodlight)
   for k in range(8):
    u=k/7;p=Vector((rr*(.45+.55*min(1,u*2))*math.cos(a),rr*(.45+.55*min(1,u*2))*math.sin(a),.18-u*.94));leaf('CP08 willow hanging leaf',p,(.35,.72,.45),R.choice([sage,leafcream,blueleaf]),(1.20,.12,a))

# Pond tone, concentric paper ripples, stepping bank facets and two swimming entities.
COL=cols['05_Water_Garden'];water.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.035,.13,.23,1);water.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.43
for name in ['duck_0','duck_1']:
 p=bpy.data.objects[name].location.copy();p.z=Z+.053
 for k in range(3):
  pts=[tuple(p+RIGHT*((.35+k*.14)*math.cos(j*2*PI/36))+BACK*((.17+k*.075)*math.sin(j*2*PI/36))) for j in range(36)];path('CP08 duck wake '+name,pts,.006,waterline,True)
for i,(dx,dy) in enumerate([(-1.3,-.5),(.3,-.9),(1.55,-.35),(-.5,.3)]):
 p=pc+RIGHT*dx+BACK*dy;p.z=Z+.052;cyl('CP08 floating lily leaf',p,.20,.014,sage)
 if i!=1:bloom('CP08 floating lily bloom',p+Vector((0,0,.03)),.30,pinklight)
for i,(dx,dy,col) in enumerate([(-.55,-.65,orange),(.75,-.7,cream)]):
 p=pc+RIGHT*dx+BACK*dy;p.z=Z+.055;fish=asset('pond_fish_'+str(i),p,R.uniform(-.6,.6));fish['entity_kind']='fish';fish['movable']=True
 with under(fish):
  ico('CP08 folded fish body',(0,0,0),(.24,.085,.045),col);mesh('CP08 folded fish tail',[(-.19,0,0),(-.37,-.11,0),(-.34,0,.035),(-.37,.11,0)],[(0,1,2),(0,2,3)],col)

# Distinct additional residents increase the ecology, retaining identifiable entities.
COL=cols['08_Residents_SCALE_PROXIES'];new_people=[]
for name,pix,coat,sc,yaw in [('child_runner',(908,553),1,.77,.6),('strolling_parent',(580,464),3,1.0,-.3),('garden_child',(1101,438),0,.78,.5),('assistant_gardener',(1282,449),5,1.0,.2),('market_browser',(1008,383),4,1.0,2.8)]:
 p=xy(pix);o=person(name,p.x,p.y,yaw,coat,Z,'stand');o.scale=(sc,sc,sc);o['entity_kind']='resident';o['movable']=True;new_people.append(name)
# A real bicycle and a rider whose limbs are separate components for later rigging.
COL=cols['04_Station_Tram'];bike=asset('street_bicycle',xy((602,417)),math.radians(12));bike['entity_kind']='bicycle';bike['movable']=True
with under(bike):
 for x in [-.48,.48]:
  wheel=asset('bicycle_wheel_'+('rear' if x<0 else 'front'),(x,0,.31));wheel.parent=bike;wheel['movable_part']=True;wheel['pivot_role']='axle local Y'
  with under(wheel):
   path('CP08 cycle tire',[(.30*math.cos(j*2*PI/28),0,.30*math.sin(j*2*PI/28)) for j in range(28)],.021,dark,True)
   for j in range(10):a=j*PI/5;beam('CP08 cycle spoke',(0,0,0),(.28*math.cos(a),0,.28*math.sin(a)),.004,woodlight)
 for a,b in [((-.48,0,.31),(-.1,0,.70)),((-.1,0,.70),(.04,0,.30)),((.04,0,.30),(-.48,0,.31)),((-.1,0,.70),(.34,0,.67)),((.34,0,.67),(.04,0,.30)),((.34,0,.67),(.48,0,.31)),((.34,0,.67),(.3,0,.91))]:beam('CP08 cycle frame',a,b,.02,navy)
 box('CP08 cycle saddle',(-.12,0,.75),(.24,.16,.045),wood);beam('CP08 cycle handlebars',(.3,-.18,.91),(.3,.18,.91),.017,dark)
 taper('CP08 cycle front basket',(.51,0,.68),(.51,0,.90),.14,.19,woodlight,8)
COL=cols['08_Residents_SCALE_PROXIES'];p=bike.location;cyclist=person('cyclist',p.x,p.y,0,2,Z,'sit');cyclist.location=bike.matrix_world@Vector((-.12,0,.29));cyclist.rotation_euler.z=bike.rotation_euler.z+PI/2;cyclist['entity_kind']='resident';cyclist['movable']=True;cyclist['attached_vehicle']='street_bicycle';new_people.append('cyclist')
for o in list(cyclist.children):
 if o.name.startswith(('Upper sleeve','Lower sleeve','Hand')):erase(o)
with under(cyclist):
 for side in [-1,1]:
  beam('CP08 cycling upper sleeve',(side*.15,0,.86),(side*.22,-.22,.70),.068,coatmats[2]);beam('CP08 cycling lower sleeve',(side*.22,-.22,.70),(side*.17,-.39,.62),.052,coatmats[2]);ico('CP08 cycling hand',(side*.17,-.39,.62),(.05,.045,.05),skin)

# Actual warm spill in the garden and beneath the tree canopy.
COL=cols['10_Lighting'];tree=bpy.data.objects['lantern_tree'];d=bpy.data.lights.new('CP08 warm tree canopy bounce','POINT');d.energy=32;d.color=(1,.34,.07);d.shadow_soft_size=.70;o=bpy.data.objects.new(d.name,d);COL.objects.link(o);o.location=tree.matrix_world@Vector((0,-.22,1.62))
d=bpy.data.lights.new('CP08 greenhouse interior wash','AREA');d.energy=48;d.shape='DISK';d.size=1.6;d.color=(1,.50,.16);o=bpy.data.objects.new(d.name,d);COL.objects.link(o);o.location=gh.matrix_world@Vector((0,0,1.70))

rec['ecosystem_details']={'new_residents':new_people,'additional_animals':['pond_fish_0','pond_fish_1'],'new_garden_planters':pots,'movable_components':['street_bicycle','bicycle_wheel_front','bicycle_wheel_rear','pond_willow','pond_willow_canopy','greenhouse_potting_table'],'runtime_implemented':False}
for me in bpy.data.meshes:
 if not me.users or not me.polygons or me.uv_layers:continue
 uv=me.uv_layers.new(name='UVMap')
 for poly in me.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(poly.normal[i]))]
  for li in poly.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]*2,p[axes[1]]*2)
for o in s.objects:
 if o.type=='CURVE':o.data.bevel_resolution=min(o.data.bevel_resolution,1)
bpy.context.view_layer.update();(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.samples=64;s.render.resolution_percentage=100;s.render.filepath=str(WORK/'ecosystem-draft.png');bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'ecosystem-draft.blend'));bpy.ops.render.render(write_still=True);print('CP08_ECOSYSTEM_DRAFT_READY',flush=True)
