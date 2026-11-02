exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
rec=json.loads((OUT/'revision-record.json').read_text())
def move(o,d):
 f=o.parent.matrix_world@o.matrix_parent_inverse if o.parent else Matrix.Identity(4);o.location+=f.to_3x3().inverted()@Vector(d)
def place(o,p):move(o,Vector(p)-o.matrix_world.translation);bpy.context.view_layer.update()
# The rear bank follows actual supported island ground, rather than a floating rectangle.
land=bpy.data.objects['Island paper layer 4'];inv=land.matrix_world.inverted();outline=[];support=[]
for r,b in [(2.50,6.95),(4.95,6.85),(4.80,7.20),(4.15,7.45),(2.50,7.65)]:
 for _ in range(20):
  p=rb(r,b,.66);h,lo,n,i=land.ray_cast(inv@p,(inv.to_3x3()@Vector((0,0,-1))).normalized(),distance=2)
  if h:break
  b-=.05
 assert h
 z=(land.matrix_world@lo).z;outline.append(rb(r,b,z-.008));support.append({'right_back':[r,b],'ground_z':z})
bank=bpy.data.objects['CP09_rear_flower_bank']
for name in [o.name for o in bank.children_recursive]:
 o=bpy.data.objects.get(name)
 if o:erase(o)
bank.matrix_world=Matrix.Identity(4);COL=cols['06_Hillside'];n=len(outline)
with under(bank):
 v=[tuple(p) for p in outline]+[(p.x,p.y,1.81) for p in outline];f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];mesh('CP09 grounded rear garden bank',v,f,terr[3])
 v=[(p.x,p.y,z) for z in [1.81,1.84] for p in outline];mesh('CP09 supported rear garden soil',v,f,sage)
place(bpy.data.objects['terrace_sakura_1'],rb(4.28,7.18,1.84));shrub=bpy.data.objects['terrace_sakura_2'];shrub.scale=(.55,.55,.48);place(shrub,rb(6.32,6.62,2.072))
pot=asset('CP09 terrace sakura planter',rb(6.32,6.62,1.872))
with under(pot):
 taper('CP09 terrace flower pot',(0,0,0),(0,0,.20),.155,.19,woodlight,8);cyl('CP09 terrace pot soil',(0,0,.198),.173,.012,sage)
place(bpy.data.objects['terrace_garden_lantern_3'],rb(5.95,6.78,1.874));place(bpy.data.objects['terrace_garden_lantern_4'],rb(6.15,5.80,1.874))
# Keep the roofs indigo under stronger warm fill, so the town does not become uniformly bright.
for mat,c in [(navy,(.026,.048,.13)),(navy2,(.049,.078,.18)),(navy3,(.067,.105,.22))]:
 mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);mat.diffuse_color=(*c,1)
# Blender 5 compositor group: restrained fog glow on the brightest light sources.
nt=bpy.data.node_groups.new('CP09 restrained lantern glow','CompositorNodeTree');nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');rl=nt.nodes.new('CompositorNodeRLayers');gl=nt.nodes.new('CompositorNodeGlare');gl.inputs['Type'].default_value='Fog Glow';gl.inputs['Quality'].default_value='High';gl.inputs['Size'].default_value=.35;out=nt.nodes.new('NodeGroupOutput')
if hasattr(gl,'threshold'):gl.threshold=2.0
if hasattr(gl,'mix'):gl.mix=-.93
if hasattr(gl,'size'):gl.size=7
if gl.inputs.get('Threshold'):gl.inputs['Threshold'].default_value=2.0
if gl.inputs.get('Strength'):gl.inputs['Strength'].default_value=.10
nt.links.new(rl.outputs['Image'],gl.inputs['Image']);nt.links.new(gl.outputs['Image'],out.inputs['Image']);s.compositing_node_group=nt
rec['supported_rear_garden']={'supports':support,'outline_world':[list(p) for p in outline],'top_soil':1.84,'right_shrub':'Real planter on existing terrace at R6.32 B6.62; not on an unsupported extension'};rec['postprocessing']={'type':'Blender compositor fog glow','intent':'Restrained glow on bright lanterns','not_exported_to_glb':True,'node_inputs':[x.name for x in gl.inputs]};bpy.context.view_layer.update();(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));s['checkpoint']='CP09 | corrected contacts and warm paper town';bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'final-visual.blend'));print('CP09_FINISH_READY',flush=True)
