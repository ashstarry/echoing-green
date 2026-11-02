import bpy,json,math
from pathlib import Path
s=bpy.context.scene;out={'rails':{},'roots':{}}
for name in ['CP02 continuous rail','CP02 continuous rail.001']:
 o=bpy.data.objects[name];row={'type':o.type,'matrix':[list(x)for x in o.matrix_world],'splines':[]}
 if o.type=='CURVE':
  for p in o.data.splines:row['splines'].append({'type':p.type,'cyclic':p.use_cyclic_u,'points':[list(o.matrix_world@v.co.to_3d())for v in p.points],'bezier':[{'co':list(o.matrix_world@v.co),'left':list(o.matrix_world@v.handle_left),'right':list(o.matrix_world@v.handle_right)}for v in p.bezier_points]})
 out['rails'][name]=row
for name in ['tram_car_front','tram_car_rear','pond_boat','duck_0','pond_fish_0','doorstep_cat','garden_fox','CP14_upper_diner_0','CP14_upper_diner_1','street_bicycle','cyclist','kite_child']:
 o=bpy.data.objects[name];out['roots'][name]={'position':list(o.matrix_world.translation),'scale':list(o.matrix_world.to_scale()),'yaw':o.matrix_world.to_euler().z,'parent':o.parent.name if o.parent else None,'children':[{'name':c.name,'type':c.type,'location':list(c.location),'dimensions':list(c.dimensions),'rotation':list(c.rotation_euler),'parent':c.parent.name if c.parent else None}for c in o.children_recursive if c.type in ['MESH','EMPTY']]}
Path('work/runtime-cp18/geometry-inspection.json').write_text(json.dumps(out,indent=2));print(json.dumps({n:[(p['type'],len(p['points']),len(p['bezier']),p['cyclic'])for p in r['splines']]for n,r in out['rails'].items()}))
