exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
from mathutils.bvhtree import BVHTree
def chain(o):
 a=[]
 while o:a.append(o);o=o.parent
 return a
def move(o,d):
 f=o.parent.matrix_world@o.matrix_parent_inverse if o.parent else Matrix.Identity(4);o.location+=f.to_3x3().inverted()@Vector(d)
def place(o,p):move(o,Vector(p)-o.matrix_world.translation);bpy.context.view_layer.update()
rec=json.loads((OUT/'revision-record.json').read_text())

# Two distinct tram bodies with an articulated-looking gap, not overlapping shells.
front=bpy.data.objects['tram_car_front'];rear=bpy.data.objects['tram_car_rear'];old=front.matrix_world.translation.copy();center=old-RIGHT*(12*math.cos(-1.17))-BACK*(6.3*math.sin(-1.17));t=-1.13;p=center+RIGHT*(12*math.cos(t))+BACK*(6.3*math.sin(t));p.z=old.z;place(front,p);d=RIGHT*(-12*math.sin(t))+BACK*(6.3*math.cos(t));front.rotation_euler.z=math.atan2(d.y,d.x);bpy.context.view_layer.update()
COL=cols['04_Station_Tram'];a=rear.matrix_world@Vector((1.51,0,.24));b=front.matrix_world@Vector((-1.51,0,.24));coupler=asset('CP09_tram_coupler');coupler.parent=front;coupler.location=front.matrix_world.inverted()@((a+b)/2);coupler['decision_part_id']='coupler';coupler['decision_owner']=front['decision_entity_id'];coupler['control_kind']='endpoint_link';coupler['other_entity']=rear['decision_entity_id'];bpy.context.view_layer.update()
with under(coupler):beam('CP09 coupling drawbar',coupler.matrix_world.inverted()@a,coupler.matrix_world.inverted()@b,.012,dark)

# Real basin under the paper water surface, leaving room for a submerged hull.
COL=cols['05_Water_Garden'];pond=bpy.data.objects['CP02 pond'];world=[pond.matrix_world@v.co for v in pond.data.vertices];top=max(p.z for p in world);outline=[p for p in world if abs(p.z-top)<1e-5];n=len(outline);verts=[(p.x,p.y,z) for z in [.32,.83] for p in outline];faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];cut=mesh('CP09 basin cutter',verts,faces,None)
land=bpy.data.objects['Island paper layer 4'];mod=land.modifiers.new('CP09 actual pond basin','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=land;bpy.ops.object.modifier_apply(modifier=mod.name);erase(cut)
def in_water(p):
 inside=False
 for a,b in zip(outline,outline[1:]+outline[:1]):
  if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:inside=not inside
 return inside
# Delete complete disconnected paving tiles that lie within the basin footprint.
o=bpy.data.objects['CP08 continuous street paving'];me=o.data;remove=set()
for poly in me.polygons:
 c=o.matrix_world@poly.center
 if in_water(c):remove.update(poly.vertices)
import bmesh
o.data=o.data.copy();bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in remove],context='VERTS');bm.to_mesh(o.data);bm.free();o.data.update()

# A watertight hollow rowboat: outer shell, rim thickness, inner sides and raised dry floor.
boat=bpy.data.objects['pond_boat']
for name in [o.name for o in boat.children]:erase(bpy.data.objects[name])
place(boat,xy((1210,611),top+.020));boat.rotation_euler.z=math.radians(8);bpy.context.view_layer.update()
outline2=[(-.90,0),(-.63,-.31),(.42,-.34),(.78,-.20),(.93,0),(.78,.20),(.42,.34),(-.63,.31)];n=len(outline2);v=[]
for scale,z in [(.70,-.11),(1,.32),(.86,.29),(.63,.08)]:v.extend([(x*scale,y*scale,z+(.025 if abs(x)>.8 and z>0 else 0)) for x,y in outline2])
f=[tuple(range(n-1,-1,-1)),tuple(range(3*n,4*n))]
for i in range(n):
 j=(i+1)%n;f.extend([(i,j,n+j,n+i),(n+i,n+j,2*n+j,2*n+i),(2*n+i,2*n+j,3*n+j,3*n+i)])
with under(boat):
 hull=mesh('CP09 hollow paper boat hull',v,f,woodlight)
 path('CP09 laminated gunwale',[(x,y,.335+(.025 if abs(x)>.8 else 0)) for x,y in outline2],.025,wood,True)
 for x in [-.38,.28]:box('CP09 boat cross bench',(x,0,.25),(.17,.54,.045),woodlight)
 for y in [-.13,0,.13]:box('CP09 boat floor board',(-.02,y,.095),(1.13,.11,.025),wood)
 mesh('CP09 bow paper deck',[(.48,-.26,.27),(.85,-.10,.31),(.93,0,.33),(.85,.10,.31),(.48,.26,.27)],[(0,1,2),(0,2,4),(2,3,4)],woodlight)
 for rad in [.035,.060,.085]:ring('CP09 coil of rope',(.62,0,.302),rad,.007,cream,20)
 for side in [-1,1]:
  oar=asset('CP09_oar_'+('left' if side<0 else 'right'),(-.16,side*.32,.32));oar.parent=boat;oar['decision_part_id']='oar_'+('left' if side<0 else 'right');oar['decision_owner']=boat['decision_entity_id'];oar['control_kind']='rotation';oar['control_axis']='local Z'
  with under(oar):
   beam('CP09 oar shaft',(.25,-side*.12,0),(-.68,side*.30,-.08),.018,woodlight)
   mesh('CP09 folded oar blade',[(-.62,side*.25,-.08),(-.85,side*.23,-.07),(-1.02,side*.39,-.09),(-.91,side*.49,-.09),(-.68,side*.35,-.08),(-.79,side*.35,-.05)],[(0,1,5),(1,2,5),(2,3,5),(3,4,5),(4,0,5)],woodlight)
  ring('CP09 brass oarlock',(-.16,side*.32,.32),.035,.009,gold,12)

# Clear animal positions with actual support, rather than burying them in planters or poles.
place(bpy.data.objects['garden_fox'],xy((1155,466),Z));annex=bpy.data.objects['small_wood_home'];place(bpy.data.objects['doorstep_cat'],annex.matrix_world@Vector((.35,-1.28,.05)))
pc=pond.matrix_world.translation.copy();place(bpy.data.objects['pond_fish_0'],rb(8.1,-4.02,top+.03));place(bpy.data.objects['pond_fish_1'],rb(9.15,-3.35,top+.035))
for name in ['CP07 garden full blossom.261','CP07 broad ground leaf.277']:
 o=bpy.data.objects.get(name)
 if o:erase(o)
# Move the lily that crossed the duck body to a bank-side patch.
for o in s.objects:
 if o.name.startswith('CP02 lily') and ('petal.005' in o.name or 'petal.006' in o.name or 'petal.007' in o.name or 'petal.008' in o.name or 'petal.009' in o.name):move(o,RIGHT*.45-BACK*.30)

# Ground the two terrestrial animals on the explicit floor/steps only.
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();sv=[];sf=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render or any(c.hide_render or c.name.startswith('12_') for c in o.users_collection):continue
 name=o.name.lower()
 if any(k in name for k in ['roof','shingle','seat','bench','table']):continue
 if not any(k in name for k in ['floor','paving','platform','deck','tread','landing','step','island paper layer','stone ring']):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();off=len(sv);sv.extend(ev.matrix_world@v.co for v in me.vertices);sf.extend(tuple(off+i for i in t.vertices) for t in me.loop_triangles);ev.to_mesh_clear()
support=BVHTree.FromPolygons(sv,sf,all_triangles=True);animal_support=[]
for name in ['garden_fox','doorstep_cat']:
 root=bpy.data.objects[name];ps=[o.matrix_world@v.co for o in root.children_recursive if o.type=='MESH' for v in o.data.vertices];low=min(p.z for p in ps);ds=[]
 for p in [p for p in ps if p.z<low+.025]:
  q,n,i,d=support.ray_cast(p+Vector((0,0,.5)),Vector((0,0,-1)),1.0)
  if q is not None:ds.append(q.z-low+.003)
 if ds:move(root,(0,0,max(ds)));animal_support.append({'animal':name,'delta':max(ds)})
rec['vehicle_and_water_repairs']={'front_tram_parameter':t,'coupling_gap_world':(a-b).length,'actual_basin_depth':top-.32,'boat':'Watertight hollow shell, inner floor, benches, rim, bow deck, rope and pivoted oars','animal_support':animal_support};bpy.context.view_layer.update();(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'vehicle-clean.blend'));print('CP09_BOAT_AND_VEHICLES_READY',flush=True)
