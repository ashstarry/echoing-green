import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'work/art-cp13';s=bpy.context.scene;tea=bpy.data.objects['tea_house'];inv=tea.matrix_world.inverted();rows=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE','EMPTY']:continue
 is_tea=o==tea or o in tea.children_recursive
 if is_tea:
  box=[inv@o.matrix_world@__import__('mathutils').Vector(v)for v in o.bound_box]if o.type!='EMPTY'else[]
  if box and max(v.z for v in box)<1.85:continue
  rows.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'local_position':list(inv@o.matrix_world.translation),'bounds':[[min(v[i]for v in box),max(v[i]for v in box)]for i in range(3)]if box else [],'material':[m.material.name if m.material else ''for m in o.material_slots]if o.type!='EMPTY'else [],'id':o.get('decision_entity_id')})
sky=[]
for o in s.objects:
 if o.name.startswith(('Paper star','Paper crescent','Moon','paper_bird','Bird paper','CP12 paper_bird')):
  sky.append({'name':o.name,'type':o.type,'matrix':[list(r)for r in o.matrix_world],'parent':o.parent.name if o.parent else None,'vertices':[list(v.co)for v in o.data.vertices]if o.type=='MESH'else[],'faces':[list(p.vertices)for p in o.data.polygons]if o.type=='MESH'else[],'materials':[m.material.name if m.material else ''for m in o.material_slots]if o.type=='MESH'else[]})
materials={}
for m in bpy.data.materials:
 if any(k in m.name.lower()for k in ['shoji','lantern','moon']):
  p=m.node_tree.nodes.get('Principled BSDF')if m.use_nodes else None
  if p:materials[m.name]={k:list(p.inputs[k].default_value)if k.endswith('Color')else p.inputs[k].default_value for k in ['Base Color','Emission Color','Emission Strength']}
data={'tea_world':[list(r)for r in tea.matrix_world],'tea':rows,'sky':sky,'materials_cp12':materials};bpy.ops.wm.open_mainfile(filepath=str(ROOT/'outputs/modeling-checkpoint-10/borrowed-wind-town-cp10.blend'));old={}
for name in materials:
 m=bpy.data.materials.get(name)
 if m and m.use_nodes:
  p=m.node_tree.nodes.get('Principled BSDF')
  if p:old[name]={k:list(p.inputs[k].default_value)if k.endswith('Color')else p.inputs[k].default_value for k in ['Base Color','Emission Color','Emission Strength']}
data['materials_cp10']=old;(W/'inspection.json').write_text(json.dumps(data,indent=2));print('INSPECTION_READY',len(rows),len(sky))
