import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-07';s=bpy.context.scene;bpy.context.view_layer.update()
def bounds(objs,matrix=None):
 pts=[o.matrix_world@Vector(v) for o in objs if o.type=='MESH' for v in o.bound_box]
 if matrix is not None:pts=[matrix@p for p in pts]
 return ([min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]) if pts else None
zones=[]
for name in ['CP05_lower_stair','CP05_upper_stair','CP06_restaurant_terrace_gallery']:
 root=bpy.data.objects[name];inv=root.matrix_world.inverted();bb=bounds([o for o in root.children_recursive if 'tread' in o.name.lower()],inv)
 if bb is None:bb=([-.58,0,-.8],[.58,1,1.3])
 zones.append({'name':name,'inverse':inv,'min':[bb[0][0]-.08,bb[0][1]-.06,bb[0][2]-.05],'max':[bb[1][0]+.08,bb[1][1]+.06,bb[1][2]+1.35]})
decks=[o for o in s.objects if o.name.startswith('CP02 bridge deck')];bridgebb=bounds(decks)
if bridgebb:zones.append({'name':'bridge deck','inverse':None,'min':[bridgebb[0][0]-.04,bridgebb[0][1]-.04,bridgebb[0][2]-.5],'max':[bridgebb[1][0]+.04,bridgebb[1][1]+.04,bridgebb[1][2]+1.3]})
def overlap(a,z):return all(a[1][i]>=z['min'][i] and a[0][i]<=z['max'][i] for i in range(3))
removed=[]
for root in [o for o in s.objects if o.name.startswith('CP07 garden cluster')]:
 hit=[]
 for z in zones:
  bb=bounds(list(root.children_recursive),z['inverse'])
  if bb and overlap(bb,z):hit.append(z['name'])
 if hit:
  removed.append({'cluster':root.name,'zones':hit})
  for name in [o.name for o in root.children_recursive]+[root.name]:
   o=bpy.data.objects.get(name)
   if o:bpy.data.objects.remove(o,do_unlink=True)
# Inspect inherited flower details too; remove only individual foliage pieces
# whose bounds intrude into these reserved walking surfaces.
cleared=[]
for o in list(s.objects):
 if o.type!='MESH' or not any(c.name=='07_Paper_Foliage' for c in o.users_collection) or o.parent:continue
 if not any(x in o.name.lower() for x in ['leaf','petal','bloom','blossom','plant']):continue
 for z in zones:
  bb=bounds([o],z['inverse'])
  if bb and overlap(bb,z):cleared.append({'object':o.name,'zone':z['name']});bpy.data.objects.remove(o,do_unlink=True);break
rec=json.loads((OUT/'revision-record.json').read_text());rec['walking_surface_decor_cleanup']={'method':'Conservative 3D bounding-box overlap of new whole plant clusters with stair tread and bridge zones; local stairs use stair coordinates, bridge uses world AABB. This is a set-dressing exclusion, not navigation.','removed_clusters':removed,'removed_inherited_pieces':cleared,'zones':[{'name':z['name'],'min':z['min'],'max':z['max']} for z in zones]};(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp07.blend'));print('CLEANUP',json.dumps({'clusters':removed,'pieces':cleared},ensure_ascii=False),flush=True)
