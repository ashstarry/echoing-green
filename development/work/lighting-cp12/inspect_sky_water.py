import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'work/lighting-cp12';s=bpy.context.scene;rows=[]
for o in s.objects:
 if o.name.startswith('Paper star')or o.get('decision_kind')in ['bird','boat','fish']or o.name.startswith(('water_lily_','duck_'))or o.name=='CP02 pond':
  row={'name':o.name,'type':o.type,'position':list(o.matrix_world.translation),'dimensions':list(o.dimensions),'parent':o.parent.name if o.parent else None,'kind':o.get('decision_kind'),'children':[]}
  for ch in o.children_recursive:
   if ch.type=='MESH':row['children'].append({'name':ch.name,'vertices':len(ch.data.vertices),'faces':len(ch.data.polygons),'position':list(ch.matrix_world.translation),'materials':[x.material.name if x.material else None for x in ch.material_slots]})
  if o.type=='MESH':row['mesh_vertices']=[list(o.matrix_world@p.co)for p in o.data.vertices];row['faces']=len(o.data.polygons);row['materials']=[x.material.name if x.material else None for x in o.material_slots]
  rows.append(row)
(WORK/'sky-water-inspection.json').write_text(json.dumps(rows,indent=2));print('SKY_WATER_INSPECTION',[(r['name'],r.get('faces'),len(r['children']))for r in rows],flush=True)
