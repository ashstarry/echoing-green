exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
from mathutils.bvhtree import BVHTree
import re
def index(n):return int(n.rsplit('.',1)[1])if re.search(r'\.\d+$',n)else 0
groups={}
for o in s.objects:
 if o.name.startswith('CP02 edge planting leaf'):groups.setdefault(index(o.name)//5,[]).append(o)
targets={52:(-9.9,-1.9),54:(-9.4,-2.4),55:(-9.1,-2.7),57:(-8.8,-2.8),58:(-7.8,-2.9),60:(-6.5,-3.15)};centers={k:sum((o.matrix_world.translation for o in obs),Vector())/len(obs)for k,obs in groups.items()}
for o in list(s.objects):
 if not o.name.startswith('CP02 edge planting bloom'):continue
 p=o.matrix_world.translation;key=min(centers,key=lambda k:Vector((p.x-centers[k].x,p.y-centers[k].y,0)).length)
 if key in targets and Vector((p.x-centers[key].x,p.y-centers[key].y,0)).length<.3:groups[key].append(o)
dg=bpy.context.evaluated_depsgraph_get();v=[];f=[]
for o in s.objects:
 if o.type!='MESH'or o.hide_render:continue
 if not any(k in o.name.lower()for k in ['island paper layer','continuous street paving','curved station platform']):continue
 ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();off=len(v);v.extend(ev.matrix_world@p.co for p in m.vertices);f.extend(tuple(off+i for i in t.vertices)for t in m.loop_triangles);ev.to_mesh_clear()
floor=BVHTree.FromPolygons(v,f,all_triangles=True);record=[];COL=cols['07_Paper_Foliage']
for key,(r,b)in targets.items():
 center=centers[key];p=rb(r,b,.61);hit,n,i,d=floor.ray_cast(p+Vector((0,0,3)),Vector((0,0,-1)),4);assert hit is not None;p.z=hit.z+.002;delta=p-Vector((center.x,center.y,.61));root=asset('CP10_static_relocated_rail_plant_'+str(key),p);root['static_decoration']=True;root['source_clump']=key;bpy.context.view_layer.update()
 for o in groups[key]:
  mw=o.matrix_world.copy();mw.translation+=delta;o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted();o.matrix_basis=mw
 record.append({'source_clump':key,'objects':[o.name for o in groups[key]],'new_root':list(p),'ground_support_z':hit.z})
bpy.context.view_layer.update();rec=json.loads((OUT/'revision-record.json').read_text());rec['station_rail_repair']['relocated_static_plant_clumps']=record;(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'station-clear.blend'));print('TRACK_PLANTS_RELOCATED',json.dumps(record),flush=True)
