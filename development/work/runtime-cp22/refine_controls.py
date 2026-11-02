import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path.cwd();A=R/'app/runtime-cp22/public/assets';reg=json.loads((A/'runtime-registry.json').read_text());by={e['id']:e for e in reg['entities']};scene=bpy.context.scene
for e in reg['entities']:
 root=bpy.data.objects[e['blender_object']]
 for p in e['parts']:
  if not (p['id'].startswith('tap_foot_') or e['kind']=='bicycle'and p['id'].startswith('wheel_') or p['id']=='turn_page'):continue
  ctrl=bpy.data.objects[p['blender_object']];children=list(ctrl.children);saved={o:o.matrix_world.copy()for o in children};pos=ctrl.matrix_world.translation.copy()
  if p['id'].startswith('tap_foot_'):
   shoe=next(o for o in children if o.type=='MESH');inv=root.matrix_world.inverted();vv=[inv@(shoe.matrix_world@Vector(v))for v in shoe.bound_box];pos=root.matrix_world@Vector(((min(v.x for v in vv)+max(v.x for v in vv))/2,max(v.y for v in vv),min(v.z for v in vv)+.001))
  target=root.matrix_world.copy();target.translation=pos;ctrl.matrix_world=target;bpy.context.view_layer.update()
  for o,mw in saved.items():o.matrix_world=mw
# Connect the existing umbrella pole to its carrier's actual right hand.
e=by['umbrella.carried_umbrella'];root=bpy.data.objects[e['blender_object']];carrier=bpy.data.objects[by['resident.water_companion']['blender_object']];arm=bpy.data.objects['water_companion__anim_elbow_right'];hand=next(o for o in arm.children_recursive if o.name.startswith('Hand'));start=hand.matrix_world.translation;end=bpy.data.objects['CP02 umbrella handle'].matrix_world.translation.copy();end.z-=.47;delta=end-start
bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.012,depth=delta.length,location=(start+end)/2);grip=bpy.context.object;grip.name='CP22 umbrella angled hand grip';grip.rotation_euler=delta.to_track_quat('Z','Y').to_euler();grip.data.materials.append(bpy.data.objects['CP02 umbrella handle'].active_material);mw=grip.matrix_world.copy();grip.parent=root;grip.matrix_world=mw
mw=root.matrix_world.copy();root.parent=arm;root.matrix_parent_inverse=arm.matrix_world.inverted();root.matrix_world=mw;e['socket_part']='anim_elbow_right';e['parent_entity']='resident.water_companion'
# Bake actual bridge support heights, not a guessed flat deck.
dg=bpy.context.evaluated_depsgraph_get();vv=[];ff=[]
for o in scene.objects:
 if not o.name.startswith('CP02 bridge deck'):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();offset=len(vv);vv.extend(ev.matrix_world@v.co for v in me.vertices);ff.extend(tuple(offset+j for j in t.vertices)for t in me.loop_triangles);ev.to_mesh_clear()
tree=BVHTree.FromPolygons(vv,ff,all_triangles=True);grid={};ox=6.1;oy=-1.7;step=.025
for ix in range(201):
 for iy in range(101):
  hit,no,idx,d=tree.ray_cast(Vector((ox+ix*step,oy+iy*step,2)),Vector((0,0,-1)),2)
  if hit is not None and no.z>.65:grid[f'{ix},{iy}']=round(hit.z,6)
(A/'local-support.json').write_text(json.dumps({'bridge':{'origin':[ox,oy],'step':step,'grid':grid}},separators=(',',':')));(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp22/town-runtime.blend'));print('CONTROL_REFINEMENT',len(grid))
