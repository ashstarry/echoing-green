import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[]
def owner(o):
 while o:
  if o.get('decision_kind'):return o['decision_kind']
  o=o.parent
for o in s.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection)or owner(o)in ['resident','bird','weather','star','celestial']or 'studio'in o.name.lower():continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();off=len(vs);vs.extend(ev.matrix_world@v.co for v in me.vertices);fs.extend(tuple(off+i for i in t.vertices)for t in me.loop_triangles);ev.to_mesh_clear()
world=BVHTree.FromPolygons(vs,fs,all_triangles=True);out={}
for kind,count in [('snow',160),('rain',100)]:
 rows=[]
 for j in range(count):
  x=-11+(j*.618%1)*22 if kind=='snow'else 8.5+(j*.6180339887%1)*2.4;y=7-(j*.731%1)*13 if kind=='snow'else .8-(j*.731%1)*2.5
  heights=[]
  for dx,dy in [(0,0),(.14,0),(-.14,0),(0,.14),(0,-.14)]:
   p,n,i,d=world.ray_cast(Vector((x+dx,y+dy,8)),Vector((0,0,-1)),12)
   if p:heights.append(p.z)
  rows.append(round(max(heights,default=.3)+.10,4))
 out[kind]=rows
Path('app/runtime-cp17/public/assets/weather-support.json').write_text(json.dumps(out))
print('WEATHER_SUPPORT_READY',max(out['snow']))
