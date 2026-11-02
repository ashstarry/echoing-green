import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'work/art-cp13';OUT=ROOT/'outputs/art-checkpoint-13';s=bpy.context.scene;tea=bpy.data.objects['tea_house'];col=bpy.data.collections['02_Teahouse_Market'];rec=json.loads((OUT/'revision-record.json').read_text())
# Protect the colored paper skin from being washed out by nearby area/point fills.
for name,base,energy,emit in [('Lantern | gentle amber',(.62,.19,.018),1.10,(1,.27,.022)),('CP05 shaded restaurant lantern paper',(.52,.145,.013),.68,(1,.24,.016))]:
 p=bpy.data.materials[name].node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*base,1);p.inputs['Emission Strength'].default_value=energy;p.inputs['Emission Color'].default_value=(*emit,1)
for o in s.objects:
 if o.type=='LIGHT'and o.name.startswith('CP11 lamp spill | hanging_light_cp05_restaurant'):o.data.energy=1.6
for name,base,energy in [('CP13 crescent paper folds',(.94,.56,.22),.59),('CP13 crescent cut edge',(.60,.30,.08),.31)]:
 p=bpy.data.materials[name].node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*base,1);p.inputs['Emission Color'].default_value=(1,.45,.10,1);p.inputs['Emission Strength'].default_value=energy
# Two short folded fabrics hang outside the rail, leaving the balcony floor untouched.
for k,(x,material)in enumerate([(-1.30,'CP13 indigo textile'),(1.30,'CP13 russet textile')]):
 vs=[]
 for j in range(5):
  xx=x-.25+j*.125;y=-1.835+(.025 if j%2 else 0);vs.extend([(xx,y,2.85),(xx,y-.015,2.47+(.015 if j%2 else 0))])
 fs=[(2*j,2*j+1,2*j+3,2*j+2)for j in range(4)];me=bpy.data.meshes.new('CP13 folded balcony cloth');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials[material]);me.update();o=bpy.data.objects.new('CP13 folded balcony cloth '+str(k),me);col.objects.link(o);o.parent=tea;o.modifiers.new('Fine paper thickness','SOLIDIFY').thickness=.006;rec['added'].append(o.name)
 # One small folded-leaf motif, modeled rather than lettering or a texture billboard.
 verts=[(x,-1.855,2.72),(x-.075,-1.855,2.64),(x,-1.87,2.58),(x+.075,-1.855,2.64),(x,-1.89,2.65)];faces=[(0,1,4),(1,2,4),(2,3,4),(3,0,4)];me=bpy.data.meshes.new('CP13 tea-leaf cloth crest');me.from_pydata(verts,[],faces);me.materials.append(bpy.data.materials['Washi | pale edge']);me.update();o=bpy.data.objects.new('CP13 tea-leaf cloth crest '+str(k),me);col.objects.link(o);o.parent=tea;rec['added'].append(o.name)
for me in bpy.data.meshes:
 if not me.users or not me.polygons or me.uv_layers:continue
 uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  for li in p.loop_indices:v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.z)
rec['art_refinement']='Lower lantern paper albedo/near-lamp spill to preserve orange saturation; subtle crescent folds; two cloth/leaf accents hung outside rail, no floor props.';(OUT/'revision-record.json').write_text(json.dumps(rec,indent=2));s.render.resolution_x=1672;s.render.resolution_y=941;s.cycles.samples=80;s.render.filepath=str(OUT/'01-overview.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp13.blend'))
s.render.resolution_x=1200;s.render.resolution_y=675;s.cycles.samples=28;s.render.filepath=str(W/'refined-overview.png');bpy.ops.render.render(write_still=True);print('CP13_REFINED_READY',flush=True)
