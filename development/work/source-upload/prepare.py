from pathlib import Path
import shutil,subprocess,json,hashlib,re
root=Path.cwd();repo=root/'publish/echoing-green';out=repo/'development';out.mkdir(exist_ok=True);manifest=[]
def copy(p,d):
 d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d);manifest.append({'original':str(p.relative_to(root)),'repository':str(d.relative_to(repo)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for app in sorted((root/'app').glob('runtime-cp*')):
 if not app.is_dir():continue
 dest=out/'app'/app.name
 for p in (app/'src').rglob('*'):
  if p.is_file():copy(p,dest/'src'/p.relative_to(app/'src'))
 for name in ['index.html','package.json','package-lock.json','server.mjs','decision-api.mjs','semantic-contract.json']:
  p=app/name
  if p.is_file():copy(p,dest/name)
 for p in (app/'scripts').rglob('*'):
  if p.is_file():copy(p,dest/'scripts'/p.relative_to(app/'scripts'))
 if app.name=='runtime-cp44':
  for p in (app/'tests').rglob('*'):
   if p.is_file():copy(p,dest/'tests'/p.relative_to(app/'tests'))
 if app.name in ['runtime-cp29','runtime-cp31']:
  for p in (app/'public/assets').glob('*.json'):copy(p,dest/'public/assets'/p.name)
api=root/'app/echoing-green-api'
for name in subprocess.check_output(['git','ls-files','-z'],cwd=api).decode().split('\0'):
 if name:copy(api/name,out/'api'/name)
for folder in sorted((root/'work').iterdir()):
 if not folder.is_dir()or not re.fullmatch(r'(modeling-cp\d+|lighting-cp\d+|art-cp\d+|runtime-cp\d+)',folder.name):continue
 for p in folder.iterdir():
  if p.is_file()and p.suffix in ['.py','.mjs','.js','.sh']:copy(p,out/'work'/folder.name/p.name)
(out/'source-provenance.json').write_text(json.dumps({'active':'app/runtime-cp44','api_source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=api,text=True).strip(),'files':manifest},ensure_ascii=False,indent=2))
# Portable development entrypoint; credentials remain outside this repository.
app=out/'app/runtime-cp44'
p=app/'decision-api.mjs';s=p.read_text();start=s.index('async function key()');end=s.index('\nexport async function available',start);s=s[:start]+'''async function key(){
 if(process.env.OPENROUTER_API_KEY?.trim())return process.env.OPENROUTER_API_KEY.trim();
 const file=process.env.OPENROUTER_API_KEY_FILE;if(!file)throw Error('Set OPENROUTER_API_KEY or OPENROUTER_API_KEY_FILE for local wishes.');
 const p=resolve(file),st=await stat(p);if(process.platform!=='win32'&&st.mode&0o077)throw Error('Keep the API key file readable only by its owner.');return(await readFile(p,'utf8')).trim();
}'''+s[end:];s=s.replace("resolve(project,'outputs/runtime-checkpoint-44/semantic-runs')","resolve(root,'.local/semantic-runs')");p.write_text(s)
p=app/'server.mjs';s=p.read_text().replace('checkpoint:42','checkpoint:44').replace('h?.checkpoint!==38','h?.checkpoint!==44');p.write_text(s)
p=app/'package.json';d=json.loads(p.read_text());d['scripts']['postinstall']='node scripts/prepare-assets.mjs';d['engines']={'node':'>=22.13.0'};p.write_text(json.dumps(d,indent=2)+'\n')
(app/'scripts/prepare-assets.mjs').write_text('''import{cp,mkdir}from'node:fs/promises';import{fileURLToPath}from'node:url';import{dirname,resolve}from'node:path';
const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'../../../../..');
await mkdir(resolve(here,'../public/assets'),{recursive:true});await cp(resolve(root,'assets'),resolve(here,'../public/assets'),{recursive:true});
console.log('Prepared the existing public assets for local development.');
''')
(out/'.gitignore').write_text('app/runtime-cp44/public/assets/\n**/node_modules/\n**/dist/\n**/.local/\n**/.wrangler/\n**/.next/\n**/.env\n**/.env.*\n**/*.log\nwork/**/*.json\nwork/**/*.png\nwork/**/*.wav\n')
p=repo/'.gitignore';s=p.read_text();s+='\n# Versioned source scripts; private data exclusions above still apply.\n!/development/work/\n';p.write_text(s)
(root/'outputs/source-upload/source-copy-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(json.dumps({'copied_files':len(manifest),'total_bytes':sum(p.stat().st_size for p in out.rglob('*') if p.is_file())}))
