import bpy,math,json,bisect
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/art-checkpoint-13';WORK=ROOT/'work/art-cp13';s=bpy.context.scene;cam=s.camera;rec=json.loads((ROOT/'outputs/modeling-checkpoint-10/revision-record.json').read_text());dg=bpy.context.evaluated_depsgraph_get();FWD=cam.rotation_euler.to_quaternion()@Vector((0,0,-1))
def root_of(o):
 while o.parent:o=o.parent
 return o
def actor_ancestor(o):
 while o:
  if o.get('entity_id') and any(c.name in ['08_Residents_SCALE_PROXIES','09_Animals_SCALE_PROXIES'] for c in o.users_collection):return o
  o=o.parent
 return None
def belongs_to(o,target):
 while o:
  if o==target:return True
  o=o.parent
 return False
verts=[];tris=[];owners=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE'] or o.hide_render or any(c.hide_viewport or c.name.startswith('12_') for c in o.users_collection):continue
 root=root_of(o);actor=actor_ancestor(o)
 if actor and actor.name!='quiet_reader':continue
 # Restrict the obstacle field to the restaurant and hillside region.
 corners=[o.matrix_world@Vector(v) for v in o.bound_box]
 if corners and (max(v.y for v in corners)<-.5 or min(v.x for v in corners)>8.5 or max(v.x for v in corners)<-7):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh()
 if not me:continue
 me.calc_loop_triangles();offset=len(verts);verts.extend(ev.matrix_world@v.co for v in me.vertices)
 for tri in me.loop_triangles:tris.append(tuple(offset+i for i in tri.vertices));owners.append(o.name)
 ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,tris,all_triangles=True)
def support(p,margin=.12):
 hit,n,idx,d=bvh.ray_cast(p+Vector((0,0,margin)),Vector((0,0,-1)),margin+.35)
 return (hit,owners[idx]) if hit is not None else (None,None)
def sample_path(points,spacing=.10):
 rows=[]
 for segment,(a,b) in enumerate(zip(points,points[1:])):
  a,b=Vector(a),Vector(b);n=max(1,math.ceil((b-a).length/spacing));tangent=Vector((b.x-a.x,b.y-a.y,0)).normalized()
  for i in range(n):rows.append((segment,a.lerp(b,i/n),tangent))
 if len(points)>1:rows.append((len(points)-2,Vector(points[-1]),rows[-1][2]))
 return rows
reports={}
for key in rec['routes']:
 points=rec['routes'][key];samples=[]
 for seg,p,tangent in sample_path(points):
  floor,name=support(p,.17 if key=='gallery_treads' else .10);expected=p.z
  if floor is not None and abs(floor.z-expected)<.18:p.z=floor.z
  side=Vector((-tangent.y,tangent.x,0));collisions=[];min_clearance=10
  half_offset=.10 if key=='stall_approach' else .18
  for lateral in [-half_offset,0,half_offset]:
   for z in [.50,.80,1.10,1.20]:
    center=p+side*lateral+Vector((0,0,z));point,normal,index,distance=bvh.find_nearest(center)
    if point is not None:
     min_clearance=min(min_clearance,distance-.25)
     if distance<.247:collisions.append({'object':owners[index],'lateral':lateral,'height':z,'penetration':.25-distance})
  visibility=[]
  for z in [.60,1.0,1.30]:
   target=p+Vector((0,0,z));hit,n,index,d=bvh.ray_cast(target-FWD*40,FWD,39.97);visibility.append({'height':z,'visible':hit is None,'blocker':owners[index] if hit is not None else None})
  samples.append({'segment':seg,'foot':list(p),'floor_hit':name,'floor_delta':None if floor is None else floor.z-expected,'body_clear':not collisions,'minimum_body_clearance':min_clearance,'collisions':collisions[:5],'visible_body_samples':sum(v['visible'] for v in visibility),'visibility':visibility})
 reports[key]={'samples':samples,'sample_count':len(samples),'tested_width':.70 if key=='stall_approach' else .86,'body_clear_count':sum(x['body_clear'] for x in samples),'no_visible_body_count':sum(x['visible_body_samples']==0 for x in samples),'note':'Four sphere heights and three lateral tracks approximate a walking body envelope; this is static geometry checking, not an animated collision/navigation system.'}
# Current exterior residents are still separately sampled at their existing poses.
vis=[]
for o in s.objects:
 if not o.get('entity_id') or not any(c.name=='08_Residents_SCALE_PROXIES' for c in o.users_collection):continue
 row={'resident':o.name}
 for label,z in [('head',1.08),('upper_body',.75)]:
  p=o.matrix_world@Vector((0,0,z));hit,loc,n,fi,obj,ma=s.ray_cast(dg,p-FWD*40,FWD,distance=41);row[label]=obj is not None and belongs_to(obj,o)
 vis.append(row)
record={'checkpoint':'CP13','body_envelope':{'radius':.25,'top_height':1.45,'lateral_offsets':[-.18,0,.18],'approximate_tested_width':.86,'path_sample_spacing':.10},'routes':reports,'existing_resident_visibility':vis,'triangles_used':len(tris),'normal_view_roof_occlusion_is_physical':True,'not_implemented':['pathfinding','motion clips','dynamic avoidance','runtime roof transitions']}
(OUT/'circulation-check.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
brief={'routes':{k:{'samples':v['sample_count'],'clear':v['body_clear_count'],'fully_occluded':v['no_visible_body_count'],'first_collisions':[{'foot':r['foot'],'objects':[c['object'] for c in r['collisions']]} for r in v['samples'] if not r['body_clear']][:7]} for k,v in reports.items()},'blocked_residents':[r for r in vis if not(r['head'] and r['upper_body'])]}
(WORK/'circulation-brief.json').write_text(json.dumps(brief,ensure_ascii=False,indent=2));print(json.dumps(brief,ensure_ascii=False,indent=2))
