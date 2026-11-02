import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'work/lighting-cp11';exec(compile((WORK/'scene_signature.py').read_text(),'<signature>','exec'))
a=json.loads((WORK/'baseline-scene-signature.json').read_text());b=json.loads(json.dumps(scene_signature(bpy.context.scene)));diff=[]
for n in set(a['objects'])|set(b['objects']):
 if a['objects'].get(n)!=b['objects'].get(n):diff.append({'name':n,'differences':{k:[a['objects'].get(n,{}).get(k),b['objects'].get(n,{}).get(k)]for k in set(a['objects'].get(n,{}))|set(b['objects'].get(n,{}))if a['objects'].get(n,{}).get(k)!=b['objects'].get(n,{}).get(k)}})
print('NORMALIZED_EQUAL',a==b,'OBJECT_DIFFERENCES',json.dumps(diff[:20]),'COUNT',len(diff),'CAMERA',a['camera']==b['camera'],'COLLECTIONS',a['collections']==b['collections'],flush=True)
