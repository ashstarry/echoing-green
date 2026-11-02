import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'work/lighting-cp11';s=bpy.context.scene
for node in s.compositing_node_group.nodes:
 if node.bl_idname=='CompositorNodeGlare':node.inputs['Threshold'].default_value=1.3;node.inputs['Strength'].default_value=.18;node.inputs['Size'].default_value=.23
s['checkpoint']='CP11 lighting refinement D';s.render.resolution_x=1100;s.render.resolution_y=619;s.render.resolution_percentage=100;s.cycles.samples=32;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.render.filepath=str(WORK/'variant-D.png');bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'variant-D.blend'));bpy.ops.render.render(write_still=True);r=json.loads((WORK/'variant-C-record.json').read_text());r['variant']='D';r['refinement']+='; localized glow threshold/strength/size 1.3/.18/.23';(WORK/'variant-D-record.json').write_text(json.dumps(r,indent=2));print('VARIANT_D_READY',flush=True)
