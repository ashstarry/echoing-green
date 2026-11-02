import bpy,json,math,time
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path.cwd();OUT=ROOT/'app/runtime-cp17/public/assets';REPORT=ROOT/'outputs/runtime-checkpoint-17';s=bpy.context.scene
registry=json.loads((ROOT/'outputs/art-checkpoint-16/decision-entities.json').read_text());rigs=[]
def ancestry(o):
 while o:
  yield o;o=o.parent
# Retain the accepted geometry, split residents at rigid motion pivots.
for e in registry['entities']:
 if e['kind']!='resident':continue
 root=bpy.data.objects[e['blender_object']];groups={}
 for o in list(root.children):
  if o.type!='MESH':continue
  n=o.name.lower();part=None;pivot=None;x=o.location.x;side='left'if x<0 else'right'
  if any(k in n for k in ['head','hair','cap brim','cap crown','eye','nose']):part='head';pivot=(0,0,.98)
  elif any(k in n for k in ['sleeve','hand'])and not any(k in n for k in ['kite holding','bicycle']):part='arm_'+side;pivot=((-1 if x<0 else 1)*.20,-.015,.82)
  elif any(k in n for k in ['trouser leg','shoe'])and not any(k in n for k in ['cp14','bicycle']):
   # Standing actors only; seated legs remain in their authored poses.
   if any('Seated' in c.name for c in root.children):continue
   part='leg_'+side;pivot=((-1 if x<0 else 1)*.1,-.01,.49)
  if part:groups.setdefault(part,{'pivot':pivot,'objects':[]})['objects'].append(o)
 for part,g in groups.items():
  p=bpy.data.objects.new(root.name+'__anim_'+part,None);s.collection.objects.link(p);p.parent=root;p.location=g['pivot'];p['decision_part_id']='anim_'+part;p['decision_owner']=e['id'];bpy.context.view_layer.update()
  for o in g['objects']:
   mw=o.matrix_world.copy();o.parent=p;o.matrix_parent_inverse=p.matrix_world.inverted()@root.matrix_world
   # matrix_basis stays in original root coordinates, inverse keeps exact model pose.
  e['parts'].append({'id':'anim_'+part,'blender_object':p.name,'control':'rigid_pivot','axis':'X'if part!='head'else'Z'});rigs.append({'entity':e['id'],'part':part,'source_meshes':[o.name for o in g['objects']]})
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
# Build a conservative ground-layer nav field from actual evaluated geometry.
walkers=['resident.child_runner','resident.market_browser','resident.customer_one','resident.courier','resident.garden_child','resident.strolling_parent']
vs=[];fs=[];names=[];ov=[];of=[];floors=[];fv=[];ff=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 chain=list(ancestry(o));owner=next((x.get('decision_entity_id')for x in chain if x.get('decision_entity_id')),None)
 if owner in walkers or any(k in o.name.lower()for k in ['rain','glint','ripple','studio floor']):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear()
 if not v:continue
 off=len(vs);vs.extend(v);fs.extend(tuple(off+i for i in t)for t in f);names.extend([o.name]*len(f))
# Walkable paving is a support surface, not a waist-high obstacle. Keep all other geometry.
for f,name in zip(fs,names):
 if 'plaza stone ring' not in name:
  off=len(ov);ov.extend(vs[i] for i in f);of.append((off,off+1,off+2))
world=BVHTree.FromPolygons(vs,fs,all_triangles=True);bodyworld=BVHTree.FromPolygons(ov,of,all_triangles=True)
# Cylinder must include rotation/gait and cell interpolation. Ground supports sampled at foot envelope.
step=.16;rad=.43;fieldrad=rad+step*math.sqrt(2)/2;nx=91;ny=55;ox=-7.2;oy=-3.6
nodes=[];grid={};fail={};start=time.time()
def clearance(x,y):
 floorhits=[]
 for dx,dy in [(0,0),(.21,0),(-.21,0),(0,.21),(0,-.21)]:
  hit,no,idx,d=world.ray_cast(Vector((x+dx,y+dy,.90)),Vector((0,0,-1)),.55)
  if hit is None or no.z<.75 or not .58<hit.z<.79:
   fail['support']=fail.get('support',0)+1
   if len(fail.get('examples',[]))<12 and -3<x<3 and -2<y<3:fail.setdefault('examples',[]).append([x,y,o.name if False else names[idx]if idx is not None else None,list(hit)if hit else None,list(no)if no else None])
   return None
  floorhits.append(hit.z)
 if max(floorhits)-min(floorhits)>.065:
  fail['step']=fail.get('step',0)+1
  if len(fail.get('step_examples',[]))<10:fail.setdefault('step_examples',[]).append([x,y,floorhits])
  return None
 z=max(floorhits)
 # Actual mesh swept cylinder, triangulated cap and sides.
 vv=[Vector((x,y,z+.035)),Vector((x,y,z+1.49))];n=16
 for zz in [z+.035,z+1.49]:
  vv.extend(Vector((x+fieldrad*math.cos(i*2*math.pi/n),y+fieldrad*math.sin(i*2*math.pi/n),zz))for i in range(n))
 faces=[]
 for i in range(n):
  j=(i+1)%n;faces.extend([(0,2+i,2+j),(1,2+n+j,2+n+i),(2+i,2+n+i,2+n+j),(2+i,2+n+j,2+j)])
 body=BVHTree.FromPolygons(vv,faces,all_triangles=True)
 if body.overlap(bodyworld):fail['body']=fail.get('body',0)+1;return None
 # Vertical interior probes catch small enclosed props; floor itself is excluded.
 for dx,dy in [(0,0),(.25,0),(-.25,0),(0,.25),(0,-.25)]:
  hit,no,idx,d=bodyworld.ray_cast(Vector((x+dx,y+dy,z+1.49)),Vector((0,0,-1)),1.445)
  if hit is not None:fail['inner']=fail.get('inner',0)+1;return None
 return round(z,5)
for iy in range(ny):
 for ix in range(nx):
  x=ox+ix*step;y=oy+iy*step;z=clearance(x,y)
  if z is not None:grid[f'{ix},{iy}']=len(nodes);nodes.append([round(x,4),round(y,4),z,ix,iy])
print('NAV',len(nodes),time.time()-start,flush=True)
print(json.dumps(fail),flush=True)
