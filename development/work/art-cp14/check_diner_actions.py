import bpy,json,math,collections
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/art-checkpoint-14';s=bpy.context.scene;tea=bpy.data.objects['tea_house'];rec=json.loads((OUT/'revision-record.json').read_text())
def geo(objects):
 dg=bpy.context.evaluated_depsgraph_get();v=[];f=[];names=[]
 for o in objects:
  if o.type not in ['MESH','CURVE']or o.hide_render:continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();k=len(v);v.extend(ev.matrix_world@p.co for p in me.vertices);f.extend(tuple(k+i for i in t.vertices)for t in me.loop_triangles);names.extend([o.name]*len(me.loop_triangles));ev.to_mesh_clear()
 return v,f,names
def tree(objects):
 v,f,n=geo(objects);return BVHTree.FromPolygons(v,f,all_triangles=True),n
floors=[bpy.data.objects[n]for n in ['Tea balcony floor','CP06 upper dining floor']];floor,nf=tree(floors);result=[];visibility=[]
for i,action in enumerate(rec['chair_exit_actions']):
 guest=bpy.data.objects[action['actor']];chair=bpy.data.objects[action['chair']];own={o.name for r in [guest,chair]for o in [r]+list(r.children_recursive)};obstacles=[o for o in s.objects if o.name not in own and o.type in ['MESH','CURVE']and not o.hide_render and not any(c.hide_render or c.name.startswith('12_')for c in o.users_collection)and 'visible paper rain'not in o.name];world,wn=tree(obstacles)
 saved_guest=guest.location.copy();saved_chair=chair.location.copy();saved_yaw=guest.rotation_euler.z
 def verify(label,include_chair=False):
  objects=list(guest.children_recursive)+(list(chair.children_recursive)if include_chair else[]);body,bn=tree(objects);pairs=[]
  for a,b in body.overlap(world):
   if bn[a].startswith('CP14 chair leg')and wn[b]in ['Tea balcony floor','CP06 upper dining floor']:continue
   pairs.append((bn[a],wn[b]))
  if not include_chair:
   ct,cn=tree(chair.children_recursive)
   pairs.extend((bn[a],cn[b])for a,b in body.overlap(ct))
  support=[]
  for o in objects:
   if o.type!='MESH'or not o.name.startswith(('Shoe CP14','CP14 chair leg')):continue
   v,f,n=geo([o]);lo=min(p.z for p in v)
   for p in v:
    if p.z>lo+.002:continue
    hit,no,idx,d=floor.ray_cast(p+Vector((0,0,.03)),Vector((0,0,-1)),.08);gap=p.z-hit.z if hit is not None else None;support.append(gap is not None and -.003<=gap<=.012)
  result.append({'actor':guest.name,'pose':label,'unexpected_pairs':[list(x)for x in sorted(set(pairs))],'support_passed':bool(support)and all(support),'support_samples':len(support),'passed':not pairs and bool(support)and all(support)})
 for delta in [0,.05,.10,.15,.20,.25,.30]:
  guest.location.x=saved_guest.x-delta;chair.location.x=saved_chair.x-delta;bpy.context.view_layer.update();verify('seated chair pullback %.2f'%delta,True)
 # Author a standing inspection pose from these same meshes. This is not a rig or animation.
 guest.location=Vector(action['standing_tea_local']);chair.location.x=saved_chair.x-.30
 meshes=list(guest.children_recursive);snap={o.name:(o.matrix_basis.copy(),o.data)for o in meshes if o.type=='MESH'}
 def reshape(o,loc,scale):
  material=o.active_material;o.data=bpy.data.meshes['Shared cube'].copy();o.modifiers.clear();o.location=loc;o.scale=scale;o.rotation_euler=(0,0,0)
  for slot in o.material_slots:slot.link='OBJECT';slot.material=material
 def limb(o,a,b,width):
  a,b=Vector(a),Vector(b);reshape(o,(a+b)*.5,(width,width,(b-a).length));o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
 for o in meshes:
  name=o.name
  if o.type!='MESH':continue
  side=1 if o.location.x>0 else -1
  if name.startswith(('CP14 diner pelvis','CP14 folded diner coat','CP14 diner neck','Head CP14','CP14 diner folded hair','CP14 diner eye','CP14 diner scarf')):o.location.z+=.265
  elif name.startswith('Seated thigh CP14'):reshape(o,(side*.10,-.04,.70),(.13,.14,.39))
  elif name.startswith('CP14 diner shin'):limb(o,(side*.10,-.04,.50),(side*.10,-.06,.13),.105)
  elif name.startswith('Shoe CP14'):o.location.y=-.10
  elif name.startswith('CP14 diner upper sleeve'):limb(o,(side*.18,-.01,1.175),(side*.20,-.02,.96),.105)
  elif name.startswith('CP14 diner lower sleeve'):limb(o,(side*.20,-.02,.96),(side*.18,-.10,.78),.085)
  elif name.startswith('CP14 diner hand'):o.location=(side*.18,-.10,.75)
 for angle in [90,112.5,135,157.5,180]:guest.rotation_euler.z=math.radians(angle);bpy.context.view_layer.update();verify('standing turn %.1f'%angle)
 for y in [-1.6,-1.4,-1.2,-1.0,-.8,-.6,-.4,-.2,0,.2]:guest.location.y=y;bpy.context.view_layer.update();verify('rearward exit y=%.1f'%y)
 # Restore channels/data for the other guest's obstacle field. Modifier changes are inspection-only.
 for o in meshes:
  if o.name in snap:o.matrix_basis=snap[o.name][0];o.data=snap[o.name][1]
 guest.location=saved_guest;guest.rotation_euler.z=saved_yaw;chair.location=saved_chair;bpy.context.view_layer.update()
record={'passed':all(r['passed']for r in result),'key_pose_count':len(result),'poses':result,'scope':'Two actual seated guest/chair assemblies sampled while pulling back; authored standing mesh pose, turn angles and rearward positions checked by evaluated triangle overlap and actual shoe/leg support. Standing pose is an inspection construction, not rigging, continuous transition, animation or runtime movement. No roof hiding or actor visibility toggles.'};(OUT/'diner-action-space-check.json').write_text(json.dumps(record,indent=2));print(json.dumps({'passed':record['passed'],'count':len(result),'failures':[r for r in result if not r['passed']]},indent=2));assert record['passed']
