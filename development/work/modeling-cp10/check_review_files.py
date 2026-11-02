from pathlib import Path
from html.parser import HTMLParser
import json,subprocess,ast,re
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-10';WORK=ROOT/'work/modeling-cp10'
class Page(HTMLParser):
 def __init__(self):super().__init__();self.refs=[];self.ids=[];self.scripts=[];self.inscript=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  for k in ['src','href','data-view']:
   if a.get(k) and not a[k].startswith(('http:','https:','#','data:')):self.refs.append(a[k])
  if 'id'in a:self.ids.append(a['id'])
  if tag=='script':self.inscript=True
 def handle_endtag(self,tag):
  if tag=='script':self.inscript=False
 def handle_data(self,data):
  if self.inscript:self.scripts.append(data)
p=Page();html=(OUT/'review.html').read_text();p.feed(html);p.refs.extend(re.findall(r"src:'([^']+)'",html));missing=[x for x in p.refs if not(OUT/x).is_file()];assert not missing,missing;assert len(p.ids)==len(set(p.ids))
js=WORK/'review-script.js';js.write_text('\n'.join(p.scripts));r=subprocess.run(['node','--check',str(js)],capture_output=True,text=True);assert r.returncode==0,r.stderr
for f in (OUT/'source').glob('*.py'):ast.parse(f.read_text())
data={'passed':True,'local_file_references':len(p.refs),'missing_files':missing,'unique_ids':len(p.ids),'javascript_syntax_passed':True,'python_source_syntax_passed':True,'browser_visual_qa':False,'scope':'Local HTML references, IDs and script syntax only. Scene images individually inspected; not browser execution or rendering validation.'};(OUT/'review-validation.json').write_text(json.dumps(data,indent=2));print(json.dumps(data))
