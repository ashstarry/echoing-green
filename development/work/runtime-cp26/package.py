from pathlib import Path
import json,hashlib,shutil,re,gzip
R=Path.cwd();A=R/'app/runtime-cp26';O=R/'outputs/runtime-checkpoint-26'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for c in iter(lambda:f.read(1048576),b''):h.update(c)
 return h.hexdigest()
contacts=json.loads((O/'contacts-final.json').read_text());support=json.loads((O/'support-final.json').read_text());assert contacts['passed']and support['passed']
capture=R/'work/runtime-cp26/capture-round1/browser-mesh-motion.json';digest=sha(capture);assert digest==contacts['capture_sha256']==support['capture_sha256']
tests=(O/'tests-final.txt').read_text();assert '# fail 0' in tests;passed=int(re.search(r'# pass (\d+)',tests)[1]);records=[json.loads(p.read_text())for p in(O/'semantic-runs').glob('*.json')];posts=sum(bool(x.get('request_sent'))for x in records);cost=round(sum(x.get('response',{}).get('usage',{}).get('cost',0)or 0 for x in records),9)
old=json.loads((R/'outputs/runtime-checkpoint-25/source-manifest.json').read_text());assert all(sha(R/'app/runtime-cp25'/f)==h for f,h in old.items())
ledger={'scope':'CP26 only; no changes to historical ledger totals','actual_posts':posts,'cost_usd':cost,'ids':[r['id']for r in records],'note':'Jev raw response and explicit-weather resolution are distinct. Executor success is not model accuracy.'};(O/'api-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2))
summary={'checkpoint':26,'url':'http://127.0.0.1:4240/','tests':passed,'body_poses':contacts['body_poses'],'frames':961,'support_samples':support['actor_samples'],'capture_sha256':digest,'geometry_passed':True,'cp25_source_unchanged':True,'api_posts':posts,'api_cost_usd':cost,'music_pieces':6,'music_bpm':76,'music_crossfade_seconds':3.2,'finite_routes_only':True};(O/'delivery-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
note=f'''借风町 CP26 · 明确天气、较大的群体走位、纸纹提示与柔和掌机音乐

原地址：http://127.0.0.1:4240/
启动器：app/runtime-cp26/打开借风町.command
保留borrowed-wind-cp24-v2存档，不删档、不离线追算，仍是独立浏览器小镇。

“下雨了”为什么失败、现在怎样处理
用户雪天夜晚的多次实际输入在CP25接口有完整记录：Jev的intent_status=change，但weather选择keep或低概率rain，scope:weather选择no，因此执行器返回空安排。并非输入格式错误或HTTP请求没到。原失败已复制到reported-failure/。
这版仍调用Jev，针对完整、明确的天气短句（下雨了/小镇下雨了/雨停了等）加确定性语义校验，不用子串碰到“雨”就执行。否定、条件、回忆、歌名、引号及多句组合不被宽泛正则吞掉。每条返回记录保留raw_weather、raw_scope和explicit-weather-v1来源；未把本地修正伪称为模型答对。复杂/诗意输入继续由Jev选择有限动作；任意输入都可收到解释，不代表系统可以无约束实现任意行为。网络失败仍诚实报错。
控制测试11句执行层11/11，包括雨/雪/停雨、否定、回忆、条件句和花火；原始模型有keep被规则纠正。真实网页再次在雪天输入“下雨了”已进入雨天（bb3a4b17-06e6-48f3-91eb-eb9894775c1b）；随后“雨停了”也真实生效。本轮总{posts}次模型POST，usage.cost合计${cost:.9f}；不是全项目账单。

动作反馈
花火使用中心广场周围分散的观看口袋，避雨优先分配建筑方向的落脚点；远目标被临时人群挡住时，规划可等待通行的路线，遇到对向的人先找安全位置让路，再恢复原目的地。明确的全镇雨天/花火活动可接管较早的街上差事，同一句里明确指定的个人安排保留。
雨中街行速度上调到0.80模型单位/秒（普通成人仍0.58），仍有转身、加减速、碰撞距离约束。花火/雨天群体回应启动更集中；晚市重复输入会让客人换摊位，邻里相聚也能走得更开。一般活动、开场、儿童和骑行的原验证不放松；未把新路由应用到所有自动背景事件。
本轮同一初始种子的45秒对照：花火的位移>2模型单位者由1到6；雨天由1到3；邻里相聚由0到4。它们是有限场景的观测，不是所有输入都达到同样数值。市场首轮未宣称全面优于旧版；其重复换摊和较长活动是额外变化。完整每10/20/30/45秒数据在event-metrics.json。
有11位居民可在街道导航网格走动；其他居民使用已有局部路线或岗位动作，不是全部32人都能离开岗位走到中心。检测发现当前三个屋檐覆盖网格点位于不连通小区域，所以没有伪称街上每个人都已躲进屋檐：街上多为换安全位置再撑伞，二楼客人有真实回帘内流程；风筝孩子仍受牵线范围限制。未来要更广泛进屋需单独增加并验证路线。

纸纹标记
真正接到个人任务、或正在被全镇事件调动的居民脚边，出现三片暖金纸纹和一枚小折角纸签（如“避雨”“逛街”），跟随位置、逐步淡出；约8秒后消失，不是整屏光圈，也不靠标记冒充位移。没有实体碰撞体；最后的颜色/大小/离地微调仅为提示可见性，不改变人物或导航。

柔和音乐（按用户最新反馈修订）
已实现六首原创掌机音色短曲：纸町晚风、灯影里的归途、檐下听雨、纸雪轻落、小街开市、今夜花开。76 BPM，柔化脉冲音色、三角低音、稀疏琶音。缓慢音头、较长持音/收尾，避免尖锐方波和短促打点。曲目有不同旋律/和声；换状态约3.2秒交叉淡入淡出。默认关，点声音开试听。背景BGM与场内吉他手分开。
浏览器使用同一合成器生成79.29秒六曲试听，峰值0.0833、RMS0.0221、未削波；不是压缩后的响度评级。初稿另存音乐初稿-较清晰.wav。详见BGM设计说明.txt和audio-preview-check.json。它是原创程序音乐试听版，没有引用已有游戏旋律或假称真实GBA硬件仿真。

验证与保存
{passed}项逻辑/状态/导航/提示/曲目等测试通过。真实浏览器240.05秒、961帧、{contacts['body_poses']}个主体姿态检查，0意外网格表面交叉；{support['actor_samples']}个鞋底支撑样本通过。捕获SHA256为{digest}。保留全部失败调试轮，不通过改松间距或删测试凑结果；这是限定场景离散检查，不是所有未来输入、每个连续时刻的保证。
没有修改GLB模型或获批灯光方向，没有新建服务端全天候模拟。source/为运行源码快照，scripts/为复现脚本，原CP25保留，API凭证未打包。数据与归档为本地保存，不是云备份。
'''
(O/'检查点说明.txt').write_text(note)
page='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>借风町 CP26 · 更清楚的回应，更柔和的音乐</title><style>body{background:#26232d;color:#efdfc8;font:17px/1.8 system-ui;margin:0}main{max-width:1100px;margin:auto;padding:32px 22px}a{color:#ebbd7c}img{max-width:100%;border-radius:14px}h1{font-family:serif;font-weight:500}audio{width:min(100%,680px)}small{color:#b8a99b}</style><main><p>借风町 · CP26</p><h1>一句话，街坊开始回应。</h1><p>明确天气输入有可靠执行；更远的群体走位，短暂的纸纹提示，和六首柔和的掌机音乐。</p><p><a href="http://127.0.0.1:4240/">打开小镇</a> · <a href="动作总表.html">动作总表</a> · <a href="检查点说明.txt">完整说明与边界</a></p><h2>试听六首柔和小曲</h2><p>日常 → 夜晚 → 雨天 → 雪天 → 晚市 → 花火，每段约12.6秒。小镇中按当前状态选曲，平滑换曲。</p><audio controls preload="none" src="借风町-掌机音色试听.wav"></audio><p><small>原创程序音乐试听草案；日常播放不下载此文件，而由浏览器实时合成。</small></p><h2>“下雨了”已实际生效</h2><img src="rain-live.jpg"><p>语义纠正与模型原始结果分开记录。有限动作和路线仍保留边界，不能任意生成新物件或让所有居民自由穿越全镇。</p></main>''';(O/'review.html').write_text(page)
for f in ['检查点说明.txt','BGM设计说明.txt','delivery-summary.json','api-ledger.json','review.html','rain-live.jpg','借风町-掌机音色试听.wav']:shutil.copy2(O/f,A/'public/assets'/f)
cap=json.loads((A/'public/assets/runtime-capabilities.json').read_text());cap.update(checkpoint=26,explicit_weather_contract=True,music_pieces=6,music_crossfade_seconds=3.2,affected_actor_paper_marks=True);(A/'public/assets/runtime-capabilities.json').write_text(json.dumps(cap,ensure_ascii=False,indent=2));shutil.copy2(A/'public/assets/runtime-capabilities.json',O/'runtime-capabilities.json')
z=O/'browser-motion.json.gz'
if not z.exists():
 with capture.open('rb')as src,gzip.open(z,'wb',compresslevel=5)as dst:shutil.copyfileobj(src,dst)
h=hashlib.sha256()
with gzip.open(z,'rb')as f:
 for c in iter(lambda:f.read(1048576),b''):h.update(c)
assert h.hexdigest()==digest
(O/'capture-archive.json').write_text(json.dumps({'raw':str(capture.relative_to(R)),'sha256':digest,'gzip':z.name,'lossless_verified':True},indent=2))
dest=O/'source';shutil.copytree(A,dest,dirs_exist_ok=True,ignore=shutil.ignore_patterns('node_modules','dist','.DS_Store'));scripts=O/'scripts';scripts.mkdir(exist_ok=True)
for p in(R/'work/runtime-cp26').iterdir():
 if p.is_file()and p.suffix in ['.mjs','.py','.txt']:shutil.copy2(p,scripts/p.name)
(O/'source-manifest.json').write_text(json.dumps({str(p.relative_to(dest)):sha(p)for p in dest.rglob('*')if p.is_file()},ensure_ascii=False,indent=2))
files=[p for p in O.rglob('*')if p.is_file()and p.name!='artifact-manifest.json'];assert not any(re.search(rb'sk-or-v1-[A-Za-z0-9_-]{30,}',p.read_bytes())for p in files)
(O/'artifact-manifest.json').write_text(json.dumps({str(p.relative_to(O)):sha(p)for p in files},ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False))
