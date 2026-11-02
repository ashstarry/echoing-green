import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path.cwd()
def revise(model,asset):
 reg=json.loads((asset/'runtime-registry.json').read_text());e=next(e for e in reg['entities']if e['id']=='resident.water_visitor');root=bpy.data.objects[e['blender_object']];before=list(root.matrix_world.translation);root.location.y-=.10;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();vv=[];ff=[]
 for o in bpy.context.scene.objects:
  if not o.name.startswith('CP02 bridge deck'):continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();off=len(vv);vv.extend(ev.matrix_world@v.co for v in me.vertices);ff.extend(tuple(off+k for k in t.vertices)for t in me.loop_triangles);ev.to_mesh_clear()
 tree=BVHTree.FromPolygons(vv,ff,all_triangles=True);fits={}
 for shoe in [o for o in root.children_recursive if o.name.startswith('Shoe')]:
  delta=-1
  for v in shoe.data.vertices:
   q=shoe.matrix_world@v.co;hit,no,idx,d=tree.ray_cast(q+Vector((0,0,.25)),Vector((0,0,-1)),.6)
   if hit is not None:delta=max(delta,hit.z+.004-q.z)
  delta=max(0,delta);m=shoe.matrix_world.copy();m.translation.z+=delta;shoe.matrix_world=m;fits[shoe.name]=delta
 e['position']=list(root.matrix_world.translation);(asset/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(model));return{'before':before,'after':e['position'],'shoe_lifts':fits}
main=revise(R/'work/runtime-cp22/town-runtime.blend',R/'app/runtime-cp22/public/assets');A=R/'app/runtime-cp22/public/assets';sockets=json.loads((A/'actor-sockets.json').read_text());sockets['resident.water_visitor']['origin']=main['after'];(A/'actor-sockets.json').write_text(json.dumps(sockets,indent=2));spaces=json.loads((A/'activity-spaces.json').read_text());spaces['residents']['resident.water_visitor']['position']=main['after'];(A/'activity-spaces.json').write_text(json.dumps(spaces,separators=(',',':')))
branch=R/'work/runtime-cp22/boarding/town-boarding.blend';bpy.ops.wm.open_mainfile(filepath=str(branch));other=revise(branch,R/'work/runtime-cp22/boarding/assets');(R/'outputs/runtime-checkpoint-22/bridge-stance-refinement.json').write_text(json.dumps({'main':main,'boarding_candidate':other},indent=2));print('BRIDGE_STANCE',main)
