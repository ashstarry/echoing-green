import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path.cwd();A=R/'app/runtime-cp18/public/assets';O=R/'outputs/runtime-checkpoint-18';ps=[Vector(p)for p in json.loads((A/'rail-path.json').read_text())['points']];N=len(ps);o=bpy.data.objects['CP02 bridge landing east'];M=o.matrix_world.copy();corners=[M@Vector((x,y,0))for x,y in [(-.5,-.5),(.5,-.5),(.5,.5),(-.5,.5)]];poly=[p.xy for p in corners];original=[list(p)for p in poly];center=o.matrix_world.translation
for i,p in enumerate(ps):
 if (p.xy-center.xy).length>1.7:continue
 t=(ps[(i+1)%N]-ps[(i-1)%N]).normalized();normal=Vector((t.y,-t.x));offset=p.xy-normal*.55;out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=(a-offset).dot(normal);db=(b-offset).dot(normal)
  if da<=0:out.append(a)
  if (da<0<db)or(db<0<da):out.append(a+(b-a)*(da/(da-db)))
 poly=out
assert len(poly)>=3
zlo=center.z-.1;zhi=center.z+.1;v=[(p.x,p.y,z)for z in [zlo,zhi]for p in poly];n=len(poly);f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];me=bpy.data.meshes.new('CP18 bridge landing fitted to moving wheels');me.from_pydata(v,[],f);me.update()
for m in o.data.materials:me.materials.append(m)
o.data=me;o.matrix_world=Matrix.Identity(4)
changes=[]
for name,factor in [('CP02 restrained flower bed leaf.101',.62),('CP02 restrained flower bed leaf.012',.62),('CP02 street planter 15 leaf.002',.70)]:
 obj=bpy.data.objects[name];obj.scale*=factor;changes.append({'object':name,'scale_factor':factor,'component_retained':True})
(O/'local-motion-clearance-edits.json').write_text(json.dumps({'bridge_landing_before':original,'bridge_landing_after':[list(p)for p in poly],'small_leaf_adjustments':changes,'core_buildings_unchanged':True},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'work/runtime-cp18/town-runtime.blend'));print('LOCAL_CLEARANCE_EDITED',len(poly))
