import bpy,json,math,collections
from pathlib import Path
from mathutils import Vector,Matrix
R=Path.cwd();A=R/'app/runtime-cp18/public/assets';O=R/'outputs/runtime-checkpoint-18';s=bpy.context.scene;reg=json.loads((A/'runtime-registry.json').read_text());proposal=json.loads((O/'rail-corridor-hard-proposal.json').read_text());points=[Vector(p)for p in proposal['proposed_points']];old=[Vector(p)for p in proposal['original_points']];N=len(points);normals=[]
for i in range(N):
 t=(points[(i+1)%N]-points[(i-1)%N]).normalized();normals.append(Vector((t.y,-t.x,0)).normalized())
for j,name in enumerate(['CP02 continuous rail','CP02 continuous rail.001']):
 o=bpy.data.objects[name];inv=o.matrix_world.inverted()
 for i,p in enumerate(o.data.splines[0].points):q=inv@(points[i]+normals[i]*(-.36 if j==0 else .36));p.co=(*q,1)
lengths=[0]
for i in range(N):lengths.append(lengths[-1]+(points[(i+1)%N]-points[i]).length)
L=lengths[-1]
def sample(d):
 d%=L;i=next(i for i in range(N)if lengths[i+1]>=d);u=(d-lengths[i])/(lengths[i+1]-lengths[i]);p=points[i].lerp(points[(i+1)%N],u);t=(points[(i+1)%N]-points[i]).normalized();return p,t
sleepers=[o for o in s.objects if o.name.startswith('CP02 sleeper')];template=sleepers[0];count=round(L/.34)
for i in range(count):
 if i<len(sleepers):o=sleepers[i]
 else:o=template.copy();o.data=template.data;bpy.context.collection.objects.link(o);o.name='CP18 sleeper'
 p,t=sample(i*L/count);o.location=(p.x,p.y,.68);o.rotation_euler.z=math.atan2(t.y,t.x)
# A layered paper rail bed supports the newly cleared outside corridor.
mat=bpy.data.materials.get('Washi | warm ivory');edge=bpy.data.materials.get('Paper foliage | blue slate')or mat
verts=[];faces=[];mi=[]
for i,p in enumerate(points):
 n=normals[i];inner=old[i]-n*.50;outer=p+n*1.15
 for q,z in [(inner,.635),(outer,.635),(outer,-.72)]:verts.append((q.x,q.y,z))
for i in range(N):
 j=(i+1)%N;faces.extend([(3*i,3*j,3*j+1,3*i+1),(3*i+1,3*j+1,3*j+2,3*i+2)]);mi.extend([0,1])
mesh=bpy.data.meshes.new('CP18 supported rail ribbon');mesh.from_pydata(verts,[],faces);mesh.materials.append(mat);mesh.materials.append(edge);mesh.polygons.foreach_set('material_index',mi);obj=bpy.data.objects.new('CP18 supported rail ribbon',mesh);s.collection.objects.link(obj)
# Correct articulated walking: separate knees and ankles while preserving the rest silhouette.
rig=[]
for e in reg['entities']:
 if e['kind']!='resident':continue
 root=bpy.data.objects[e['blender_object']]
 for side,sgn in [('left',-1),('right',1)]:
  part=next((p for p in e['parts']if p['id']=='anim_leg_'+side),None)
  if not part:continue
  hip=bpy.data.objects[part['blender_object']];trousers=next((o for o in hip.children_recursive if o.name.startswith('Trouser leg')),None);shoe=next((o for o in hip.children_recursive if o.name.startswith('Shoe')),None)
  if not trousers or not shoe:continue
  def control(name,pos,parent):
   o=bpy.data.objects.new(root.name+'__'+name,None);s.collection.objects.link(o);o.parent=parent;o.matrix_world=root.matrix_world@Matrix.Translation(Vector(pos));o['decision_part_id']=name;o['decision_owner']=e['id'];e['parts'].append({'id':name,'blender_object':o.name,'control':'rigid_hinge','axis':'X'});return o
  knee=control('anim_knee_'+side,(sgn*.1,-.01,.29),hip);ankle=control('anim_ankle_'+side,(sgn*.1,-.01,.11),knee);bpy.context.view_layer.update()
  # The old trouser box becomes two matching paper segments; no higher-detail body needed.
  material=trousers.active_material;oldname=trousers.name;bpy.data.objects.remove(trousers,do_unlink=True)
  for label,z,length,parent in [('upper',.395,.21,hip),('lower',.20,.18,knee)]:
   me=bpy.data.meshes.get('Shared cube').copy();o=bpy.data.objects.new('CP18 '+label+' trouser '+root.name+' '+side,me);s.collection.objects.link(o);o.parent=parent;o.matrix_world=root.matrix_world@Matrix.Translation(Vector((sgn*.1,-.01,z)))@Matrix.Diagonal((.14,.14,length,1));o.data.materials.clear();o.data.materials.append(material)
  mw=shoe.matrix_world.copy();shoe.parent=ankle;shoe.matrix_world=mw;rig.append([e['id'],side])
# Initial train placement comes from the real path. Both cars keep their original dimensions.
car_rows=[]
for name in ['tram_car_front','tram_car_rear']:
 o=bpy.data.objects[name];p=o.matrix_world.translation;idx=min(range(N),key=lambda i:(points[i]-p).length);d=lengths[idx];q,t=sample(d);yaw=math.atan2(t.y,t.x);o.location=(q.x,q.y,.864);o.rotation_euler.z=yaw;car_rows.append({'id':o.get('decision_entity_id'),'yaw':yaw,'scale':list(o.scale),'start_distance':d})
reg['parts_count']=sum(len(e['parts'])for e in reg['entities']);reg['source_checkpoint']='CP18 dynamic derivative of accepted CP16; CP17 preserved'
for e in reg['entities']:e['position']=list(bpy.data.objects[e['blender_object']].matrix_world.translation)
bpy.context.view_layer.update();(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));(A/'rail-path.json').write_text(json.dumps({'points':[list(p)for p in points],'lengths':lengths,'length':L,'root_height_above_rail':.124,'cars':car_rows},indent=2));(O/'model-changes.json').write_text(json.dumps({'rail_length':L,'sleepers':count,'max_radial_rail_shift':max(proposal['profile']),'core_building_transforms_changed':False,'rigged_leg_pairs':rig,'parts':reg['parts_count'],'source_checkpoint':'CP17'},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp18/town-runtime.blend'));print('MODEL_READY',L,reg['parts_count'])
