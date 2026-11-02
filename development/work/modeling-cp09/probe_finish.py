import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];s=bpy.context.scene;bank=bpy.data.objects['CP09_rear_flower_bank'];land=bpy.data.objects['Island paper layer 4'];inv=land.matrix_world.inverted();rows=[]
for x in [-2.05,0,2.05]:
 for y in [-.27,.27]:
  p=bank.matrix_world@Vector((x,y,0));h,lo,n,i=land.ray_cast(inv@(p+Vector((0,0,.05))),(inv.to_3x3()@Vector((0,0,-1))).normalized(),distance=5);rows.append({'point':list(p),'ground_found':h,'ground_z':(land.matrix_world@lo).z if h else None})
data={'rear_bank_support':rows,'scene_compositor_properties':[p.identifier for p in bpy.types.Scene.bl_rna.properties if 'composit' in p.identifier or 'node' in p.identifier],'has_node_tree':hasattr(s,'node_tree'),'has_use_nodes':hasattr(s,'use_nodes'),'has_compositing_node_group':hasattr(s,'compositing_node_group')}
for name in ['CompositorNodeGlare','CompositorNodeComposite','CompositorNodeRLayers']:
 try:data[name]=getattr(bpy.types,name).bl_rna.description
 except Exception as e:data[name]=str(e)
(ROOT/'work/modeling-cp09/finish-probe.json').write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))
