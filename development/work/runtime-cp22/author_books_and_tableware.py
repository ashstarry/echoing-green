import bpy,bmesh,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path.cwd();A=R/'app/runtime-cp22/public/assets';reg=json.loads((A/'runtime-registry.json').read_text());by={e['id']:e for e in reg['entities']};scene=bpy.context.scene

def attach(o,p):
 mw=o.matrix_world.copy();o.parent=p;o.matrix_parent_inverse=p.matrix_world.inverted();o.matrix_world=mw
# Preserve the open silhouette, add a real thin turning leaf and a separate closing half-cover.
e=by['book.terrace_reader_book'];book=bpy.data.objects[e['blender_object']];page=bpy.data.objects[next(p['blender_object']for p in e['parts']if p['id']=='turn_page')];rightPages=bpy.data.objects['CP19 book folded pages.001'];cover=bpy.data.objects['CP19 book cover'];oldCoverMat=cover.active_material
close=bpy.data.objects.new('CP22 reader book closing cover',None);scene.collection.objects.link(close);close.matrix_world=book.matrix_world@Matrix.Translation((0,0,.031));close.parent=book;close.matrix_parent_inverse=book.matrix_world.inverted();close['decision_part_id']='close_cover';close['decision_owner']=e['id'];e['parts'].append({'id':'close_cover','blender_object':close.name,'control':'rigid_hinge','axis':'Y'});attach(rightPages,close)
inv=book.matrix_world.inverted();verts=[inv@(cover.matrix_world@v.co)for v in cover.data.vertices];faces=[tuple(p.vertices)for p in cover.data.polygons]
for name,inner in [('left',False),('right',True)]:
 me=bpy.data.meshes.new('CP22 split book '+name);me.from_pydata(verts,[],faces);bm=bmesh.new();bm.from_mesh(me);cut=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=(0,0,0),plane_no=(1,0,0),clear_inner=inner,clear_outer=not inner);edges=[x for x in cut['geom_cut']if isinstance(x,bmesh.types.BMEdge)];bmesh.ops.holes_fill(bm,edges=edges,sides=0);bm.to_mesh(me);bm.free();me.materials.append(oldCoverMat);o=bpy.data.objects.new('CP22 book '+name+' cover',me);scene.collection.objects.link(o);o.matrix_world=book.matrix_world.copy();attach(o,close if name=='right'else book)
bpy.data.objects.remove(cover,do_unlink=True)
# Existing turn-page identity now operates a single thin leaf, not half the book block.
me=bpy.data.meshes.new('CP22 thin turning leaf');me.from_pydata([(0.003,-.09,.044),(.14,-.09,.044),(.14,.09,.044),(.003,.09,.044)],[],[(0,1,2,3)]);me.materials.append(bpy.data.objects['CP19 book folded pages'].active_material);leaf=bpy.data.objects.new('CP22 individual paper leaf',me);scene.collection.objects.link(leaf);leaf.matrix_world=book.matrix_world.copy();solid=leaf.modifiers.new('paper thickness','SOLIDIFY');solid.thickness=.0012;attach(leaf,page)
# Give existing table objects identities so they are picked up and put back, not duplicated.
metadata={}
for i in range(2):
 table=bpy.data.objects['CP14_upper_dining_table_'+str(i)];actor='resident.upper_diner_'+str(i);items={}
 for kind,prefix in [('cup','CP14 dinner tea cup'),('food','CP14 small rice bun')]:
  objects=[o for o in table.children_recursive if o.type=='MESH'and o.name.startswith(prefix)];obj=objects[0];vv=[obj.matrix_world@Vector(v)for v in obj.bound_box];pos=Vector(((min(v.x for v in vv)+max(v.x for v in vv))/2,(min(v.y for v in vv)+max(v.y for v in vv))/2,min(v.z for v in vv)));id=f'{kind}.upper_table_{i}';root=bpy.data.objects.new('CP22 '+id,None);scene.collection.objects.link(root);root.matrix_world=table.matrix_world.copy();root.matrix_world.translation=pos;root['decision_entity_id']=id;root['decision_kind']=kind;attach(root,table);attach(obj,root)
  reg['entities'].append({'id':id,'kind':kind,'blender_object':root.name,'label':'餐桌茶杯'if kind=='cup'else'餐桌点心','position':list(pos),'parent_entity':'workstation.upper_dining_table_'+str(i),'parts':[],'state':{'owner':actor,'place':'table'},'actions':[{'id':'sip_tea'if kind=='cup'else'taste_food','implementation':'CP22 local action executor'}],'anchors':[]});items[kind]=id
 metadata[actor]=items
(A/'dining-props.json').write_text(json.dumps(metadata,indent=2));reg['parts_count']=sum(len(e['parts'])for e in reg['entities']);reg['entities_count']=len(reg['entities']);(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp22/town-runtime.blend'));print('BOOK_AND_DINING_PROPS',len(reg['entities']),reg['parts_count'])
