import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/art-checkpoint-16';s=bpy.context.scene
s['checkpoint']='CP16 | lower upper-story proportions and central tea-service cabinet';s['review_status']='Awaiting art review; same two-goal upper diner contract; no animation/runtime';s.cycles.samples=80;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=5;s.render.resolution_x=1672;s.render.resolution_y=941;s.render.resolution_percentage=100;s.render.filepath=str(OUT/'01-overview.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp16.blend'));print('CP16_MASTER_SAVED')
