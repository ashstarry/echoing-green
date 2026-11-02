import bpy,json,math,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path.cwd();OUT=ROOT/'app/runtime-cp30/public/assets';s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();registry=json.loads((OUT/'runtime-registry.json').read_text());moving=set(json.loads((OUT/'motion-activities.json').read_text())['clips'])
def ancestry(o):
 while o:yield o;o=o.parent
for e in registry['entities']:e['position']=list(bpy.data.objects[e['blender_object']].matrix_world.translation)
# Build a conservative ground-layer nav field from actual evaluated geometry.
walkers=['resident.water_visitor','resident.water_companion','resident.quiet_reader','resident.returning_resident','resident.gardener','resident.assistant_gardener','resident.listener','resident.child_listener','resident.elder','resident.waiting_passenger','resident.waiting_passenger_2','resident.station_traveler','resident.child_runner','resident.market_browser','resident.customer_one','resident.courier','resident.garden_child','resident.strolling_parent','resident.customer_two','resident.customer_three','resident.postman','resident.kite_child','resident.child_parent']
vs=[];fs=[];names=[];ov=[];of=[];floors=[];fv=[];ff=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 chain=list(ancestry(o));owner=next((x.get('decision_entity_id')for x in chain if x.get('decision_entity_id')),None)
 if any(x.get('decision_entity_id')in walkers for x in ancestry(o)) or owner in moving or owner in ['resident.cyclist','kite.plaza_kite'] or any(k in o.name.lower()for k in ['visible paper rain','glint','ripple','studio floor']):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear()
 if not v:continue
 off=len(vs);vs.extend(v);fs.extend(tuple(off+i for i in t)for t in f);names.extend([o.name]*len(f))
# Walkable paving is a support surface, not a waist-high obstacle. Keep all other geometry.
for f,name in zip(fs,names):
 if 'plaza stone ring' not in name:
  off=len(ov);ov.extend(vs[i] for i in f);of.append((off,off+1,off+2))
world=BVHTree.FromPolygons(vs,fs,all_triangles=True);bodyworld=BVHTree.FromPolygons(ov,of,all_triangles=True)
# Cylinder must include rotation/gait and cell interpolation. Ground supports sampled at foot envelope.
step=.16;rad=.43;fieldrad=rad+step*math.sqrt(2)/2;nx=146;ny=86;ox=-11.6;oy=-7.2
nodes=[];grid={};fail={};start=time.time()
def clearance(x,y):
 floorhits=[]
 for dx,dy in [(0,0),(.21,0),(-.21,0),(0,.21),(0,-.21)]:
  hit,no,idx,d=world.ray_cast(Vector((x+dx,y+dy,1.0)),Vector((0,0,-1)),.55)
  if hit is None or no.z<.75 or not .58<hit.z<.82:return None
  floorhits.append(hit.z)
 if max(floorhits)-min(floorhits)>.09:return None
 z=max(floorhits)
 # Actual mesh swept cylinder, triangulated cap and sides.
 vv=[Vector((x,y,z+.035)),Vector((x,y,z+1.72))];n=16
 for zz in [z+.035,z+1.72]:
  vv.extend(Vector((x+fieldrad*math.cos(i*2*math.pi/n),y+fieldrad*math.sin(i*2*math.pi/n),zz))for i in range(n))
 faces=[]
 for i in range(n):
  j=(i+1)%n;faces.extend([(0,2+i,2+j),(1,2+n+j,2+n+i),(2+i,2+n+i,2+n+j),(2+i,2+n+j,2+j)])
 body=BVHTree.FromPolygons(vv,faces,all_triangles=True)
 if body.overlap(bodyworld):return None
 # Vertical interior probes catch small enclosed props; floor itself is excluded.
 for dx,dy in [(0,0),(.25,0),(-.25,0),(0,.25),(0,-.25)]:
  hit,no,idx,d=bodyworld.ray_cast(Vector((x+dx,y+dy,z+1.72)),Vector((0,0,-1)),1.675)
  if hit is not None:return None
 return round(z,5)
for iy in range(ny):
 for ix in range(nx):
  x=ox+ix*step;y=oy+iy*step;z=clearance(x,y)
  if z is not None:grid[f'{ix},{iy}']=len(nodes);nodes.append([round(x,4),round(y,4),z,ix,iy])
print('NAV',len(nodes),time.time()-start,flush=True)
actors=[]
for e in registry['entities']:
 if e['id']in walkers:
  r=bpy.data.objects[e['blender_object']];nearest=sorted(range(len(nodes)),key=lambda i:(nodes[i][0]-e['position'][0])**2+(nodes[i][1]-e['position'][1])**2)[:12];actors.append({'id':e['id'],'position':e['position'],'scale':list(r.matrix_world.to_scale()),'yaw':r.matrix_world.to_euler().z,'nearest':nearest})
nav={'version':1,'coordinates':'Blender Z-up; root soles .02*scale above origin','step':step,'radius':rad,'field_radius':fieldrad,'height':1.49,'origin':[ox,oy],'size':[nx,ny],'nodes':nodes,'grid':grid,'actors':actors,'scope':'Conservative ground layer, not stairs/interiors/rail/water. Static meshes and non-walking actors retained as obstacles. Cell expansion guards interpolation; runtime actor separation remains required.'}
(OUT/'event-navigation.json').write_text(json.dumps(nav,separators=(',',':')))
