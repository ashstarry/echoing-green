import bpy,json,math,re
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'work/lighting-cp12';OUT=ROOT/'outputs/lighting-checkpoint-12';s=bpy.context.scene;Q=s.camera.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));BACK=Vector((-RIGHT.y,RIGHT.x,0));FWD=Q@Vector((0,0,-1))
reg=json.loads((ROOT/'outputs/lighting-checkpoint-11/decision-entities.json').read_text());before_ids={e['id']for e in reg['entities']};notes={}
# Recover overall environmental readability while retaining CP11's local light structure.
for name,power in [('Soft overhead blue hour',1350),('Quiet front paper fill',450),('CP09 warm town fill',140),('CP12 rain-sky soft fill',40),('CP12 bridge lamp reflected fill',16),('CP11 lamp spill | street_lantern_09',30),('CP11 lamp spill | street_lantern_08',26)]:bpy.data.objects[name].data.energy=power
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.32
def actions(names):return [{'id':a,'implementation':'declared; executor/animation unimplemented','preconditions':'Validate current state, allowed target, occupancy and spatial constraints before executing.'}for a in names]
# Each existing paper star gets an independent emissive material and stable logical identity.
stars=sorted([o for o in s.objects if o.name.startswith('Paper star ')],key=lambda o:o.name)
for i,o in enumerate(stars):
 mat=o.active_material.copy();mat.name='CP12 star paper '+str(i);p=mat.node_tree.nodes['Principled BSDF'];power=[2.2,2.8,2.4,2.0,2.6][i%5];p.inputs['Emission Strength'].default_value=power;p.inputs['Emission Color'].default_value=(1,.68,.30,1);p.inputs['Roughness'].default_value=.88;o.material_slots[0].link='OBJECT';o.material_slots[0].material=mat
 eid='star.sky_star_%02d'%i;o['decision_entity_id']=eid;o['decision_kind']='star';o['decision_actions']=json.dumps(['set_brightness','twinkle','settle']);o['decision_actuation']='independent_material_emission';o['decision_status']='authoring_only_runtime_unimplemented'
 reg['entities'].append({'id':eid,'label':o.name,'kind':'star','blender_object':o.name,'position':list(o.matrix_world.translation),'parent_entity':None,'parts':[],'actions':actions(['set_brightness','twinkle','settle']),'actuation':'independent_material_emission','state':{'brightness':'medium','pattern':'steady'},'material_bindings':[mat.name],'brightness_levels':{'off':0,'low':.65,'medium':power,'high':3.6},'anchors':[],'runtime_ready':False,'requires_animation_binding':False,'note':'Existing real paper-star mesh; current glow is static, no twinkle executor.'})
# Split the existing two-triangle wing mesh into two control nodes, preserving its world triangles.
wing_changes=[]
for bird in [o for o in s.objects if o.get('decision_kind')=='bird']:
 old=next(o for o in bird.children if o.type=='MESH'and o.name.startswith('Bird paper wings'));old_faces=[];new_faces=[];parts=[]
 for pi,poly in enumerate(old.data.polygons):
  pid='wing_left'if pi==0 else'wing_right';node=bpy.data.objects.new(bird.name+'__'+pid,None);old.users_collection[0].objects.link(node);node.parent=bird;node.matrix_parent_inverse=old.matrix_parent_inverse.copy();node.matrix_basis=old.matrix_basis.copy();node['decision_part_id']=pid;node['decision_owner']=bird['decision_entity_id'];node['control_kind']='rotation';node['control_axis']='local X';node['authoring_rotation_limit_degrees']=35
  ids=list(poly.vertices);me=bpy.data.meshes.new('CP12 '+bird.name+' '+pid);me.from_pydata([old.data.vertices[j].co[:]for j in ids],[],[tuple(range(len(ids)))]);me.update();obj=bpy.data.objects.new('CP12 '+bird.name+' '+pid,me);old.users_collection[0].objects.link(obj);obj.parent=node;me.materials.append(old.material_slots[poly.material_index].material);me.polygons[0].use_smooth=poly.use_smooth
  if old.data.uv_layers.active:
   uv=me.uv_layers.new(name='UVMap')
   for li,oldli in enumerate(poly.loop_indices):uv.data[li].uv=old.data.uv_layers.active.data[oldli].uv
  old_faces.append(sorted([tuple(round(x,6)for x in old.matrix_world@old.data.vertices[j].co)for j in ids]));parts.append(node)
 bpy.context.view_layer.update()
 for node in parts:
  ob=node.children[0];new_faces.append(sorted([tuple(round(x,6)for x in ob.matrix_world@v.co)for v in ob.data.vertices]))
 assert sorted(old_faces)==sorted(new_faces)
 old_name=old.name;bpy.data.objects.remove(old,do_unlink=True)
 row=next(e for e in reg['entities']if e['id']==bird['decision_entity_id']);row['parts']=[{'id':o['decision_part_id'],'blender_object':o.name,'control':'rotation','axis':'local X','local_matrix':[list(r)for r in o.matrix_local],'authoring_angle_limit_degrees':35}for o in parts];row['actions']+=actions(['flap','glide']);row['motion_note']='Real folded-body and separate paper-wing meshes. Control pivots authored; no flight path, flap clip or airborne collision solver.';wing_changes.append({'bird':bird.name,'removed_wing_mesh':old_name,'parts':[o.name for o in parts],'world_triangles_preserved':True})
# Build a conservative obstacle field for two small floating paper lamps.
dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 if o.name=='CP02 pond'or any(k in o.name.lower()for k in ['visible paper rain','water glint','duck wake','water ripple','rain ripple']):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();off=len(vs);vs.extend(ev.matrix_world@v.co for v in me.vertices);fs.extend(tuple(off+j for j in t.vertices)for t in me.loop_triangles);ev.to_mesh_clear()
world=BVHTree.FromPolygons(vs,fs,all_triangles=True);pond=bpy.data.objects['CP02 pond'];ev=pond.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();water=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(t.vertices)for t in me.loop_triangles],all_triangles=True);ev.to_mesh_clear()
# Preserve a clear corridor for a whole tram body around the front/right arc.
car=bpy.data.objects['tram_car_front'];center=car.matrix_world.translation-RIGHT*(12*math.cos(-1.13))-BACK*(6.3*math.sin(-1.13));iv=car.matrix_world.inverted();cv=[iv@o.matrix_world@v.co for o in car.children_recursive if o.type=='MESH'for v in o.data.vertices];lo=[min(p[j]for p in cv)for j in range(2)];hi=[max(p[j]for p in cv)for j in range(2)];boxes=[]
for k in range(281):
 t=-1.4+k*1.4/280;p=center+RIGHT*(12*math.cos(t))+BACK*(6.3*math.sin(t));d=RIGHT*(-12*math.sin(t))+BACK*(6.3*math.cos(t));m=Matrix.Translation(p)@Matrix.Rotation(math.atan2(d.y,d.x),4,'Z')@Matrix.Diagonal((*car.scale,1));pts=[m@Vector((x,y,0))for x,y in [(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]];boxes.append([(p.dot(RIGHT),p.dot(BACK))for p in pts])
def rail_limit(r):
 ys=[]
 for poly in boxes:
  for a,b in zip(poly,poly[1:]+poly[:1]):
   if min(a[0],b[0])<=r<=max(a[0],b[0])and abs(b[0]-a[0])>1e-8:ys.append(a[1]+(b[1]-a[1])*(r-a[0])/(b[0]-a[0]))
 return max(ys)if ys else -100
candidates=[]
for ix in range(33):
 for iy in range(26):
  p=Vector((5.55+ix*.145,-2.95+iy*.145,.635));h,n,idx,d=water.ray_cast(p+Vector((0,0,.35)),Vector((0,0,-1)),.7)
  if h is None:continue
  p.z=h.z
  if any(water.ray_cast(p+Vector((x,y,.25)),Vector((0,0,-1)),.5)[0]is None for x in [-.19,.19]for y in [-.19,.19]):continue
  if p.dot(BACK)-rail_limit(p.dot(RIGHT))<.44:continue
  near,no,idx,dist=world.find_nearest(p+Vector((0,0,.14)))
  if dist<.31:continue
  visible=sum(world.ray_cast(p+offset-FWD*30,FWD,29.98)[0]is None for offset in [Vector((0,-.13,.16)),Vector((.13,0,.16)),Vector((0,0,.28))])
  if visible<2:continue
  candidates.append(p)
assert len(candidates)>2,'No clear visible water locations';selected=[]
for preferred in [Vector((6.8,-1.0,.635)),Vector((9.2,-2.0,.635))]:
 possible=[p for p in candidates if all((p-q).length>1.05 for q in selected)];assert possible;p=min(possible,key=lambda q:(q-preferred).length);selected.append(p)
col=bpy.data.collections['05_Water_Garden'];wood=bpy.data.materials['Cut wood edges'];cube=bpy.data.meshes.new('CP12 shared lamp frame cube');cube.from_pydata([(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),(-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)],[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);cube.materials.append(wood);cube.update()
def box(name,parent,p,scale):
 o=bpy.data.objects.new(name,cube);col.objects.link(o);o.parent=parent;o.location=p;o.scale=scale;return o
for i,p in enumerate(selected):
 root=bpy.data.objects.new('CP12_floating_paper_lantern_'+str(i),None);col.objects.link(root);root.location=p;root.rotation_euler.z=.18 if i==0 else-.14;eid='water_lantern.pond_paper_lantern_'+str(i);root['decision_entity_id']=eid;root['decision_kind']='water_lantern';root['decision_actions']=json.dumps(['drift_to','moor','set_brightness','extinguish','relight']);root['decision_status']='authoring_only_runtime_unimplemented';root['decision_actuation']='water_constrained_root_and_emission'
 mat=bpy.data.materials['Washi | pale edge'].copy();mat.name='CP12 glowing water-lantern paper '+str(i);bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.95,.66,.30,1);bs.inputs['Emission Color'].default_value=(1,.44,.09,1);bs.inputs['Emission Strength'].default_value=2.6;bs.inputs['Roughness'].default_value=.86
 box('CP12 floating lamp tray '+str(i),root,(0,0,.002),(.34,.34,.035))
 for x in [-.135,.135]:
  for y in [-.135,.135]:box('CP12 lamp corner post',root,(x,y,.15),(.012,.012,.28))
 for sign in [-1,1]:
  box('CP12 lamp top frame',root,(0,sign*.135,.286),(.29,.012,.012));box('CP12 lamp top frame',root,(sign*.135,0,.286),(.012,.29,.012))
  for axis in [0,1]:
   pts=[(-.12,sign*.13,.035),(.12,sign*.13,.035),(.12,sign*.13,.275),(-.12,sign*.13,.275),(0,sign*.138,.155)]
   if axis==1:pts=[(y,x,z)for x,y,z in pts]
   me=bpy.data.meshes.new('CP12 folded lamp paper');me.from_pydata(pts,[],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)]);me.materials.append(mat);me.update();o=bpy.data.objects.new('CP12 folded lamp paper',me);col.objects.link(o);o.parent=root
 d=bpy.data.lights.new('CP12 water-lantern spill '+str(i),'POINT');d.energy=1.6;d.color=(1,.47,.14);d.shadow_soft_size=.11;o=bpy.data.objects.new(d.name,d);bpy.data.collections['10_Lighting'].objects.link(o);o.parent=root;o.location=(0,-.19,.13);o['decision_owner']=eid;o['lighting_role']='Small warm light attached to its floating paper lantern'
 reg['entities'].append({'id':eid,'label':root.name,'kind':'water_lantern','blender_object':root.name,'position':list(p),'parent_entity':None,'parts':[],'actions':actions(['drift_to','moor','set_brightness','extinguish','relight']),'actuation':'water_constrained_root_and_emission','state':{'activity':'floating','brightness':'medium'},'material_bindings':[mat.name],'brightness_levels':{'off':0,'low':.7,'medium':2.6,'high':3.8},'anchors':[],'constraints':['Inside the validated water region','Avoid boat, animals, lilies, banks and rail corridor','Current placement checked; drift trajectories not implemented'],'runtime_ready':False,'requires_animation_binding':False})
bpy.context.view_layer.update()
for me in bpy.data.meshes:
 if not me.users or not me.polygons or me.uv_layers:continue
 uv=me.uv_layers.new(name='UVMap')
 for poly in me.polygons:
  axes=[j for j in range(3)if j!=max(range(3),key=lambda j:abs(poly.normal[j]))]
  for li in poly.loop_indices:v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*2,v[axes[1]]*2)
reg['source_checkpoint']='CP12';reg['entity_count']=len(reg['entities']);reg['parts_count']=sum(len(e['parts'])for e in reg['entities']);reg['cp12_new_entity_ids']=sorted({e['id']for e in reg['entities']}-before_ids);reg['unimplemented']=list(dict.fromkeys(reg.get('unimplemented',[])+['bird flap/flight animation','star twinkle executor','floating lantern drift simulation']))
(OUT/'decision-entities.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));notes={'scope':'Brighter overall environment retaining CP11 local structure; readable rain bridge; two floating paper lights; five independent glowing paper stars; six wing control pivots','source_geometry':'CP11 with only two added floating lanterns; existing wing triangles split without shape change','stars':[o.name for o in stars],'bird_wing_changes':wing_changes,'water_lantern_positions':[list(p)for p in selected],'water_lantern_candidate_count':len(candidates),'water_placement_method':'Actual pond corner support, .31 obstacle sphere clearance, main-camera sightlines and conservative rail-body exclusion margin .44','new_entities':reg['cp12_new_entity_ids'],'entity_count':reg['entity_count'],'parts_count':reg['parts_count'],'runtime_implemented':False};(OUT/'revision-record.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2));s['checkpoint']='CP12 global readability, local rain and controllable paper lights';s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100;bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'variant-C.blend'));print('CP12_C_READY',json.dumps(notes),flush=True)
# Two draft views, from the unchanged main camera and CP11 water-detail framing.
main=s.camera;s.cycles.samples=24;s.render.resolution_x=1100;s.render.resolution_y=619;s.render.filepath=str(WORK/'variant-C-overview.png');bpy.ops.render.render(write_still=True)
focus=(bpy.data.objects['greenhouse'].matrix_world.translation+bpy.data.objects['pond_boat'].matrix_world.translation)/2+Vector((0,0,.85));d=bpy.data.cameras.new('CP12 C draft water');d.type='ORTHO';d.ortho_scale=8.8;c=bpy.data.objects.new(d.name,d);s.collection.objects.link(c);c.rotation_euler=main.rotation_euler;c.location=focus-FWD*30;s.camera=c;s.render.resolution_x=1000;s.render.resolution_y=786;s.render.filepath=str(WORK/'variant-C-water.png');bpy.ops.render.render(write_still=True);print('CP12_C_DRAFTS_READY',flush=True)
