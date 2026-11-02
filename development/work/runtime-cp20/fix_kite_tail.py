import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path.cwd();A=R/'app/runtime-cp20/public/assets';root=bpy.data.objects['plaza_kite'];body=bpy.data.objects['Red paper kite'];old=bpy.data.objects['CP02 kite ribbon'];material=old.active_material;oldloc=list(old.matrix_world.translation);bpy.data.objects.remove(old,do_unlink=True)
tip=min((body.matrix_world@v.co for v in body.data.vertices),key=lambda p:p.z);points=[tip,tip+Vector((.07,0,-.16)),tip+Vector((.24,.035,-.34)),tip+Vector((.14,.06,-.53))];inv=root.matrix_world.inverted();verts=[];faces=[]
for p in points:
 for dy in [-.004,.004]:
  for dx in [-.027,.027]:verts.append(inv@(p+Vector((dx,dy,0))))
for i in range(3):
 a=i*4;b=(i+1)*4;faces.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
faces.extend([(0,1,3,2),(12,14,15,13)])
mesh=bpy.data.meshes.new('CP20 folded kite tail');mesh.from_pydata(verts,[],faces);mesh.materials.append(material);o=bpy.data.objects.new('CP02 kite ribbon',mesh);bpy.context.scene.collection.objects.link(o);o.parent=root;o.matrix_basis=Matrix.Identity(4);o['runtime_role']='owned folded paper tail'
reg=json.loads((A/'runtime-registry.json').read_text());e=next(e for e in reg['entities']if e['id']=='kite.plaza_kite');e['tether_note']='Runtime articulated hand endpoint and deforming tether; folded tail belongs to kite body and follows holder motion.';e['executable_modes']=['tethered_wind_sway','follow_holder','hand_attached_tether'];(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));(R/'outputs/runtime-checkpoint-20/kite-tail-correction.json').write_text(json.dumps({'old_static_object':'CP02 kite ribbon','old_transform_origin':oldloc,'now_parent':'plaza_kite','paper_strip_segments':3,'root_and_residents_unchanged':True,'scope':'Old unparented ribbon replaced with a folded strip rooted at the actual kite lower vertex.'},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp20/town-runtime.blend'));print('KITE_TAIL_BOUND')
