from pathlib import Path
import hashlib,json,zipfile,struct
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-03';ZIP=ROOT/'outputs/借风町-建模检查点-CP03.zip'
def sha(data):return hashlib.sha256(data).hexdigest()
assert json.loads((OUT/'validation.json').read_text())['passed']
check=json.loads((OUT/'review-static-check.json').read_text());check['javascript_syntax_check_passed']=True
(OUT/'review-static-check.json').write_text(json.dumps(check,ensure_ascii=False,indent=2))
for f in OUT.glob('*.png'):
 d=f.read_bytes();assert d[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack('>II',d[16:24]);assert w>1000 and h>600
manifest={}
for p in sorted(OUT.rglob('*')):
 if not p.is_file() or p.name in ['file-manifest.json','archive-verification.json']:continue
 data=p.read_bytes()
 if p.suffix in ['.py','.txt','.json','.html']:assert b'sk-or-v1-' not in data
 manifest[str(p.relative_to(OUT))]={'sha256':sha(data),'bytes':len(data)}
(OUT/'file-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(OUT.rglob('*')):
  if p.is_file() and p.name!='archive-verification.json':z.write(p,arcname=str(Path(OUT.name)/p.relative_to(OUT)))
with zipfile.ZipFile(ZIP) as z:
 assert z.testzip() is None
 for name,entry in manifest.items():assert sha(z.read(OUT.name+'/'+name))==entry['sha256']
 entry={'date':'2026-10-24','type':'CP03 camera, building orientations, hillside stair and reserved movement spaces','archive':str(ZIP.relative_to(ROOT)),'sha256':sha(ZIP.read_bytes()),'bytes':ZIP.stat().st_size,'verified':True,'model_reopened_and_validated':True,'browser_visual_qa':False,'status':'Stopped for user review; real modeling checkpoint, not finished reference fidelity or runtime'}
(OUT/'archive-verification.json').write_text(json.dumps({**entry,'verified_file_count':len(manifest),'zip_crc_passed':True,'roundtrip_sha256_passed':True,'credential_pattern_check_passed':True},ensure_ascii=False,indent=2))
latest=ROOT/'outputs/experiment-archive/LATEST.json';data=json.loads(latest.read_text());data.setdefault('addenda',[]).append(entry);latest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
index=ROOT/'outputs/experiment-archive/实验档案索引.txt'
with index.open('a') as f:f.write('\n2026-10-24 CP03 建模追加档案\n用户复核 CP02 后继续要求贴近参考：镜头小幅降低、修正建筑朝向、体现右上高台阶梯，未来细节不挤占人物活动面。CP03 已保存并停下等待审阅。入口 outputs/modeling-checkpoint-03/review.html；工程与真实渲染、参考/CP02对照、活动空间图、脚本和验证已归档到 outputs/借风町-建模检查点-CP03.zip。主相机43°正交，24人物/7动物占位；静态头部与上半身中心采样24/24可见，不代表动画或导航验证。CP01/CP02保留，没有实现骨骼、网页或全天候后台。ZIP逐文件哈希复核通过；本地保存，未上传云端。\n')
print(json.dumps(entry,ensure_ascii=False))
