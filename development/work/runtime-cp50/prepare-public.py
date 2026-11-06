from pathlib import Path
import shutil,subprocess,re,json,hashlib,struct
root=Path.cwd();app=root/'app/runtime-cp50';out=root/'publish/echoing-green';report=root/'outputs/runtime-checkpoint-50'
subprocess.run(['node','scripts/build.mjs'],cwd=app,check=True)
out.mkdir(parents=True,exist_ok=True)
for name in ['index.html','src','vendor']:
 source=app/'dist'/name;dest=out/name
 if source.is_dir():shutil.copytree(source,dest,dirs_exist_ok=True)
 else:shutil.copy2(source,dest)
# Exclude byte-identical local duplicate decoder copies from the generated bundle.
for p in (out/'vendor').rglob('*'):
 if p.is_file() and re.search(r' \d+(?=\.|$)',p.name):
  original=p.with_name(re.sub(r' \d+(?=\.|$)','',p.name))
  if not original.exists() or p.read_bytes()!=original.read_bytes():raise RuntimeError('Unexpected vendor duplicate')
  p.unlink()
(out/'src/deployment-config.mjs').write_text("// Public URL only; provider credentials live in the cloud Secret store.\nexport const API_BASE = 'https://echoing-green-api.dongyuanshun.chatgpt.site';\n")
assets=set(re.findall(r"['\"]/assets/([^'\"]+)",(app/'src/main.mjs').read_text()))
assets.update(['interaction-catalog.json','lanterns-awake-loop.wav','action-inventory.json','action-list.html','动作总表.csv','动作总表.html'])
(out/'assets').mkdir(exist_ok=True)
for name in sorted(assets):shutil.copy2(app/'public/assets'/name,out/'assets'/name)
(out/'.nojekyll').write_text('')
(out/'CNAME').write_text('koyoi.fun\n')
(out/'.gitignore').write_text('.env\n.env.*\n*.key\n*.pem\n*.log\n.DS_Store\nnode_modules/\nwork/\nprivate/\noutputs/\n')
(out/'README.md').write_text('''# Koyoi · 今宵

A living, cut-paper miniature town. Current scene: Borrowed Wind Town / 借风町.

Public website: https://koyoi.fun/ . The frontend stays on GitHub Pages; Cloudflare provides the domain and DNS. New visitors begin with the default town, with browser-local saves on this domain.

English is the first-visit default. Music is enabled by default; browser autoplay rules may require your first click or keypress. Language and sound choices are saved locally.

The town simulates life in your browser and pauses when you leave. Snow, rain, fireworks and market gatherings are short events with arrivals, a main scene, and a gentle closing. Self-propelled boat trips are retired. The fox has slender articulated paper legs, trots across open ground, then raises its front paws and nuzzles near a neighbor. A nearby neighbor can make room for a local greeting. Tram gifts are collected from a visible luggage tray and passed to a neighbor. Local protagonists are followed by a small breeze of folded cherry petals, with subtle warm fill. Street paper lamps brighten one by one at a gentle pace. Children and the fox listen beside the guitarist; paper lamps are physically taken from stands and returned. See [the complete interaction verification](verification/) for all tested wishes. One user-triggered interaction runs at a time. Input and activity choices stay locked until it finishes. Activities continue while their visible response progresses and wind down when that response settles or stalls; there is no fixed 15-second cutoff. Tram greetings appear only when the tram and traveler are ready. Sparse event sounds accompany selected fireworks, market opening and closing; the master sound switch controls both music and effects. Use weather buttons, the Town journal and selectable actions to explore. Free-text wishes use a separately hosted secure Jev proxy; no provider credentials are included in this repository or in GitHub Pages.

## Run locally

Serve this directory with any static HTTP server. No build step is required for this public snapshot. GitHub Pages serves the main branch root.

## Sources and credits

- Koyoi means 今宵 / tonight in Japanese: https://kotobank.jp/word/今宵-505038
- Three.js and its decoder libraries retain their bundled license notices under `vendor/`.
- Default background music: the user-provided **灯火未眠 B — game loop**, played at its original speed and pitch.
- Town models, scene design, behavior logic and original soft chiptune arrangements are project assets. No license grant is implied for these assets.

## Security

Never add API keys, private configuration, raw API logs or research archives. `src/deployment-config.mjs` may contain only a public proxy URL. The provider key belongs in the proxy host’s secret storage, never in frontend environment variables or repository files.
''')
with (out/'.gitignore').open('a') as f:f.write('\n# Ignore desktop-generated vendor copies.\nvendor/**/* [0-9]*\n')
# Keep the editable source entry visible across future frontend releases.
if (out/'development').exists():
 with (out/'README.md').open('a') as f:f.write('\n## Editable source and project history\n\nSee [development/](development/README.md) for current editable code, API source, tests and authoring history.\n')
 with (out/'.gitignore').open('a') as f:f.write('\n!/development/work/\n')
# A release-wide module tag prevents mixed old/new module graphs in Pages caches.
module_files=sorted((out/'src').glob('*.mjs'))
version='cp50-friendly-fox-'+hashlib.sha256(b''.join(p.name.encode()+p.read_bytes() for p in module_files)).hexdigest()[:12]
for module in module_files:
 text=module.read_text()
 text=re.sub(r"((?:from\s*|import\s*\(\s*|import\s*)['\"])(\./[^'\"?]+\.mjs)(['\"])",lambda m:m[1]+m[2]+'?v='+version+m[3],text)
 # Stamp changed models/routes too, so cached CP29 geometry cannot mix with CP30 rigs.
 text=re.sub(r"(['\"])(\./assets/[^'\"?]+\.(?:json|glb|png))(['\"])",lambda m:m[1]+m[2]+'?v='+version+m[3],text)
 module.write_text(text)
p=out/'index.html';p.write_text(p.read_text().replace('./src/main.mjs','./src/main.mjs?v='+version).replace('./src/style.css','./src/style.css?v='+version))
for name in ['action-list.html','动作总表.html']:
 p=out/'assets'/name;p.write_text(p.read_text().replace('../src/i18n.mjs','../src/i18n.mjs?v='+version))
(out/'release.json').write_text(json.dumps({'release':version,'checkpoint':50,'brand':'Koyoi'},indent=2))
patterns={
 'provider_token':re.compile(rb'sk-(?:or-v1-)?[A-Za-z0-9_-]{24,}'),
 'github_token':re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})'),
 'private_key':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
 'local_user_path':re.compile(rb'/Users/|/home/ashstarry/'),
}
# Exact private credentials are compared in memory, never printed or copied.
known=[]
key=root/'work/private/openrouter.key'
if key.exists():known.append(key.read_bytes().strip())
findings=[];manifest=[]
for p in sorted(out.rglob('*')):
 if '.git' in p.relative_to(out).parts or p.relative_to(out).parts[0]=='development':continue
 if p.is_symlink():raise RuntimeError('Symlink in public package')
 if not p.is_file():continue
 data=p.read_bytes();rel=str(p.relative_to(out));manifest.append({'path':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 for name,pattern in patterns.items():
  if pattern.search(data):findings.append({'path':rel,'kind':name})
 for secret in known:
  if secret and secret in data:findings.append({'path':rel,'kind':'known_private_credential'})
 forbidden=['api-ledger','delivery-summary','review.html','检查点说明','server.mjs','decision-api.mjs','.command','semantic-runs']
 if any(x in rel for x in forbidden):findings.append({'path':rel,'kind':'non_public_file'})
# Source is versioned separately from the frontend package but still checked for credentials.
source_files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z','--','development'],cwd=out).decode().split('\0') if (out/'development').exists() else []
for rel in set(source_files):
 if not rel:continue
 p=out/rel
 if not p.is_file():continue
 data=p.read_bytes()
 for name,pattern in patterns.items():
  if name!='local_user_path' and pattern.search(data):findings.append({'path':rel,'kind':name})
 for secret in known:
  if secret and secret in data:findings.append({'path':rel,'kind':'known_private_credential'})
result={'file_count':len(manifest),'total_bytes':sum(x['bytes'] for x in manifest),'findings':findings,'files':manifest}
(report/'public-package-scan.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False))
if findings:raise SystemExit('Public package blocked by security scan')
