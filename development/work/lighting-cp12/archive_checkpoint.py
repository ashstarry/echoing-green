from pathlib import Path
import json,hashlib,zipfile,shutil,datetime,re
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/lighting-checkpoint-12';W=ROOT/'work/lighting-cp12'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['validation','light-binding-check','sky-control-check','full-body-contact-check','water-lantern-placement-check','web-asset-validation','web-material-bindings','glb-roundtrip-check','review-validation','image-review']:
 assert json.loads((OUT/(name+'.json')).read_text())['passed'],name
assert 'CP12_RENDERS_COMPLETE'in(W/'final-renders.log').read_text();assert 'GLB_ROUNDTRIP_COMPLETE'in(W/'glb-roundtrip.log').read_text()
rt=json.loads((OUT/'glb-roundtrip-check.json').read_text());assert rt['source_model_sha256']==digest(OUT/'borrowed-wind-town-cp12.blend');assert rt['glb_sha256']==digest(OUT/'borrowed-wind-town-cp12-web.glb')
for p in W.glob('*.py'):shutil.copy2(p,OUT/'source'/p.name)
for name in ['finalize.log','geometry-validation.log','full-contacts.log','final-renders.log','export.log','glb-roundtrip.log','web-validation.log','sky-water-inspection.json','variant-C.log']:
 shutil.copy2(W/name,OUT/'source'/name)
shutil.copy2(ROOT/'AGENTS.md',OUT/'source/AGENTS-at-delivery.txt')
studies=OUT/'studies';studies.mkdir(exist_ok=True)
for name in ['variant-A.png','variant-B.png','variant-A-record.json','variant-B-record.json','variant-C-overview.png','variant-C-water.png']:
 shutil.copy2(W/name,studies/name)
for p in OUT.rglob('*'):
 if p.is_file()and p.suffix in ['.json','.txt','.py','.html','.js','.log']:assert not re.search(r'sk-or-v1-[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,}',p.read_text()),str(p)
manifest={p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':digest(p)}for p in sorted(OUT.rglob('*'))if p.is_file()and p.name!='file-manifest.json'};(OUT/'file-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
archive=ROOT/'outputs/\u501f\u98ce\u753a-\u706f\u5149\u68c0\u67e5\u70b9-CP12.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in sorted(OUT.rglob('*')):
  if p.is_file():z.write(p,'lighting-checkpoint-12/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for name,row in manifest.items():assert hashlib.sha256(z.read('lighting-checkpoint-12/'+name)).hexdigest()==row['sha256']
now=datetime.datetime.now(ZoneInfo('America/Los_Angeles')).isoformat();verification={'created_local':now,'archive':str(archive.relative_to(ROOT)),'sha256':digest(archive),'bytes':archive.stat().st_size,'file_count':len(manifest)+1,'zip_crc_passed':True,'per_file_sha256_passed':True,'source_model_reopened':True,'geometry_changes_limited_to_documented_additions':True,'glb_decoded_and_reimported':True,'glb_visual_parity_passed':False,'browser_visual_qa':False,'browser_fps_measured':False,'weather_and_fireworks_design_only':True,'api_requests':0,'cloud_upload':False};(ROOT/'outputs/\u501f\u98ce\u753a-\u706f\u5149\u68c0\u67e5\u70b9-CP12-\u5f52\u6863\u6821\u9a8c.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2))
latest=ROOT/'outputs/experiment-archive/LATEST.json';data=json.loads(latest.read_text());prior={k:v for k,v in data.items()if k!='addenda'}
entry={'date':'2026-10-25','created_local':now,'type':'CP12 brighter rain bridge, two paper water lanterns, bird/star controls and weather/festival design','archive':verification['archive'],'sha256':verification['sha256'],'bytes':verification['bytes'],'verified':True,'entities':191,'movable_parts':82,'active_cycles_lights':72,'glb_visual_parity_passed':False,'browser_visual_qa':False,'browser_fps_measured':False,'status':'Awaiting art review; no runtime, weather/firework effects or new API calls'}
data.setdefault('addenda',[]);data['addenda']=[e for e in data['addenda']if e.get('archive')!=entry['archive']]+[entry];assert {k:v for k,v in data.items()if k!='addenda'}==prior;latest.write_text(json.dumps(data,ensure_ascii=False,indent=2))
index=ROOT/'outputs/experiment-archive/\u5b9e\u9a8c\u6863\u6848\u7d22\u5f15.txt';marker='CP12 - readable rain bridge, paper water lights and sky controls'
if marker not in index.read_text():
 with index.open('a')as f:f.write('\n\n'+marker+'\n2026-10-25: Brighter global fill, restrained local rainy-bridge light, two new paper water lamps, six bird-wing pivots, five independently glowing existing stars. Actual CPU renders, 46 current assembly contact checks, 562 car poses against new lamps, 191 entities/82 parts, 61 owned-light binding checks. 427184 master triangles; no runtime lighting, weather/fireworks effects or FPS claims. Weather/festival design saved. CP01-CP11 preserved; prior 407 API requests and cost provenance unchanged.\nReview: outputs/lighting-checkpoint-12/review.html\nArchive: '+verification['archive']+'\nSHA256: '+verification['sha256']+'\nLocal archive with CRC/per-file SHA256 verified.\n')
text=index.read_text();start=text.index(marker);tail=re.sub(r'(?m)^SHA256: [a-f0-9]+$','SHA256: '+verification['sha256'],text[start:],count=1);index.write_text(text[:start]+tail)
print(json.dumps(verification,ensure_ascii=False,indent=2))
