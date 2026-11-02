import json,math
from pathlib import Path
R=Path.cwd();A=R/'app/runtime-cp22/public/assets';sock=json.loads((A/'actor-sockets.json').read_text());st=json.loads((R/'work/runtime-cp22/stair-surfaces.json').read_text())
clamp=lambda v,a,b:max(a,min(b,v))
def ease(t):t=clamp(t,0,1);return t*t*(3-2*t)
def lerp(a,b,t):return [x+(y-x)*t for x,y in zip(a,b)]
def yawdiff(a,b):return math.atan2(math.sin(b-a),math.cos(b-a))
def forward(yaw):return [math.sin(yaw),-math.cos(yaw)]
def cross(yaw):return [math.cos(yaw),math.sin(yaw)]
def add(a,b):return [x+y for x,y in zip(a,b)]
class Walker:
 def __init__(self,id,home=None,yaw=None):
  self.id=id;self.s=sock[id]['scale'][2];self.home=(home or sock[id]['origin'])[:];self.yaw=sock[id]['yaw']if yaw is None else yaw;self.startYaw=self.yaw;self.floor=self.home[2]+.02*self.s+.004;self.feet={};self.frames=[];self.time=0;self.side=0
  for i,side in enumerate(['left','right']):
   x=(-.1 if side=='left'else .1)*self.s;y=-.01*self.s;c=math.cos(self.yaw);n=math.sin(self.yaw);self.feet[side]=[self.home[0]+c*x-n*y,self.home[1]+n*x+c*y,self.floor]
  self.emit(self.feet,self.yaw,0)
 def emit(self,feet,yaw,t,ground=None):
  mid=[sum(feet[x][i]for x in feet)/2 for i in range(3)];D=forward(yaw);root=[mid[0]-D[0]*.01*self.s,mid[1]-D[1]*.01*self.s,(mid[2]if ground is None else ground)-.0186-.08]
  self.frames.append({'time':self.time+t,'root':root+[yaw],'legs':self.solve(feet,root,yaw),'feet':{k:v[:]for k,v in feet.items()}})
 def solve(self,feet,root,yaw):
  legs={};c=math.cos(yaw);n=math.sin(yaw)
  for side,F in feet.items():
   dx=F[0]-root[0];dy=F[1]-root[1];xx=(c*dx+n*dy)/self.s-(-.1 if side=='left'else .1);yy=(-n*dx+c*dy)/self.s+.01;zz=(F[2]+.09*self.s-root[2])/self.s-.49;roll=-math.atan2(xx,-zz);z=-math.hypot(xx,zz);L1=.20;L2=.18;k=math.acos(clamp((yy*yy+z*z-L1*L1-L2*L2)/(2*L1*L2),-1,1));hip=math.atan2(yy,-z)-math.atan2(L2*math.sin(k),L1+L2*math.cos(k));legs[side]=[hip,k,-hip-k,roll]
  return legs
 def turn(self,yaw,duration=1.6):
  old=self.yaw;mid=[sum(self.feet[x][i]for x in self.feet)/2 for i in range(3)];initial={k:v[:]for k,v in self.feet.items()};count=round(duration*30)
  for j in range(1,count+1):
   u=j/count;a=old+yawdiff(old,yaw)*ease(u);r=a-old;cs=math.cos(r);sn=math.sin(r);fs={}
   for k,p in initial.items():
    dx=p[0]-mid[0];dy=p[1]-mid[1];fs[k]=[mid[0]+cs*dx-sn*dy,mid[1]+sn*dx+cs*dy,p[2]+.025*math.sin(math.pi*u)**2*max(0,math.sin(u*math.pi*4+(0 if k=='left'else math.pi)))]
   self.emit(fs,a,duration*u,sum(p[2]for p in initial.values())/2)
  self.yaw=old+yawdiff(old,yaw);self.feet={k:[v[0],v[1],initial[k][2]]for k,v in fs.items()};self.time+=duration
 def step(self,point,yaw=None,duration=.78):
  if yaw is not None and abs(yawdiff(self.yaw,yaw))>.01:self.turn(yaw)
  side=['left','right'][self.side%2];self.side+=1;sgn=-1 if side=='left'else 1;crossv=cross(self.yaw);goal=[point[0]+crossv[0]*sgn*.1*self.s,point[1]+crossv[1]*sgn*.1*self.s,point[2]+.020];start=self.feet[side][:];count=round(duration*30)
  for j in range(1,count+1):
   u=j/count;v=ease((u-.22)/.56);F=lerp(start,goal,v);nominal=F[2];clear=max(start[2],goal[2])+.055;F[2]=start[2]+(clear-start[2])*ease(u/.22)if u<.22 else clear+(goal[2]-clear)*ease((u-.78)/.22)if u>.78 else clear;fs={k:p[:]for k,p in self.feet.items()};fs[side]=F;ground=(nominal+sum(p[2]for k,p in self.feet.items()if k!=side))/2;self.emit(fs,self.yaw,duration*u,ground)
  self.feet[side]=goal;self.time+=duration
 def hold(self,duration=1.5):
  for j in range(1,round(duration*30)+1):self.emit(self.feet,self.yaw,j/30)
  self.time+=duration
 def end(self,home=None,yaw=None):
  originalHome=self.home[:];originalYaw=self.startYaw;self.home=(home or self.home)[:];yaw=self.startYaw if yaw is None else yaw
  # Restore exact original pose without changing the roof or hiding the resident.
  last=self.frames[-1];duration=1.3;count=round(duration*30);goal={};c=math.cos(yaw);n=math.sin(yaw)
  for side in ['left','right']:
   x=(-.1 if side=='left'else .1)*self.s;y=-.01*self.s;goal[side]=[self.home[0]+c*x-n*y,self.home[1]+n*x+c*y,self.home[2]+.02*self.s]
  for j in range(1,count+1):
   u=ease(j/count);root=lerp(last['root'][:3],self.home,u);yy=last['root'][3]+yawdiff(last['root'][3],yaw)*u;feet={k:lerp(self.feet[k],goal[k],u)for k in goal};self.frames.append({'time':self.time+j/30,'root':root+[yy],'legs':self.solve(feet,root,yy),'feet':feet})
  self.time+=duration
  first=self.frames[0];intro=[]
  for j in range(31):
   u=ease(j/30);root=lerp(originalHome,first['root'][:3],u);initialFeet={};cc=math.cos(originalYaw);nn=math.sin(originalYaw)
   for side in ['left','right']:
    xx=(-.1 if side=='left'else .1)*self.s;yy=-.01*self.s;initialFeet[side]=[originalHome[0]+cc*xx-nn*yy,originalHome[1]+nn*xx+cc*yy,originalHome[2]+.02*self.s]
   feet={k:lerp(initialFeet[k],first['feet'][k],u)for k in goal};intro.append({'time':j/30,'root':root+[originalYaw],'legs':self.solve(feet,root,originalYaw),'feet':feet})
  for f in self.frames:f['time']+=1
  self.frames=intro+self.frames[1:];self.time+=1
  return {'duration':self.time,'frames':self.frames,'authoring_status':'candidate actual-foot-target stair gait; requires decoded-browser collision/support validation'}
def flight(name,u,z=None):
 m=st[name]['matrix'];p=[m[0][3]+m[0][1]*u,m[1][3]+m[1][1]*u,z if z is not None else m[2][3]];return p
lo='CP05_lower_stair';up='CP05_upper_stair';up_yaw=math.atan2(st[up]['matrix'][1][1],st[up]['matrix'][0][1])+math.pi/2;lo_yaw=math.atan2(st[lo]['matrix'][1][1],st[lo]['matrix'][0][1])+math.pi/2
id='resident.returning_resident';upper=[2.8057,7.241584,1.8524];lower=flight(lo,-.28,.6594);middle=sock[id]['origin'];middleYaw=sock[id]['yaw'];upperYaw=math.atan2(7.63-upper[1],4.04-upper[0])+math.pi/2;lowerYaw=lo_yaw+math.pi
anchors={'landing':{'root':middle+[middleYaw]},'terrace':{'root':upper+[upperYaw]},'street':{'root':lower+[lowerYaw]}};clips={}
def start(anchor):a=anchors[anchor]['root'];return Walker(id,a[:3],a[3])
def finish(w,source,target):
 a=anchors[target]['root'];c=w.end(a[:3],a[3]);c['from']=source;c['to']=target;clips[source+'_'+target]=c
w=start('landing');w.turn(up_yaw);w.step(flight(up,-.235,1.241))
for i in range(5):w.step(flight(up,i*.2-.03,1.3612+i*.1222))
w.step(flight(up,1.10,1.8675));w.step(flight(up,1.10,1.8675));
for xy in [[2.12,6.25],[2.10,6.45]]:w.step(xy+[1.871])
w.turn(math.atan2(.45,0)+math.pi/2)
for xy in [[2.10,6.55],[2.10,6.72],[2.10,6.90]]:w.step(xy+[1.871])
w.turn(math.atan2(.341584,.7057)+math.pi/2)
for xy in [[2.33,7.013],[2.57,7.127],upper[:2],upper[:2]]:w.step(xy+[1.871])
w.turn(upperYaw);finish(w,'landing','terrace')
w=start('terrace');w.turn(math.atan2(-.341584,-.7057)+math.pi/2)
for xy in [[2.57,7.127],[2.33,7.013],[2.10,6.90]]:w.step(xy+[1.871])
w.turn(math.atan2(-.45,0)+math.pi/2)
for xy in [[2.10,6.72],[2.10,6.55],[2.10,6.45]]:w.step(xy+[1.871])
w.turn(up_yaw+math.pi)
w.step([2.02,6.206,1.871]);w.step(flight(up,1.10,1.8675));w.step(flight(up,1.10,1.8675))
for i in range(4,-1,-1):w.step(flight(up,i*.2+.12,1.3612+i*.1222))
w.step(flight(up,-.235,1.241));w.step(middle[:2]+[1.241]);w.step(middle[:2]+[1.241]);w.turn(middleYaw);finish(w,'terrace','landing')
w=start('landing');w.turn(lo_yaw+math.pi);w.step(flight(lo,1.20,1.241))
for i in range(4,-1,-1):w.step(flight(lo,i*.2+.12,.750198+i*.1222))
w.step(flight(lo,-.28,.677998));w.step(flight(lo,-.28,.677998));finish(w,'landing','street')
w=start('street');w.turn(lo_yaw)
for i in range(5):w.step(flight(lo,i*.2-.03,.750198+i*.1222))
w.step(flight(lo,1.20,1.241));w.step(middle[:2]+[1.241]);w.step(middle[:2]+[1.241]);w.turn(middleYaw);finish(w,'street','landing')
out={id:{'initial':'landing','anchors':anchors,'clips':clips}}
# A second scoped walker uses the existing wide balcony and two stable stopping places.
id='resident.porch_resident';origin=sock[id]['origin'];yaw=sock[id]['yaw'];D=[-math.cos(yaw),-math.sin(yaw)];end=[origin[0]+D[0]*.55,origin[1]+D[1]*.55,origin[2]];anchors={'porch':{'root':origin+[yaw]},'window':{'root':end+[yaw]}};clips={}
w=Walker(id,origin,yaw);w.turn(yaw-math.pi/2)
for d in [.18,.36,.55,.55]:w.step([origin[0]+D[0]*d,origin[1]+D[1]*d,origin[2]+.0186])
w.turn(yaw);c=w.end(end,yaw);c.update({'from':'porch','to':'window'});clips['porch_window']=c
w=Walker(id,end,yaw);w.turn(yaw+math.pi/2)
for d in [.37,.19,0,0]:w.step([origin[0]+D[0]*d,origin[1]+D[1]*d,origin[2]+.0186])
w.turn(yaw);c=w.end(origin,yaw);c.update({'from':'window','to':'porch'});clips['window_porch']=c
out[id]={'initial':'porch','anchors':anchors,'clips':clips}
(A/'local-routes.json').write_text(json.dumps(out,separators=(',',':')));print('LOCAL_ROUTES',{id:{k:round(c['duration'],2)for k,c in r['clips'].items()}for id,r in out.items()})
