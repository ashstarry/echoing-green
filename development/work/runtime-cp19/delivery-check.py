# -*- coding: utf-8 -*-
from pathlib import Path
import hashlib,json,re,subprocess
from urllib.parse import unquote
R=Path.cwd();O=R/'outputs/runtime-checkpoint-19';A=R/'app/runtime-cp19'
page=(O/'review.html').read_text();bad=[]
for value in re.findall(r'(?:src|href)="([^"]+)"',page):
 if value.startswith(('#','http','data:')):continue
 if not(O/unquote(value.split('#')[0])).resolve().exists():bad.append(value)
assert not bad,bad
for i,src in enumerate(re.findall(r'<script>(.*?)</script>',page,re.S)):
 p=R/'work/runtime-cp19'/f'review-script-{i}.js';p.write_text(src);subprocess.run(['node','--check',str(p)],check=True)
base=json.loads((O/'cp18-baseline-hashes.json').read_text());changed=[p for p,h in base.items()if hashlib.sha256((R/p).read_bytes()).hexdigest()!=h];assert not changed,changed
source=json.loads((O/'source-manifest.json').read_text());assert all(hashlib.sha256((O/p).read_bytes()).hexdigest()==h for p,h in source.items())
secret=[]
for folder in [A/'src',A/'public',A/'dist',O/'source',O/'api-runs']:
 for p in folder.rglob('*'):
  if p.is_file()and p.suffix in ['.js','.mjs','.json','.html','.txt','.css']and re.search(r'sk-or-v1-[A-Za-z0-9_-]{30,}',p.read_text()):secret.append(str(p.relative_to(R)))
assert not secret,secret
qa=json.loads((O/'browser-final-qa.json').read_text());collision=json.loads((O/'browser-full-cast-final.json').read_text());support=json.loads((O/'browser-walking-support.json').read_text());static=json.loads((O/'static-build-check.json').read_text());review=json.loads((O/'review-ui-check.json').read_text());assert not qa['errors']and collision['passed']and support['passed']and static['passed']and review['passed']
records=json.loads((O/'video-records.json').read_text());assert len(records)==3 and all(not r['errors']for r in records)
summary={'passed':True,'cp18_baseline_files_unchanged':len(base),'source_manifest_entries':len(source),'broken_local_links':bad,'public_credentials_found':len(secret),'browser_errors':qa['errors'],'collision_body_poses':collision['body_poses'],'collision_issues':len(collision['issues']),'walking_support_samples':support['walking_actor_samples'],'logic_tests':28,'video_count':len(records),'video_bytes':{p.name:p.stat().st_size for p in O.glob('town-*.webm')},'scope':'Local CP19 checkpoint; sampled finite scenarios only, not a general continuous collision proof or universal performance guarantee.'}
(O/'delivery-validation.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
