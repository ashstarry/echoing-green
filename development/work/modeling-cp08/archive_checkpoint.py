from pathlib import Path
import json,hashlib,zipfile,shutil,datetime,re
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-08';WORK=ROOT/'work/modeling-cp08'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((OUT/'validation.json').read_text())['passed'];assert json.loads((OUT/'web-asset-validation.json').read_text())['passed'];assert json.loads((OUT/'review-validation.json').read_text())['passed'];rt=json.loads((OUT/'glb-roundtrip-check.json').read_text());assert rt['passed'];assert rt['glb_sha256']==digest(OUT/'borrowed-wind-town-cp08-web.glb');assert rt['source_model_sha256']==digest(OUT/'borrowed-wind-town-cp08.blend')
for name in ['01-overview.png','02-plaza.png','03-garden-water.png','04-station.png','05-terrace.png','06-plan.png','07-glb-roundtrip.png','reference/cp07-plaza.png']:assert(OUT/name).stat().st_size>10000
for p in WORK.glob('*.py'):shutil.copy2(p,OUT/'source'/p.name)
shutil.copy2(ROOT/'AGENTS.md',OUT/'source/AGENTS-at-delivery.txt')
for p in OUT.glob('*.blend1'):shutil.move(str(p),str(WORK/('backup-'+p.name)))
for p in OUT.rglob('*'):
 if p.is_file() and p.suffix in ['.json','.txt','.py','.html','.js']:
  txt=p.read_text();assert not re.search(r'sk-or-v1-[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,}',txt),'Credential-like value found in '+str(p)
files=[p for p in OUT.rglob('*') if p.is_file() and p.name!='file-manifest.json'];manifest={p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(files)};(OUT/'file-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
archive=ROOT/'outputs/\u501f\u98ce\u753a-\u5efa\u6a21\u68c0\u67e5\u70b9-CP08.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(OUT.rglob('*')):
  if p.is_file():z.write(p,'modeling-checkpoint-08/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name,row in manifest.items():assert hashlib.sha256(z.read('modeling-checkpoint-08/'+name)).hexdigest()==row['sha256']
now=datetime.datetime.now(ZoneInfo('America/Los_Angeles')).isoformat();verify={'created_local':now,'archive':str(archive.relative_to(ROOT)),'sha256':digest(archive),'bytes':archive.stat().st_size,'file_count':len(manifest)+1,'zip_crc_passed':True,'per_file_sha256_passed':True,'source_model_reopened':True,'glb_decoded_and_reimported':True,'entity_and_part_bindings_verified':True,'api_integration_implemented':False,'browser_fps_measured':False,'cloud_upload':False};(ROOT/'outputs/\u501f\u98ce\u753a-\u5efa\u6a21\u68c0\u67e5\u70b9-CP08-\u5f52\u6863\u6821\u9a8c.json').write_text(json.dumps(verify,ensure_ascii=False,indent=2))
latest=ROOT/'outputs/experiment-archive/LATEST.json';data=json.loads(latest.read_text());entry={'date':'2026-10-25','created_local':now,'type':'CP08 reference spatial/ecosystem revision and Decision-addressable asset contract','archive':str(archive.relative_to(ROOT)),'sha256':verify['sha256'],'bytes':verify['bytes'],'verified':True,'model_reopened_and_validated':True,'glb_decoded_and_reimported':True,'entities':168,'movable_parts':69,'browser_visual_qa':False,'browser_fps_measured':False,'status':'Awaiting art review; authoring bindings verified, no API integration, character rigging or runtime'};data.setdefault('addenda',[]);data['addenda']=[x for x in data['addenda'] if x.get('archive')!=entry['archive']]+[entry];latest.write_text(json.dumps(data,ensure_ascii=False,indent=2))
index=ROOT/'outputs/experiment-archive/\u5b9e\u9a8c\u6863\u6848\u7d22\u5f15.txt';marker='CP08 \xb7 \u6d3b\u52a8\u7a7a\u95f4\u3001\u751f\u6001\u4e0e Decision \u5bf9\u8c61\u7ed3\u6784'
if marker not in index.read_text():
 with index.open('a') as f:f.write('\n\n'+marker+'\n2026-10-25\uff1a\u7528\u6237\u8981\u6c42\u758f\u5f00\u5916\u5708\u82b1\u5e26\u3001\u6062\u590d\u4e2d\u592e\u6d3b\u52a8\u533a\uff0c\u589e\u52a0\u5c45\u6c11\u548c\u6e29\u5ba4/\u6c60\u5858\u7ec6\u8282\uff0c\u5e76\u786e\u4fdd\u53ef\u52a8\u5bf9\u8c61\u53ef\u63a5\u5165 Decision\u3002CP08 \u4fdd\u7559\u56fa\u5b9a\u4e3b\u955c\u5934\u4e0e\u5b8c\u6574\u5c4b\u9876\uff0c\u91cd\u505a\u4f4e\u6d45\u8f66\u7ad9\u4e0e\u4e2d\u592e\u805a\u96c6\u533a\uff0c\u670930\u4eba\u7269\u4e0e9\u52a8\u7269/\u7eb8\u9e1f/\u9c7c\u3002168\u903b\u8f91\u5b9e\u4f53\u300169\u53ef\u52a8\u90e8\u4ef6\u7684ID/\u7236\u5b50\u5173\u7cfb/\u63a7\u5236\u8f74\u5728\u6bcd\u7248\u548cGLB\u4e2d\u6838\u5bf9\uff1b\u4e0d\u7b49\u4e8eAPI\u6216\u52a8\u4f5c\u7cfb\u7edf\u5df2\u5b9e\u73b0\u3002\u4e2d\u592e\u9759\u6001\u91c7\u6837\u4e0e\u5b9e\u9645\u8fd1\u666f\u5bf9\u7167\u4fdd\u5b58\u3002\u9762\u6570\u7ea640.9\u4e07\uff0cGLB\u7ea610.38MB\uff1b\u672a\u6d4b\u6d4f\u89c8\u5668\u5e27\u7387\u3002\u539f407\u6b21\u6a21\u578b\u5b9e\u9a8c\u4e0e\u8d39\u7528\u6570\u636e\u672a\u6539\u3002\n\u4ea4\u4ed8\uff1aoutputs/modeling-checkpoint-08/review.html\n\u5f52\u6863\uff1a'+entry['archive']+'\nSHA256\uff1a'+verify['sha256']+'\n\u6821\u9a8c\uff1aoutputs/\u501f\u98ce\u753a-\u5efa\u6a21\u68c0\u67e5\u70b9-CP08-\u5f52\u6863\u6821\u9a8c.json\uff0cCRC\u53ca\u9010\u6587\u4ef6SHA256\u901a\u8fc7\uff0c\u4ec5\u672c\u5730\u4fdd\u5b58\u3002\n')
print(json.dumps(verify,ensure_ascii=False,indent=2))
