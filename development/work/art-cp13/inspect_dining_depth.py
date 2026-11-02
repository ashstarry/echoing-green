import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'work/art-cp13';s=bpy.context.scene;tea=bpy.data.objects['tea_house'];dg=bpy.context.evaluated_depsgraph_get();out=[]
for x in [-1.3,0,1.3]:
 for z in [2.6,2.9,3.1]:
  pos=tea.matrix_world@Vector((x,-1.32,z));di=(tea.matrix_world.to_3x3()@Vector((0,1,0))).normalized();hit,p,n,idx,obj,ma=s.ray_cast(dg,pos,di,distance=5);out.append({'x':x,'z':z,'hit':obj.name if obj else None,'tea_local_hit':list(tea.matrix_world.inverted()@p)if hit else None})
print(json.dumps(out,indent=2));(W/'dining-depth-rays.json').write_text(json.dumps(out,indent=2))
m=bpy.data.materials['Cedar frame'].copy();m.name='CP13 dining alcove dark cedar';p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.16,.072,.029,1);p.inputs['Roughness'].default_value=.88;p.inputs['Emission Strength'].default_value=0
for name in ['CP06 upper back wall','CP06 upper west wall']:
 o=bpy.data.objects[name];o.material_slots[0].link='OBJECT';o.material_slots[0].material=m
main=s.camera;f=main.rotation_euler.to_quaternion()@Vector((0,0,-1));d=bpy.data.cameras.new('CP13 depth test');d.type='ORTHO';d.ortho_scale=8.1;c=bpy.data.objects.new(d.name,d);s.collection.objects.link(c);c.rotation_euler=main.rotation_euler;c.location=tea.matrix_world@Vector((0,-1.05,2.02))-f*30;s.camera=c;s.render.resolution_x=900;s.render.resolution_y=665;s.cycles.samples=24;s.render.filepath=str(W/'depth-test.png');bpy.ops.render.render(write_still=True)
