exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
from mathutils.bvhtree import BVHTree
def chain(o):
 a=[]
 while o:a.append(o);o=o.parent
 return a
def move(o,d):
 f=o.parent.matrix_world@o.matrix_parent_inverse if o.parent else Matrix.Identity(4);o.location+=f.to_3x3().inverted()@Vector(d)
def place(o,p):move(o,Vector(p)-o.matrix_world.translation);bpy.context.view_layer.update()
def deform(o,frame,fn):
 if o.type!='MESH':return
 o.data=o.data.copy();m=frame.inverted()@o.matrix_world;inv=o.matrix_world.inverted()@frame
 for v in o.data.vertices:v.co=inv@fn(m@v.co)
 o.data.update()
tea=bpy.data.objects['tea_house']
for o in list(tea.children_recursive):
 if o.name.startswith(('CP07 menu tablet','CP07 menu ink')):move(o,tea.matrix_world.to_3x3()@Vector((0,1.61,0)))
 if o.name.startswith('CP07 short indigo noren'):move(o,tea.matrix_world.to_3x3()@Vector((0,-.64,0)))
 if o.name.startswith('tea_house story beam') and (tea.matrix_world.inverted()@o.matrix_world.translation).z<.5:erase(o)

# Restore the separation of the west annex and post-office roofs around the balcony.
home=bpy.data.objects['west_home'];annex=bpy.data.objects['small_wood_home'];post=bpy.data.objects['post_office'];move(annex,-RIGHT*.36);move(post,RIGHT*.32)
for o in bpy.data.objects['small_wood_home roof'].children_recursive:
 def trim(p):
  if p.x>1.0:p.x=1.0+(p.x-1.0)*.02
  return p
 deform(o,annex.matrix_world,trim)
for o in home.children:
 if o.name.startswith(('CP02 west balcony','CP02 balcony baluster','CP02 balcony handrail','CP09 balcony side','CP09 balcony diagonal')):
  def widen(p):p.x*=1.20;return p
  deform(o,home.matrix_world,widen)
 if o.name.startswith(('CP07 laundry cord','CP07 folded balcony cloth')):move(o,home.matrix_world.to_3x3()@Vector((0,-.50,0)))

# Keep complete passenger heads in front of the canopy silhouette.
st=bpy.data.objects['station_main']
for name in ['waiting_passenger','waiting_passenger_2','station_seat_A','station_seat_B']:move(bpy.data.objects[name],st.matrix_world.to_3x3()@Vector((0,-.13,0)))
move(bpy.data.objects['station_attendant'],st.matrix_world.to_3x3()@Vector((0,-.08,0)))
move(bpy.data.objects['station_traveler'],st.matrix_world.to_3x3()@Vector((-.27,0,0)))
for o in s.objects:
 if 'paving seam' in o.name.lower():move(o,(0,0,-.012))
if bpy.data.objects.get('garden_planter_02'):move(bpy.data.objects['garden_planter_02'],-RIGHT*.28)
o=bpy.data.objects.get('CP07 broad ground leaf.390')
if o:move(o,-RIGHT*.22)
place(bpy.data.objects['garden_child'],xy((1090,485),Z+.01));move(bpy.data.objects['gardener'],-BACK*.22)

# Refit crank and limbs with side clearance. Real holes in the hands surround the grips.
COL=cols['08_Residents_SCALE_PROXIES'];bike=bpy.data.objects['street_bicycle'];rider=bpy.data.objects['cyclist'];place(bike,xy((985,580),Z));bpy.context.view_layer.update()
for name in [o.name for o in rider.children if o.name.startswith(('CP09 cyclist thigh','CP09 cyclist shin','CP09 cyclist shoe','CP09 cyclist upper','CP09 cyclist forearm','CP09 cyclist hand'))]:erase(bpy.data.objects[name])
for name in [o.name for o in bike.children if o.name.startswith(('CP09 crank','CP09 cycle pedal'))]:erase(bpy.data.objects[name])
def local(p):return rider.matrix_world.inverted()@(bike.matrix_world@Vector(p))
with under(rider):
 for side in [-1,1]:
  hip=(-.12,side*.12,.85);knee=(.18,side*.25,.62 if side<0 else .53);foot=(.11 if side<0 else -.07,side*.27,.49 if side<0 else .29)
  beam('CP09 cyclist thigh',local(hip),local(knee),.062,navy);beam('CP09 cyclist shin',local(knee),local((foot[0],foot[1],foot[2]+.05)),.049,navy);box('CP09 cyclist shoe',local(foot),(.12,.22,.075),dark)
  elbow=(.07,side*.22,1.02);wrist=(.215,side*.18,.95);beam('CP09 cyclist upper sleeve',local((-.12,side*.15,1.265)),local(elbow),.065,coatmats[2]);taper('CP09 cyclist forearm',local(elbow),local(wrist),.052,.041,coatmats[2],10)
  vs=[];fs=[];n=16
  for y in [side*.18-.032,side*.18+.032]:
   for r in [.021,.049]:
    for j in range(n):a=2*PI*j/n;vs.append(tuple(local((.30+r*math.cos(a),y,.91+r*math.sin(a)))))
  for j in range(n):
   k=(j+1)%n;fs.extend([(j,k,n+k,n+j),(2*n+j,3*n+j,3*n+k,2*n+k),(j,2*n+j,2*n+k,k),(n+j,n+k,3*n+k,3*n+j)])
  mesh('CP09 open grip hand',vs,fs,skin)
COL=cols['04_Station_Tram']
with under(bike):
 beam('CP09 crank axle',(.02,-.14,.34),(.02,.14,.34),.018,dark)
 for side in [-1,1]:
  x=.11 if side<0 else -.07;z=.437 if side<0 else .237;beam('CP09 crank arm',(.02,side*.14,.34),(x,side*.205,z),.010,gold);box('CP09 cycle pedal',(x,side*.27,z),(.18,.13,.025),dark)
for o in bike.children:
 if o.name=='CP08 cycle saddle':move(o,bike.matrix_world.to_3x3()@Vector((0,0,.0095)))

# Make the kite tether terminate at a raised hand instead of crossing another resident.
COL=cols['08_Residents_SCALE_PROXIES'];child=bpy.data.objects['kite_child']
for o in list(child.children):
 if o.type=='MESH' and o.name.startswith(('Upper sleeve','Lower sleeve','Hand')) and o.location.x<0:erase(o)
with under(child):
 beam('CP09 kite upper sleeve',(-.15,0,.86),(-.28,-.08,.98),.07,coatmats[1]);beam('CP09 kite raised forearm',(-.28,-.08,.98),(-.28,-.12,1.17),.055,coatmats[1]);ico('CP09 kite holding hand',(-.28,-.12,1.17),(.05,.048,.06),skin)
bpy.context.view_layer.update();hand=child.matrix_world@Vector((-.28,-.12,1.19));body=bpy.data.objects['Red paper kite'];tip=min((body.matrix_world@v.co for v in body.data.vertices),key=lambda p:p.z);line=bpy.data.objects.get('CP02 kite string') or bpy.data.objects['Kite string'];inv=line.matrix_world.inverted();pts=[hand,hand.lerp(tip,.52)+RIGHT*.04,tip]
for q,p in zip(line.data.splines[0].points,pts):q.co=(*(inv@p),1)

# Search only the rebuilt balcony floor for a full-body, collision-free standing location.
bpy.context.view_layer.update();porch=bpy.data.objects['porch_resident'];dg=bpy.context.evaluated_depsgraph_get();vv=[];ff=[];owner=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE'] or o.hide_render or porch in chain(o) or any(c.hide_render or c.name.startswith('12_') for c in o.users_collection):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();off=len(vv);vv.extend(ev.matrix_world@v.co for v in me.vertices)
 for t in me.loop_triangles:ff.append(tuple(off+i for i in t.vertices));owner.append(o.name)
 ev.to_mesh_clear()
world=BVHTree.FromPolygons(vv,ff,all_triangles=True);localv=[];localf=[];oldinv=porch.matrix_world.inverted()
for o in porch.children_recursive:
 if o.type!='MESH':continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();off=len(localv);localv.extend(oldinv@ev.matrix_world@v.co for v in me.vertices);localf.extend(tuple(off+i for i in t.vertices) for t in me.loop_triangles);ev.to_mesh_clear()
floor=bpy.data.objects['CP02 west balcony'];top=max((floor.matrix_world@v.co).z for v in floor.data.vertices);candidates=[]
for x in [-1.0,-.85,-.70,-.55,-.40,-.25,0,.25,.45,.65]:
 for y in [-1.76,-1.88,-2.02,-2.12]:
  p=home.matrix_world@Vector((x,y,0));p.z=top-.0216+.003;m=Matrix.Translation(p)@Matrix.Rotation(home.rotation_euler.z,4,'Z')@Matrix.Diagonal(Vector((1.08,1.08,1.08,1)));bv=BVHTree.FromPolygons([m@v for v in localv],localf,all_triangles=True);pairs=bv.overlap(world);bad=set(owner[b] for a,b in pairs);uv=pixel(p);score=len(pairs)*1000+(uv[0]-333)**2+(uv[1]-366)**2;candidates.append({'local':[x,y],'position':list(p),'pairs':len(pairs),'obstacles':sorted(bad),'score':score})
best=min(candidates,key=lambda x:x['score']);place(porch,Vector(best['position']));rec=json.loads((OUT/'revision-record.json').read_text());rec['remaining_contact_repairs']={'balcony_search_best':best,'balcony_candidates':candidates,'post_office_right_shift':.32,'annex_additional_left_shift':.36,'balcony_width_factor':1.2,'cyclist_moved_to_pixel':[985,580],'hands':'Actual open ring grips, .021 inner radius around .017 handlebar','pedals':'Sole and pedal surfaces separated by .003','kite_tether_reanchored':True};(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'resolved-contacts.blend'));print('BALCONY_SEARCH',json.dumps(best),flush=True)
