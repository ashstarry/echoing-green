import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path.cwd();A=R/'app/runtime-cp30/public/assets';out=R/'work/runtime-cp30';dg=bpy.context.evaluated_depsgraph_get();reg=json.loads((A/'runtime-registry.json').read_text());objects=[];tri=[];names=[];v=[];faces=[]
def ancestry(o):
 while o:yield o;o=o.parent
for o in bpy.context.scene.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 chain=list(ancestry(o));owner=next((p.get('decision_entity_id') for p in chain if p.get('decision_entity_id')),None)
 if any(str(p.get('decision_entity_id','')).startswith(('resident.','animal.','fish.','bird.','tram.','kite.','boat.'))for p in chain):continue
 if any(k in o.name.lower() for k in ['glint','ripple','studio floor','rain','water surface']):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();pts=[ev.matrix_world@p.co for p in me.vertices];fs=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear()
 off=len(v);v.extend(pts);faces.extend(tuple(off+i for i in f)for f in fs);names.extend([o.name]*len(fs))
 if any(x in o.name.lower()for x in ['bridge deck','stair','paving','plaza stone','terrace deck','platform','landing','bench']):
  objects.append({'name':o.name,'bounds':[[min(p[k]for p in pts)for k in range(3)],[max(p[k]for p in pts)for k in range(3)]],'matrix':[list(x)for x in o.matrix_world]})
  for f in fs:
   aa,bb,cc=[pts[i]for i in f];n=(bb-aa).cross(cc-aa)
   if n.length>1e-6 and n.normalized().z>.45:tri.append([[round(x,6)for x in p]for p in [aa,bb,cc]])
(out/'world-surfaces.json').write_text(json.dumps({'objects':objects,'triangles':tri},separators=(',',':')))
# Detailed seated part bounding boxes in each actor's local coordinates.
result={}
for e in reg['entities']:
 if e['kind']!='resident':continue
 root=bpy.data.objects[e['blender_object']];meshes=[]
 for o in root.children_recursive:
  if o.type=='MESH' and any(x in o.name.lower()for x in ['seated','shoe']):
   pts=[root.matrix_world.inverted()@o.matrix_world@Vector(p)for p in o.bound_box];meshes.append({'name':o.name,'parent':o.parent.name,'bounds':[[min(p[k]for p in pts)for k in range(3)],[max(p[k]for p in pts)for k in range(3)]]})
 result[e['id']]={'object':root.name,'position':list(root.matrix_world.translation),'meshes':meshes}
(out/'seated-parts.json').write_text(json.dumps(result,indent=2));print('SURFACES',len(tri),'OBJECTS',len(objects),flush=True)
