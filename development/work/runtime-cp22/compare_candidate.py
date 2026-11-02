import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path.cwd();W=R/'work/runtime-cp22';excluded={'tram.tram_car_front','resident.station_traveler'}
def signature():
 out={}
 for o in bpy.context.scene.objects:
  if o.type not in ['MESH','CURVE']:continue
  p=o;owner=None
  while p:
   if p.get('decision_entity_id'):owner=p.get('decision_entity_id');break
   p=p.parent
  if owner in excluded:continue
  if o.type=='MESH':v=[tuple(round(x,5)for x in (o.matrix_world@v.co))for v in o.data.vertices];f=[tuple(p.vertices)for p in o.data.polygons]
  else:v=[tuple(round(x,5)for x in row)for row in o.matrix_world];f=[(len(sp.points),len(sp.bezier_points))for sp in o.data.splines]
  out[o.name]=hashlib.sha256(repr((v,f,[m.name if m else None for m in o.data.materials])).encode()).hexdigest()
 return out
before=signature();bpy.ops.wm.open_mainfile(filepath=str(W/'boarding/town-boarding.blend'));after=signature();changed=[k for k in before if before[k]!=after.get(k)];missing=[k for k in before if k not in after];new=[k for k in after if k not in before];report={'passed':not changed and not missing and not new,'compared_objects':len(before),'authorized_changes':sorted(excluded),'unexpected_changed':changed,'unexpected_missing':missing,'unexpected_added':new};(R/'outputs/runtime-checkpoint-22/boarding-scope-check.json').write_text(json.dumps(report,indent=2));print(report);assert report['passed']
