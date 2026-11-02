import bpy,json,math,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path.cwd();A=R/'app/runtime-cp19/public/assets';O=R/'outputs/runtime-checkpoint-19';s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();nav=json.loads((A/'navigation.json').read_text());v=[];f=[];names=[]
for ob in s.objects:
 if ob.type not in ['MESH','CURVE']or ob.hide_render or any(c.hide_render or c.name.startswith('12_')for c in ob.users_collection):continue
 if not any(x in ob.name.lower()for x in ['roof','awning','canopy']):continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vs=[ev.matrix_world@p.co for p in me.vertices];fs=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear();off=len(v);v.extend(vs);f.extend(tuple(off+k for k in tri)for tri in fs);names.extend([ob.name]*len(fs))
roof=BVHTree.FromPolygons(v,f,all_triangles=True);shelters=[]
for i,p in enumerate(nav['nodes']):
 hits=[]
 for dx,dy in [(0,0),(.18,0),(-.18,0),(0,.18),(0,-.18)]:
  h,n,ix,d=roof.ray_cast(Vector((p[0]+dx,p[1]+dy,p[2]+1.49)),Vector((0,0,1)),5)
  if h is not None:hits.append(names[ix])
 if len(hits)>=3:shelters.append({'node':i,'point':p[:3],'cover':hits[0],'rays':len(hits)})
for a in nav['actors']:
 p=a['position'];hits=[]
 for height in [1.15,1.3,1.45]:
  h,n,ix,d=roof.ray_cast(Vector((p[0],p[1],p[2]+height)),Vector((0,0,1)),5)
  hits.append(names[ix]if h is not None else None)
 print('HOME_COVER',a['id'],p,hits)
tea=bpy.data.objects['tea_house'];inv=tea.matrix_world.inverted();room=[]
for ob in s.objects:
 if any(k in ob.name for k in ['CP06 dining','CP15 folded noren','Tea balcony floor','CP13 tea interior','Tea warm','CP16 tea cabinet']):room.append({'name':ob.name,'local':list(inv@ob.matrix_world.translation),'size':list(ob.dimensions)})
reg=json.loads((A/'runtime-registry.json').read_text());actors=[]
for e in reg['entities']:
 if e['kind']=='resident':actors.append({'id':e['id'],'p':e['position'],'yaw':bpy.data.objects[e['blender_object']].matrix_world.to_euler().z})
(O/'activity-space-inspection.json').write_text(json.dumps({'shelters':shelters,'room':room,'actors':actors,'tea_matrix':[list(r)for r in tea.matrix_world]},indent=2));print('SHELTER',len(shelters),collections.Counter(x['cover']for x in shelters));print('ROOM',json.dumps(room[:30]));print('RESIDENTS',len(actors))
