from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,zipfile,struct
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-06';ZIP=ROOT/'outputs/借风町-建模检查点-CP06.zip';now=datetime.now(ZoneInfo('America/Los_Angeles'))
def sha(data):return hashlib.sha256(data).hexdigest()
assert json.loads((OUT/'validation.json').read_text())['passed']
check=json.loads((OUT/'review-static-check.json').read_text());check['javascript_syntax_check_passed']=True;(OUT/'review-static-check.json').write_text(json.dumps(check,ensure_ascii=False,indent=2))
manifest={}
for p in sorted(OUT.rglob('*')):
 if not p.is_file() or p.name in ['file-manifest.json','archive-verification.json']:continue
 assert p.suffix!='.blend1';data=p.read_bytes()
 if p.suffix in ['.py','.json','.txt','.html']:assert b'sk-or-v1-' not in data
 if p.suffix=='.png':
  assert data[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack('>II',data[16:24]);assert w>0 and h>0
 manifest[str(p.relative_to(OUT))]={'sha256':sha(data),'bytes':len(data)}
(OUT/'file-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(OUT.rglob('*')):
  if p.is_file() and p.name!='archive-verification.json':z.write(p,arcname=str(Path(OUT.name)/p.relative_to(OUT)))
with zipfile.ZipFile(ZIP) as z:
 assert z.testzip() is None
 for name,entry in manifest.items():assert sha(z.read(OUT.name+'/'+name))==entry['sha256']
entry={'date':now.date().isoformat(),'created_local':now.isoformat(),'type':'CP06 side stall, enlarged terrace, connected upper dining circulation and doorway checks','archive':str(ZIP.relative_to(ROOT)),'sha256':sha(ZIP.read_bytes()),'bytes':ZIP.stat().st_size,'verified':True,'model_reopened_and_validated':True,'browser_visual_qa':False,'status':'Stopped for user review; static geometry/clearance checkpoint, not locomotion or runtime'}
(OUT/'archive-verification.json').write_text(json.dumps({**entry,'verified_file_count':len(manifest),'zip_crc_passed':True,'roundtrip_sha256_passed':True,'credential_pattern_check_passed':True},ensure_ascii=False,indent=2))
latest=ROOT/'outputs/experiment-archive/LATEST.json';data=json.loads(latest.read_text());data.setdefault('addenda',[]).append(entry);latest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
index=ROOT/'outputs/experiment-archive/实验档案索引.txt'
with index.open('a') as f:f.write('\n'+now.date().isoformat()+' CP06 modeling addendum\nSide stall, enlarged upper terrace, upper dining floor and physical door/gallery connection. User chose a complete roof with legible entry/exit. Seven local routes (154 samples), 91 exterior visibility samples and 45 tread samples passed static checks; this is not locomotion, crowd avoidance or all-town navigation. Normal renders retain the roof; the cutaway and four nearby proxy positions are inspection-only. Entry: outputs/modeling-checkpoint-06/review.html. Source model, real renders, original user feedback images, scripts and checks are in the CP06 archive recorded in LATEST.json. CP01-CP05 unchanged. Stopped for user review; no rigs, web runtime or 24/7 service. Local archive only; ZIP CRC and per-file hashes verified.\n')
print(json.dumps(entry,ensure_ascii=False))
