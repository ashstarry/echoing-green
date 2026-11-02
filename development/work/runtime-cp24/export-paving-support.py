import bpy,json,math
from pathlib import Path
triangles=[];names=[];dg=bpy.context.evaluated_depsgraph_get()
for obj in bpy.context.scene.objects:
 if obj.type not in ['MESH','CURVE'] or obj.hide_render or any(c.hide_render for c in obj.users_collection):continue
 if not any(k in obj.name.lower()for k in ['continuous street paving','plaza stone ring']):continue
 ev=obj.evaluated_get(dg);mesh=ev.to_mesh();mesh.calc_loop_triangles();vs=[ev.matrix_world@v.co for v in mesh.vertices]
 count=0
 for t in mesh.loop_triangles:
  a,b,c=[vs[i]for i in t.vertices];normal=(b-a).cross(c-a)
  if normal.length<1e-9 or normal.normalized().z<.45:continue
  if max(a.z,b.z,c.z)>.85 or min(a.z,b.z,c.z)<.50:continue
  triangles.append([[round(v.x,6),round(v.y,6),round(v.z,6)]for v in [a,b,c]]);count+=1
 if count:names.append(obj.name)
 ev.to_mesh_clear()
data={'version':1,'coordinates':'Blender Z-up','cell':.4,'triangles':triangles,'source_objects':names,'scope':'Actual evaluated paving top surfaces; independent of whether a cell is navigable. Used only for rendering foot contact, not to make new routes walkable.'}
p=Path.cwd()/'app/runtime-cp24/public/assets/paving-support.json';p.write_text(json.dumps(data,separators=(',',':')))
(Path.cwd()/'outputs/runtime-checkpoint-24/paving-support-export.json').write_text(json.dumps({'objects':len(names),'triangles':len(triangles),'bytes':p.stat().st_size,'source_model':'outputs/runtime-checkpoint-22/borrowed-wind-town-cp22.blend'},indent=2));print('PAVING',len(names),len(triangles),p.stat().st_size)
