import bpy,math,json,hashlib,itertools
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-04';s=bpy.context.scene;cam=s.camera
def body_overlaps(scene):
 bodies=[o for o in scene.objects if o.name.endswith('paper body')]
 def polygon(o):
  p=[o.matrix_world@Vector(v) for v in o.bound_box];pts=list({(round(v.x,5),round(v.y,5)) for v in p});cx=sum(x for x,y in pts)/len(pts);cy=sum(y for x,y in pts)/len(pts)
  return sorted(pts,key=lambda v:math.atan2(v[1]-cy,v[0]-cx))
 def collide(a,b):
  for points in [a,b]:
   for p,q in zip(points,points[1:]+points[:1]):
    axis=(-(q[1]-p[1]),q[0]-p[0]);aa=[x*axis[0]+y*axis[1] for x,y in a];bb=[x*axis[0]+y*axis[1] for x,y in b]
    if min(max(aa),max(bb))-max(min(aa),min(bb))<1e-5:return False
  return True
 return sorted([sorted([a.name,b.name]) for a,b in itertools.combinations(bodies,2) if collide(polygon(a),polygon(b))])
final_overlaps=body_overlaps(s)
reference_camera=json.loads((OUT/'revision-record.json').read_text())['camera_unchanged']
camera_unchanged=all(abs(a-b)<1e-6 for a,b in zip(cam.location,reference_camera['location'])) and all(abs(a-b)<1e-6 for a,b in zip(cam.rotation_euler,reference_camera['rotation'])) and abs(cam.data.ortho_scale-reference_camera['ortho_scale'])<1e-6
fwd=cam.rotation_euler.to_quaternion()@Vector((0,0,-1));view=Vector((-fwd.x,-fwd.y,0)).normalized();dg=bpy.context.evaluated_depsgraph_get()
angles={};bounds={}
for name in ['tea_house','west_home']:
 o=bpy.data.objects[name];q=o.rotation_euler.to_quaternion();angles[name]=[math.degrees(math.acos((q@Vector(n)).dot(view))) for n in [(0,-1,0),(-1,0,0)]]
 ps=[]
 for child in o.children_recursive:
  if child.type=='MESH':ps.extend(world_to_camera_view(s,cam,child.matrix_world@v.co) for v in child.data.vertices)
 bounds[name]={'left':min(p.x for p in ps),'right':max(p.x for p in ps),'bottom':min(p.y for p in ps),'top':max(p.y for p in ps)}
res=[o for o in s.objects if o.get('entity_id') and any(c.name=='08_Residents_SCALE_PROXIES' for c in o.users_collection)]
animals=[o for o in s.objects if o.get('entity_id') and any(c.name=='09_Animals_SCALE_PROXIES' for c in o.users_collection)]
visibility=[]
for r in res:
 row={'resident':r.name}
 for label,z in [('head',1.08),('upper_body',.75)]:
  p=r.matrix_world@Vector((0,0,z));hit,loc,n,fi,o,m=s.ray_cast(dg,p-fwd*40,fwd,distance=41);ancestor=o
  while ancestor and ancestor.parent:ancestor=ancestor.parent
  row[label]=ancestor==r
 visibility.append(row)
invalid=[o.name for o in s.objects if not all(math.isfinite(v) for row in o.matrix_world for v in row)]
previous={}
for num in ['01','02','03']:
 p=ROOT/('outputs/modeling-checkpoint-'+num);f='borrowed-wind-town-cp'+num+'.blend';manifest=json.loads((p/'file-manifest.json').read_text());previous['CP'+num]=hashlib.sha256((p/f).read_bytes()).hexdigest()==manifest[f]['sha256']
record={'saved_model_reopened':True,'camera_unchanged_from_cp03':camera_unchanged,'camera_type':cam.data.type,'camera_elevation':math.degrees(math.asin(abs(fwd.z))),'horizontal_face_angles':angles,'target_buildings_projected_bounds_normalized':bounds,'invalid_transforms':invalid,'resident_proxy_count':len(res),'animal_proxy_count':len(animals),'visibility_rechecked':visibility,'previous_models_unchanged':previous,'guide_hidden_in_saved_main':bpy.data.collections['12_CP04_MOVEMENT_RESERVATIONS'].hide_render and bpy.data.collections['12_CP04_MOVEMENT_RESERVATIONS'].hide_viewport,'architecture_body_footprint_overlaps':final_overlaps,'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'armatures':sum(o.type=='ARMATURE' for o in s.objects),'animation_or_navigation_tested':False,'overall_reference_similarity_score':None}
# Read the previous checkpoint only to distinguish inherited body intersections.
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'outputs/modeling-checkpoint-03/borrowed-wind-town-cp03.blend'),load_ui=False,use_scripts=False)
baseline=body_overlaps(bpy.context.scene);record['cp03_body_footprint_overlaps']=baseline;record['new_body_footprint_overlaps']=[p for p in final_overlaps if p not in baseline]
record['passed']=camera_unchanged and not invalid and len(res)==24 and len(animals)==7 and all(previous.values()) and record['guide_hidden_in_saved_main'] and all(all(abs(a-45)<.001 for a in values) for values in angles.values()) and not record['new_body_footprint_overlaps'] and all(v['head'] and v['upper_body'] for v in visibility)
(OUT/'validation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False));assert record['passed']
