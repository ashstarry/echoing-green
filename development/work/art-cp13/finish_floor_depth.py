import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/art-checkpoint-13';W=ROOT/'work/art-cp13';s=bpy.context.scene;o=bpy.data.objects['CP06 upper dining floor'];m=bpy.data.materials['Cut wood edges'].copy();m.name='CP13 dining floor cedar';p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.25,.11,.045,1);p.inputs['Roughness'].default_value=.89;o.material_slots[0].link='OBJECT';o.material_slots[0].material=m
# The camera sees the floor through these openings. Thin inset board seams make that depth legible.
dark=bpy.data.materials['Cedar frame'].copy();dark.name='CP13 floor seam';p=dark.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.065,.026,.01,1);tea=bpy.data.objects['tea_house'];col=bpy.data.collections['02_Teahouse_Market'];rec=json.loads((OUT/'revision-record.json').read_text());vs=[];fs=[]
for y in [-1.08,-.76,-.44,-.12,.20,.52,.84,1.16]:
 j=len(vs);vs.extend([(-2.59,y-.004,2.2555),(2.59,y-.004,2.2555),(2.59,y+.004,2.2555),(-2.59,y+.004,2.2555)]);fs.append((j,j+1,j+2,j+3))
me=bpy.data.meshes.new('CP13 subtle floor board seams');me.from_pydata(vs,[],fs);me.materials.append(dark);me.update();uv=me.uv_layers.new(name='UVMap')
for loop in me.loops:uv.data[loop.index].uv=me.vertices[loop.vertex_index].co.xy
n=bpy.data.objects.new('CP13 subtle floor board seams',me);col.objects.link(n);n.parent=tea;rec['added'].append(n.name);rec['floor_readability']='Camera rays showed the flat orange band was the upper floor, not a remaining wall. Floor changed to darker cedar with eight fine board seams, preserving its geometry and passage width.';(OUT/'revision-record.json').write_text(json.dumps(rec,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp13.blend'));print('CP13_FLOOR_DEPTH_SAVED')
