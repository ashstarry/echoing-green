from pathlib import Path
import json,hashlib,zipfile,shutil,datetime,re
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/art-checkpoint-15';W=ROOT/'work/art-cp15'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['validation','decoration-control-check','diner-endpoint-check','full-body-contact-check','web-asset-validation','glb-roundtrip-check','review-validation','image-review']:assert json.loads((OUT/(n+'.json')).read_text())['passed'],n
assert 'CP15_RENDERS_COMPLETE'in(W/'final-renders.log').read_text();assert 'GLB_ROUNDTRIP_COMPLETE'in(W/'glb-roundtrip.log').read_text();r=json.loads((OUT/'glb-roundtrip-check.json').read_text());assert r['source_model_sha256']==sha(OUT/'borrowed-wind-town-cp15.blend')and r['glb_sha256']==sha(OUT/'borrowed-wind-town-cp15-web.glb')
for p in W.glob('*.py'):shutil.copy2(p,OUT/'source'/p.name)
for n in ['build.log','finalize.log','validation.log','final-renders.log','export.log','glb-roundtrip.log','web-validation.log']:shutil.copy2(W/n,OUT/'source'/n)
(OUT/'studies').mkdir(exist_ok=True);shutil.copy2(W/'draft-restaurant.png',OUT/'studies/draft-restaurant.png');shutil.copy2(ROOT/'AGENTS.md',OUT/'source/AGENTS-at-delivery.txt')
for p in OUT.glob('*.blend1'):shutil.move(str(p),str(W/('saved-backup-'+p.name)))
for p in OUT.rglob('*'):
 if p.is_file()and p.suffix in ['.json','.txt','.py','.html','.js','.log']:assert not re.search(r'sk-or-v1-[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,}',p.read_text()),str(p)
manifest={p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(OUT.rglob('*'))if p.is_file()and p.name!='file-manifest.json'};(OUT/'file-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));archive=ROOT/'outputs/\u501f\u98ce\u753a-\u7f8e\u672f\u68c0\u67e5\u70b9-CP15.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in sorted(OUT.rglob('*')):
  if p.is_file():z.write(p,'art-checkpoint-15/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for n,r in manifest.items():assert hashlib.sha256(z.read('art-checkpoint-15/'+n)).hexdigest()==r['sha256']
now=datetime.datetime.now(ZoneInfo('America/Los_Angeles')).isoformat();v={'created_local':now,'archive':str(archive.relative_to(ROOT)),'sha256':sha(archive),'bytes':archive.stat().st_size,'file_count':len(manifest)+1,'zip_crc_passed':True,'per_file_sha256_passed':True,'source_model_reopened':True,'glb_decoded_and_reimported':True,'glb_visual_parity_passed':False,'browser_visual_qa':False,'browser_fps_measured':False,'api_requests':0,'cloud_upload':False};(ROOT/'outputs/\u501f\u98ce\u753a-\u7f8e\u672f\u68c0\u67e5\u70b9-CP15-\u5f52\u6863\u6821\u9a8c.json').write_text(json.dumps(v,ensure_ascii=False,indent=2))
latest=ROOT/'outputs/experiment-archive/LATEST.json';d=json.loads(latest.read_text());prior={k:x for k,x in d.items()if k!='addenda'};entry={'date':'2026-10-26','created_local':now,'type':'CP15 restored striped awnings, upper noren and two non-emissive ornaments; two-endpoint upper diner contract','archive':v['archive'],'sha256':v['sha256'],'bytes':v['bytes'],'verified':True,'entities':199,'movable_parts':91,'active_cycles_lights':77,'glb_visual_parity_passed':False,'browser_fps_measured':False,'status':'Awaiting art review; endpoints declared, no transition/hide-show/indoor runtime implemented'};d.setdefault('addenda',[]);d['addenda']=[x for x in d['addenda']if x.get('archive')!=entry['archive']]+[entry];assert prior=={k:x for k,x in d.items()if k!='addenda'};latest.write_text(json.dumps(d,ensure_ascii=False,indent=2))
index=ROOT/'outputs/experiment-archive/\u5b9e\u9a8c\u6863\u6848\u7d22\u5f15.txt';marker='CP15 - noren, striped awnings and two diner endpoints'
if marker not in index.read_text():
 with index.open('a')as f:f.write('\n\n'+marker+'\n2026-10-26: Existing awnings exposed, seven noren panels, wind bell and paper cranes added; no new lighting. Two upper diners expose only retreat-behind-curtain / come-out-to-dine. 422595 triangles, 199 entities/91 parts; current contacts and hidden endpoint probes checked, no runtime or transition claims. CP01-CP14 and original experiments preserved.\nReview: outputs/art-checkpoint-15/review.html\nArchive: '+v['archive']+'\nSHA256: '+v['sha256']+'\nLocal ZIP CRC and per-file SHA256 verified.\n')
text=index.read_text();start=text.index(marker);tail=re.sub(r'(?m)^SHA256: [a-f0-9]+$','SHA256: '+v['sha256'],text[start:],count=1);index.write_text(text[:start]+tail);print(json.dumps(v,ensure_ascii=False,indent=2))
