import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path.cwd();A=R/'app/runtime-cp19/public/assets';O=R/'outputs/runtime-checkpoint-19';s=bpy.context.scene;reg=json.loads((A/'runtime-registry.json').read_text());tea=bpy.data.objects['tea_house'];C=bpy.data.collections.new('19_CP19_INTERIOR');s.collection.children.link(C)
def mat(name,color,emission=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.9
 if emission:p.inputs['Emission Color'].default_value=(.8,.28,.07,1);p.inputs['Emission Strength'].default_value=emission
 return m
amber=mat('CP19 warm inner shoji',(.40,.23,.10),.12);wood=mat('CP19 cedar screens',(.12,.056,.025));cloth=mat('CP19 inner indigo cloth',(.075,.15,.19));cream=mat('CP19 soft paper pages',(.65,.58,.43));green=mat('CP19 garden-can folded sage',(.20,.34,.25));red=mat('CP19 book vermilion',(.34,.085,.045))
def cube(name,parent,pos,size,material):
 me=bpy.data.meshes['Shared cube'].copy();o=bpy.data.objects.new(name,me);C.objects.link(o);o.parent=parent;o.location=pos;o.scale=size;me.materials.clear();me.materials.append(material);return o
# A real folded partition behind the two passage envelopes: no fake resident silhouettes.
for j,(x,w,depth)in enumerate([(-1.9,1.45,.24),(-.25,1.75,.36),(1.55,1.75,.23)]):
 cube('CP19 warm rear shoji '+str(j),tea,(x,depth,3.05),(w,.035,1.58),amber)
 for dx in [-w/2,0,w/2]:cube('CP19 screen cedar upright',tea,(x+dx,depth-.03,3.05),(.025,.045,1.62),wood)
 for z in [2.27,2.80,3.32,3.84]:cube('CP19 screen cross bar',tea,(x,depth-.034,z),(w+.04,.045,.022),wood)
cube('CP19 side folding screen',tea,(-2.65,-.12,2.93),(.04,.68,1.38),cloth)
cube('CP19 deep tea sideboard',tea,(-.35,-.06,2.55),(.72,.32,.60),wood)
cube('CP19 sideboard top',tea,(-.35,-.06,2.87),(.80,.38,.045),cream)
for x in [-.55,-.30,-.06]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.055,depth=.09);o=bpy.context.object;o.name='CP19 inner tea cup';o.parent=tea;o.location=(x,-.08,2.94);o.data.materials.append(cream)
# Tangible, low-complexity props for a readable seated and gardening intent.
def attach(id,name,owner,position,kind):
 actor=bpy.data.objects[next(e['blender_object']for e in reg['entities']if e['id']==owner)];root=bpy.data.objects.new(name,None);C.objects.link(root);root.parent=actor;root.location=position;root['decision_entity_id']=id;root['decision_kind']=kind
 reg['entities'].append({'id':id,'label':name,'kind':kind,'blender_object':name,'position':[0,0,0],'actions':[{'id':'read'if kind=='book'else'water_plants','implementation':'bounded owner activity'}],'parts':[],'state':{'owner':owner},'parent_entity':owner,'anchors':[],'runtime_binding_status':'owner_driven','executable_modes':['read_prop'if kind=='book'else'hand_attached_pour']});return root,actor
book,reader=attach('book.terrace_reader_book','CP19 terrace reading book','resident.quiet_reader',(0,-.29,.61),'book')
cube('CP19 book cover',book,(0,0,0),(.30,.20,.025),red)
for side in [-1,1]:
 o=cube('CP19 book folded pages',book,(side*.073,0,.024),(.142,.18,.022),cream);o.rotation_euler.y=side*.10
can,gardener=attach('watering_can.garden_can','CP19 small garden watering can','resident.gardener',(.28,-.04,.72),'watering_can')
bpy.context.view_layer.update();arm=bpy.data.objects['gardener__anim_arm_right'];mw=can.matrix_world.copy();can.parent=arm;can.matrix_world=mw
cube('CP19 watering can paper body',can,(0,-.04,-.16),(.19,.16,.18),green)
# Box spout and a small open square handle retain the cut-paper construction.
o=cube('CP19 watering can spout',can,(0,-.20,-.09),(.045,.23,.045),green);o.rotation_euler.x=-.25
for x in [-.07,.07]:cube('CP19 can handle upright',can,(x,0,-.02),(.018,.028,.16),wood)
cube('CP19 can handle top',can,(0,0,.06),(.16,.028,.018),wood)
bpy.context.view_layer.update()
for e in reg['entities']:e['position']=list(bpy.data.objects[e['blender_object']].matrix_world.translation)
(A/'runtime-registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp19/town-runtime.blend'));(O/'interior-authoring.json').write_text(json.dumps({'full_roof_retained':True,'rear_screen_tea_local_y':[.23,.24,.36],'hidden_endpoint_tea_local_y_approx':-.45,'new_props':['book.terrace_reader_book','watering_can.garden_can'],'note':'Actual low-poly room screens and sideboard; all new movement still needs browser collision verification.'},indent=2));print('INTERIOR_READY')
