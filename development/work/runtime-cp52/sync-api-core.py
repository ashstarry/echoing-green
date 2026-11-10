# -*- coding: utf-8 -*-
from pathlib import Path
import re,shutil
src=Path('app/runtime-cp52');api=Path('app/echoing-green-api')
for name in ['experience-choices.mjs','atmosphere.mjs','catalog.mjs','craft-design.mjs','scene-events.mjs']:
 shutil.copy2(src/'src'/name,api/'runtime'/name)
s=(src/'decision-api.mjs').read_text().split('async function key()')[0]
s=re.sub(r"import .*? from 'node:[^']+';\n",'',s).replace("const root=dirname(fileURLToPath(import.meta.url)),project=resolve(root,'../..');\n",'')
s=s.replace("JSON.parse(await readFile(resolve(root,'semantic-contract.json'),'utf8'))",(src/'semantic-contract.json').read_text().strip()).replace("JSON.parse(await readFile(resolve(root,'public/assets/runtime-registry.json'),'utf8'))",(src/'public/assets/runtime-registry.json').read_text().strip()).replace("from './src/","from '../runtime/")
(api/'server/decision-core.mjs').write_text(s)
s=(src/'tests/experience-choices.test.mjs').read_text().replace('../src/','../runtime/').replace('../decision-api.mjs','../server/decision-core.mjs');(api/'tests/experience-choices.test.mjs').write_text(s)
p=api/'tests/gateway.test.mjs';p.write_text(p.read_text().replace('Object.keys(r.questions).length,127','Object.keys(r.questions).length,128'))
print('Synced the new bounded expression question and contextual performance policy.')
