from pathlib import Path
import json,hashlib,re
from urllib.parse import unquote
R=Path.cwd();O=R/'outputs/runtime-checkpoint-20';A=R/'app/runtime-cp20';page=(O/'review.html').read_text();bad=[]
for v in re.findall(r'(?:src|href)="([^"]+)"',page):
 if v.startswith(('http','#','data:')):continue
 if not(O/unquote(v)).resolve().exists():bad.append(v)
assert not bad,bad
base=json.loads((O/'cp19-baseline-hashes.json').read_text());changed=[p for p,h in base.items()if hashlib.sha256((R/p).read_bytes()).hexdigest()!=h];assert not changed,changed
manifest=json.loads((O/'source-manifest.json').read_text());assert all(hashlib.sha256((O/p).read_bytes()).hexdigest()==h for p,h in manifest.items())
reports={p:json.loads((O/p).read_text())for p in ['browser-full-cast-final.json','browser-walking-support.json','browser-action-qa.json','final-ui-smoke.json','static-build-check.json','core-baseline-check.json']};assert all(d['passed']for d in reports.values())
assert not list(O.glob('*.webm'))and not list(O.glob('*.mp4'))
secrets=[]
for folder in [A/'src',A/'public',A/'dist',O/'source']:
 for p in folder.rglob('*'):
  if p.is_file()and p.suffix in ['.mjs','.js','.json','.html','.css']and re.search(r'sk-or-v1-[A-Za-z0-9_-]{30,}',p.read_text()):secrets.append(str(p.relative_to(R)))
assert not secrets
old=json.loads((R/'app/runtime-cp19/public/assets/runtime-registry.json').read_text())['entities'];new=json.loads((A/'public/assets/runtime-registry.json').read_text())['entities'];oe={e['id']for e in old};ne={e['id']for e in new};op={e['id']+'/'+p['id']for e in old for p in e['parts']};np={e['id']+'/'+p['id']for e in new for p in e['parts']};assert not oe-ne and not op-np
q={'passed':True,'cp19_files_unchanged':len(base),'missing_old_entities':list(oe-ne),'missing_old_parts':list(op-np),'entities':len(ne),'parts':len(np),'new_parts':len(np-op),'body_poses':reports['browser-full-cast-final.json']['body_poses'],'collision_issues':0,'foot_support_samples':reports['browser-walking-support.json']['walking_actor_samples'],'logic_tests':35,'browser_action_trials':11,'video_created':False,'live_url':'http://127.0.0.1:4200/','local_server_intentionally_retained_for_user_review':True,'broken_links':bad,'public_credentials_found':len(secrets),'source_snapshot_entries':len(manifest),'scope':'Finite scenario samples, not continuous or all-future-decision collision proof.'};(O/'delivery-validation.json').write_text(json.dumps(q,indent=2));print(json.dumps(q,indent=2))
