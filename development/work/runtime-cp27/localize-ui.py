from pathlib import Path
import re
A=Path('app/runtime-cp27')
# Replace only the UI's text setters, keeping source strings out of persisted simulation state.
def transform(text):
 pat=re.compile(r"(document\.querySelector\((?:'[^']*'|\"[^\"]*\")\)|[A-Za-z_$][\w$]*)\.textContent\s*=")
 replacements=[]
 for m in pat.finditer(text):
  i=m.end();depth=0;quote=None;escape=False;j=i
  while j<len(text):
   c=text[j]
   if quote:
    if escape:escape=False
    elif c=='\\':escape=True
    elif c==quote:quote=None
   elif c in "'\"`":quote=c
   elif c in '([{':depth+=1
   elif c in ')]}':depth-=1
   elif c==';'and depth==0:break
   j+=1
  assert j<len(text),(m.group(0),i)
  replacements.append((m.start(),j,'writeText('+m.group(1)+','+text[i:j]+')'))
 for start,end,repl in reversed(replacements):text=text[:start]+repl+text[end:]
 return text
for name in ['main.mjs','reaction-feedback.mjs','sound.mjs']:
 p=A/'src'/name;s=transform(p.read_text());s="import {writeText,t,initializeI18n} from './i18n.mjs';\n"+s
 if name=='main.mjs':s=s.replace('let viewDirector=null;', 'initializeI18n();\nlet viewDirector=null;').replace('b.title=trial.description','b.title=t(trial.description)')
 p.write_text(s)
p=A/'index.html';s=p.read_text().replace('<title>借风町 · 一句话，成为晚风</title>','<title>言外 · 话语落下，小镇有了回声</title>').replace('<span class="eyebrow">言灵世界</span><h1>借风町</h1><p>让一句话，成为晚风。</p>','<span class="eyebrow">借风町 · 微观世界</span><h1 title="取意于《六一诗话》：含不尽之意，见于言外。">言外</h1><p>话语落下，小镇有了回声。</p>').replace('<nav><button id="sound"','<nav><button id="language" type="button">English</button><button id="sound"').replace('href="/assets/动作总表.html"','href="/assets/action-list.html"')
s=s.replace('<details><summary>运行检查</summary>', '<details><summary>关于名字</summary><p>“含不尽之意，见于言外。”取意于《六一诗话》所记梅尧臣论诗。Afterwords 是英文创作性对应：话语之后，世界开始回应。</p><p><a href="https://zh.wikisource.org/zh-hans/%E5%85%AD%E4%B8%80%E8%A9%A9%E8%A9%B1" target="_blank" rel="noopener">阅读典故原文 ↗</a></p></details><details><summary>运行检查</summary>')
p.write_text(s)
print('Explicit bilingual UI renderers wired; world state and input values unchanged.')
