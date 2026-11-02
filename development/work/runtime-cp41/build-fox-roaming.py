import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path.cwd();A=R/'app/runtime-cp41/public/assets';nav=json.loads((A/'navigation.json').read_text());reg=json.loads((A/'runtime-registry.json').read_text());kinds={e['id']:e['kind']for e in reg['entities']};dg=bpy.context.evaluated_depsgraph_get();fox=bpy.data.objects['garden_fox'];foxobjs=[o for o in fox.children_recursive if o.type=='MESH'];vfox=[];ffox=[];inv=fox.matrix_world.inverted()
for o in foxobjs:
 ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();off=len(vfox);vfox.extend(inv@(ev.matrix_world@v.co)for v in m.vertices);ffox.extend(tuple(off+i for i in t.vertices)for t in m.loop_triangles);ev.to_mesh_clear()
def lineage(o):
 while o:yield o;o=o.parent
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 owner=next((q.get('decision_entity_id')for q in lineage(o)if q.get('decision_entity_id')),None)
 if owner and kinds.get(owner)in ['resident','animal','bird','fish','bicycle','tram','plant','tree','weather','water_lantern']:continue
 if any(t in o.name.lower()for t in ['plaza stone','plaza_ground','terrain','ripple','rain','glint','studio floor','petal','leaf','flower','foliage','sakura','grass']):continue
 ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@x.co for x in m.vertices];f=[tuple(t.vertices)for t in m.loop_triangles];ev.to_mesh_clear()
 if not v or max(x.z for x in v)<.66:continue
 off=len(vs);vs.extend(v);fs.extend(tuple(off+i for i in t)for t in f)
world=BVHTree.FromPolygons(vs,fs,all_triangles=True);heights=json.loads((R/'work/runtime-cp41/fox-floor.json').read_text());accepted=[];rejected=0
# Existing supported paving nodes only; samples test the entire original fox at eight headings.
for index,p in enumerate(nav['nodes']):
 x,y,z=p[:3];z=heights.get(str(index),z)
 if not (2.8<=x<=5.12 and .24<=y<=2.24):continue
 ok=True
 for j in range(8):
  matrix=Matrix.Translation(Vector((x,y,z-.03)))@Matrix.Rotation(j*math.pi/4,4,'Z')@Matrix.Scale(1.05,4)
  verts=[matrix@v for v in vfox];body=BVHTree.FromPolygons(verts,ffox,all_triangles=True)
  if body.overlap(world):ok=False;break
 if ok:accepted.append({'nav':index,'p':[x,y,z-.03]})
 else:rejected+=1
lookup={r['nav']:i for i,r in enumerate(accepted)};edges=[]
for r in accepted:
 p=nav['nodes'][r['nav']];es=[]
 for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
  n=nav['grid'].get(f'{p[3]+dx},{p[4]+dy}')
  if n in lookup and abs(nav['nodes'][n][2]-p[2])<.07:es.append(lookup[n])
 edges.append(es)
# Retain the connected region nearest the current fox, excluding isolated decorative pockets.
start=min(range(len(accepted)),key=lambda i:(accepted[i]['p'][0]-3.05375)**2+(accepted[i]['p'][1]-1.58395)**2);seen={start};stack=[start]
while stack:
 for k in edges[stack.pop()]:
  if k not in seen:seen.add(k);stack.append(k)
order=sorted(seen);mapping={v:i for i,v in enumerate(order)};data={'nodes':[accepted[i]['p']for i in order],'edges':[[mapping[k]for k in edges[i]if k in seen]for i in order],'navNodes':[accepted[i]['nav']for i in order],'scope':'Existing garden paving; full original fox mesh sampled at eight headings against hard static objects. Soft foliage and dynamic bodies handled separately; not a continuous collision proof.'}
assert len(data['nodes'])>8,(len(data['nodes']),len(accepted));m=json.loads((A/'motion-activities.json').read_text());m['foxRoaming']=data;(A/'motion-activities.json').write_text(json.dumps(m,separators=(',',':')));(R/'outputs/runtime-checkpoint-41/fox-roaming-check.json').write_text(json.dumps({'accepted_connected':len(order),'accepted_all':len(accepted),'rejected':rejected,**data},indent=2));print('FOX_ROAMING',len(order),'bounds',[(min(p[i]for p in data['nodes']),max(p[i]for p in data['nodes']))for i in [0,1]])
