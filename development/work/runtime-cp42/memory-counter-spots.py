import bpy,json,math
from pathlib import Path
from mathutils import Vector
scene=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();spots=[]
for index,name in enumerate(['Stall counter','Stall counter.001','Stall counter.002']):
 o=bpy.data.objects[name];candidates=[];lo=[min(p[i]for p in o.bound_box)for i in range(3)];hi=[max(p[i]for p in o.bound_box)for i in range(3)]
 for x in[i*.12 for i in range(-7,8)]:
  for y in[-.72,-.48,-.24,0,.24,.48,.72]:
   p=o.matrix_world@Vector(((lo[0]+hi[0])/2+x*(hi[0]-lo[0])/2,(lo[1]+hi[1])/2+y*(hi[1]-lo[1])/2,hi[2]));hit,loc,no,face,target,m=scene.ray_cast(dg,p+Vector((0,0,.18)),Vector((0,0,-1)),distance=.3)
   if x==0 and y==0:print(name,'CENTER',list(p),'HIT',target.name if hit else None)
   if hit and target.name==name and no.z>.9 and (index or all(math.hypot(p.x-q[0],p.y-q[1])>q[2]for q in[(-3.14,1.72,.40),(-2.61,1.91,.23)])):candidates.append((abs(y)+abs(x-.24)*.2,p))
 picked=[]
 for score,p in sorted(candidates,key=lambda x:x[0]):
  if all((p-q).length>.22 for q in picked):picked.append(p)
  if len(picked)==2:break
 for p in picked:spots.append({'anchor':[p.x,p.y,p.z+.008],'stand':[[-2.4,1.6],[-.9,2.68],[.59,3.8]][index],'counter':name})
Path('work/runtime-cp42/memory-counter-spots.json').write_text(json.dumps(spots,indent=2));print('MEMORY_SPOTS',len(spots),spots)
