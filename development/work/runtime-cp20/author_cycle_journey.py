import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path.cwd();A=R/'app/runtime-cp20/public/assets';O=R/'outputs/runtime-checkpoint-20';s=bpy.context.scene;reg=json.loads((A/'runtime-registry.json').read_text());nav=json.loads((A/'navigation.json').read_text());activities=json.loads((A/'motion-activities.json').read_text());root=bpy.data.objects['street_bicycle'];inv=root.matrix_world.inverted();scale=root.matrix_world.to_scale();dg=bpy.context.evaluated_depsgraph_get()
def chain(o):
 while o:yield o;o=o.parent
def geo(o):
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear();return v,f
v=[];f=[];own={o.name for o in [root]+list(root.children_recursive)}
for o in root.children_recursive:
 if o.type not in ['MESH','CURVE']:continue
 q,t=geo(o);off=len(v);v.extend(inv@p for p in q);f.extend(tuple(off+i for i in tri)for tri in t)
wv=[];wf=[];wn=[];gv=[];gf=[];walkers={a['id']for a in nav['actors']if a.get('entry')}
for o in s.objects:
 if o.name in own or o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 owner=next((a.get('decision_entity_id')for a in chain(o)if a.get('decision_entity_id')),None)
 if owner in walkers or owner in activities['clips']or any(k in o.name.lower()for k in ['visible paper rain','ripple','glint','studio floor']):continue
 q,t=geo(o);off=len(wv);wv.extend(q);wf.extend(tuple(off+i for i in tri)for tri in t);wn.extend([o.name]*len(t))
 if any(k in o.name.lower()for k in ['continuous street paving','plaza stone ring']):
  off=len(gv);gv.extend(q);gf.extend(tuple(off+i for i in tri)for tri in t)
world=BVHTree.FromPolygons(wv,wf,all_triangles=True);ground=BVHTree.FromPolygons(gv,gf,all_triangles=True);checks=[];chosen=None
# Closed, tangent-continuous circuit; the cyclist coasts, wheels roll, hands stay on the handlebar.
for cy in [-2.95]:
 if chosen:break
 for left,right,rad in [(-1.3,3.2,.5)]:
  straight=right-left;L=2*straight+2*math.pi*rad;samples=[];bad=[]
  for i in range(321):
   d=i/320*L
   if d<straight:p=Vector((right-d,cy+rad,0));yaw=math.pi
   elif d<straight+math.pi*rad:u=(d-straight)/rad;theta=math.pi/2+u;p=Vector((left+rad*math.cos(theta),cy+rad*math.sin(theta),0));yaw=theta+math.pi/2
   elif d<2*straight+math.pi*rad:u=d-straight-math.pi*rad;p=Vector((left+u,cy-rad,0));yaw=0
   else:u=(d-2*straight-math.pi*rad)/rad;theta=-math.pi/2+u;p=Vector((right+rad*math.cos(theta),cy+rad*math.sin(theta),0));yaw=theta+math.pi/2
   heights=[]
   for off in [-.55,.55]:
    x=p.x+math.cos(yaw)*off;y=p.y+math.sin(yaw)*off
    hits=[ground.ray_cast(Vector((x+dx,y+dy,.95)),Vector((0,0,-1)),.5)for dx,dy in [(0,0),(.035,0),(-.035,0),(0,.035),(0,-.035)]]
    supports=[h for h,n,j,dist in hits if h is not None and n.z>.45 and .55<h.z<.79]
    if not supports:bad.append('wheel support');break
    heights.append(max(h.z for h in supports))
   if bad:break
   p.z=max(heights)-min(x.z for x in v)*scale.z+.008
   m=Matrix.Translation(p)@Matrix.Rotation(yaw,4,'Z')@Matrix.Diagonal((*scale,1));body=BVHTree.FromPolygons([m@x for x in v],f,all_triangles=True);hits=body.overlap(world)
   if hits:bad.extend(wn[j]for _,j in hits[:20]);break
   samples.append([p.x,p.y,p.z,yaw,0,0])
  checks.append({'center_y':cy,'left':left,'right':right,'radius':rad,'passed':not bad,'obstacles':list(set(bad)),'samples':len(samples)})
  print(checks[-1],flush=True)
  if not bad:
   chosen={'kind':'bicycle','radius':1.02,'duration':L/.63,'samples':samples,'motion':'ride','scale':scale.z,'length':L,'authored_yaw':samples[0][3],'coasting':True,'stops':[{'clock':straight/L*(L/.63),'label':'车站旁等一等'},{'clock':(2*straight+math.pi*rad)/L*(L/.63),'label':'池塘边看看水'}]};break
if chosen:
 first=chosen['samples'][0];root.matrix_world=Matrix.Translation(Vector(first[:3]))@Matrix.Rotation(first[3],4,'Z')@Matrix.Diagonal((*scale,1));activities['clips']['bicycle.street_bicycle']=chosen;(A/'motion-activities.json').write_text(json.dumps(activities,separators=(',',':')));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp20/town-runtime.blend'))
(O/'cycle-journey-authoring.json').write_text(json.dumps({'passed':chosen is not None,'attempts':checks,'scope':'321 sampled full bike-and-rider mesh poses plus both wheel support points. Moving walkers/creatures excluded here and require runtime avoidance.'},indent=2))
