import bpy,json,math,collections
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
R=Path.cwd();A=R/'app/runtime-cp18/public/assets';O=R/'outputs/runtime-checkpoint-18';s=bpy.context.scene;reg=json.loads((A/'runtime-registry.json').read_text());C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)));CI=C.inverted();tea=bpy.data.objects['tea_house'];T=tea.matrix_world;tx=(T.to_3x3()@Vector((1,0,0))).normalized();ty=(T.to_3x3()@Vector((0,1,0))).normalized();tea_yaw=math.atan2(tx.y,tx.x)
def geo(o):
 dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear();return v,f
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def mixM(a,b,u):
 ap,aq,asc=a.decompose();bp,bq,bsc=b.decompose();return Matrix.LocRotScale(ap.lerp(bp,u),aq.slerp(bq,u),asc.lerp(bsc,u))
def limb(a,b,w):
 a,b=Vector(a),Vector(b);return Matrix.Translation((a+b)*.5)@(b-a).to_track_quat('Z','Y').to_matrix().to_4x4()@Matrix.Diagonal((w,w,(b-a).length,1))
configs={};checks=[]
for e in reg['entities']:
 if not e['id'].startswith('resident.upper_diner_'):continue
 idx=int(e['id'][-1]);root=bpy.data.objects[e['blender_object']];chair=bpy.data.objects['CP06 dining chair '+str(idx)];origin=root.matrix_world.copy();scale=origin.to_scale();seat=origin.translation.copy();yaw=origin.to_euler().z;chair_base=chair.matrix_world.copy();inv=origin.inverted();meshes=[o for o in root.children_recursive if o.type=='MESH'];components=[]
 for j,o in enumerate(meshes):
  old=inv@o.matrix_world;standing=old.copy();n=o.name;side=1 if old.translation.x>0 else-1
  if n.startswith(('CP14 diner pelvis','CP14 folded diner coat','CP14 diner neck','Head CP14','CP14 diner folded hair','CP14 diner eye','CP14 diner scarf')):standing.translation.z+=.265
  elif n.startswith('Seated thigh CP14'):standing=Matrix.Translation(Vector((side*.10,-.04,.70)))@Matrix.Diagonal((.13,.14,.39,1))
  elif n.startswith('CP14 diner shin'):standing=limb((side*.10,-.04,.50),(side*.10,-.06,.13),.105)
  elif n.startswith('Shoe CP14'):standing.translation.y=-.10
  elif n.startswith('CP14 diner upper sleeve'):standing=limb((side*.18,-.01,1.175),(side*.20,-.02,.96),.105)
  elif n.startswith('CP14 diner lower sleeve'):standing=limb((side*.20,-.02,.96),(side*.18,-.10,.78),.085)
  elif n.startswith('CP14 diner hand'):standing.translation=Vector((side*.18,-.10,.75))
  v,f=geo(o);v=[inv@p for p in v];control=o.parent if o.parent and str(o.parent.get('decision_part_id','')).startswith('pose_') else None
  if control is None:
   control=bpy.data.objects.new(root.name+'__pose_%02d'%j,None);s.collection.objects.link(control);control.parent=root;control.matrix_basis=Matrix.Identity(4);control['decision_part_id']='pose_%02d'%j;control['decision_owner']=e['id'];bpy.context.view_layer.update();mw=o.matrix_world.copy();o.parent=control;o.matrix_world=mw
  if not any(p['id']==control['decision_part_id']for p in e['parts']):e['parts'].append({'id':control['decision_part_id'],'blender_object':control.name,'control':'affine_pose_channel','axis':None})
  components.append({'part':control['decision_part_id'],'name':n,'old':old,'stand':standing,'v':v,'f':f})
 # Actual remaining scene, except the flexible curtain aperture that will fold open during passage.
 own={o.name for r in [root,chair]for o in [r]+list(r.children_recursive)};wv=[];wf=[];wn=[]
 for o in s.objects:
  if o.name in own or o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection)or any(k in o.name for k in ['visible paper rain','CP15 folded noren panel','CP15 noren hem']):continue
  v,f=geo(o);off=len(wv);wv.extend(v);wf.extend(tuple(off+i for i in t)for t in f);wn.extend([o.name]*len(f))
 world=BVHTree.FromPolygons(wv,wf,all_triangles=True);chairv=[];chairf=[]
 for o in chair.children_recursive:
  if o.type!='MESH':continue
  v,f=geo(o);off=len(chairv);chairv.extend(v);chairf.extend(tuple(off+i for i in t)for t in f)
 portal=Vector(next(a['position']for a in e['anchors']if a['id']=='behind_noren'));standpoint=seat+tx*.14+ty*.24
 def frame(t,enter=False):
  # 0..4.8: pull chair, stand up, turn and walk through a folded-open noren.
  if not enter:
   if t<.8:u=smooth(t/.8);p=seat-tx*(.3*u);stand=0;angle=yaw;chair_delta=-tx*.3*u;walk=0
   elif t<1.8:u=smooth((t-.8)/1);p=(seat-tx*.3).lerp(standpoint,u);stand=u;angle=yaw;chair_delta=-tx*.3;walk=0
   elif t<2.3:u=smooth((t-1.8)/.5);p=standpoint;stand=1;angle=yaw+math.pi/2*u;chair_delta=-tx*.3;walk=0
   else:u=smooth((t-2.3)/2.5);p=standpoint.lerp(portal,u)+tx*(.14*math.sin(math.pi*u)if idx==0 else 0);stand=1;angle=yaw+math.pi/2;chair_delta=-tx*.3;walk=math.sin(math.pi*u)**.5
  else:
   if t<2.5:u=smooth(t/2.5);p=portal.lerp(standpoint,u)+tx*(.14*math.sin(math.pi*u)if idx==0 else 0);stand=1;angle=yaw-math.pi/2;chair_delta=-tx*.3;walk=math.sin(math.pi*u)**.5
   elif t<3:u=smooth((t-2.5)/.5);p=standpoint;stand=1;angle=yaw-math.pi/2*(1-u);chair_delta=-tx*.3;walk=0
   elif t<4:u=smooth((t-3)/1);p=standpoint.lerp(seat-tx*.3,u);stand=1-u;angle=yaw;chair_delta=-tx*.3;walk=0
   else:u=smooth((t-4)/.8);p=seat-tx*.3*(1-u);stand=0;angle=yaw;chair_delta=-tx*.3*(1-u);walk=0
  rootm=Matrix.Translation(p)@Matrix.Rotation(angle,4,'Z')@Matrix.Diagonal((*scale,1));vs=[];fs=[];names=[];parts={}
  for c in components:
   n=c['name'];target=c['stand'].copy();side=1 if c['old'].translation.x>0 else-1;drop=.22*smooth((stand-.45)/.4)
   gait=math.sin(t*7+(0 if side<0 else math.pi))*.055*walk;lift=max(0,math.cos(t*7+(0 if side<0 else math.pi)))*.045*walk
   if n.startswith(('Seated thigh CP14','CP14 diner shin')):
    hip=Vector((side*.10,-.04,.895-drop));ankle=Vector((side*.10,-.06+gait,.13+lift));dy=ankle.y-hip.y;dz=ankle.z-hip.z;L1=.395;L2=.37;d2=dy*dy+dz*dz;knee_angle=math.acos(max(-1,min(1,(d2-L1*L1-L2*L2)/(2*L1*L2))));hip_angle=math.atan2(dy,-dz)-math.atan2(L2*math.sin(knee_angle),L1+L2*math.cos(knee_angle));knee=hip+Vector((0,L1*math.sin(hip_angle),-L1*math.cos(hip_angle)));target=limb(hip,knee,.13)if n.startswith('Seated thigh')else limb(knee,ankle,.105)
   elif n.startswith('Shoe CP14'):target.translation.y+=gait;target.translation.z+=lift
   else:target=Matrix.Translation(Vector((0,0,.895-drop)))@Matrix.Rotation(.12,4,'X')@Matrix.Translation(Vector((0,0,-.895)))@target
   pose=mixM(c['old'],target,stand)
   delta=pose@c['old'].inverted();dm=C@delta@CI;parts[c['part']]=[dm[r][col]for col in range(4)for r in range(4)];off=len(vs);vs.extend(rootm@delta@v for v in c['v']);fs.extend(tuple(off+i for i in tri)for tri in c['f']);names.extend([n]*len(c['f']))
  body=BVHTree.FromPolygons(vs,fs,all_triangles=True);pairs=set((names[i],wn[j])for i,j in body.overlap(world));ch=BVHTree.FromPolygons([v+chair_delta for v in chairv],chairf,all_triangles=True)
  for i,j in body.overlap(ch):pairs.add((names[i],'own chair'))
  if pairs:checks.append({'id':e['id'],'clip':'enter'if enter else'exit','t':t,'pairs':[list(p)for p in pairs]})
  return {'root':[p.x,p.y,p.z,angle],'parts':parts,'chair':[chair_base.translation.x+chair_delta.x,chair_base.translation.y+chair_delta.y,chair_base.translation.z+chair_delta.z],'curtain_open':max(0,min(1,(t-1.9)/.4, (5.2-t)/.4))if not enter else max(0,min(1,(3.1-t)/.4))}
 clips={name:{'duration':4.8,'frames':[frame(i*.05,enter)for i in range(97)]}for name,enter in [('exit',False),('enter',True)]};curtain=next(x for x in reg['entities']if x['id']=='curtain.restaurant_upper_noren');panel=min(curtain['parts'],key=lambda x:(bpy.data.objects[x['blender_object']].matrix_world.translation-portal).xy.length)
 configs[e['id']]={'clips':clips,'chair':next(x['id']for x in reg['entities']if x['blender_object']==chair.name),'curtain_part':panel['id'],'scale':list(scale),'yaw':yaw}
reg['parts_count']=sum(len(e['parts'])for e in reg['entities']);(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));(A/'diner-clips.json').write_text(json.dumps(configs,separators=(',',':')));(O/'diner-transition-check-round3.json').write_text(json.dumps({'passed':not checks,'frames_checked':388,'failures':checks,'scope':'Both actual diner bodies against static evaluated meshes plus moving own chair; curtain cloth excluded only for an explicitly folding aperture. Discrete 0.05-second samples.'},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp18/town-runtime.blend'));print(json.dumps({'failures':len(checks),'examples':checks[:8]},indent=2))
