from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,zipfile,struct
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-04';ZIP=ROOT/'outputs/借风町-建模检查点-CP04.zip'
now=datetime.now(ZoneInfo('America/Los_Angeles'))
def sha(data):return hashlib.sha256(data).hexdigest()
assert json.loads((OUT/'validation.json').read_text())['passed']
check=json.loads((OUT/'review-static-check.json').read_text());check['javascript_syntax_check_passed']=True
(OUT/'review-static-check.json').write_text(json.dumps(check,ensure_ascii=False,indent=2))
manifest={}
for p in sorted(OUT.rglob('*')):
 if not p.is_file() or p.name in ['file-manifest.json','archive-verification.json']:continue
 assert p.suffix!='.blend1'
 data=p.read_bytes()
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
entry={'date':now.date().isoformat(),'created_local':now.isoformat(),'type':'CP04 two-face architecture and side-wall modeling','archive':str(ZIP.relative_to(ROOT)),'sha256':sha(ZIP.read_bytes()),'bytes':ZIP.stat().st_size,'verified':True,'model_reopened_and_validated':True,'browser_visual_qa':False,'status':'Stopped for user review; real model revision, no claim of finished reference fidelity or runtime'}
(OUT/'archive-verification.json').write_text(json.dumps({**entry,'verified_file_count':len(manifest),'zip_crc_passed':True,'roundtrip_sha256_passed':True,'credential_pattern_check_passed':True},ensure_ascii=False,indent=2))
latest=ROOT/'outputs/experiment-archive/LATEST.json';data=json.loads(latest.read_text());data.setdefault('addenda',[]).append(entry);latest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
index=ROOT/'outputs/experiment-archive/实验档案索引.txt'
with index.open('a') as f:f.write('\n'+now.date().isoformat()+' CP04 建模追加档案\n用户要求后部和左上建筑转角朝向镜头，能看到两面光影。CP04 固定沿用 CP03 主镜头，将茶屋/西侧住宅的水平立面夹角调至45°，补充实际侧窗、木构与阳台转角，更新局部比例和活动预留。入口 outputs/modeling-checkpoint-04/review.html；工程、真实渲染、历史对照、脚本和验证保存于 outputs/借风町-建模检查点-CP04.zip。相机43°俯角与建筑水平45°是不同量。CP01–CP03未覆盖，24人物/7动物占位保留；静态中心视线通过，不代表完整动作/导航或整体1:1。已有附属小屋与住家体块连接仍需精修。已经停在检查点等待用户反馈。ZIP完整性及逐文件哈希验证通过，仅本地归档。\n')
print(json.dumps(entry,ensure_ascii=False))
