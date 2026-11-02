from pathlib import Path
import json,hashlib,zipfile,shutil,datetime,re
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/lighting-checkpoint-11';WORK=ROOT/'work/lighting-cp11'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['validation','light-binding-check','web-asset-validation','glb-roundtrip-check','review-validation','image-review']:assert json.loads((OUT/(n+'.json')).read_text())['passed'],n
assert 'CP11_RENDERS_COMPLETE'in(WORK/'final-renders.log').read_text();rt=json.loads((OUT/'glb-roundtrip-check.json').read_text());assert rt['source_model_sha256']==digest(OUT/'borrowed-wind-town-cp11.blend');assert rt['glb_sha256']==digest(OUT/'borrowed-wind-town-cp11-web.glb')
for p in WORK.glob('*.py'):shutil.copy2(p,OUT/'source'/p.name)
for n in ['final-validation.log','final-renders.log','high-precision-export.log','glb-roundtrip.log','light-bindings.log','scene-inspection.json']:shutil.copy2(WORK/n,OUT/'source'/n)
studies=OUT/'studies';studies.mkdir(exist_ok=True)
for v in ['A','B','C','D']:
 for suffix in ['.png','-record.json']:shutil.copy2(WORK/('variant-'+v+suffix),studies/('variant-'+v+suffix))
shutil.copy2(ROOT/'AGENTS.md',OUT/'source/AGENTS-at-delivery.txt')
for p in OUT.glob('*.blend1'):shutil.move(str(p),str(WORK/('backup-'+p.name)))
for p in OUT.rglob('*'):
 if p.is_file()and p.suffix in ['.json','.txt','.py','.html','.js','.log']:assert not re.search(r'sk-or-v1-[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,}',p.read_text()),str(p)
manifest={p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':digest(p)}for p in sorted(OUT.rglob('*'))if p.is_file()and p.name!='file-manifest.json'};(OUT/'file-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));archive=ROOT/'outputs/\u501f\u98ce\u753a-\u706f\u5149\u68c0\u67e5\u70b9-CP11.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in sorted(OUT.rglob('*')):
  if p.is_file():z.write(p,'lighting-checkpoint-11/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for n,row in manifest.items():assert hashlib.sha256(z.read('lighting-checkpoint-11/'+n)).hexdigest()==row['sha256']
now=datetime.datetime.now(ZoneInfo('America/Los_Angeles')).isoformat();verify={'created_local':now,'archive':str(archive.relative_to(ROOT)),'sha256':digest(archive),'bytes':archive.stat().st_size,'file_count':len(manifest)+1,'zip_crc_passed':True,'per_file_sha256_passed':True,'source_model_reopened':True,'evaluated_geometry_equal_to_cp10':True,'light_parent_bindings_checked':True,'glb_decoded_and_reimported':True,'glb_visual_parity_passed':False,'browser_visual_qa':False,'browser_fps_measured':False,'api_requests':0,'cloud_upload':False};(ROOT/'outputs/\u501f\u98ce\u753a-\u706f\u5149\u68c0\u67e5\u70b9-CP11-\u5f52\u6863\u6821\u9a8c.json').write_text(json.dumps(verify,ensure_ascii=False,indent=2))
latest=ROOT/'outputs/experiment-archive/LATEST.json';data=json.loads(latest.read_text());prior={k:v for k,v in data.items()if k!='addenda'};entry={'date':'2026-10-25','created_local':now,'type':'CP11 local warm lighting and material-response candidate on unchanged CP10 geometry','archive':verify['archive'],'sha256':verify['sha256'],'bytes':verify['bytes'],'verified':True,'geometry_equal_to_cp10':True,'entities':184,'movable_parts':76,'active_cycles_lights':68,'glb_visual_parity_passed':False,'browser_visual_qa':False,'browser_fps_measured':False,'status':'Awaiting lighting review; no geometry/pose changes, new animation, API integration or runtime lighting'};data.setdefault('addenda',[]);data['addenda']=[e for e in data['addenda']if e.get('archive')!=entry['archive']]+[entry];assert {k:v for k,v in data.items()if k!='addenda'}==prior;latest.write_text(json.dumps(data,ensure_ascii=False,indent=2))
index=ROOT/'outputs/experiment-archive/\u5b9e\u9a8c\u6863\u6848\u7d22\u5f15.txt';marker='CP11 - warm local lighting on unchanged CP10 geometry'
if marker not in index.read_text():
 with index.open('a')as f:f.write('\n\n'+marker+'\n2026-10-25: A/B fill trials, C readability refinement and D localized glow. Actual CPU renders, unchanged evaluated geometry/camera/poses/visibility, 184 entities/76 parts, 57 active owned-light transform checks. Offline authoring uses 68 active lights; no browser lighting/bake/FPS or new simulation. CP01-CP10 preserved; old 407 requests and API cost evidence unchanged.\nReview: outputs/lighting-checkpoint-11/review.html\nArchive: '+verify['archive']+'\nSHA256: '+verify['sha256']+'\nLocal archive, CRC and per-file SHA256 verified.\n')
text=index.read_text();start=text.index(marker);tail=text[start:];tail=re.sub(r'(?m)^SHA256: [a-f0-9]+$', 'SHA256: '+verify['sha256'],tail,count=1);index.write_text(text[:start]+tail)
print(json.dumps(verify,ensure_ascii=False,indent=2))
