from pathlib import Path
import json,hashlib,re,shutil,html,statistics
R=Path.cwd();A=R/'app/runtime-cp27';O=R/'outputs/runtime-checkpoint-27'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for c in iter(lambda:f.read(1048576),b''):h.update(c)
 return h.hexdigest()
def read(p):return json.loads((O/p).read_text())
base=read('poetry-results.json');improved=read('integrated-poetry/poetry-results.json');confirmation=read('confirmation-results.json');matrix=read('mood-state-matrix.json');tests=(O/'tests-final.txt').read_text();assert '# fail 0' in tests;passed=int(re.search(r'# pass (\d+)',tests)[1])
records=[]
for folder in[O/'semantic-runs',O/'mood-experiment']:
 for p in folder.glob('*.json'):
  x=json.loads(p.read_text())
  if isinstance(x,dict)and x.get('request_sent')and x.get('id'):records.append((p,x))
ledger={'scope':'CP27 only; prior experiments and raw calls preserved','actual_posts':len(records),'cost_usd':round(sum(x.get('response',{}).get('usage',{}).get('cost',0)or 0 for p,x in records),9),'runs':[{'id':x['id'],'file':str(p.relative_to(O)),'ms':x.get('ms'),'cost':x.get('response',{}).get('usage',{}).get('cost')}for p,x in records]};(O/'api-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2))
unchanged=['src/simulation.mjs','src/community.mjs','src/life-plans.mjs','src/town-response.mjs','src/navigation.mjs','src/motion.mjs','src/foot-support.mjs','src/passengers.mjs','src/life-view.mjs','src/art-direction.mjs','src/environment-view.mjs','src/view-director.mjs','src/response-markers.mjs','public/assets/town.glb'];checks={p:sha(A/p)==sha(R/'app/runtime-cp26'/p)for p in unchanged};assert all(checks.values());(O/'world-unchanged.json').write_text(json.dumps(checks,indent=2))
poetic=lambda rows:[r for r in rows if not r['control']]
summary={'checkpoint':27,'brand':{'zh':'言外','en':'Afterwords','scene_zh':'借风町','scene_en':'Borrowed Wind Town'},'url':'http://127.0.0.1:4240/','ui_languages':['zh','en'],'single_call_model':'typesafe/jev-1.14','baseline':{'poetic_cases':16,'nonempty':sum(r['nonempty']for r in poetic(base)),'control_false_triggers':sum(r['nonempty']for r in base if r['control'])},'same_cases_after_change':{'nonempty':sum(r['nonempty']for r in poetic(improved)),'noticeable_proxy':sum(r['noticeableProxy']for r in poetic(improved)),'strict_original_domain_check_pass':sum(r['scopePlausible']and r['nonempty']for r in poetic(improved)),'control_false_triggers':sum(r['nonempty']for r in improved if r['control'])},'fresh_confirmation':{'poetic_cases':8,'accepted':sum(r['pass']for r in confirmation if r['expected']=='mood'),'keep_controls_pass':sum(r['pass']for r in confirmation if r['expected']=='none'),'literal_controls_pass':sum(r['pass']for r in confirmation if r['expected']in ['reader','rain'])},'execution_matrix':{'cases':len(matrix),'noticeable_proxy':sum(r['noticeableProxy']for r in matrix),'failed_jobs':sum(r['failedJobs']for r in matrix)},'logic_tests_passed':passed,'api_posts':ledger['actual_posts'],'api_cost_usd':ledger['cost_usd'],'locomotion_and_assets_unchanged':True,'perception_proxy_not_human_accuracy':True};(O/'delivery-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
note=f'''言外 / Afterwords · CP27 检查点

打开：http://127.0.0.1:4240/
启动：app/runtime-cp27/打开言外.command
当前小镇仍叫借风町，保存键仍borrowed-wind-cp24-v2，没有重置世界。没有发布到互联网。

名字
采用「言外 · Afterwords」。典故来自欧阳修《六一诗话》所记梅尧臣论诗：“含不尽之意，见于言外。”取意于语言的留白和读者会意；Afterwords是创作性英文对应，暗含话语之后世界开始回应，不冒称古典原词的直译。中文题签：话语落下，小镇有了回声。英文：Words settle. A world stirs.
原文：https://zh.wikisource.org/zh-hans/六一詩話 （梅圣俞论诗段）。本版采用这一名称，当前场景仍保留借风町及已认可的纸雕和风风格。

氛围输入实验：先失败，再修正，分别保留
第一轮冻结16句中英文纯氛围/诗意话语，加4句赞美、保持现状和假设对照。旧入口16句均无执行安排，4对照没有误触发。不是Jev没被调用，而是原入口用明确对象和逐项动作范围限制诗意输入。
另做2问题的整体氛围实验，比较同20句，并额外冻结12句新表达（9氛围、3对照）。此为独立探索，不冒称已接入3D的结果。
最终把mood_intent与atmosphere加入同一次Jev请求；不是前置生成式LLM，也没有串联第二次API。正常请求112个选择问题，点选可动作物件另加2个。模型可选6种整体方向：温柔、相聚、庆祝、梦境、静谧、希望。本地将方向组合为已有的光、风、日夜和集体活动。它们不是6段固定录像，居民仍按当前状态、空间和避让规则行动；原32居民的独立行为仍在。
同一16句修订后15句有安排并达到模拟可见指标，4对照仍未误触发。这是已见句对照，不是独立准确率。另冻结的8句新氛围表达有7句接住，2句保持现状与2句具体动作对照均正确。英文天气、合书、保持不变又另做3句检查，均通过。
“今晚的小镇，像有人留了一把空椅子。”仍被保守保留；“一封没有写完的信”在原组也未触发。不能说任意隐晦句子都能变成正确效果。

怎样判断明显
使用同种子、同初始状态，与无输入自然运行对照，分别在20秒/45秒观察。可见代理指标为：至少3个街行居民相对对照的位置差超过1模型单位，或天气/日夜/花火状态不同。它不是主观艺术感评分，也不是米数、所有人都移动或整句语义百分百正确。
另用6个氛围方向×晴朗黄昏/雨夜夜晚/雪天白昼做18组执行回放，18组达到上述指标，没有任务失败。没有另算成18次模型准确率。
预先允许领域的严格检查也保留：修订后只有7句非空结果完全落在原先较窄的领域集合；另外8句带了设计上附加的暖灯、风、转夜等配套。例如“相聚”配暖灯、“庆祝”配夜晚。这些是人工设定的氛围组合，不伪称Jev逐项独立理解了每个变化。用户可撤回。
实际网页已验证英文There is a reunion waiting in the air.，Jev选择together，并显示完整英文回应。更隐晦/多义的表达可能保留原状；赞美和明确不改动会友好说明“保持现在安排”，不再误说没有理解。

双语
右上角English/中文切换，偏好保存在afterwords.locale.v1，和世界存档分离。标题、按钮、角色/动作、选中角色意图、反馈、事件、提示、无障碍文本、名字说明与动作总表均有英文呈现。用户原话不翻译、不清空，模型ID不变；切换时保留输入、选中角色、暂停和模拟进度。
采用显式writeText/源文案目录，未用全页MutationObserver或外部翻译服务。保存与模拟继续保留原始语义数据，避免语言切换改变行为。234行动目录行实际检查没有残留中文（语言切换按钮除外）；32居民菜单逐一检查并修复发现的遗漏，所有采集的源文案和236个可选目录标签都有英语映射。旧动作总表链接继续有效，CSV原始数据保留中文并标注。
手机390×844实际检查无横向溢出；普通宽屏与手机仍保留原来的全景/近景。静态/demo/路径实际打开、切换语言、打开并搜索动作表，无API请求。静态版只提供本地活动，诗意语义仍需要本地代理。

保持的范围与验证
{passed}项测试通过；模型、材质、镜头方向、移动/避让/脚部支撑、6首柔和音乐的合成逻辑均保留。声音按钮仅加了翻译。脚边低透明度圆环保留，没有恢复头顶文字。
本轮没有新建角色模型/路线，未重跑或扩大CP26的49011姿态几何检查；该证据仅在原有限场景范围内继承。新增验证为语义原始响应、成对模拟、跨状态执行、语言状态保持、源文案完整性和实际网页。不能用这些结果保证所有新输入下的连续碰撞或全场景准确性。

保存
本轮实际模型POST共{ledger['actual_posts']}次，response.usage.cost合计${ledger['cost_usd']:.9f}，含基线、探索、整合复测、新句确认、英文控制和实际页面验证，分组原始记录保留。旧项目账本不覆盖。凭证不在前端和归档。source/是本版源码快照，scripts/是复现脚本；这仍是本地档案，不是云备份。
''';(O/'检查点说明.txt').write_text(note)
rows=[]
for a,b in zip(base,improved):
 if a['control']:continue
 moved=max(len(z['actorsDifferentFromControl'])for z in b['observations']);choices=b['plan'].get('resolution')or{};rows.append('<tr><td>'+html.escape(a['text'])+'</td><td>'+('无安排'if not a['nonempty']else'有安排')+'</td><td>'+html.escape(b['plan']['summary'])+'</td><td>'+('达到代理指标'if b['noticeableProxy']else'未触发')+f' · 对照位置差人数 {moved}</td></tr>')
page='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>言外 · 氛围与双语检查点</title><style>body{background:#27242d;color:#f1e1ca;font:16px/1.8 system-ui;margin:0}main{max-width:1200px;padding:32px 24px;margin:auto}h1{font:40px "Songti SC",serif}a{color:#e0b77e}img{max-width:100%;border-radius:12px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ffffff20;padding:10px;text-align:left;vertical-align:top}.scroll{overflow:auto}small{color:#baaea2}@media(max-width:700px){.grid{grid-template-columns:1fr}h1{font-size:32px}}</style><main><p>CP27 / 言外 · Afterwords</p><h1>话语落下，小镇有了回声。</h1><p><a href="http://127.0.0.1:4240/">打开小镇</a> · <a href="action-list.html">双语动作总表</a> · <a href="检查点说明.txt">完整实验说明</a></p><p>取意于《六一诗话》所记“含不尽之意，见于言外”。Afterwords是创作性英文对应，当前场景仍叫借风町。</p><div class="grid"><div><img src="afterwords-zh.jpg"><p>中文界面 · 实际网页</p></div><div><img src="afterwords-en.jpg"><p>English interface · actual webpage</p></div></div><h2>先测现状，再修入口</h2><p>旧入口16句纯氛围话语均无安排；修订后同组15句有安排并达到模拟可见代理指标。另8句新表达中7句被接住；保持现状和具体动作对照均正确。一次Jev调用同时判断具体意图与整体氛围。</p><p><small>代理指标不是人的艺术感评分。同组复测是已见数据；暖灯、夜色等配套来自设计好的组合，不是每一项都由原句明确指定。非常隐晦的空椅子、未完信件仍有边界。</small></p><h2>逐句对照</h2><div class="scroll"><table><tr><th>输入</th><th>原入口</th><th>新解释</th><th>模拟观测</th></tr>'''+''.join(rows)+'''</table></div><p>可以试：“空气里像有一场久别重逢。” “给这个疲惫的傍晚一点喘息。” “这片灯火，应该配得上一场小小的欢喜。”</p><p><a href="https://zh.wikisource.org/zh-hans/%E5%85%AD%E4%B8%80%E8%A9%A9%E8%A9%B1">典故原文</a> · <a href="api-ledger.json">本轮实验账本</a></p></main>''';(O/'review.html').write_text(page)
for f in ['检查点说明.txt','delivery-summary.json','api-ledger.json','review.html','afterwords-en.jpg','afterwords-zh.jpg','mobile-en.jpg','mobile-zh.jpg']:
 assert(O/f).exists(),f;shutil.copy2(O/f,A/'public/assets'/f)
cap=json.loads((A/'public/assets/runtime-capabilities.json').read_text());cap.update(checkpoint=27,brand=summary['brand'],ui_languages=['zh','en'],atmosphere_directions=6,atmosphere_same_api_call=True,overhead_labels=False,affected_actor_paper_marks=False,affected_actor_faint_foot_ring=True);(A/'public/assets/runtime-capabilities.json').write_text(json.dumps(cap,ensure_ascii=False,indent=2));shutil.copy2(A/'public/assets/runtime-capabilities.json',O/'runtime-capabilities.json')
dest=O/'source';shutil.copytree(A,dest,dirs_exist_ok=True,ignore=shutil.ignore_patterns('node_modules','dist','.DS_Store'));scripts=O/'scripts';scripts.mkdir(exist_ok=True)
for p in(R/'work/runtime-cp27').iterdir():
 if p.is_file()and p.suffix in ['.mjs','.py','.txt','.json']:shutil.copy2(p,scripts/p.name)
(O/'source-manifest.json').write_text(json.dumps({str(p.relative_to(dest)):sha(p)for p in dest.rglob('*')if p.is_file()},ensure_ascii=False,indent=2));files=[p for p in O.rglob('*')if p.is_file()and p.name!='artifact-manifest.json'];assert not any(re.search(rb'sk-or-v1-[A-Za-z0-9_-]{30,}',p.read_bytes())for p in files);(O/'artifact-manifest.json').write_text(json.dumps({str(p.relative_to(O)):sha(p)for p in files},ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False))
