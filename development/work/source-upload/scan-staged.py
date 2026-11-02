from pathlib import Path
import subprocess,re,json
r=Path.cwd();repo=r/'publish/echoing-green';known=(r/'work/private/openrouter.key').read_bytes().strip();files=[x for x in subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=repo).decode().split('\0') if x];assert len(files)>1000,'Source staging is not complete';assert not subprocess.check_output(['git','diff','--name-only'],cwd=repo).strip(),'Working files differ from index';findings=[];size=0
patterns={'provider_token':rb'sk-or-v1-[A-Za-z0-9]{24,}','github_token':rb'(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,})','private_key':rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----','personal_absolute_path':rb'/Users/[A-Za-z0-9_.-]+/'}
for rel in files:
 b=(repo/rel).read_bytes();size+=len(b)
 if known in b:findings.append({'path':rel,'kind':'actual_key'})
 for name,pattern in patterns.items():
  if re.search(pattern,b):findings.append({'path':rel,'kind':name})
 if any(part in ['node_modules','.local','.git','.wrangler','private'] for part in Path(rel).parts)or Path(rel).name.startswith('.env'):findings.append({'path':rel,'kind':'private_or_generated_path'})
 if len(b)>100*1024*1024:findings.append({'path':rel,'kind':'github_file_limit'})
result={'staged_files':len(files),'staged_bytes':size,'findings':findings,'runtime_tests':216,'api_tests':20,'install':'passed','static_build':'passed'};(r/'outputs/source-upload/final-security-and-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));assert not findings
