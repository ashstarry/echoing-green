exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
import sys
dg=bpy.context.evaluated_depsgraph_get();rows=[]
def own(o,root):
 while o:
  if o==root:return True
  o=o.parent
 return False
for root in s.objects:
 if root.get('decision_kind')!='resident':continue
 for o in root.children_recursive:
  if o.type!='MESH'or not o.name.startswith(('Shoe','Head','Hand','Coat body','CP07 guitar body','CP09 cyclist shoe','CP09 open grip hand')):continue
  ps=[o.matrix_world@v.co for v in o.data.vertices];p=sum(ps,Vector())/len(ps);hit,loc,n,i,block,ma=s.ray_cast(dg,p-FWD*30,FWD,distance=30.01);rows.append({'actor':root.name,'component':o.name,'visible':bool(block and own(block,root)),'blocker':block.name if block else None})
baseline='--baseline'in sys.argv;p=WORK/'cp09-actor-readability.json'if baseline else OUT/'actor-readability.json';p.write_text(json.dumps({'samples':rows,'scope':'Actual component-center visibility samples, supplemental visual evidence only, not collision validation.'},indent=2));print('ACTOR_VISIBILITY',sum(x['visible']for x in rows),'/',len(rows),flush=True)
