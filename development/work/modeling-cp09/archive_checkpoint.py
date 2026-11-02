from pathlib import Path
import json,hashlib,zipfile,shutil,datetime,re
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-09';WORK=ROOT/'work/modeling-cp09'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['validation','full-body-contact-check','control-clearance-check','web-asset-validation','review-validation','glb-roundtrip-check','image-review']:
 assert json.loads((OUT/(name+'.json')).read_text())['passed'],name
assert 'CP09_RENDER_SET_COMPLETE' in (WORK/'final-cpu-renders.log').read_text()
assert 'CP09_RENDER_SET_COMPLETE' in (WORK/'final-repair-renders.log').read_text()
rt=json.loads((OUT/'glb-roundtrip-check.json').read_text());assert rt['glb_sha256']==digest(OUT/'borrowed-wind-town-cp09-web.glb');assert rt['source_model_sha256']==digest(OUT/'borrowed-wind-town-cp09.blend')
for p in WORK.glob('*.py'):shutil.copy2(p,OUT/'source'/p.name)
for name in ['final-cpu-renders.log','final-repair-renders.log','final-surface-validation-export.log','glb-roundtrip.log']:shutil.copy2(WORK/name,OUT/'source'/name)
shutil.copy2(ROOT/'AGENTS.md',OUT/'source/AGENTS-at-delivery.txt')
for p in OUT.glob('*.blend1'):shutil.move(str(p),str(WORK/('backup-'+p.name)))
for p in OUT.rglob('*'):
 if p.is_file() and p.suffix in ['.json','.txt','.py','.html','.js','.log']:
  txt=p.read_text();assert not re.search(r'sk-or-v1-[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,}',txt),'Credential-like value found in '+str(p)
files=[p for p in OUT.rglob('*')if p.is_file()and p.name!='file-manifest.json'];manifest={p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':digest(p)}for p in sorted(files)};(OUT/'file-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
archive=ROOT/'outputs/\u501f\u98ce\u753a-\u5efa\u6a21\u68c0\u67e5\u70b9-CP09.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(OUT.rglob('*')):
  if p.is_file():z.write(p,'modeling-checkpoint-09/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for name,row in manifest.items():assert hashlib.sha256(z.read('modeling-checkpoint-09/'+name)).hexdigest()==row['sha256']
now=datetime.datetime.now(ZoneInfo('America/Los_Angeles')).isoformat();reg=json.loads((OUT/'decision-entities.json').read_text());verify={'created_local':now,'archive':str(archive.relative_to(ROOT)),'sha256':digest(archive),'bytes':archive.stat().st_size,'file_count':len(manifest)+1,'zip_crc_passed':True,'per_file_sha256_passed':True,'source_model_reopened':True,'glb_decoded_and_reimported':True,'current_pose_contacts_checked':True,'sampled_mechanical_poses_checked':True,'full_animation_collision_tested':False,'api_integration_implemented':False,'browser_fps_measured':False,'cloud_upload':False};(ROOT/'outputs/\u501f\u98ce\u753a-\u5efa\u6a21\u68c0\u67e5\u70b9-CP09-\u5f52\u6863\u6821\u9a8c.json').write_text(json.dumps(verify,ensure_ascii=False,indent=2))
latest=ROOT/'outputs/experiment-archive/LATEST.json';data=json.loads(latest.read_text());prior={k:v for k,v in data.items()if k!='addenda'};entry={'date':'2026-10-25','created_local':now,'type':'CP09 contact repairs, restored western silhouette, grouped paper planting, hollow boat and warm lighting','archive':verify['archive'],'sha256':verify['sha256'],'bytes':verify['bytes'],'verified':True,'model_reopened_and_validated':True,'glb_decoded_and_reimported':True,'entities':reg['entity_count'],'movable_parts':reg['parts_count'],'browser_visual_qa':False,'browser_fps_measured':False,'status':'Awaiting user art review; current poses and sampled mechanical controls checked, no API integration, rigging or runtime'};data.setdefault('addenda',[]);data['addenda']=[x for x in data['addenda']if x.get('archive')!=entry['archive']]+[entry];assert {k:v for k,v in data.items()if k!='addenda'}==prior;latest.write_text(json.dumps(data,ensure_ascii=False,indent=2))
index=ROOT/'outputs/experiment-archive/\u5b9e\u9a8c\u6863\u6848\u7d22\u5f15.txt';marker='CP09 - model contact repair and warm paper town'
if marker not in index.read_text():
 with index.open('a')as f:f.write('\n\n'+marker+'\n2026-10-25: User feedback on CP08 corrected in actual geometry. Western building heights restored; station/balcony/cyclist fitted; real hollow boat, grouped outer planting and pink terrace garden added. 44 current dynamic-object poses, 156 local route samples, 45 stair supports and 29 discrete mechanical poses pass their scoped checks. CP01-CP08 preserved. 184 entity IDs / 76 parts; CPU renders; no runtime or full animation test. Original experiment requests/cost evidence unchanged.\nReview: outputs/modeling-checkpoint-09/review.html\nArchive: '+entry['archive']+'\nSHA256: '+verify['sha256']+'\nLocal only; ZIP CRC and per-file SHA256 verified.\n')
print(json.dumps(verify,ensure_ascii=False,indent=2))
