import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'work/art-cp14';OUT=ROOT/'outputs/art-checkpoint-14';s=bpy.context.scene;tea=bpy.data.objects['tea_house'];inv=tea.matrix_world.inverted();rec=json.loads((OUT/'revision-record.json').read_text())
for o in tea.children:
 if o.name.startswith('Awning'):o.location.z+=.19
bpy.context.view_layer.update()
for o in tea.children:
 if o.name.startswith('Awning folded stripe'):
  o.data=o.data.copy();back=o.matrix_world.inverted()@tea.matrix_world
  for v in o.data.vertices:
   p=inv@o.matrix_world@v.co;t=max(0,min(1,(p.y+2.0461)/.7922));p.z-=.067*t;v.co=back@p
  o.data.update()
rec['headroom_revision']['awning_shift_local']=0;rec['headroom_revision']['awning_back_edge_lowered_local']=.067;rec['headroom_revision']['awning_note']='Original front edge/bar stays at CP13 height so ground-floor heads remain visible; only rising back tips are lowered below the upper walking surface.'
(OUT/'revision-record.json').write_text(json.dumps(rec,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(W/'ready-final.blend'));print('CP14_AWNING_REFINED')
