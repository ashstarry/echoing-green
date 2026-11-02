from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,zipfile,struct
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-05';ZIP=ROOT/'outputs/借风町-建模检查点-CP05.zip';now=datetime.now(ZoneInfo('America/Los_Angeles'))
def sha(data):return hashlib.sha256(data).hexdigest()
assert json.loads((OUT/'validation.json').read_text())['passed']
check=json.loads((OUT/'review-static-check.json').read_text());check['javascript_syntax_check_passed']=True;(OUT/'review-static-check.json').write_text(json.dumps(check,ensure_ascii=False,indent=2))
manifest={}
for p in sorted(OUT.rglob('*')):
 if not p.is_file() or p.name in ['file-manifest.json','archive-verification.json']:continue
 assert p.suffix!='.blend1';data=p.read_bytes()
 if p.suffix in ['.py','.json','.txt','.html']:assert b'sk-or-v1-' not in data
 if p.suffix=='.png':
  assert data[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack('>II',data[16:24]);assert w>=1000 and h>=600
 manifest[str(p.relative_to(OUT))]={'sha256':sha(data),'bytes':len(data)}
(OUT/'file-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(OUT.rglob('*')):
  if p.is_file() and p.name!='archive-verification.json':z.write(p,arcname=str(Path(OUT.name)/p.relative_to(OUT)))
with zipfile.ZipFile(ZIP) as z:
 assert z.testzip() is None
 for name,entry in manifest.items():assert sha(z.read(OUT.name+'/'+name))==entry['sha256']
entry={'date':now.date().isoformat(),'created_local':now.isoformat(),'type':'CP05 broad restaurant facade and two-flight terrace','archive':str(ZIP.relative_to(ROOT)),'sha256':sha(ZIP.read_bytes()),'bytes':ZIP.stat().st_size,'verified':True,'model_reopened_and_validated':True,'browser_visual_qa':False,'status':'Stopped for user review; real modeling checkpoint, not final art or runtime'}
(OUT/'archive-verification.json').write_text(json.dumps({**entry,'verified_file_count':len(manifest),'zip_crc_passed':True,'roundtrip_sha256_passed':True,'credential_pattern_check_passed':True},ensure_ascii=False,indent=2))
latest=ROOT/'outputs/experiment-archive/LATEST.json';data=json.loads(latest.read_text());data.setdefault('addenda',[]).append(entry);latest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
index=ROOT/'outputs/experiment-archive/实验档案索引.txt'
with index.open('a') as f:f.write('\n'+now.date().isoformat()+' CP05 建模追加档案\n用户要求收回饭店过强的45°转角、强调长立面及外围装饰基础，并把右上露台改为两段式楼梯；其余核心元素已认可。CP05饭店水平转角25°，主镜头仍43°正交，其他所列核心对象变换及CP01–CP04哈希均保持。露台5级＋中间转折平台＋5级，完善支撑、住家衔接、座椅及边缘构件。24人物/7动物占位保留，24组头部/上半身中心视线及30踏面采样通过，非完整导航/动作验证。入口outputs/modeling-checkpoint-05/review.html；工程、真实渲染、参考和CP04对照、脚本与记录归档到outputs/借风町-建模检查点-CP05.zip，逐文件哈希复核通过。本轮已停止等待审阅，未实现骨骼、网页或全天候后台。\n')
print(json.dumps(entry,ensure_ascii=False))
