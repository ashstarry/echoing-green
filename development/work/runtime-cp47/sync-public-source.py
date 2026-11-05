from pathlib import Path
import shutil,json,subprocess,hashlib,re
root=Path.cwd();repo=root/'publish/echoing-green';dev=repo/'development';src=root/'app/runtime-cp47';dest=dev/'app/runtime-cp47';manifest=[]
def copy(p,d):
 d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d);manifest.append({'original':str(p.relative_to(root)),'repository':str(d.relative_to(repo)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for folder in ['src','tests','scripts']:
 for p in (src/folder).rglob('*'):
  if p.is_file():copy(p,dest/folder/p.relative_to(src/folder))
for name in ['package.json','package-lock.json','index.html','semantic-contract.json','server.mjs','decision-api.mjs','qa-harness.mjs']:copy(src/name,dest/name)
p=dest/'decision-api.mjs';s=p.read_text();start=s.index('async function key()');end=s.index('\nexport async function available',start)
portable=(dev/'app/runtime-cp44/decision-api.mjs').read_text();a=portable.index('async function key()');b=portable.index('\nexport async function available',a)
s=s[:start]+portable[a:b]+s[end:];s=s.replace("resolve(project,'outputs/runtime-checkpoint-47/semantic-runs')","resolve(root,'.local/semantic-runs')");p.write_text(s)
shutil.copy2(dev/'app/runtime-cp44/scripts/prepare-assets.mjs',dest/'scripts/prepare-assets.mjs')
p=dest/'package.json';d=json.loads(p.read_text());d['scripts']['postinstall']='node scripts/prepare-assets.mjs';d['engines']={'node':'>=22.13.0'};p.write_text(json.dumps(d,indent=2)+'\n')
p=dev/'.gitignore';s=p.read_text();line='app/runtime-cp47/public/assets/\n';p.write_text(s if line in s else line+s)
api=root/'app/echoing-green-api'
for name in subprocess.check_output(['git','ls-files','-z'],cwd=api).decode().split('\0'):
 if name:copy(api/name,dev/'api'/name)
for p in (root/'work/runtime-cp47').iterdir():
 if p.is_file() and p.suffix in ['.py','.mjs','.js','.sh']:copy(p,dev/'work/runtime-cp47'/p.name)
p=dev/'README.md';s=p.read_text();s=re.sub(r'\| `app/runtime-cp\d+/` \| Current', '| `app/runtime-cp47/` | Current',s);s=re.sub(r'cd development/app/runtime-cp\d+', 'cd development/app/runtime-cp47',s);s=re.sub(r'`app/runtime-cp17/` … `app/runtime-cp\d+/`','`app/runtime-cp17/` … `app/runtime-cp46/`',s);p.write_text(s)
p=dev/'source-provenance.json';d=json.loads(p.read_text());d['active']='app/runtime-cp47';d['api_source_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=api,text=True).strip();replaced={m['repository'] for m in manifest};d['files']=[m for m in d['files'] if m['repository'] not in replaced]+manifest
for m in d['files']:
 f=repo/m['repository']
 if f.is_file():m['repository_sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'active':d['active'],'copied':len(manifest),'api':d['api_source_commit']}))
