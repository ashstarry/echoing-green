from pathlib import Path
import json,math
R=Path.cwd();A=R/'app/runtime-cp30/public/assets'
# Reuse the authored two-foot gait builder, not an unvalidated new stair gait.
source=(R/'work/runtime-cp22/build_local_routes.py').read_text().split('def flight(')[0]
exec(source)
A=R/'app/runtime-cp30/public/assets';configs=json.loads((A/'event-trips.json').read_text());local=json.loads((A/'local-routes.json').read_text());stairs=local['resident.returning_resident'];surfaces=json.loads((A/'event-support.json').read_text())['triangles']
bins={}
for i,t in enumerate(surfaces):
 for x in range(math.floor(min(p[0]for p in t)*2),math.floor(max(p[0]for p in t)*2)+1):
  for y in range(math.floor(min(p[1]for p in t)*2),math.floor(max(p[1]for p in t)*2)+1):bins.setdefault((x,y),[]).append(i)
def surface(x,y,expected):
 best=-1e9
 for i in bins.get((math.floor(x*2),math.floor(y*2)),[]):
  a,b,c=surfaces[i]
  if x<min(a[0],b[0],c[0]) or x>max(a[0],b[0],c[0]) or y<min(a[1],b[1],c[1]) or y>max(a[1],b[1],c[1]):continue
  D=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(D)<1e-9:continue
  u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/D;v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/D;w=1-u-v
  if min(u,v,w)<-.0001:continue
  z=u*a[2]+v*b[2]+w*c[2]
  if expected-.23<z<expected+.20:best=max(best,z)
 return expected if best<-1e8 else best

def simplify(points,eps=.025):
 if len(points)<3:return points
 a,b=points[0],points[-1];v=[b[k]-a[k]for k in range(3)];d=sum(x*x for x in v);scores=[]
 for i,p in enumerate(points[1:-1],1):
  t=max(0,min(1,sum((p[k]-a[k])*v[k]for k in range(3))/(d or 1)));scores.append((sum((p[k]-a[k]-v[k]*t)**2 for k in range(3)),i))
 score,i=max(scores)
 return simplify(points[:i+1],eps)[:-1]+simplify(points[i:],eps)if score>eps*eps else [a,b]

def sole_height(x,y,yaw,expected,scale):
 cs,sn=math.cos(yaw),math.sin(yaw);return max(surface(x+(cs*dx-sn*dy)*scale,y+(sn*dx+cs*dy)*scale,expected)for dx in [-.065,0,.065]for dy in [-.14,0,.075])
def fit_clearance(frames,scale):
 for f in frames:
  changes=[]
  for side,F in f['feet'].items():
   height=sole_height(F[0],F[1],f['root'][3],F[2]-.020,scale)+.020;change=max(0,height-F[2]);F[2]+=change;changes.append(change)
  f['root'][2]+=sum(changes)/2 if f is not frames[0] and f is not frames[-1] else 0
 return frames

def walk(id,points,yaw,final=None):
 scale=sock[id]['scale'][2];w=Walker(id,points[0][:3],yaw);points=simplify(points)
 for a,b in zip(points,points[1:]):
  d=math.hypot(b[0]-a[0],b[1]-a[1]);angle=math.atan2(b[1]-a[1],b[0]-a[0])+math.pi/2
  if d<.015:continue
  if abs(yawdiff(w.yaw,angle))>.035:w.turn(angle,max(.25,min(.9,abs(yawdiff(w.yaw,angle))/2.6)))
  count=max(1,math.ceil(d/.36))
  for j in range(1,count+1):
   p=[a[k]+(b[k]-a[k])*j/count for k in range(3)];expected=p[2]+.02*scale-.006;z=surface(p[0],p[1],expected);w.step([p[0],p[1],z],duration=.64)
 # Bring the trailing foot onto the final support before turning or handing over.
 last=points[-1];w.step([last[0],last[1],surface(last[0],last[1],last[2]+.02*scale-.006)],duration=.64)
 if final is not None and abs(yawdiff(w.yaw,final))>.02:w.turn(final,max(.3,min(.9,abs(yawdiff(w.yaw,final))/2.6)))
 clip=w.end(last[:3],w.yaw);fit_clearance(clip['frames'],scale);return [{'time':f['time']/1.35,'root':f['root'],'feet':f['feet']}for f in clip['frames']]

def concat(*clips):
 frames=[];clock=0
 for rows in clips:
  if not rows:continue
  if frames:
   # These clips share the exact authored stopping anchor.
   assert math.dist(frames[-1]['root'][:3],rows[0]['root'][:3])<.006,(frames[-1]['root'],rows[0]['root'])
  frames.extend([{**f,'time':clock+f['time']}for f in rows[1:]if frames]if frames else rows)
  clock=frames[-1]['time']
 return frames

def stair(key):return [{'time':f['time']/1.55,'root':f['root'],'feet':f['feet']}for f in stairs['clips'][key]['frames']]

def root(x,y,z,id):return[x,y,surface(x,y,z)-.02*sock[id]['scale'][2]+.006]
for id,c in configs.items():
 if id not in ['resident.quiet_reader','resident.returning_resident']:
  c['outFrames']=walk(id,c['entry'],c['home'][3]);c['backFrames']=walk(id,list(reversed(c['entry'])),c['outFrames'][-1]['root'][3]+math.pi,c['home'][3]);continue
 street=stairs['anchors']['street']['root'];terrace=stairs['anchors']['terrace']['root'];landing=stairs['anchors']['landing']['root'];post=[street[:3],root(2.65,4.08,.65,id),root(2.2,3.8,.65,id),root(2.2,3.2,.65,id),c['entry'][-1]]
 post_out=walk(id,post,street[3]);post_back=walk(id,list(reversed(post)),post_out[-1]['root'][3]+math.pi,street[3])
 if id=='resident.quiet_reader':
  pre=[c['entry'][0],root(4.08,6.95,1.871,id),root(3.45,6.95,1.871,id),terrace[:3]]
  pre_out=walk(id,pre,c['home'][3],terrace[3]);pre_back=walk(id,list(reversed(pre)),terrace[3],c['home'][3]);c.pop('departGateTime',None);c['outFrames']=concat(pre_out,stair('terrace_landing'),stair('landing_street'),post_out);c['backFrames']=concat(post_back,stair('street_landing'),stair('landing_terrace'),pre_back)
 else:
  c['outFramePaths']={'street':post_out,'landing':concat(stair('landing_street'),post_out),'terrace':concat(stair('terrace_landing'),stair('landing_street'),post_out)}
  c['backFramePaths']={'street':post_back,'landing':concat(post_back,stair('street_landing')),'terrace':concat(post_back,stair('street_landing'),stair('landing_terrace'))};c['outFrames']=c['outFramePaths']['landing'];c['backFrames']=c['backFramePaths']['landing']
configs['resident.water_visitor'].pop('departAfterAt',None);configs['resident.assistant_gardener'].pop('departAfterAt',None)
(A/'event-trips.json').write_text(json.dumps(configs,separators=(',',':')))
print({id:[round(c['outFrames'][-1]['time'],2),round(c['backFrames'][-1]['time'],2)]for id,c in configs.items()})
