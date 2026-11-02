import hashlib,json,re,shutil
from pathlib import Path
root=Path.cwd();out=root/'outputs/runtime-checkpoint-21';app=root/'app/runtime-cp21'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((out/'cp20-baseline-hashes.json').read_text());changed=[p for p,h in baseline.items() if sha(root/p)!=h];assert not changed,changed
same=[]
for p in (root/'app/runtime-cp20/public/assets').iterdir():
 if p.is_file():assert sha(p)==sha(app/'public/assets'/p.name),p.name;same.append('public/assets/'+p.name)
for name in ['simulation','navigation','motion','presentation','community','cadence','actions','catalog','fireworks','sound']:
 rel='src/'+name+'.mjs';assert sha(root/'app/runtime-cp20'/rel)==sha(app/rel),name;same.append(rel)
for file in ['reaction-browser-qa.json','feedback-edge-qa.json','static-build-check.json']:
 assert json.loads((out/file).read_text())['passed'],file
assert '# pass 41' in (root/'work/runtime-cp21/logic-tests-final.log').read_text()
# Never emit matching credential values.
secret_files=[]
for base in [app/'src',app/'public',app/'dist']:
 for p in base.rglob('*'):
  if p.is_file() and p.suffix in ['.mjs','.js','.json','.html','.txt','.css','.command']:
   if re.search(rb'sk-or-v1-[a-fA-F0-9]{40,}',p.read_bytes()):secret_files.append(str(p.relative_to(root)))
assert not secret_files,'Credential found in public artifact'
source=out/'source';source.mkdir(exist_ok=True)
for p in app.iterdir():
 if p.name in ['node_modules','dist'] or p.is_symlink():continue
 if p.is_dir():shutil.copytree(p,source/p.name,dirs_exist_ok=True)
 else:shutil.copy2(p,source/p.name)
prod=out/'production-scripts';prod.mkdir(exist_ok=True)
for p in (root/'work/runtime-cp21').iterdir():
 if p.is_file() and p.suffix in ['.py','.cjs'] :shutil.copy2(p,prod/p.name)
shutil.copy2(root/'work/runtime-cp21/logic-tests-final.log',out/'unit-tests.txt')
manifest={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()};(out/'source-manifest.json').write_text(json.dumps(manifest,indent=2))
broken=[]
for target in re.findall(r'(?:href|src)="([^"]+)"',(out/'review.html').read_text()):
 if not target.startswith(('http','#')) and not (out/target).exists():broken.append(target)
assert not broken,broken
report={'passed':True,'cp20_files_unchanged':len(baseline),'identical_assets_and_behavior_files':same,'entities':201,'parts':391,'logic_tests':41,'real_api_functionality_requests':1,'new_collision_sweeps':0,'previous_discrete_collision_scope':'Inherited CP20 only; no new physical behaviors in CP21.','source_snapshot_entries':len(manifest),'public_credentials_found':len(secret_files),'broken_links':broken,'video_created':False,'live_url':'http://127.0.0.1:4210/','local_server_intentionally_retained_for_user_review':True}
(out/'delivery-validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print(json.dumps({k:v for k,v in report.items() if k!='identical_assets_and_behavior_files'},ensure_ascii=False,indent=2))
