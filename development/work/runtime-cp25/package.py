from pathlib import Path
import json,hashlib,shutil,re,gzip
R=Path.cwd();A=R/'app/runtime-cp25';O=R/'outputs/runtime-checkpoint-25'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for c in iter(lambda:f.read(1048576),b''):h.update(c)
 return h.hexdigest()
contacts=json.loads((O/'contacts-final.json').read_text());support=json.loads((O/'support-final.json').read_text());assert contacts['passed']and support['passed']
source=R/'work/runtime-cp25/capture-round1/browser-mesh-motion.json';digest=sha(source);assert digest==contacts['capture_sha256']==support['capture_sha256']
tests=(O/'tests-final.txt').read_text();assert '# fail 0' in tests;n=int(re.search(r'# pass (\d+)',tests)[1])
records=[json.loads(p.read_text())for p in(O/'semantic-runs').glob('*.json')];posts=sum(bool(r.get('request_sent'))for r in records);cost=round(sum(r.get('response',{}).get('usage',{}).get('cost',0)or 0 for r in records),9)
ledger={'scope':'CP25 only; CP24 archives and user-reported runs unchanged','actual_posts':posts,'cost_usd':cost,'ids':[r['id']for r in records]};(O/'api-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2))
base=json.loads((R/'outputs/runtime-checkpoint-24/source-manifest.json').read_text());unchanged=all(sha(R/'app/runtime-cp24'/f)==h for f,h in base.items());assert unchanged
note=f'''借风町 CP25 · 日月、快捷活动与更积极的生活

使用原地址：http://127.0.0.1:4240/
启动：app/runtime-cp25/打开借风町.command

修复
1. 晨曦时太阳和月亮曾同时带透明度显示在同一个位置。现在按互斥交接显示，16种时段切换及中途反向均检查；保留平滑天空变化，不再出现叠在一起的日月。
2. 用户的花火快捷句曾被Jev范围问题判成“没有明确要求”，并非不存在花火执行器。全部5个快捷按钮改为确定性活动入口，点击即执行，不消耗API也不会被语义门槛拦截。花火先转入夜晚并让居民找位置；下雨时等待雨停。自由输入仍直接调用Jev，已加强期待花火、时间陈述、等待雨停条件句的提示。

更有回应的生活
一次全镇心愿会安排一轮约30秒的分批响应：街上居民更早出发，优先走到另一处；楼梯、阳台、桥边及商贩也错开回应。天气、角色、已占用空间和手持物收尾仍优先。明确的个人任务不被群体响应覆盖，个人指令不会强制全镇换状态；撤回取消后续响应，不倒带位置。已处于晚市/某个时段，也可再次表达同类愿望，带出新一轮回应。
刚打开时有约16秒的分批开场。几位街坊较早出发，局部路线错开；日常调度避免所有可行走的人同时陷入长手势。速度没有调快，仍以起步、转身、避让和原路线为基础。保存的安静要求与刚合上的书也保留。

对照结果
同一场景、相同测试流程、三个种子：输入晚市后15秒内，直线位置改变超过1模型单位的人数，CP24为2人，CP25为6–7人；累计行走超过1单位的为3人→8–11人。总行程约6.91–7.39→16.74–31.23模型单位。首次累计行走超过0.2单位约2.30–2.65秒→0.35–1.45秒。这里单位不是米，也不是所有输入的保证。
开场第10秒，仍有实际行走速度的人数0→3，局部行走2条；动静错开，并不让所有人一直走。

验证
{n}项测试通过。200秒/801帧真实浏览器捕获，{contacts['body_poses']}主体姿态，0意外网格表面交叉；{support['actor_samples']}鞋底支撑采样通过。
初始稀疏鞋角/中心探针在84.05秒报告一处悬空。密集诊断发现右脚覆盖了窄砖面，121个包围框诊断探针中63个有支撑；最终检查使用实际鞋底凸轮廓内8×8探针，保留原失败报告support-corner-probes.json与诊断记录。没有移动模型去掩盖它，也没有放宽垂直间隙阈值。碰撞和支撑报告绑定同一原始捕获SHA256：{digest}。
这些仍是限定场景离散检查，不是任意未来输入的连续数学保证。最终两项保守守卫（不重开刚合的书、不打断明确安静）不扩展运动，捕获场景未触发这两个分支。

语义测试不夸大
两个开发/复测轮各10句，第一轮严格7/10，第二轮严格8/10，全部原始结果保留。第二轮剩下差异是：全镇晚市同时指定了一个逛摊居民；夜晚暖灯句只切到夜晚，原本已warm的灯没有另外重设。这不是通用准确率。三个花火表达、否定、过去赞美、雨停条件、重复晚市及单人范围均分别记录。快捷按钮的可靠性不依赖这些模型结果，实际网页已验证晨曦无月亮、花火按钮聚集到燃放；没有制作视频。
本轮{posts}次实际模型POST，usage.cost合计${cost:.9f}。未改历史账本，凭证未打包。

范围
动作目录仍为32人、56类目标/310绑定，每人5–15个；本轮是编排与反馈密度改进，不把重新组合或多走几步算成新动画。205 GLB实体/466部件及既有模型未改。保留纸雕和风、温暖可读、完整屋顶和43度默认方向。无全天候后端、上线、离线追算。原CP24的81个源文件与归档保留。
'''
(O/'检查点说明.txt').write_text(note)
summary={'checkpoint':25,'url':'http://127.0.0.1:4240/','tests':n,'body_poses':contacts['body_poses'],'frames':801,'support_samples':support['actor_samples'],'capture_sha256':digest,'geometry_passed':True,'cp24_source_unchanged':unchanged,'api_posts':posts,'api_cost_usd':cost,'quick_buttons_deterministic':True,'sun_moon_mutually_exclusive':True,'bounded_sampling_only':True};(O/'delivery-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
page='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>借风町 · CP25 回应更鲜明</title><style>body{background:#26232d;color:#efdfc8;font:17px/1.8 system-ui;margin:0}main{max-width:1100px;margin:auto;padding:32px 22px}a{color:#ebbd7c}img{max-width:100%;border-radius:14px}h1{font-family:serif;font-weight:500}section{margin:28px 0}small{color:#b8a99b}</style><main><p>借风町 · CP25</p><h1>从第一眼，就开始生活。</h1><p>日月不再重叠，快捷活动点击即可发生。街坊分批走近、换位置和做事，让你的一句话带来更鲜明的回应。</p><p><a href="http://127.0.0.1:4240/">打开实时小镇</a> · <a href="动作总表.html">动作总表</a> · <a href="检查点说明.txt">完整验证说明</a></p><section><h2>晨曦</h2><img src="dawn-fixed.jpg"><small>实际网页截图：太阳与月亮互斥显示。</small></section><section><h2>等一场花火</h2><img src="fireworks-shortcut.jpg"><small>实际点击快捷按钮后，从聚集到燃放；自由输入仍使用Jev。</small></section><p>输入晚市后15秒的对照中，明显改变位置的街坊由2人增加到6–7人；没有加速走路或取消避让。</p><p>检查覆盖限定场景与离散采样，仍保留复杂语义和有限路线的边界。</p></main>'''
(O/'review.html').write_text(page)
for f in ['检查点说明.txt','delivery-summary.json','api-ledger.json','review.html','dawn-fixed.jpg','fireworks-shortcut.jpg']:shutil.copy2(O/f,A/'public/assets'/f)
cap=json.loads((A/'public/assets/runtime-capabilities.json').read_text());cap['checkpoint']=25;cap['quick_wishes']='five deterministic finite controls; free text uses Jev';cap['response_orchestration']='staggered opening and broad-wish reactions using existing safe actions and routes';(A/'public/assets/runtime-capabilities.json').write_text(json.dumps(cap,ensure_ascii=False,indent=2));shutil.copy2(A/'public/assets/runtime-capabilities.json',O/'runtime-capabilities.json')
# Keep large raw geometry out of web assets, but retain a lossless verified archive.
zipfile=O/'browser-motion.json.gz'
if not zipfile.exists():
 with source.open('rb')as src,gzip.open(zipfile,'wb',compresslevel=5)as dst:shutil.copyfileobj(src,dst)
h=hashlib.sha256()
with gzip.open(zipfile,'rb')as src:
 for c in iter(lambda:src.read(1048576),b''):h.update(c)
assert h.hexdigest()==digest
(O/'capture-archive.json').write_text(json.dumps({'raw':str(source.relative_to(R)),'raw_sha256':digest,'gzip':'browser-motion.json.gz','lossless_verified':True,'bytes':zipfile.stat().st_size},indent=2))
dest=O/'source';shutil.copytree(A,dest,dirs_exist_ok=True,ignore=shutil.ignore_patterns('node_modules','dist','.DS_Store'));scripts=O/'scripts';scripts.mkdir(exist_ok=True)
for p in(R/'work/runtime-cp25').iterdir():
 if p.is_file()and p.suffix in ['.py','.mjs','.txt']:shutil.copy2(p,scripts/p.name)
manifest={str(p.relative_to(dest)):sha(p)for p in dest.rglob('*')if p.is_file()};(O/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
files=[p for p in O.rglob('*')if p.is_file()and p.name!='artifact-manifest.json'];assert not any(re.search(rb'sk-or-v1-[A-Za-z0-9_-]{30,}',p.read_bytes())for p in files)
(O/'artifact-manifest.json').write_text(json.dumps({str(p.relative_to(O)):sha(p)for p in files},ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False))
