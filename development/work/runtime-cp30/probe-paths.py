exec(open('work/runtime-cp30/inspect-world.py').read().split("(out/'world-surfaces.json')")[0])
world=BVHTree.FromPolygons(v,faces,all_triangles=True);routes={
'bridge':[[10.47,-.72,.936],[9.8,-.65,1.03],[9,-.48,1.08],[8,-.27,1.12],[7,-.06,1.10],[6,.15,.98],[5,.36,.82],[4.55,.45,.81],[4.15,.45,.654],[3.6,.32,.654]],
'reader':[[4.08,7.35,1.874],[4.08,6.95,1.874],[3.45,6.95,1.874],[2.8057,7.241584,1.874]],
'stair_exit':[[3.3056,4.0954,.678],[2.65,4.08,.654],[2.2,3.8,.654],[2.2,3.2,.654]],
'gardener':[[5,3.32,.63],[4.8,3.65,.63],[3.8,3.7,.63],[2.65,3.7,.63],[2.4,3.2,.654]],
'assistant':[[6.99,2.01,.63],[6.3,1.6,.63],[5.6,1.5,.63],[4.7,1.5,.63],[4.0,1.5,.654],[3.7,1.5,.654]],
'listener':[[.0,0,0]],
'waiting_left':[[-5.03,-5.41,.793],[-5,-5.8,.793],[-4.2,-5.8,.793],[-4.0,-5.3,.793],[-4,-4.3,.654],[-4.4,-3.36,.654]],
'waiting_right':[[.02,-5.26,.793],[.4,-5.7,.793],[1.2,-5.3,.793],[1.7,-4.8,.63]],
}
res={}
for key,points in routes.items():
 failures=[]
 for a,b in zip(points,points[1:]):
  for j in range(11):
   u=j/10;p=Vector([a[k]*(1-u)+b[k]*u for k in range(3)]);bad=set()
   for h,rad in [(.12,.27),(.50,.32),(.95,.25),(1.3,.22)]:
    for k in range(12):
     ang=k*math.pi/6;vec=Vector((math.cos(ang),math.sin(ang),0));hit,no,idx,d=world.ray_cast(p+Vector((0,0,h)),vec,rad)
     if hit is not None:bad.add(names[idx])
   if bad:failures.append({'p':list(p),'obstacles':list(bad)})
 res[key]=failures
(out/'route-obstacles-v2.json').write_text(json.dumps(res,indent=2));print({k:len(v)for k,v in res.items()},flush=True)
