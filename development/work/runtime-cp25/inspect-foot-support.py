exec(open('work/runtime-cp25/check-support-final.py').read().split('for fr in d[\'frames\'][::4]:')[0])
fr=next(f for f in d['frames']if abs(f['time']-84.05)<.01);who='resident.market_browser'
for i in foot_mesh[who]:
 m=mat(fr['matrices'][i]);vs=[m@v for v in geos[d['meshes'][i]['gid']]['v']];low=min(v.z for v in vs);sole=[v for v in vs if v.z<low+.015];x0,x1=min(v.x for v in sole),max(v.x for v in sole);y0,y1=min(v.y for v in sole),max(v.y for v in sole)
 hits=[]
 for a in range(11):
  for b in range(11):
   p=Vector((x0+(x1-x0)*a/10,y0+(y1-y0)*b/10,low));hit,no,idx,dist=static.ray_cast(p+Vector((0,0,.045)),Vector((0,0,-1)),.5)
   if hit is not None and no.z>.4:hits.append(p.z-hit.z)
 print(d['meshes'][i]['name'],low,'samples',len(hits),'lowest',sorted(hits)[:10],'supported',sum(-.006<=g<=.05 for g in hits))
