# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,shutil,re
R=Path.cwd();A=R/'app/runtime-cp22';O=R/'outputs/runtime-checkpoint-22';W=R/'work/runtime-cp22';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((O/'cp21-baseline-hashes.json').read_text());changed=[f for f,h in baseline.items()if sha(R/f)!=h];assert not changed,changed
old=json.loads((R/'app/runtime-cp21/public/assets/runtime-registry.json').read_text());new=json.loads((A/'public/assets/runtime-registry.json').read_text());oldids={e['id']for e in old['entities']};newids={e['id']for e in new['entities']};oldparts={(e['id'],p['id'])for e in old['entities']for p in e['parts']};newparts={(e['id'],p['id'])for e in new['entities']for p in e['parts']};assert oldids<=newids and oldparts<=newparts
raw=json.loads((O/'browser-full-cast-final.json').read_text());correction=json.loads((O/'final-rail-flower-recheck.json').read_text());moved={x['name']for x in json.loads((O/'final-rail-flower-adjustment.json').read_text())['objects']};assert correction['passed'];assert all(c['source_obstacle']in moved for x in raw['issues']for c in x['contacts']);shutil.copy2(O/'browser-full-cast-final.json',O/'browser-full-cast-before-final-flower-fix.json');aggregate={'passed':True,'method':'Complete browser scenario plus targeted verification of the final correction','full_scenario_record':'browser-full-cast-before-final-flower-fix.json','body_poses':raw['body_poses'],'frames':1041,'duration_seconds':260,'original_final_issue_records':len(raw['issues']),'corrected_objects':len(moved),'correction_verification':'final-rail-flower-recheck.json','remaining_detected_issues':0,'not_a_fresh_repeated_full_sweep':True,'scope':'Discrete bounded scenarios, with explicit articulated-assembly/hand-grip/liquid handling. Not all possible future inputs or continuous-time proof.'};(O/'browser-full-cast-final.json').write_text(json.dumps(aggregate,indent=2))
for name in ['support-final.json','boarding-contact-final.json','final-browser-qa.json','static-build-check.json','boarding-state-check.json']:assert json.loads((O/name).read_text())['passed'],name
assert '# pass 46' in (W/'logic-tests-final.log').read_text()
inventory=json.loads((O/'action-inventory.json').read_text());caps={'checkpoint':'CP22','counts':inventory['stats'],'executable_catalog':'action-inventory.json','runtime_bindings':'runtime-bindings.json','old_registry_actions_are_authoring_history':True,'new_natural_language_selector_mapping_complete':False,'semantic_provider':'OpenRouter / OpenAI Decisions (unchanged)','autonomy_api_calls':0,'continuous_offline_world':False,'validation':aggregate};(A/'public/assets/runtime-capabilities.json').write_text(json.dumps(caps,ensure_ascii=False,indent=2));(O/'runtime-capabilities.json').write_text(json.dumps(caps,ensure_ascii=False,indent=2));shutil.copy2(O/'runtime-bindings.json',A/'public/assets/runtime-bindings.json')
parts=inventory['parts'];(O/'部件绑定.json').write_text(json.dumps(parts,ensure_ascii=False,indent=2))
for filename in ['动作总表.html','动作总表.csv']:
 shutil.copy2(O/filename,A/'public/assets'/filename)
# Candidate assets remain in work/boarding; only the selected town is shipped in the application.
for name in ['town-boarding.glb','boarding-registry.json']:
 p=A/'public/assets'/name
 if p.exists():p.unlink()
source=O/'source';source.mkdir(exist_ok=True)
for p in A.iterdir():
 if p.name in ['dist','node_modules']or p.is_symlink():continue
 if p.is_dir():shutil.copytree(p,source/p.name,dirs_exist_ok=True)
 else:shutil.copy2(p,source/p.name)
prod=O/'production-scripts';prod.mkdir(exist_ok=True)
for p in W.rglob('*'):
 if p.is_file()and p.suffix in ['.py','.cjs','.mjs']:
  target=prod/p.relative_to(W);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
secret=[]
for base in [source,A/'public',A/'src']:
 for p in base.rglob('*'):
  if p.is_file()and p.suffix in ['.json','.mjs','.js','.html','.txt','.css','.command']and re.search(rb'sk-or-v1-[A-Fa-f0-9]{40,}',p.read_bytes()):secret.append(str(p.relative_to(R)))
assert not secret,'Credential detected in public/source artifact'
manifest={str(p.relative_to(source)):sha(p)for p in source.rglob('*')if p.is_file()};(O/'source-manifest.json').write_text(json.dumps(manifest,indent=2));shutil.copy2(W/'town-runtime.blend',O/'borrowed-wind-town-cp22.blend');shutil.copy2(W/'logic-tests-final.log',O/'unit-tests.txt')
broken=[]
for page in ['review.html','动作总表.html']:
 for u in re.findall(r'(?:href|src)="([^"]+)"',(O/page).read_text()):
  if not u.startswith(('http','#'))and not(O/u).exists():broken.append([page,u])
assert not broken,broken
report={'passed':True,'previous_cp21_files_unchanged':len(baseline),'preserved_entity_ids':len(oldids),'preserved_part_ids':len(oldparts),'current_entities':len(newids),'current_parts':len(newparts),'logic_tests':46,'runtime_stats':inventory['stats'],'physical_validation':aggregate,'foot_support_samples':json.loads((O/'support-final.json').read_text())['actor_samples'],'live_url':'http://127.0.0.1:4220/','source_snapshot_entries':len(manifest),'credential_findings':0,'broken_links':broken,'videos_created':0,'new_semantic_api_calls':0,'server_retained_for_user_review':True};(O/'delivery-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items()if k not in ['physical_validation','runtime_stats']},ensure_ascii=False,indent=2))
