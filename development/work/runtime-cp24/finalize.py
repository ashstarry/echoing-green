from pathlib import Path
import json,hashlib,re,shutil,subprocess,html
R=Path.cwd();O=R/'outputs/runtime-checkpoint-24';A=R/'app/runtime-cp24'
def read(name):return json.loads((O/name).read_text())
def sha(path):
 h=hashlib.sha256()
 with path.open('rb')as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
capture=R/'work/runtime-cp24/capture-round6/browser-mesh-motion.json'
contacts,support=read('contacts-final.json'),read('support-final.json')
assert contacts['passed'] and support['passed'],'Physical checks must pass before packaging'
digest=sha(capture);assert contacts.get('capture_sha256')==digest==support.get('capture_sha256'),'Checks must refer to final capture'
tests=(O/'logic-tests-final.txt').read_text();assert re.search(r'# fail 0\b',tests),'Logic suite must pass'
test_count=int(re.search(r'# pass (\d+)',tests).group(1))
inv=read('action-inventory.json');stats=inv['stats'];runs=[]
for p in (O/'semantic-runs').glob('*.json'):
 r=json.loads(p.read_text());raw=r.get('response',{});runs.append({'id':r['id'],'file':str(p.relative_to(R)),'model':raw.get('model',r['model']),'http_status':r.get('status'),'ms':r.get('ms'),'cost_usd':raw.get('usage',{}).get('cost'),'request_sent':r.get('request_sent',False),'error':r.get('error')})
ledger={'scope':'CP24 only; prior experiments unchanged','actual_posts':sum(r['request_sent']for r in runs),'cost_usd':round(sum(r['cost_usd']or 0 for r in runs),9),'runs':runs};(O/'api-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2))
old=json.loads((R/'outputs/runtime-checkpoint-22/source-manifest.json').read_text());changed=[p for p,h in old.items()if sha(R/'app/runtime-cp22'/p)!=h];assert not changed
(O/'cp22-preserved.json').write_text(json.dumps({'checked':len(old),'changed':changed,'passed':not changed},indent=2))
capabilities={'checkpoint':24,'semantic_model':'typesafe/jev-1.14','provider':'OpenRouter','generative_frontend':False,'network_calls_per_utterance':1,'simulation':'independent browser session; pause/save on leaving; no offline catch-up','residents':32,'resident_goal_labels':stats['resident_action_vocabulary'],'resident_goal_bindings':stats['resident_assignments'],'compound_goals':8,'object_groups_in_language':15,'selected_registered_object_actions':True,'macro_domains':['weather','day_phase','light','breeze','festival','occasion','train'],'day_phases':['dawn','day','dusk','night'],'new_runtime_effect':'effect.daylight_sun','constraints':['Finite action and identity allowlists','Independent scope judgments plus deterministic guards','Role/held-prop/route/weather checks','Completion-based sequences','No teleport for undo or replanning','Full roofs retained'],'limits':['No arbitrary house entry or unrestricted navigation','Reader stays at bench; bridge residents stay in their reserved areas','One validated passenger/vehicle boarding route','Bicycle glides/stops; no full pedaling or dismount','No bird landing/nesting; boat remains moored','Ambiguous/unsupported requests may be withheld; semantic accuracy is not universal']}
for p in [O/'runtime-capabilities.json',A/'public/assets/runtime-capabilities.json']:p.write_text(json.dumps(capabilities,ensure_ascii=False,indent=2))
note=f'''借风町 CP24 · Jev 接入与可见的生活

打开实时小镇：http://127.0.0.1:4240/
动作总表：http://127.0.0.1:4240/assets/动作总表.html
启动：在 Finder 双击 app/runtime-cp24/打开借风町.command。关闭启动终端会停服务；浏览器保存小镇状态。这里仍是独立的本地浏览器小镇，没有上线或全天候模拟。

这次完成的体验
Jev 已通过 OpenRouter 真正接到小镇。一次原话请求同时返回有限动作与对象范围判断，本地执行器再检查当前状态和时序；没有前置生成式大模型。32 位居民、15 组物件和7个环境领域可参与选择；点选具体已注册物件时，可以单独使用其已有动作。书、杯、壶、椅子等动作会落到真实使用者，不重复下发。

新增8种连贯生活目标：合书喝茶再读；喂鱼、指给同伴看再聊天；检查花叶、浇水再招呼；擦柜台后端点心迎客；出来吃点心喝茶再回帘内；上露台眺望再走回街边；核对信件再沿街走；弹一小段琴后休息打招呼。
每步等待真实完成。普通可打断姿势约0.65秒柔和收住，再响应新愿望；手持饮食、投喂和行走转场保留安全收尾。雨天安排会等待条件；未知或含糊的请求可能暂不下发。撤回恢复意愿，位置和时间不会倒带。

全镇可以在晨曦、白昼、黄昏、夜晚之间渐变。增加了真实低面数纸雕太阳，月亮和星星随时段变化；日夜带出错开的角色反应，夜晚与雨中仍保持可见。自动花火只在暮色/夜间发生；用户停止花火会同时关掉未来自动演出。
默认画面更充分使用宽屏空间；保留固定43度方向，支持平滑近景、跟随所选对象、手动拖动取消跟随、回到全景。手机近景单独放大，并用真实投影检查避开底部输入卡。文字提示是辅助，光圈已不作为主要反馈。画面提供流畅/细腻两档；默认流畅，模型、灯光参数和动作不减少。单个预览实例的固定种子绘制测量中，流畅档约12.0–12.1ms/帧，细腻档约13.3ms/帧（每档60样本，包含GPU完成等待）。这不是实时显示帧率或手机硬件保证；多开预览会争用资源，原始测量也保留。

真实动作数量
32 位居民，每人{stats['resident_min']}–{stats['resident_max']}个可选目标；{stats['resident_action_vocabulary']}类人物行为目标、{stats['resident_assignments']}条人物—目标绑定。新增8种是复用现有动作的连贯目标，不是8套新动画。202个非人物组件（含成组效果），196个有独立或联动控制；完整范围见动作总表。

验证
{test_count}项逻辑、存档、导航、动作、范围、脚部支撑和镜头投影测试通过。
最终完整实际浏览器采样300秒、1201帧、{contacts['body_poses']}个主体姿态，检查网格表面、动态环境和牵线；0项意外交叉。{support['actor_samples']}组真实鞋底支撑采样通过。原失败记录保留：初始雨伞扫到车筐、桥底擦板、狐尾擦灯柱、乘车后姿势残留，以及后续脚尖擦砖/统一抬脚导致悬空。最终采用实际砖面独立支撑数据（约0.4MB），不是把所有脚一直垫高。
修复人车互等：从动态占用的起始格重新找路时，朝畅通的下一处前进，保留距离检查。原有孩子活动与骑行停靠测试恢复通过，没有放松标准。
这些是已列场景和离散采样，不是对任意未来输入、所有连续时刻的数学保证。碰撞与落脚检查直接使用最终捕获数据的SHA256：{digest}。

语言实验的实情
既有CP23测试、CP24开发/回归、10条新表达、点选物件测试都分别保存。修订过程不合并成普遍准确率：10条当时未参与修订的新表达9/10，另1句被门槛过严拦下；之后环境门槛有所调整。点选灯、书、杯、工作台、风筝、纸鸟的最后6项全部通过，但属于修订后的复测。真实网页已验证停用花火、夜晚加落雪、停雪回黄昏并安排读者生活片段。
本轮实际模型POST {ledger['actual_posts']}次，response.usage.cost合计 ${ledger['cost_usd']:.9f}；这不是整个账号或全部历史项目的账单。所有请求、响应、耗时与失败样本在semantic-runs/，接口凭证未放进网页、报告或源码归档。

仍保留的边界
没有任意生成新物件、任意房屋进出、鸟归巢、自由航船、全镇自由导航或完整骑车蹬踏/下车。读者留在长椅，桥上两人在自己的安全区域；乘车路线目前只开放一位旅客。复杂省略或含糊指代仍可能被保守拦下，可先点选对象再说。

来源与复现
app/runtime-cp24/ 为运行源码；source/为本次快照；原CP22的64个归档文件未变。GLB沿用CP22，日夜太阳是运行时真实几何，新落脚和行为在代码中完成，不伪称改过Blender母版。可编辑母版仍见 outputs/runtime-checkpoint-22/borrowed-wind-town-cp22.blend。
原始运动矩阵在 work/runtime-cp24/capture-round1…6/；6轮完整数据同时无损压缩存于 captures/，解压后的SHA256逐一验证，索引为capture-archive-index.json。最后的捕获与检查脚本在 scripts/。静态交付版已在/demo/子路径实际打开，动作表可用，未发送API请求；该版只有本地生活，Jev需要本地代理。归档保存在本地，没有云部署。
'''
(O/'检查点说明.txt').write_text(note)
summary={'checkpoint':24,'model':'typesafe/jev-1.14','test_count':test_count,'contacts':{'passed':True,'body_poses':contacts['body_poses'],'frames':1201,'capture_sha256':digest},'support':{'passed':True,'actor_samples':support['actor_samples']},'stats':stats,'api_posts':ledger['actual_posts'],'api_cost_usd':ledger['cost_usd'],'cp22_unchanged':True,'review_url':'http://127.0.0.1:4240/','not_a_continuous_physics_guarantee':True}
(O/'delivery-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
cards=[('overview-final.jpg','更大的全景，保持纸雕小镇的温暖'),('night-snow.jpg','夜晚与落雪，人物和桥面仍可看清'),('reader-near.jpg','近看手中的书与小动作'),('mobile-near.jpg','手机近景：操作与主体分开')]
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>借风町 CP24 · 心愿开始生活</title><style>body{margin:0;background:#25232c;color:#f4e3c8;font:16px/1.8 system-ui}main{max-width:1200px;margin:auto;padding:40px 26px}h1{font:40px "Songti SC",serif}h2{font-size:22px;font-weight:500}a{color:#e4b878}.entry{display:inline-block;background:#d7ad75;color:#302a2c;padding:10px 18px;border-radius:9px;text-decoration:none;margin-right:12px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}figure{margin:0;background:#302c35;padding:14px;border-radius:14px}img{max-width:100%;max-height:650px;display:block;margin:auto;border-radius:9px}figcaption,small{color:#bfb1a7;font-size:13px}table{border-collapse:collapse;width:100%}td,th{padding:10px;border-bottom:1px solid #ffffff20;text-align:left}p{max-width:930px}blockquote{border-left:2px solid #d7ad75;margin:12px 0;padding-left:16px} @media(max-width:700px){.grid{grid-template-columns:1fr}main{padding:24px 16px}h1{font-size:30px}}</style><main><p>言灵世界 / CP24</p><h1>让一句话，变成小镇的生活。</h1><p>Jev 已接入实时场景。人物按自己的状态行动，环境也会回应；你可以把变化拉近来看。</p><p><a class="entry" href="http://127.0.0.1:4240/">打开小镇</a><a href="动作总表.html">查看所有动作</a></p><h2>可以这样试</h2><blockquote>让小镇进入夜晚，飘一点纸片雪。</blockquote><blockquote>让雪停，回到温暖黄昏。露台上的读者合书、喝茶，再读几页。</blockquote><blockquote>桥边红衣人给鱼喂点吃的。</blockquote><p>收到单个人的安排后，点击“看近一点”。也可先点选居民或物件，再用“他”“这个”来表达。</p><div class="grid">'''
for filename,caption in cards:
 assert (O/filename).exists(),filename
 page+=f'<figure><img src="{filename}" loading="lazy"><figcaption>{caption} · 实际网页截图</figcaption></figure>'
page+=f'''</div><h2>这一版增加了什么</h2><p>8种连贯生活目标；晨曦、白昼、黄昏与夜晚；真实纸雕太阳；宽屏全景与手机近景；逐件控制和角色动作归属；雨天等待、动作收尾、撤回与本地存档。</p><table><tr><th>检查</th><th>结果</th></tr><tr><td>逻辑与状态</td><td>{test_count}项通过</td></tr><tr><td>实际模型运动</td><td>1201帧 / {contacts['body_poses']}个主体姿态，未发现意外交叉</td></tr><tr><td>脚底支撑</td><td>{support['actor_samples']}组采样通过</td></tr><tr><td>人物行为目标</td><td>32位居民 / 56类目标 / 310条绑定，含8种连贯片段</td></tr></table><p><small>上述模型检查是离散、限定场景的验证，不是所有未来动作的连续证明。语义仍可能拒绝模糊请求；连贯目标复用已有动作，不等于新增同数动画。</small></p><p><a href="检查点说明.txt">完整检查点说明</a> · <a href="delivery-summary.json">验证摘要</a> · <a href="api-ledger.json">实验记录索引</a></p></main></html>'''
(O/'review.html').write_text(page)
for f in ['review.html','检查点说明.txt','delivery-summary.json','api-ledger.json']+[f for f,_ in cards]:shutil.copy2(O/f,A/'public/assets'/f)
# Source and reproducibility records; no credentials or dependencies.
dest=O/'source';shutil.copytree(A,dest,dirs_exist_ok=True,ignore=shutil.ignore_patterns('node_modules','dist','.DS_Store'))
scripts=O/'scripts';scripts.mkdir(exist_ok=True)
for p in (R/'work/runtime-cp24').iterdir():
 if p.is_file()and p.suffix in ['.mjs','.py','.txt']:shutil.copy2(p,scripts/p.name)
sources={str(p.relative_to(dest)):sha(p)for p in dest.rglob('*')if p.is_file()};(O/'source-manifest.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2))
files=[p for p in O.rglob('*')if p.is_file()and p.name!='artifact-manifest.json'];assert not any(re.search(rb'sk-or-v1-[A-Za-z0-9_-]{30,}',p.read_bytes())for p in files),'credential scan'
(O/'artifact-manifest.json').write_text(json.dumps({str(p.relative_to(O)):sha(p)for p in files},ensure_ascii=False,indent=2))
print(json.dumps(summary,ensure_ascii=False))
