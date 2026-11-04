from pathlib import Path
import json,html,csv,shutil,re,hashlib
root=Path.cwd();out=root/'outputs/runtime-checkpoint-46';report=out/'report';report.mkdir(exist_ok=True)
H=lambda s:html.escape(str(s),quote=True)
greys=json.loads((out/'frozen-grey-cases.json').read_text());runs=json.loads((out/'grey-audit-signed.json').read_text());language=json.loads((out/'language-final-78.json').read_text())+json.loads((out/'stateful-final-replay.json').read_text())
# Human-reviewed causal descriptions, separate from automatic execution evidence.
notes={
 'tea':('端茶暖手','客人靠近柜台；店员用茶壶倒茶、递杯；客人接杯饮用后放回。','茶杯有柜台和使用者，递接沿同一物件发生。局部反馈，近看更清楚。'),
 'paper':('一笺一愿','一位居民走去写笺、折好，再走到树边亲手挂起，留下这句话。','一次心愿留一张笺；保留作者和原句。阅读/收取复用原物，不让多人同时挤到树边。'),
 'umbrella':('借伞同行','两位邻居靠近，交出同一把伞、展开，短程并行，再收好。','伞由人拿取和交接；局部雨云跟随，两人共享雨具。'),
 'homecoming':('晚归开门','晚归的居民走到家门前，自己打开门；暖窗亮起，窗边邻居招手。','从最容易到达门前的人选中执行者，避免两个人挤在狭窄门口互等。没有假装建成室内生活。'),
 'spring':('花走进街角','居民从物品处拿花盆，搬到街角、摆好，折纸花展开；园丁照料花叶。','盆先被拿起再搬运，固定点位保证落脚；是几位居民的小事。'),
 'fox':('狐狸打招呼','狐狸很快抬前爪、摇尾，附近街坊回应；之后回到自然走动。','先回应再走动，不要求它先绕很远；没有整只模型原地快速打圈。'),
 'laundry':('把小布巾晾到风里','居民从篮子取布、展开，走到有支杆的晾绳前挂好；布留在风里。','工作点移出屋顶遮挡，也避开狐狸常走的地方。不会刚挂上就立即收回；之后下雨会收同一批布。'),
 'cloud':('一小片行走的雨','云移向有人活动的街段，局部落雨；下方有人撑伞，有人移开，随后云归位。','雨到哪里，附近的人才反应；并不把整座小镇都设成雨天。近看兼顾云与下面的人。'),
 'prepare':('一起准备开心的晚上','有人搬点心，有人搬小凳，孩子把纸灯递给邻居，物件摆到位。','先分工准备，再留下布置结果。交接点改到开阔处，递的是同一盏灯。'),
 'snack':('揭笼递点心','蒸笼揭开冒热气，店员端出点心递给客人；客人接过、品尝、放回。','点心来自餐厅，使用食盘与品尝动作；与喝茶的杯子/啜饮分开。'),
 'leaves':('替晚风扫扫落叶','在较空的边缘选一片落叶，一位居民拿扫帚扫拢，收进篮子。','扫帚本体会随动作摆动并接近地面；不再只有手动、扫帚不动。选择一个合适工作区，不强塞两个清扫者。'),
 'memory':('留一件小纪念','取出小件，看一看，放进柜台的纪念角；点击后可看到留下的原话。','数量有上限，原句与物件身份保留。局部细节，需要近看；不是全镇大事件。'),
 'reopen':('雨后重新生活','雨收住，居民收伞；有人擦干座椅，有人摆回商品，店员擦柜台；自行车和动物恢复日常。','动作针对实际座椅/柜台/商品，撤掉了空地上没有目标的擦拭。已有雨时会先过渡，再做整理。'),
 'music':('孩子们的小演奏','两名孩子走到乐手旁，原有的小听众也拍手；狐狸走来听琴、看向乐手、轻摇尾。','不会把全镇成年人围到中央。自行车先礼让，附近其他居民去做自己的事；与花火大会区分。'),
 'parcel':('电车捎来的包裹','电车靠站后，旅客提包裹从出口走出来，在右侧开阔处交给街坊；接收者带去餐厅放好。','只在电车和旅客可参与时推荐。交接移出车站屋顶遮挡，近看跟着包裹；物件身份不变。'),
 'pond':('喂喂池塘的鱼','桥边居民看向水面，抬手投下食物，小鱼在附近活动。','人停在桥上投喂，不把站着看水当作唯一反馈。是局部动作，不强迫其他居民集合。'),
 'night':('把纸灯带到街边','原有灯串逐渐点亮；两位居民从可见的灯架拿起纸灯，提到街边，再放回同一处。','灯、绳和支撑先就存在；手提灯经历拿取、携带、归还，不从空中长出来。暖窗与柔和夜灯保留。')}
macro={('weather','rain'):'下雨，居民撑伞或避雨',('weather','snow'):'纸雪与居民的冬日反应',('weather','clear'):'雨雪收住',('day_phase','dawn'):'晨曦',('day_phase','night'):'夜色',('day_phase','day'):'白昼',('occasion','quiet'):'安静角落与放慢脚步',('occasion','reunion'):'邻里相聚',('occasion','supper'):'热食与餐厅等候',('occasion','market'):'夜市与排队',('festival','fireworks'):'定点花火与观众',('neighborhood','homecoming'):'晚归开门与邻人招呼',('neighborhood','spring'):'搬花盆与春日变化',('neighborhood','prepare'):'分工筹备',('neighborhood','reopen'):'雨后整理',('paper','hang'):'写一张纸笺并挂起',('paper','share'):'写笺并亲手赠给邻居',('paper','read'):'读已有纸笺',('paper','collect'):'读过后收好已有纸笺',('craft','tea'):'倒茶、递杯、饮用',('craft','snack'):'揭蒸笼、递点心、品尝',('craft','umbrella'):'借伞与同行',('craft','laundry'):'展开并挂布',('craft','leaves'):'扫拢落叶',('craft','remember'):'留下纪念物',('craft','recall'):'取起阅读后放回原位',('craft','putaway'):'把纪念物从陈列收起',('journey','deliver'):'靠站包裹交接',('cloud','wander'):'局部雨云游走',('cloud','rest'):'小云归位',('music','play'):'乐手弹琴',('street','gather'):'孩子与狐狸来到乐手边',('street','wander'):'街坊恢复各自活动',('street','quiet'):'放慢街头节奏',('light','warm'):'暖灯',('light','soft'):'柔和灯光',('breeze','gentle'):'轻风',('breeze','lively'):'较活泼的风',('breeze','calm'):'风放轻'}
def meaning(row):
 p=row['plan'];parts=[]
 for i in p.get('items',[]):
  key=(i['target'],i['action']);text=macro.get(key)
  if key==('day_phase','night') and 'lantern' in (row.get('execution') or {}).get('scenes',[]):text='夜色与提灯活动'
  if not text:
   if i['target']=='animal.garden_fox':text={'greet':'狐狸摇尾招呼','play':'狐狸邀玩','rest':'狐狸歇息'}.get(i['action'],'狐狸的局部动作')
   elif i['target']=='resident.water_visitor' and i['action']=='feed_pond':text='桥边居民喂鱼'
   elif i['action']=='greet':text='一位街坊挥手回应'
   elif i.get('field')=='object.plants':text='花草随风轻摆'
   else:text=i.get('label') or (i.get('target_label','')+' '+i['action'])
  if text not in parts:parts.append(text)
 return '；'.join(parts) if parts else '确认保持原状，不触发新动作'
issues={'G16-en':'首次只让鱼觅食、缺少居民投喂；复测补上投喂者的动作与鱼的反应。','G09-en':'删除不会真正展开的第二场相聚，仅保留具体筹备流程。','E04':'集体准备优先：实际分工摆点心，不再宣称同时开三场活动。','D09':'把细雨与雨伞意象解释为一段借伞同行；这是局部阵雨，不是全镇降雨。','H07':'把对厨房灯光的想念解释为写笺留念与暖灯。','G04-zh':'首次把晚归误当接电车；增加旅程语境校验后，回到家门活动。','D12':'修复“回家”被错误转成电车迎接。','G05-zh':'首次因花草批量动作超过旧上限未执行；修复数量限制与活跃任务保留。','D06':'首次只弹琴；复测补上孩子与狐狸的局部听众。','D17':'去掉与音乐场景冲突的重复个人目的地。','D18':'首次把狐狸的心情变成全镇团聚；复测限定到狐狸。','N01':'新表达首次触发全镇团聚；复测改为橘色小家伙的局部招呼。','N02':'新表达首次触发全镇团聚；复测改为狐狸招呼。','N03':'首次误变成全镇安静；复测明确不打扰狐狸、其他人照旧。','E06':'自行航行已撤下；明确说明小舟系泊，没有船夫，不假装执行。','E07':'自行航行已撤下；说明限制，并用短招呼回应。','E09':'首次有一次未安排动作；修复后用短招呼回应无意义字符，不编造天气。','E10':'天气优先，说明本次不同时展开夜市，避免宣称两场都执行。','S01':'首次误收走纪念物；修复“放回原位”与“收起来”的区别，同一物件仍在陈列。','S02':'同一张纸笺由树上进入口袋，没有另造一张。','S03':'树上没有纸笺时说明缺少物件并招呼，不自作主张写一张。','S04':'修复过渡期提前解锁；雨收住后整理继续，收尾才解锁。','S05':'同一批已挂着的两块布被收回；无晾布时不会凭空生成待收物。'}
visual=json.loads((out/'visual-observations.json').read_text()) if (out/'visual-observations.json').exists() else []
latest={r['id']:r for r in visual}
# Include individually captured night images even if the early observation preceded the shared list.
grey_rows=[]
for idx,c in enumerate(greys,1):
 rr=[r for r in runs if r['id']==c['id']];title,effect,logic=notes[c['id']];passed=len(rr)==2 and all(not r.get('error') and r.get('phase')=='done' and r.get('progress') and all(j['status']=='done' for j in r.get('recipes',[])) for r in rr)
 files=[p.name for p in sorted((out/'evidence').glob(c['id']+'-final*.png'))];samples={v['file']:v.get('stageSeconds',0) for v in visual};files.sort(key=lambda f:samples.get(f,999));files=[f for f in files if c['id']!='music' or f=='music-final-face.png']
 if not files and c['id'] in latest:files=[latest[c['id']]['file']]
 grey_rows.append({'id':f'G{idx:02d}','key':c['id'],'zh':c['zh'],'en':c['en'],'title':title,'effect':effect,'logic':logic,'runs':len(rr),'status':'两组状态完成' if passed else '需要继续检查','durations':[r.get('seconds') for r in rr],'evidence':files})
lang_rows=[]
for r in language:
 ex=r.get('execution');category='保持不变' if not r['plan'].get('items') else '说明与招呼' if r['id'] in ['E05','E06','E07','E09','S03'] else '动作回应'
 ok=not ex or bool(ex.get('progress')) and ex.get('phase')=='done' and not ex.get('error')
 lang_rows.append({'id':r['id'],'group':r.get('group','stateful-language'),'text':r['text'],'response':meaning(r),'category':category,'status':'已核对' if ok else '未通过','seconds':ex.get('seconds') if ex else None,'request_id':r['requestId'],'provider_ms':r.get('ms'),'note':issues.get(r['id'],'已通过真实接口取得选择，并用最终执行器复测。' if r.get('verification') else '已调用真实接口并检查实际执行。'),'before':r.get('before'),'after':r.get('after'),'verification':r.get('verification','实际接口调用与执行')})
failed=[r['id'] for r in lang_rows if r['status']!='已核对'];assert not failed,failed;assert all(r['status']=='两组状态完成' for r in grey_rows),grey_rows
payload={'checkpoint':46,'grey_count':len(grey_rows),'grey_runs':len(runs),'language_cases':len(lang_rows),'grey':grey_rows,'inputs':lang_rows,'limits':'有限动作系统；这些样本不是任意语言/全部世界状态的保证。局部活动不等于全镇变化。截图为实际网页关键帧，完整状态流程另行执行验证。'}
(report/'cases.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2))
with (report/'cases.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['编号','原句','实际回应','类别','执行秒','备注']);w.writerows([r['id'],r['text'],r['response'],r['category'],r['seconds'],r['note']]for r in lang_rows)
(report/'images').mkdir(exist_ok=True)
for r in grey_rows:
 for name in r['evidence']:
  src=out/'evidence'/name
  if src.exists():shutil.copy2(src,report/'images'/name)
# The report renders text as escaped HTML; raw provider requests/responses are never packaged.
grey_html=''.join(f'''<article class="wish"><div class="eyebrow">{r['id']} · {H(r['status'])}</div><h3>{H(r['title'])}</h3><p class="quote">{H(r['zh'])}</p><p class="en">{H(r['en'])}</p><dl><dt>实际变化</dt><dd>{H(r['effect'])}</dd><dt>前因后果</dt><dd>{H(r['logic'])}</dd><dt>两次执行</dt><dd>{' / '.join(str(round(x,1))+' 秒' for x in r['durations'])} · 结束后解除输入锁</dd></dl><details><summary>查看实际网页关键画面</summary>{''.join('<figure><img loading="lazy" src="images/'+H(f)+'" alt="'+H(r['title'])+'"><figcaption>本地验收画面；左上为测试控制面板。</figcaption></figure>' for f in r['evidence']) or '<p>画面证据待补齐</p>'}</details></article>''' for r in grey_rows)
rows=''.join(f'''<tr data-group="{H(r['group'])}" data-category="{H(r['category'])}"><td>{r['id']}</td><td>{H(r['text'])}</td><td>{H(r['response'])}<span class="badge">{H(r['category'])}</span></td><td>{H(r['note'])}</td><td>{'—' if r['seconds'] is None else str(round(r['seconds'],1))+' 秒'}</td></tr>'''for r in lang_rows)
page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Echoing Green · 逐项验收记录</title><style>
:root{{color-scheme:light;--ink:#303c3a;--muted:#6d7470;--line:#ddd2bd;--gold:#966b39}}*{{box-sizing:border-box}}[hidden]{{display:none!important}}body{{margin:0;background:#f4efdf;color:var(--ink);font:15px/1.75 system-ui,-apple-system,"PingFang SC",sans-serif}}main{{max-width:1250px;margin:auto;padding:48px 28px}}a{{color:#536f63}}h1,h2,h3{{font-family:"Iowan Old Style",Georgia,"Songti SC",serif;line-height:1.3}}h1{{font-size:clamp(32px,5vw,56px);font-weight:500;margin:16px 0}}h2{{margin-top:50px;font-size:29px}}h3{{font-size:23px;margin:9px 0}}.eyebrow{{font-size:12px;letter-spacing:.12em;color:var(--gold)}}.intro{{max-width:870px;font-size:17px}}.stats{{display:flex;flex-wrap:wrap;gap:10px;margin:24px 0}}.stats span,.badge{{border:1px solid var(--line);border-radius:20px;padding:5px 12px;font-size:13px;background:#fbf8ef}}.notice{{padding:18px 22px;background:#e9edde;border-left:3px solid #758b68;border-radius:0 10px 10px 0}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}.wish{{padding:24px;background:#fffdf7;border:1px solid var(--line);border-radius:14px}}.quote{{font-size:17px;margin-bottom:3px}}.en{{font-size:13px;color:var(--muted);margin-top:0}}dt{{font-size:12px;color:var(--gold);margin-top:12px}}dd{{margin:2px 0}}details{{border-top:1px solid var(--line);padding-top:12px;margin-top:20px}}summary{{cursor:pointer;color:#516a5c}}figure{{margin:14px 0 0}}img{{width:100%;height:auto;border-radius:8px}}figcaption,.muted{{font-size:12px;color:var(--muted)}}.controls{{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0;position:sticky;top:0;background:#f4efdfed;padding:12px 0;backdrop-filter:blur(12px)}}input,select{{font:inherit;padding:10px 14px;border:1px solid var(--line);border-radius:8px;background:#fffdf7;color:var(--ink)}}input{{flex:1;min-width:220px}}.table{{overflow:auto}}table{{border-collapse:collapse;width:100%;background:#fffdf7;min-width:850px}}th,td{{text-align:left;vertical-align:top;padding:14px;border-bottom:1px solid var(--line)}}th{{font-size:13px;color:var(--gold)}}td:first-child{{white-space:nowrap;font-size:12px;color:var(--gold)}}td:nth-child(2){{width:29%}}td:nth-child(3){{width:25%}}td:nth-child(4){{width:29%;font-size:13px}}td:last-child{{white-space:nowrap}}.badge{{display:block;width:max-content;max-width:100%;margin-top:6px;padding:2px 8px;font-size:11px}}footer{{margin-top:40px;padding-top:20px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}}@media(max-width:760px){{main{{padding:28px 16px}}.grid{{grid-template-columns:1fr}}.wish{{padding:19px}}.table{{margin:0 -8px}}}}
</style><main><div class="eyebrow">ECHOING GREEN · CP46 · 2026-11-04</div><h1>一条心愿，<br>先有回应，再有来由。</h1><p class="intro">这份记录逐项列出灰字与自由输入的实际表现。检查分成<strong>真实接口选择、完整动作执行、关键画面查看</strong>三部分；不会把“接口返回了结果”直接当作画面好看、动作合理。</p><p><a href="../">回到小镇 ↗</a>　<a href="cases.csv">下载全部输入 CSV</a>　<a href="cases.json">下载结构化记录</a></p><div class="stats"><span>{len(grey_rows)} 条现行灰字</span><span>{len(runs)} 次不同状态的灰字执行</span><span>{len(lang_rows)} 句真实接口输入</span><span>一次一个互动 · 持续有进展才继续</span></div>
<div class="notice"><strong>先看这三处：</strong>无人划船的自行航行已经撤下；琴声邀请孩子与狐狸围在乐手附近，成年人照常生活；纸灯有常设灯串和真实灯架，经过拿取、携带与归还。其余检查还修了写笺拥挤、包裹遮挡、晾布位置、扫帚不随手动、回家误判成接车、纪念物误收走以及活动过渡提前解锁等问题。</div>
<h2>17 条灰字，逐条看因果</h2><p>每条分别在“运行 10 秒”和另一随机种子“运行 120 秒”的小镇状态中执行。表里的时间包含行走与收尾；不是固定时长，也不是所有设备的性能保证。小活动以明确的手部动作、道具或位置变化为目标，不要求全镇一起动。</p><p class="muted">“让小船看看池塘另一边”已从灰字、活动菜单与可选航行动作中撤下。舟仍系泊在岸边，随水轻摇。</p><div class="grid">{grey_html}</div>
<h2>全部 {len(lang_rows)} 句实际输入</h2><p>G 为 17 条灰字的中英文原句；D 为自由表达；H 为预先留出的新表达；E 为边界与否定；N 为新增动物表达；S 为带前置状态的连续互动。每句都实际调用过 Jev，原始响应留在本地档案；修复后的执行复测会复用已记录的真实响应，关键失败句另做了新调用。</p><p>“说明与招呼”代表原字面要求做不到或物件不存在，<strong>不是已完成原请求</strong>；明确要求保持原样的句子只确认，不强行动画。无法保证所有任意文字和所有拥挤状态都正确，但每个下列样本都有具体结果可追溯。</p><div class="controls"><input id="search" placeholder="搜索原句、动作或编号…" aria-label="搜索测试记录"><select id="filter" aria-label="筛选类别"><option value="all">全部记录</option><option value="grey-language">灰字中英文</option><option value="free-language">自由输入</option><option value="stateful-language">带前置状态</option><option value="保持不变">保持不变</option><option value="说明与招呼">说明与招呼</option></select><span id="count"></span></div><div class="table"><table><thead><tr><th>编号</th><th>用户原句</th><th>实际回应</th><th>合理性／复测说明</th><th>执行时间</th></tr></thead><tbody>{rows}</tbody></table></div>
<footer><p>验收边界：这是已实现动作的有限组合与较敏感的语义映射，不是任意生成新的 3D 能力。截图是实际浏览器关键帧，测试面板用于控制观察时刻；不代表逐帧录像或全部设备 FPS 测量。读茶、纪念物、写笺等属于局部反馈，建议使用“看近一点”。</p><p>细节依据：真实接口记录、两组世界状态的执行结果、对象身份/归还检查、输入锁定与过渡回归、逐项画面检查。API 密钥与原始请求档案不包含在公开报告中。</p></footer></main><script>const search=document.querySelector('#search'),filter=document.querySelector('#filter'),rows=[...document.querySelectorAll('tbody tr')];function update(){{const q=search.value.toLowerCase(),f=filter.value;let count=0;for(const r of rows){{const show=r.textContent.toLowerCase().includes(q)&&(f==='all'||r.dataset.group===f||r.dataset.category===f);r.hidden=!show;if(show)count++;}}document.querySelector('#count').textContent=count+' 条';}}search.addEventListener('input',update);filter.addEventListener('change',update);update();</script></html>'''
page=page.replace('</style>','@media(max-width:760px){.table table{min-width:0}.table thead{display:none}.table tr{display:block;margin:12px 0;border:1px solid var(--line);border-radius:12px;padding:10px}.table td{display:block;width:auto!important;border:0;padding:5px 8px}.table td:nth-child(2){font-size:17px}.table td:nth-child(3){color:#466553}.table td:last-child{font-size:12px;color:var(--muted)}}'+'</style>');(report/'index.html').write_text(page)
print(json.dumps({'grey':len(grey_rows),'runs':len(runs),'inputs':len(lang_rows),'images':len(list((report/'images').glob('*.png'))),'categories':{k:sum(r['category']==k for r in lang_rows)for k in set(r['category']for r in lang_rows)}},ensure_ascii=False))
