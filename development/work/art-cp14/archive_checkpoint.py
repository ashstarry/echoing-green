from pathlib import Path
import json,hashlib,zipfile,shutil,datetime,re
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/art-checkpoint-14';W=ROOT/'work/art-cp14'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['validation','diner-action-space-check','sky-control-check','full-body-contact-check','light-binding-check','web-asset-validation','web-material-bindings','glb-roundtrip-check','review-validation','image-review']:
 assert json.loads((OUT/(n+'.json')).read_text())['passed'],n
c=json.loads((OUT/'circulation-check.json').read_text());assert all(r['body_clear_count']==r['sample_count']for r in c['routes'].values());assert all(all(p['floor_delta']is not None and abs(p['floor_delta'])<.18 for p in r['samples'])for r in c['routes'].values())
for name in ['final-renders.log']:assert 'CP14_RENDERS_COMPLETE'in(W/name).read_text()
assert 'GLB_ROUNDTRIP_COMPLETE'in(W/'glb-roundtrip.log').read_text();rt=json.loads((OUT/'glb-roundtrip-check.json').read_text());assert rt['source_model_sha256']==sha(OUT/'borrowed-wind-town-cp14.blend')and rt['glb_sha256']==sha(OUT/'borrowed-wind-town-cp14-web.glb')
for p in W.glob('*.py'):shutil.copy2(p,OUT/'source'/p.name)
for name in ['build.log','finalize.log','diner-actions-final.log','validation.log','circulation-final.log','final-renders.log','export.log','glb-roundtrip.log','web-validation.log','circulation-brief.json']:shutil.copy2(W/name,OUT/'source'/name)
studies=OUT/'studies';studies.mkdir(exist_ok=True)
for name in ['draft-overview.png','draft-restaurant.png','final-draft-overview.png','final-draft-restaurant.png']:shutil.copy2(W/name,studies/name)
shutil.copy2(ROOT/'AGENTS.md',OUT/'source/AGENTS-at-delivery.txt')
for p in OUT.glob('*.blend1'):shutil.move(str(p),str(W/('saved-backup-'+p.name)))
for p in OUT.rglob('*'):
 if p.is_file()and p.suffix in ['.json','.txt','.py','.html','.js','.log']:assert not re.search(r'sk-or-v1-[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,}',p.read_text()),str(p)
manifest={p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(OUT.rglob('*'))if p.is_file()and p.name!='file-manifest.json'};(OUT/'file-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));archive=ROOT/'outputs/\u501f\u98ce\u753a-\u7f8e\u672f\u68c0\u67e5\u70b9-CP14.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in sorted(OUT.rglob('*')):
  if p.is_file():z.write(p,'art-checkpoint-14/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for name,row in manifest.items():assert hashlib.sha256(z.read('art-checkpoint-14/'+name)).hexdigest()==row['sha256']
now=datetime.datetime.now(ZoneInfo('America/Los_Angeles')).isoformat();v={'created_local':now,'archive':str(archive.relative_to(ROOT)),'sha256':sha(archive),'bytes':archive.stat().st_size,'file_count':len(manifest)+1,'zip_crc_passed':True,'per_file_sha256_passed':True,'source_model_reopened':True,'glb_decoded_and_reimported':True,'glb_visual_parity_passed':False,'browser_visual_qa':False,'browser_fps_measured':False,'api_requests':0,'cloud_upload':False};(ROOT/'outputs/\u501f\u98ce\u753a-\u7f8e\u672f\u68c0\u67e5\u70b9-CP14-\u5f52\u6863\u6821\u9a8c.json').write_text(json.dumps(v,ensure_ascii=False,indent=2))
latest=ROOT/'outputs/experiment-archive/LATEST.json';d=json.loads(latest.read_text());prior={k:x for k,x in d.items()if k!='addenda'};entry={'date':'2026-10-25','created_local':now,'type':'CP14 open dining balcony, two new guests and enveloping warm lighting','archive':v['archive'],'sha256':v['sha256'],'bytes':v['bytes'],'verified':True,'entities':196,'movable_parts':82,'active_cycles_lights':77,'glb_visual_parity_passed':False,'browser_fps_measured':False,'status':'Awaiting art review; no animation, API calls or runtime implementation'};d.setdefault('addenda',[]);d['addenda']=[x for x in d['addenda']if x.get('archive')!=entry['archive']]+[entry];assert prior=={k:x for k,x in d.items()if k!='addenda'};latest.write_text(json.dumps(d,ensure_ascii=False,indent=2))
index=ROOT/'outputs/experiment-archive/\u5b9e\u9a8c\u6863\u6848\u7d22\u5f15.txt';marker='CP14 - open dining balcony and a warmer inhabited town'
if marker not in index.read_text():
 with index.open('a')as f:f.write('\n\n'+marker+'\n2026-10-25: Round lantern row recomposed as five slim pendants and six concealed sources; two diners and table workstations, slightly deeper balcony and lifted complete roof with headroom; chair pullback and exit key poses checked; warm activity pools, background and glow refined. 421737 master triangles; 196 entities/82 parts. Current contact checks, 187 local route samples and 44 diner/chair key poses pass within documented scope. No runtime/FPS claims. CP01-CP13 and original experiments preserved.\nReview: outputs/art-checkpoint-14/review.html\nArchive: '+v['archive']+'\nSHA256: '+v['sha256']+'\nLocal ZIP CRC and per-file SHA256 verified.\n')
text=index.read_text();start=text.index(marker);tail=re.sub(r'(?m)^SHA256: [a-f0-9]+$','SHA256: '+v['sha256'],text[start:],count=1);index.write_text(text[:start]+tail);print(json.dumps(v,ensure_ascii=False,indent=2))
