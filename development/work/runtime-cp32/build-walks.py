from pathlib import Path
import json,math,bisect
R=Path.cwd();A=R/'app/runtime-cp32/public/assets';old=R/'app/runtime-cp31/public/assets';sock=json.loads((A/'actor-sockets.json').read_text());nav=json.loads((A/'navigation.json').read_text());local=json.loads((old/'local-routes.json').read_text());trips=json.loads((old/'event-trips.json').read_text());rigs=json.loads((A/'seated-rigs.json').read_text());tri=json.loads((A/'event-support.json').read_text())['triangles'];bins={}
for i,t in enumerate(tri):
 for x in range(math.floor(min(p[0]for p in t)*2),math.floor(max(p[0]for p in t)*2)+1):
  for y in range(math.floor(min(p[1]for p in t)*2),math.floor(max(p[1]for p in t)*2)+1):bins.setdefault((x,y),[]).append(i)
def floor(x,y,z):
 best=None
 for i in bins.get((math.floor(x*2),math.floor(y*2)),[]):
  a,b,c=tri[i];D=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(D)<1e-9:continue
  u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/D;v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/D;w=1-u-v
  if min(u,v,w)<-.001:continue
  h=u*a[2]+v*b[2]+w*c[2]
  if z-.25<h<z+.25:best=h if best is None else max(best,h)
 return z if best is None else best
angle=lambda a,b: math.atan2(math.sin(b-a),math.cos(b-a))
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def simplify(ps,eps=.055):
 if len(ps)<3:return ps
 a,b=ps[0],ps[-1];d=[b[k]-a[k] for k in range(3)];length=sum(v*v for v in d)
 distances=[]
 for i,p in enumerate(ps[1:-1],1):
  t=max(0,min(1,sum((p[k]-a[k])*d[k]for k in range(3))/(length or 1)));distances.append((sum((p[k]-a[k]-t*d[k])**2 for k in range(3)),i))
 maximum,i=max(distances)
 return simplify(ps[:i+1],eps)[:-1]+simplify(ps[i:],eps)if maximum>eps**2 else[a,b]
def prepare(ps):
 ps=simplify(ps);dense=[ps[0][:3]]
 for a,b in zip(ps,ps[1:]):
  n=max(1,math.ceil(math.dist(a[:2],b[:2])/.035))
  for j in range(1,n+1):dense.append([a[k]+(b[k]-a[k])*j/n for k in range(3)])
 # Round only small corners; preserve doorway, tread and landing locations.
 for _ in range(3):dense=[dense[0]]+[[sum(dense[i+j][k]*w for j,w in[(-1,.25),(0,.5),(1,.25)])for k in range(3)]for i in range(1,len(dense)-1)]+[dense[-1]]
 lengths=[0]
 for a,b in zip(dense,dense[1:]):lengths.append(lengths[-1]+math.dist(a[:2],b[:2]))
 def sample(d):
  d=max(0,min(lengths[-1],d));i=max(0,min(len(dense)-2,bisect.bisect_right(lengths,d)-1));u=(d-lengths[i])/(lengths[i+1]-lengths[i]or 1);return[dense[i][k]+(dense[i+1][k]-dense[i][k])*u for k in range(3)]
 return sample,lengths[-1]
def legs(feet,root,yaw,scale):
 out={};c,s=math.cos(yaw),math.sin(yaw)
 for side,F in feet.items():
  dx,dy=F[0]-root[0],F[1]-root[1];x=(c*dx+s*dy)/scale-(-.1 if side=='left'else .1);y=(-s*dx+c*dy)/scale+.01;z=(F[2]+.09*scale-root[2])/scale-.49;roll=-math.atan2(x,-z);z=-math.hypot(x,z);k=math.acos(max(-1,min(1,(y*y+z*z-.2**2-.18**2)/(.072))));h=math.atan2(y,-z)-math.atan2(.18*math.sin(k),.2+.18*math.cos(k));out[side]=[h,k,-h-k,roll]
 return out
def walk(id,points,yaw,endYaw=None,speed=.95):
 scale=sock[id]['scale'][2];sample,length=prepare(points);rows=[];d=0;v=0;t=0;lastYaw=yaw
 heights=[floor(*sample(min(length,i*.035))[:2],sample(min(length,i*.035))[2]+.02*scale)for i in range(math.ceil(length/.035)+1)]
 smooth=[sum(heights[max(0,min(len(heights)-1,i+j))]*(6-abs(j))for j in range(-5,6))/36 for i in range(len(heights))]
 def bodyHeight(d):
  at=d/.035;i=min(len(smooth)-2,int(at));u=min(1,at-i);return smooth[i]*(1-u)+smooth[i+1]*u
 while True:
  p=sample(d);ahead=sample(min(length,d+.25));behind=sample(max(0,d-.06));want=math.atan2(ahead[1]-behind[1],ahead[0]-behind[0])+math.pi/2 if math.dist(ahead[:2],behind[:2])>.001 else lastYaw
  yaw+=max(-.10,min(.10,angle(yaw,want)));remaining=length-d;weight=min(1,d/.18,remaining/.20);rootz=bodyHeight(d)-.02*scale+.006-.026*scale*weight;rootz=points[0][2]+(rootz-points[0][2])*ease(d/.20) if d<.20 else points[-1][2]+(rootz-points[-1][2])*ease(remaining/.20) if remaining<.20 else rootz;feet={};stride=.56*scale
  for side,offset in [('left',0),('right',.5)]:
   phase=(d/stride+offset)%1;base=d-phase*stride;u=max(0,(phase-.6)/.4);left=base+.14*scale;right=left+stride
   fd=left+(right-left)*ease(u);F=sample(fd);fa=sample(min(length,fd+.1));fb=sample(max(0,fd-.1));fyaw=math.atan2(fa[1]-fb[1],fa[0]-fb[0])+math.pi/2 if math.dist(fa[:2],fb[:2])>.001 else yaw
   sideX=(-.1 if side=='left'else .1)*scale;x=F[0]+math.cos(fyaw)*sideX;y=F[1]+math.sin(fyaw)*sideX;A=sample(left);B=sample(right);ga=floor(A[0]+math.cos(fyaw)*sideX,A[1]+math.sin(fyaw)*sideX,A[2]+.02*scale);gb=floor(B[0]+math.cos(fyaw)*sideX,B[1]+math.sin(fyaw)*sideX,B[2]+.02*scale);ground=ga+(gb-ga)*ease(u);z=ground+.02*scale+((.105+max(0,gb-ga)*.45)*math.sin(math.pi*u)*weight if phase>=.6 else 0)
   sx=p[0]+math.cos(yaw)*sideX;sy=p[1]+math.sin(yaw)*sideX;sz=floor(sx,sy,p[2]+.02*scale)+.02*scale;feet[side]=[sx+(x-sx)*weight,sy+(y-sy)*weight,sz+(z-sz)*weight]
  row={'time':round(t,6),'root':[p[0],p[1],rootz,yaw],'feet':feet};row['legs']=legs(feet,row['root'],yaw,scale);rows.append(row)
  if remaining<.0001:break
  desired=min(speed,math.sqrt(max(0,2*1.8*remaining)))*max(.35,math.cos(angle(yaw,want)));v+=max(-.06,min(.06,desired-v));d=min(length,d+max(.04,v)/30);t+=1/30;lastYaw=yaw
 if endYaw is not None:
  first=rows[-1];duration=max(.15,abs(angle(yaw,endYaw))/2.8);count=math.ceil(duration*30)
  for j in range(1,count+1):
   u=ease(j/count);yy=yaw+angle(yaw,endYaw)*u;p=sample(length);feet={}
   for side in ['left','right']:
    x=p[0]+math.cos(yy)*(-.1 if side=='left'else .1)*scale;y=p[1]+math.sin(yy)*(-.1 if side=='left'else .1)*scale;feet[side]=[x,y,floor(x,y,p[2]+.02*scale)+.02*scale]
   root=[p[0],p[1],p[2],yy];rows.append({'time':round(t+duration*j/count,6),'root':root,'feet':feet,'legs':legs(feet,root,yy,scale)})
 return rows
# Regenerate everyday stair clips too; not just event-only locomotion.
for id,c in local.items():
 for key,clip in c['clips'].items():
  points=[f['root'][:3]for f in clip['frames']];points[0]=c['anchors'][clip['from']]['root'][:3];points[-1]=c['anchors'][clip['to']]['root'][:3]
  rows=walk(id,points,c['anchors'][clip['from']]['root'][3],c['anchors'][clip['to']]['root'][3],.78);clip['frames']=rows;clip['duration']=rows[-1]['time']
(A/'local-routes.json').write_text(json.dumps(local,separators=(',',':')))
# Additional neighbours use real continuous routes into the plaza.
extras={
 'resident.child_listener':[[-1.75,-1.95,.64],[-1.6,-2.4,.64]],
 'resident.listener':[[-1.2,-1.9,.64],[-1.1,-2.45,.64]],
 'resident.waiting_passenger':[[-5.0,-5.8,.77],[-6.3,-5.5,.77],[-6.4,-4.5,.64],[-5.6,-3.7,.64],[-4.6,-3.2,.64]],
 'resident.waiting_passenger_2':[[.2,-5.6,.77],[1.6,-5.3,.77],[1.3,-4.3,.64],[1.4,-3.3,.64],[2.1,-2.8,.64]],
 'resident.station_traveler':[[-1.7,-6.4,.77],[.7,-6.0,.77],[1.6,-5.3,.77],[1.3,-4.3,.64],[1.4,-3.3,.64],[2.1,-2.8,.64]],
 'resident.elder':[[-10,-2.9,.67],[-9,-4.1,.64],[-7.2,-4.8,.64],[-6.4,-4.4,.64],[-5.7,-3.5,.64],[-4.8,-3.2,.64]]}
main=set(json.loads((R/'work/runtime-cp30/main-nodes.json').read_text()))
for id,points in extras.items():
 h=sock[id]['origin']+[sock[id]['yaw']];scale=sock[id]['scale'][2];start=h[:3]
 if id in rigs:start=[h[0]+math.sin(h[3])*.235*scale,h[1]-math.cos(h[3])*.235*scale,h[2]]
 portal=min(main,key=lambda i:math.dist(nav['nodes'][i][:2],points[-1][:2]));point=nav['nodes'][portal];points[-1]=[point[0],point[1],point[2]-.02*scale+.006];trips[id]={'home':h,'seated':id in rigs,'scale':scale,'entry':[start]+points,'portal':portal}
for id,c in trips.items():
 c.pop('events',None);c.pop('departAfter',None);c.pop('departWhen',None);c.pop('returnAfter',None)
 if id in ['resident.child_listener','resident.listener']:c['waitForBicycleBay']=True
 if id=='resident.quiet_reader':c['departAfter']='resident.returning_resident';c['departAfterAt']=3
 if id=='resident.water_visitor':c['departAfter']='resident.water_companion';c['departAfterAt']=2.0
 if id=='resident.assistant_gardener':c['departAfter']='resident.water_visitor';c['departWhen']='hold'
 if id=='resident.returning_resident':c['returnAfter']='resident.quiet_reader'
 if id=='resident.water_companion':c['returnAfter']='resident.water_visitor'
 if c.get('paths'):
  c['outFramePaths']={};c['backFramePaths']={}
  for anchor,points in c['paths'].items():
   h=local[id]['anchors'][anchor]['root'];c['outFramePaths'][anchor]=walk(id,points,h[3]);c['backFramePaths'][anchor]=walk(id,list(reversed(points)),c['outFramePaths'][anchor][-1]['root'][3]+math.pi,h[3]);
  c['outFrames']=c['outFramePaths']['landing'];c['backFrames']=c['backFramePaths']['landing']
 else:
  c['outFrames']=walk(id,c['entry'],c['home'][3]);c['backFrames']=walk(id,list(reversed(c['entry'])),c['outFrames'][-1]['root'][3]+math.pi,c['home'][3])
 if not any(a['id']==id for a in nav['actors']):nav['actors'].append({'id':id,'position':c['home'][:3],'yaw':c['home'][3],'scale':sock[id]['scale'],'entry':[c['portal']],'eventOnly':True})
for a,b in {'resident.assistant_gardener': 'resident.water_companion', 'resident.station_traveler': 'resident.waiting_passenger_2', 'resident.child_listener': 'resident.listener', 'resident.waiting_passenger': 'resident.elder', 'resident.gardener': 'resident.returning_resident'}.items():trips[a]['returnAfter']=b
nav['previous']={'signature':1312,'actors':19};nav['revision']='cp32-crowd';(A/'navigation.json').write_text(json.dumps(nav,separators=(',',':')));(A/'event-trips.json').write_text(json.dumps(trips,separators=(',',':')))
print({id:round(c['outFrames'][-1]['time'],2)for id,c in trips.items()})
