import json,math
from pathlib import Path
R=Path.cwd();A=R/'app/runtime-cp30/public/assets';sockets=json.loads((A/'actor-sockets.json').read_text());nav=json.loads((A/'navigation.json').read_text());local=json.loads((A/'local-routes.json').read_text());surfaces=json.loads((R/'work/runtime-cp30/world-surfaces.json').read_text());tris=surfaces['triangles'];bins={}
for i,t in enumerate(tris):
 for x in range(math.floor(min(p[0]for p in t)*2),math.floor(max(p[0]for p in t)*2)+1):
  for y in range(math.floor(min(p[1]for p in t)*2),math.floor(max(p[1]for p in t)*2)+1):bins.setdefault((x,y),[]).append(i)
def floor(x,y,expected):
 vals=[]
 for i in bins.get((math.floor(x*2),math.floor(y*2)),[]):
  a,b,c=tris[i];D=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(D)<1e-8:continue
  u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/D;v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/D;w=1-u-v
  if min(u,v,w)<-.0001:continue
  z=a[2]*u+b[2]*v+c[2]*w
  if expected-.23<z<expected+.20:vals.append(z)
 return max(vals)if vals else expected
out={}
def add(id,points,seated=False):
 s=sockets[id];home=s['origin']+[s['yaw']];scale=s['scale'][2];start=home[:3]
 if seated:start=[start[0]+math.sin(s['yaw'])*.235*scale,start[1]-math.cos(s['yaw'])*.235*scale,start[2]]
 points=[start]+points;entry=[start]
 for a,b in zip(points,points[1:]):
  count=max(1,math.ceil(math.hypot(a[0]-b[0],a[1]-b[1])/.08))
  for j in range(1,count+1):
   p=[a[k]+(b[k]-a[k])*j/count for k in range(3)];entry.append([p[0],p[1],floor(*p)-.02*scale+.006])
 portal=min(json.loads((R/'work/runtime-cp30/main-nodes.json').read_text()),key=lambda i:math.dist(nav['nodes'][i][:2],entry[-1][:2]));q=nav['nodes'][portal];entry.append([q[0],q[1],q[2]-.02*scale+.006]);out[id]={'home':home,'seated':seated,'scale':scale,'entry':entry,'portal':portal}
bridge=[[10.3,-.75,.97],[9.7,-.63,1.04],[9,-.49,1.08],[8,-.28,1.12],[7,-.07,1.10],[6,.15,.98],[5,.36,.82],[4.55,.45,.81],[4.15,.45,.654],[4.15,-.3,.654],[4.32,-.72,.628]]
add('resident.water_visitor',bridge)
add('resident.water_companion',[[9,-.49,1.08]]+bridge[3:])
add('resident.gardener',[[4.8,3.65,.63],[3.8,3.7,.63],[2.65,3.7,.63],[2.4,3.2,.654]])
add('resident.assistant_gardener',[[6.3,1.6,.63],[5.6,1.5,.63],[4.7,1.5,.63],[4.75,.5,.81],[4.15,-.3,.654],[4.32,-.72,.628]])
add('resident.child_listener',[[-1.68,-1.95,.654],[-1.8,-2.4,.654]])
add('resident.listener',[[-1.33,-1.9,.654],[-1.25,-2.4,.654]],True)
# The reader uses the existing two-flight stair centerline and real support heights.
stairs=local['resident.returning_resident'];st=json.loads((R/'work/runtime-cp22/stair-surfaces.json').read_text())
def flight(name,u,z):
 m=st[name]['matrix'];return [m[0][3]+m[0][1]*u,m[1][3]+m[1][1]*u,z]
upper=[[2.57,7.127,1.871],[2.33,7.013,1.871],[2.10,6.9,1.871],[2.10,6.45,1.871],[2.02,6.206,1.871],flight('CP05_upper_stair',1.1,1.8675)]+[flight('CP05_upper_stair',i*.2+.12,1.3612+i*.1222)for i in range(4,-1,-1)]+[flight('CP05_upper_stair',-.235,1.241),sockets['resident.returning_resident']['origin'][:2]+[1.241]]
lower=[flight('CP05_lower_stair',1.2,1.241)]+[flight('CP05_lower_stair',i*.2+.12,.750198+i*.1222)for i in range(4,-1,-1)]+[flight('CP05_lower_stair',-.28,.677998)]
chain=upper+lower
end=[[2.65,4.08,.654],[2.2,3.8,.654],[2.2,3.2,.654]]
add('resident.quiet_reader',[[4.08,6.95,1.874],[3.45,6.95,1.874],[2.8057,7.241584,1.874]]+chain+end,True)
add('resident.returning_resident',lower+end)
red=out['resident.returning_resident'];red['paths']={}
for anchor in ['landing','terrace','street']:
 steps=[]
 if anchor=='terrace':steps=chain
 elif anchor=='landing':steps=lower
 home=stairs['anchors'][anchor]['root'];original=sockets['resident.returning_resident']['origin'];yaw=sockets['resident.returning_resident']['yaw'];sockets['resident.returning_resident']['origin']=home[:3];sockets['resident.returning_resident']['yaw']=home[3]
 add('resident.returning_resident',steps+end);red['paths'][anchor]=out['resident.returning_resident']['entry'];sockets['resident.returning_resident']['origin']=original;sockets['resident.returning_resident']['yaw']=yaw
out['resident.returning_resident']=red
out['resident.quiet_reader']['departAfter']='resident.returning_resident';red['returnAfter']='resident.quiet_reader';out['resident.gardener']['returnAfter']='resident.quiet_reader'
out['resident.water_visitor']['departAfter']='resident.water_companion';out['resident.water_companion']['returnAfter']='resident.water_visitor'
out['resident.listener']['returnAfter']='resident.child_listener';out['resident.listener']['departAfter']='resident.child_listener'
for id in ['resident.quiet_reader','resident.water_visitor','resident.listener']:out[id]['departWhen']='hold'
out['resident.assistant_gardener']['returnAfter']='resident.water_visitor';out['resident.assistant_gardener']['departAfter']='resident.water_visitor';out['resident.assistant_gardener']['departWhen']='hold'
out.pop('resident.child_listener');out.pop('resident.listener')
for id in ['resident.gardener','resident.assistant_gardener']:out[id]['events']=[]
(A/'event-trips.json').write_text(json.dumps(out,separators=(',',':')));(A/'event-support.json').write_text(json.dumps({'triangles':tris},separators=(',',':')))
print('TRIPS',{k:{'points':len(v['entry']),'portal':v['portal']}for k,v in out.items()})
