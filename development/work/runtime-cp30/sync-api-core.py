from pathlib import Path
import re,shutil
src=Path('app/runtime-cp30');api=Path('app/echoing-green-api');seen=set()
def copy(name):
 if name in seen:return
 seen.add(name);s=(src/'src'/name).read_text();(api/'runtime'/name).write_text(s)
 for child in re.findall(r"from\s*['\"]\./([^'\"]+)['\"]",s):copy(child)
for name in ['explicit-scenes.mjs','atmosphere.mjs','explicit-intents.mjs','object-actions.mjs','life-plans.mjs']:copy(name)
s=(src/'decision-api.mjs').read_text().split('async function key()')[0]
s=re.sub(r"import .*? from 'node:[^']+';\n",'',s).replace("const root=dirname(fileURLToPath(import.meta.url)),project=resolve(root,'../..');\n",'')
s=s.replace("JSON.parse(await readFile(resolve(root,'semantic-contract.json'),'utf8'))",(src/'semantic-contract.json').read_text().strip()).replace("JSON.parse(await readFile(resolve(root,'public/assets/runtime-registry.json'),'utf8'))",(src/'public/assets/runtime-registry.json').read_text().strip()).replace("from './src/","from '../runtime/")
(api/'server/decision-core.mjs').write_text(s)
s=(src/'tests/explicit-scenes.test.mjs').read_text().replace('../src/explicit-scenes.mjs','../runtime/explicit-scenes.mjs').replace('../decision-api.mjs','../server/decision-core.mjs');(api/'tests/explicit-scenes.test.mjs').write_text(s)
print('Synced pure planner dependency closure:',len(seen),'files; no private files copied.')
