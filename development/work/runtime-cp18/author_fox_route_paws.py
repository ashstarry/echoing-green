import bpy,json,math,collections
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path.cwd();A=R/'app/runtime-cp18/public/assets';O=R/'outputs/runtime-checkpoint-18';s=bpy.context.scene;reg=json.loads((A/'runtime-registry.json').read_text());by={e['id']:e for e in reg['entities']}
def chain(o):
 while o:yield o;o=o.parent
def control(e,part,pos,meshes):
 r=bpy.data.objects[e['blender_object']];old=next((x for x in e['parts']if x['id']==part),None)
 if old:return bpy.data.objects[old['blender_object']]
 p=bpy.data.objects.new(r.name+'__'+part,None);s.collection.objects.link(p);p.parent=r;p.location=pos;p['decision_part_id']=part;p['decision_owner']=e['id'];bpy.context.view_layer.update()
 for o in meshes:
  mw=o.matrix_world.copy();o.parent=p;o.matrix_world=mw
 e['parts'].append({'id':part,'blender_object':p.name,'control':'rigid_hinge','axis':'Z'if part=='tail'else'Y'});return p
for e in reg['entities']:
 r=bpy.data.objects[e['blender_object']]
 if e['kind']=='fish':
  tail=[o for o in r.children_recursive if 'fish tail'in o.name];control(e,'tail',(-.11,0,0),tail)
 if e['id']in ['animal.garden_fox','animal.doorstep_cat']:
  names=['head','ear','muzzle','eye'];control(e,'head',(-.21,0,.37)if 'fox'in e['id']else(-.13,0,.30),[o for o in r.children_recursive if o.type=='MESH'and any(k in o.name.lower()for k in names)])
  tail=[o for o in r.children_recursive if 'tail'in o.name.lower()];control(e,'tail',(.32,0,.33)if 'fox'in e['id']else(.10,0,.19),tail)
  if 'cat'in e['id']and not any('CP18 cat paw'in o.name for o in r.children_recursive):
   mat=next(o.active_material for o in r.children_recursive if o.type=='MESH')
   for i,(x,y)in enumerate([(-.09,-.07),(-.09,.07),(.09,-.07),(.09,.07)]):
    me=bpy.data.meshes['Shared cube'].copy();o=bpy.data.objects.new('CP18 cat paw '+str(i),me);s.collection.objects.link(o);o.parent=r;o.location=(x,y,.08);o.scale=(.05,.05,.12);o.data.materials.clear();o.data.materials.append(mat)
   verts=[(.11,-.025,.20),(.11,.025,.20),(.29,-.02,.34),(.29,.02,.34),(.23,0,.47)];me=bpy.data.meshes.new('CP18 folded cat tail');me.from_pydata(verts,[],[(0,1,3,2),(2,3,4),(0,2,4),(1,4,3)]);me.materials.append(mat);o=bpy.data.objects.new('CP18 folded cat tail',me);s.collection.objects.link(o);o.parent=r;control(e,'tail',(.10,0,.19),[]);p=bpy.data.objects[next(x['blender_object']for x in e['parts']if x['id']=='tail')];bpy.context.view_layer.update();mw=o.matrix_world.copy();o.parent=p;o.matrix_world=mw
  legs=[o for o in r.children_recursive if o.type=='MESH'and ('Fox leg'in o.name or 'CP18 cat paw'in o.name)]
  for i,o in enumerate(legs):
   inv=r.matrix_world.inverted();pos=inv@o.matrix_world.translation;pos.z=.25 if'fox'in e['id']else.14;control(e,'leg_'+str(i),pos,[o])
 if e['id'].startswith('animal.duck_'):control(e,'head',(-.12,0,.25),[o for o in r.children_recursive if o.type=='MESH'and any(k in o.name for k in ['Duck head','Duck bill','Duck neck'])])
reference=json.loads((R/'outputs/art-checkpoint-16/scene-signature.json').read_text())['objects']
for e in reg['entities']:
 if e['id']=='animal.garden_fox':
  values=reference[e['blender_object']]['matrix'];ob=bpy.data.objects[e['blender_object']];ob.matrix_world=Matrix([values[i:i+4]for i in range(0,16,4)])
  if e['kind']=='fish':m=ob.matrix_world.copy();m.translation.z=.57;ob.matrix_world=m
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
def geo(o):
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear();return v,f
moving=[e for e in reg['entities']if e['id']=='animal.garden_fox'];moveids={e['id']for e in moving}|{a['id']for a in json.loads((A/'navigation.json').read_text())['actors']if a.get('entry')}|{'bicycle.street_bicycle','resident.cyclist'};wv=[];wf=[];wn=[];supportv=[];supportf=[];water=None
for o in s.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 owner=next((a.get('decision_entity_id')for a in chain(o)if a.get('decision_entity_id')),None)
 if owner in moveids or any(k in o.name.lower()for k in ['rain','ripple','glint','studio floor','duck wake']):continue
 v,f=geo(o)
 if o.name=='CP02 pond':water=BVHTree.FromPolygons(v,f,all_triangles=True);continue
 off=len(wv);wv.extend(v);wf.extend(tuple(off+i for i in t)for t in f);wn.extend([o.name]*len(f))
 if any(k in o.name.lower()for k in ['continuous street paving','plaza stone ring']):
  off=len(supportv);supportv.extend(v);supportf.extend(tuple(off+i for i in t)for t in f)
world=BVHTree.FromPolygons(wv,wf,all_triangles=True);ground=BVHTree.FromPolygons(supportv,supportf,all_triangles=True);activities=json.loads((A/'motion-activities.json').read_text());checks=[]
for e in moving:
 root=bpy.data.objects[e['blender_object']];orig=root.matrix_world.copy();inv=orig.inverted();scale=orig.to_scale();p0=orig.translation.copy();yaw0=orig.to_euler().z;v=[];f=[]
 for o in root.children_recursive:
  if o.type!='MESH':continue
  q,t=geo(o);off=len(v);v.extend(inv@p for p in q);f.extend(tuple(off+i for i in tri)for tri in t)
 iswater=e['kind']=='fish'or'duck_'in e['id'];isbird=e['kind']=='bird';chosen=None
 candidates=[1.0,.8,.6]if isbird else ([1,.7,.45,.3]if iswater else[1,.7,.5,.35])
 shifts=sorted([Vector((dx*.2,dy*.2,0))for dx in range(-16,5)for dy in range(-10,8)],key=lambda v:v.length)
 pairs=[(amp,shift,flow)for shift in shifts for amp in candidates for flow in ([1,-1]if iswater else[1])]
 for amp,shift,flow in pairs:
  samples=[];bad=[];N=160;duration=18 if isbird else(24 if iswater else 18)
  for i in range(N+1):
   u=i/N;phi=2*math.pi*u
   if isbird:dx=math.sin(phi)*1.8*amp;dy=(1-math.cos(phi))*.65*amp;dz=(1-math.cos(phi))*.42*amp;vx=math.cos(phi)*1.8;vy=math.sin(phi)*.65;vz=math.sin(phi)*.42;face=math.atan2(vy,vx);pitch=math.atan2(vz,math.hypot(vx,vy))*.5;bank=-math.sin(phi)*.12
   elif iswater:dx=flow*(1-math.cos(phi))*.36*amp;dy=math.sin(phi)*.15*amp;dz=0;vx=flow*math.sin(phi)*.36;vy=math.cos(phi)*.15;face=math.atan2(vy,vx)+(math.pi if'duck'in e['id']else 0);pitch=bank=0
   else:dx=(1-math.cos(phi))*.48*amp;dy=math.sin(phi)*.24*amp;dz=0;vx=math.sin(phi)*.48;vy=math.cos(phi)*.24;face=math.atan2(vy,vx)+math.pi;pitch=bank=0
   p=p0+shift+Vector((dx,dy,dz));face_delta=math.atan2(math.sin(face-yaw0),math.cos(face-yaw0));face=yaw0+face_delta
   if not isbird and not iswater:
    hits=[ground.ray_cast(Vector((p.x+dx,p.y+dy,.95)),Vector((0,0,-1)),.5)for dx,dy in [(0,0),(.06,0),(-.06,0),(0,.06),(0,-.06),(.25,.1),(.25,-.1),(-.25,.1),(-.25,-.1)]]
    supports=[h for h,no,j,d in hits if h is not None and no.z>.45 and .55<h.z<.79]
    if not supports:bad.append('unsupported');break
    lo=min(x.z for x in v)*scale.z;p.z=max(h.z for h in supports)-lo+.008
   if iswater:
    for other,oc in activities['clips'].items():
     if ('duck_'in other and'duck_'in e['id'])or(other.startswith('fish.')and e['id'].startswith('fish.')):
      op=oc['samples'][i];gap=.67 if'duck_'in e['id']else.61
      if math.hypot(p.x-op[0],p.y-op[1])<gap:bad.append('water actor spacing');break
   if bad:break
   m=Matrix.Translation(p)@Matrix.Rotation(face,4,'Z')@Matrix.Rotation(-pitch,4,'Y')@Matrix.Rotation(bank,4,'X')@Matrix.Diagonal((*scale,1));vv=[m@x for x in v];body=BVHTree.FromPolygons(vv,f,all_triangles=True);hits=body.overlap(world)
   if hits:bad.extend(wn[j]for _,j in hits[:10]);break
   if iswater:
    for point in vv[::max(1,len(vv)//14)]:
     hit,no,j,d=water.ray_cast(Vector((point.x,point.y,1)),Vector((0,0,-1)),.7)
     if hit is None:bad.append('outside water');break
   if bad:break
   samples.append([p.x,p.y,p.z,face,pitch,bank])
  if not bad:
   chosen={'kind':e['kind'],'radius':.34 if iswater else(.23 if'cat'in e['id']else.64)if not isbird else.45,'duration':duration,'samples':samples,'motion':'fly'if isbird else'swim'if iswater else'creature_walk','scale':scale.z,'amplitude_factor':amp,'authored_yaw':face,'flow':flow,'start_shift':list(shift)};break
  checks.append({'id':e['id'],'amplitude':amp,'passed':False,'obstacles':sorted(set(bad))[:12]})
 if chosen:
  first=chosen['samples'][0];root.matrix_world=Matrix.Translation(Vector(first[:3]))@Matrix.Rotation(first[3],4,'Z')@Matrix.Rotation(-first[4],4,'Y')@Matrix.Rotation(first[5],4,'X')@Matrix.Diagonal((*scale,1));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();chosen['authored_yaw']=first[3];activities['clips'][e['id']]=chosen;checks.append({'id':e['id'],'amplitude':chosen['amplitude_factor'],'start_shift':chosen['start_shift'],'passed':True,'samples':161});print('PASS',e['id'],chosen['amplitude_factor'],chosen['start_shift'],flush=True)
 else:print('NO ROUTE',e['id'],checks[-1],flush=True)
reg['parts_count']=sum(len(e['parts'])for e in reg['entities']);(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));(A/'motion-activities.json').write_text(json.dumps(activities,separators=(',',':')));(O/'fox-route-check-paws.json').write_text(json.dumps(checks,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp18/town-runtime.blend'));print('CREATURES',len(activities['clips']))
