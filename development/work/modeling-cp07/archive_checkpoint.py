from pathlib import Path
import json,hashlib,zipfile,shutil,datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-07';WORK=ROOT/'work/modeling-cp07'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((OUT/'validation.json').read_text())['passed'];assert json.loads((OUT/'web-asset-validation.json').read_text())['passed'];assert json.loads((OUT/'review-validation.json').read_text())['passed']
rt=json.loads((OUT/'glb-roundtrip-check.json').read_text());assert rt['glb_sha256']==digest(OUT/'borrowed-wind-town-cp07-web.glb');assert rt['source_model_sha256']==digest(OUT/'borrowed-wind-town-cp07.blend')
for name in ['01-overview.png','02-restaurant.png','03-terrace.png','04-water-garden.png','05-paper-neighborhood.png','06-plan.png','07-glb-roundtrip.png']:assert(OUT/name).stat().st_mtime>(OUT/'borrowed-wind-town-cp07.blend').stat().st_mtime
for p in WORK.glob('*.py'):
 if p.name not in ['audit_draft.py','inspect_export.py']:shutil.copy2(p,OUT/'source'/p.name)
for p in OUT.glob('*.blend1'):shutil.move(str(p),str(WORK/('backup-'+p.name)))
files=[p for p in OUT.rglob('*') if p.is_file() and p.name!='file-manifest.json'];manifest={p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(files)};(OUT/'file-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
archive=ROOT/'outputs/借风町-建模检查点-CP07.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(OUT.rglob('*')):
  if p.is_file():z.write(p,'modeling-checkpoint-07/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name,row in manifest.items():assert hashlib.sha256(z.read('modeling-checkpoint-07/'+name)).hexdigest()==row['sha256']
now=datetime.datetime.now(ZoneInfo('America/Los_Angeles')).isoformat();verify={'created_local':now,'archive':str(archive.relative_to(ROOT)),'sha256':digest(archive),'bytes':archive.stat().st_size,'file_count':len(manifest)+1,'zip_crc_passed':True,'per_file_sha256_passed':True,'source_model_reopened':True,'glb_decoded_and_reimported':True,'browser_fps_measured':False,'cloud_upload':False};(ROOT/'outputs/借风町-建模检查点-CP07-归档校验.json').write_text(json.dumps(verify,ensure_ascii=False,indent=2))
latest=ROOT/'outputs/experiment-archive/LATEST.json';data=json.loads(latest.read_text());entry={'date':'2026-10-25','created_local':now,'type':'CP07 cut-paper environment finish, ImageGen-derived normal textures, longer bench and optimized GLB candidate','archive':str(archive.relative_to(ROOT)),'sha256':verify['sha256'],'bytes':verify['bytes'],'verified':True,'model_reopened_and_validated':True,'glb_decoded_and_reimported':True,'browser_visual_qa':False,'browser_fps_measured':False,'status':'Environment art pass completed for review; unrigged assets, no web runtime or 24/7 service'};data.setdefault('addenda',[]);data['addenda']=[x for x in data['addenda'] if x.get('archive')!=entry['archive']]+[entry];latest.write_text(json.dumps(data,ensure_ascii=False,indent=2))
index=ROOT/'outputs/experiment-archive/实验档案索引.txt';marker='CP07 · 纸雕环境精修与浏览器候选资产'
if marker not in index.read_text():
 with index.open('a') as f:f.write('\n\n'+marker+'\n2026-10-25：用户认可 CP06 后授权尽可能接近完成，保留纸雕风格和浏览器资源约束。交付目录 outputs/modeling-checkpoint-07/，包括可编辑母版、实际渲染、生成材质源/法线/提示词、通行检查、资源统计、约 9.81 MB GLB 候选资产与源码。母版约 43.4 万三角面，比 CP06 少约 35.1%。GLB 已在 Blender 解码重导入；不是网页 FPS 验证。旧实验原始数据、407 次 API 调用与费用统计未改。\n归档：'+entry['archive']+'\nSHA256：'+verify['sha256']+'\n校验：outputs/借风町-建模检查点-CP07-归档校验.json；CRC 与逐文件 SHA256 通过；仅本地保存。\n')
print(json.dumps(verify,ensure_ascii=False,indent=2))
