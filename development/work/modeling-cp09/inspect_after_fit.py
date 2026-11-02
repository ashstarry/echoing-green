import bpy,json,math,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'work/modeling-cp09';s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();actors=[]
def chain(o):
 a=[]
 while o:a.append(o);o=o.parent
 return a
def owner(o):return next((x for x in chain(o) if x.get('decision_kind')),None)
def geom(o):
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@x.co for x in me.vertices];f=[tuple(t.vertices) for t in me.loop_triangles];ev.to_mesh_clear();return v,f
statv=[];statf=[];names=[];body=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE'] or o.hide_render or any(c.hide_render or c.name.startswith('12_') for c in o.users_collection):continue
 ow=owner(o)
 if ow and ow.get('decision_kind') in ['resident','animal','bird','fish','instrument','letter','umbrella','kite']:continue
 v,f=geom(o);off=len(statv);statv.extend(v);statf.extend(tuple(off+i for i in q) for q in f);names.extend([o.name]*len(f))
static=BVHTree.FromPolygons(statv,statf,all_triangles=True)
reports=[]
for root in [o for o in s.objects if o.get('decision_kind')=='resident']:
 vv=[];ff=[];on=[];bodies=[]
 for o in root.children_recursive:
  if o.type!='MESH' or owner(o)!=root:continue
  v,f=geom(o);off=len(vv);vv.extend(v);ff.extend(tuple(off+i for i in q) for q in f);on.extend([o.name]*len(f));bodies.append({'name':o.name,'bbox_min':[min(p[i] for p in v) for i in range(3)],'bbox_max':[max(p[i] for p in v) for i in range(3)]})
 bvh=BVHTree.FromPolygons(vv,ff,all_triangles=True);pairs=bvh.overlap(static);counts=collections.Counter((on[a],names[b]) for a,b in pairs)
 reports.append({'actor':root.name,'origin':list(root.matrix_world.translation),'scale':list(root.scale),'rotation':list(root.rotation_euler),'surface_overlap_candidates':[{'body':a,'other':b,'triangle_pairs':n} for (a,b),n in counts.most_common(30)],'components':bodies})
detail={}
for name in ['west_home','small_wood_home','porch_resident','station_main','quiet_reader','CP05_overlook_bench','cyclist','street_bicycle','pond_boat']:
 o=bpy.data.objects[name];detail[name]={'matrix':[list(r) for r in o.matrix_world],'children':[{'name':c.name,'type':c.type,'location':list(c.location),'scale':list(c.scale)} for c in o.children if not(c.name.startswith('CP05 balcony foliage') or 'shingle'in c.name)]}
(WORK/'contact-after-fit.json').write_text(json.dumps({'actor_reports':reports,'details':detail,'method':'Actual mesh triangle BVH overlap candidates, prior to contact classification and closed-solid containment checks.'},indent=2));print(json.dumps([{'actor':r['actor'],'candidates':r['surface_overlap_candidates'][:12]} for r in reports if r['surface_overlap_candidates']],indent=2))
