import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path.cwd();A=R/'app/runtime-cp19/public/assets';O=R/'outputs/runtime-checkpoint-19';nav=json.loads((A/'navigation.json').read_text());reg=json.loads((A/'runtime-registry.json').read_text());s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();moving={a['id']for a in nav['actors']if a['entry']}|set(json.loads((A/'motion-activities.json').read_text())['clips']);v=[];f=[];rv=[];rf=[]
def chain(o):
 while o:yield o;o=o.parent
for o in s.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 if any(a.get('decision_entity_id')in moving for a in chain(o))or any(k in o.name.lower()for k in ['visible paper rain','glint','ripple','studio floor']):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vs=[ev.matrix_world@p.co for p in me.vertices];fs=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear();off=len(v);v+=vs;f.extend(tuple(off+k for k in tri)for tri in fs)
 if any(k in o.name.lower()for k in ['roof','awning','canopy']):
  off=len(rv);rv+=vs;rf.extend(tuple(off+k for k in tri)for tri in fs)
world=BVHTree.FromPolygons(v,f,all_triangles=True);roof=BVHTree.FromPolygons(rv,rf,all_triangles=True)
def umbrella_clear(p):
 n=16;vs=[Vector((p[0]+.52*math.cos(i*2*math.pi/n),p[1]+.52*math.sin(i*2*math.pi/n),p[2]+h))for h in [1.48,1.86]for i in range(n)];fs=[]
 for i in range(n):j=(i+1)%n;fs.extend([(i,j,j+n),(i,j+n,i+n)])
 fs+=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))];b=BVHTree.FromPolygons(vs,fs)
 if b.overlap(world):return False
 h,no,ix,d=world.ray_cast(Vector((p[0],p[1],p[2]+1.86)),Vector((0,0,-1)),.38);return h is None
def cover(p,height=1.3):
 h,no,ix,d=roof.ray_cast(Vector((p[0],p[1],p[2]+height)),Vector((0,0,1)),5);return h is not None
rows=[{'node':i,'covered':cover(p,1.49),'umbrellaClear':umbrella_clear(p)}for i,p in enumerate(nav['nodes'])]
residents={e['id']:{'position':e['position'],'yaw':bpy.data.objects[e['blender_object']].matrix_world.to_euler().z,'covered':cover(e['position']),'umbrellaClear':umbrella_clear(e['position'])}for e in reg['entities']if e['kind']=='resident'}
for id in ['resident.water_visitor','resident.water_companion','resident.quiet_reader']:residents[id]['umbrellaClear']=False
out={'nodes':rows,'residents':residents,'scope':'Authored roof ray and conservative 0.52-radius umbrella head-volume sweep. Dynamic people/animals excluded here; occupancy is handled by runtime.'};(A/'activity-spaces.json').write_text(json.dumps(out,separators=(',',':')));(O/'shelter-slot-audit.json').write_text(json.dumps({'covered_nodes':sum(x['covered']for x in rows),'umbrella_safe_nodes':sum(x['umbrellaClear']for x in rows),'residents':residents},indent=2));print('COVER',sum(x['covered']for x in rows),'UMBRELLA',sum(x['umbrellaClear']for x in rows))
