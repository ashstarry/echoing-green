import json,hashlib,datetime,html
from pathlib import Path
R=Path.cwd();O=R/'outputs/runtime-checkpoint-17';A=R/'app/runtime-cp17';caps=json.loads((O/'runtime-capabilities.json').read_text());qa=json.loads((O/'browser-qa.json').read_text());accept=json.loads((O/'acceptance.json').read_text());actual=hashlib.sha256((R/'outputs/art-checkpoint-16/borrowed-wind-town-cp16.blend').read_bytes()).hexdigest();assert actual==accept['sha256'];runs=[json.loads(p.read_text())for p in (O/'api-runs').glob('*.json')];cost=sum(float(r['response'].get('usage',{}).get('cost')or 0)for r in runs);now=datetime.datetime.now(datetime.timezone.utc).isoformat()
summary={'checkpoint':'CP17','created_utc':now,'accepted_cp16_unchanged':True,'cp16_sha256':actual,'entities':199,'parts':235,'walkers':5,'registered_humans':32,'nav_cells':1016,'logic_tests':11,'motion_body_samples':2400,'motion_interval_seconds':.5,'motion_duration_seconds':239.55,'language_tuning_set':{'passed':16,'total':16},'language_holdout_openai':{'passed':5,'total':8},'language_posthoc_jev':{'passed':5,'total':8},'actual_api_calls':len(runs),'actual_api_cost_usd':cost,'performance':qa['performance'],'source_geometry_triangles':423973,'runtime_glb_bytes':(A/'public/assets/town.glb').stat().st_size,'no_24_7_simulation':True,'local_proxy_only':True,'unavailable':['upper diner sit/stand/curtain transition','full actual rail-spline train circulation/boarding','bicycle riding','boat/oar route','walking animals and fish routes','stairs and all-town navigation'],'art_limit':'First browser material/light translation; not approved render parity or a production art-performance result.'};(O/'delivery-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
notes=f'''CP17 动态检查点 · {now}

这是第一次可运行的网页小镇。CP16 认可模型的原文件没有修改；其 SHA256 为 {actual}。
运行副本位于 app/runtime-cp17；可编辑刚性控制点副本位于 work/runtime-cp17/town-runtime.blend。动作由网页程序实时计算，没有成片式固定动画。

打开方法
双击 app/runtime-cp17/打开借风町.command，随后浏览器打开 http://127.0.0.1:4173。
页面可以写诗句，也可以点选人物、在小镇手记里直接试动作；鼠标拖动或双指移动平移，滚轮/双指缩放，视角不旋转。“声音关”可打开本地合成的简短拨弦声。
网页隐藏/关闭后暂停；浏览器本地存档恢复时不会补算离线时间。启动器的终端只提供静态文件和按需决策代理，不模拟离线小镇。关闭该终端会停止本地服务。生产部署/云存档/账户同步未实现。

当前已经执行
199 个原有对象身份保留；235 个可寻址控制部件，其中新增 144 个刚性身体转轴。
5 位居民可以在经过净空检查的地面区域走动、停留、避让；全局街道意愿和个人意愿分别处理。花园孩子的入口检查不通过，保持原位并占用空间，其他人不会把它当作不存在。
人物采用轻量的摆腿、摆臂、张望；乐手拨弦和摊主小幅照料动作不替代完整的角色行为系统。
3 只纸雕鸟在有限的空中范围移动/振翅/悬停；风车转速连续改变；门帘和吊饰小幅随风；灯火强弱与星光变化；局部纸雨、纸片雪、纸花火小样。
雨雪有从模型取得的屋顶/地面终止高度。花火是低成本效果原型，尚非最终主打演出的美术完成度。
每条诗句只发起一次 OpenRouter Decisions 请求，同时选择有限问题；不把生成式 LLM 串在前面。日常模拟和逐帧动作不调用 API。当前默认 openai/gpt-6-luna-decisions；typesafe/jev-1.14 保留为可替换模型。
有限候选不是语义正确性的保证。接口失败、缺答、未知动作、旧结果或重复结果不会直接修改世界。可撤回上一组意愿，但不倒带时间或瞬移人物。

测试与界限
11 项逻辑测试通过，含连续 30 分钟模拟、两两间距、连续位置、导航邻接、暂停、存档恢复、个人指代、未知/过期/重复决策、撤回。
从实际 4 分钟轨迹提取 2,400 个完整身体姿态，按运行时的位置、转向、摆腿和抬脚回放到模型三角面，与静态场景及原位居民检查，未发现表面相交。这是每 0.5 秒的离散采样；不是所有动作和连续时间的绝对证明。
导航是 1,016 个地面格，包含两个主要连通区；石砖窄缝按小步跨越处理。没有把它称为全镇导航或楼梯系统。
列车的旧椭圆试跑会与后部已改线的场景冲突，不能拿旧椭圆替代实际轨道样条。列车本轮保持静止。这个失败记录不是对实际轨道整圈的最终验证。
真实浏览器通过加载、点选、真实接口到动画、暂停、保存/恢复、模拟网络故障、手机布局、可选声音检查，未记录页面脚本错误。静态构建另测手动交互和撤回。
本机 Chromium / Apple M2 Pro / 1600×1000 / DPR 1 的性能记录见 browser-qa.json。它不是其它电脑或手机的 FPS 承诺，渲染调用包含阴影及后处理，不能等同于材质数。

语言测试
先冻结候选与人工预期，再调用接口，保留全部请求、响应和费用。
四轮调试记录全部保留，最终调试集 16/16；新增、未参与调试的表达，OpenAI 为 5/8。主要问题是漏掉停雪、漏掉指定成年客人的意图，以及把“留在空中慢慢飞”理解为空中悬停。
Jev 在同一组已见留出句上的后续比较也是 5/8，错误分布不同，不能据此宣称一个模型普遍更优。默认模型未因这 8 句就切换。
本轮截至本记录实际发起 {len(runs)} 次付费接口调用，usage.cost 合计 ${cost:.8f}；旧实验档案没有覆盖，密钥未加入输出或静态构建。
这些是本任务小样本验收，不是严格代表性准确率评测。后续要扩充未参与调试的句子、场景状态和歧义案例。

尚未开放
二楼两位客人仍保留“门帘后/出来用餐”两个目标，但坐起、退椅、穿帘的连续执行器未实现。不会把直接隐藏人物当作完成这个动作。
列车完整环线/停靠/登车、自行车骑行、小船划行、动物游走、鱼游动、楼梯交通尚未开放。它们保留原有身份和控制边界。
居民关系、长期需求和更完整的社会事件仍需继续增加；这版是决策到执行的第一条可验收链路。
网页实时材质和灯光与 CP16 离线认可图还有差距，尤其灯火的空间层次、纸张细腻感和部分发白高光。CP16 仍是美术目标，不能因为网页能跑就降低这个标准。

具体证据
runtime-capabilities.json / runtime-body-check.json / entry-motion-check.json / unit-tests.txt
browser-qa.json / static-build-check.json / semantic-evaluation-round4.json / holdout-evaluation.json
jev-runtime-comparison.json / api-runs/ / motion-trace.json / town-live.webm
''';(O/'检查点说明.txt').write_text(notes)
road='''后续 Decision 与动作推进顺序

A. 二楼两点行为：先做退椅、站立、转身、门帘遮挡区、回到座位；尊重 CP16 已降低的层高。测试每个过渡姿态和中途反向指令，保证两个客人不抢同一席位。完整屋顶保留。
B. 主街和生活目的：在当前经过验证的地面移动上增加工作台/座位占用、接近-停下-动作-离开循环；再扩展人物数量，而不是先让所有人随机跑。
C. 水边与小动物：分别建立水域/桥面约束，小船、鸭子、鱼和漂灯相互避让。猫/狐狸需要独立身体范围与步态，不直接套用人的导航半径。
D. 交通：从真实轨道样条建立车轮/车厢跟随、两车连接和完整连续扫掠检查，再开放停靠和乘客上下车。自行车要把车、人、脚踏和车轮作为组合体校验。
E. 季节与节日：花火增加纸质形态、节奏和居民观看反应；天气触发避雨/撑伞/回家等具体行为。效果只是表现，活动目标仍由状态规则决定。
F. 美术和资源：继续对齐 CP16 的暖光与纸雕层次；评估静态光照烘焙/更多实例化，保留对象 ID 到实例的映射。不能只减面数就宣称性能已优化。
G. 语言质量：扩大独立留出集，覆盖省略、隐喻、否定、反事实、指代与中途变更。按真实可用候选选择；不偷偷添加第二次串行模型调用掩盖错误。

每轮验收共同条件：原认可模型可回退；所有新增可动对象有稳定 ID；动作前置条件与占用检查；当前动作中途切换与失败恢复；实际身体几何的路线/姿态验证；真实浏览器画面与性能采样；保存所有未通过用例。全天候服务器仍不在当前范围。
''';(O/'后续决策与动作路线.txt').write_text(road)
fps=qa['performance']['mean_fps'];page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>借风町 CP17 · 动态验收</title><style>*{{box-sizing:border-box}}body{{margin:0;background:#102b43;color:#eedfc9;font:16px/1.75 system-ui,-apple-system,"PingFang SC",sans-serif}}main{{max-width:1280px;margin:auto;padding:36px 28px 70px}}.eyebrow{{color:#e1ac6b;font-size:12px;letter-spacing:.15em}}h1{{font-size:40px;font-weight:500;margin:8px 0 12px}}h2{{font-size:22px;font-weight:500;margin-top:38px}}p{{color:#bed0db}}a{{color:#f0bc7d}}video,img{{max-width:100%;border-radius:14px;display:block}}video{{width:100%;background:#0a1e30}}.cards,.pair{{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}}.cards article{{background:#17364f;border:1px solid #ffffff18;padding:20px;border-radius:12px}}.tag{{font-size:12px;color:#e6b97b}}li{{margin:6px 0}}table{{border-collapse:collapse;width:100%;font-size:14px}}td,th{{border-bottom:1px solid #ffffff20;padding:12px;text-align:left}}th{{color:#e6b97b}}.start{{display:inline-block;padding:10px 18px;background:#dbb27e;color:#162d3e;text-decoration:none;border-radius:9px;margin:6px 12px 8px 0}}small{{color:#9cb3c5}}code{{font-size:13px;overflow-wrap:anywhere}}@media(max-width:700px){{main{{padding:24px 16px}}h1{{font-size:29px}}.cards,.pair{{grid-template-columns:1fr}}}}</style><main><div class="eyebrow">言灵世界 · CP17 · 浏览器动态检查点</div><h1>让小镇，开始有自己的日常。</h1><p>CP16 认可模型保留。本轮把一部分 Decision 接到真实运动、天气与灯火上；下面是实际网页运行录像。</p><video src="town-live.webm" poster="01-living-town.png" controls playsinline preload="metadata"></video><p><a class="start" href="http://127.0.0.1:4173">打开已经启动的小镇</a><a href="../../app/runtime-cp17/打开借风町.command">本地启动文件</a></p><small>试玩前，在 Finder 双击“打开借风町.command”。页面关闭后小镇暂停，重新打开从本机存档继续。录像和本验收页不依赖服务运行。</small><div class="cards"><article><span class="tag">已经可以玩</span><h2>意愿变成动作</h2><ul><li>5 位居民沿街走动、停留、让路，个人目标独立。</li><li>拨弦、摊位小动作、纸鸟振翅、风车和门帘变化。</li><li>暖灯、星光、局部纸雨、纸雪与纸花火小样。</li><li>点选、拖动缩放、可选拨弦声、暂停/存档/撤回。</li></ul></article><article><span class="tag">边界保持清楚</span><h2>还没有开放</h2><ul><li>二楼退椅、站起和走进门帘。</li><li>列车完整环线、登车、自行车、小船及动物路线。</li><li>楼梯交通、全镇导航与长期社会关系。</li><li>网页灯光仍需继续对齐认可的 CP16 美术效果。</li></ul></article></div><h2>决策如何进入这个世界</h2><p>一句话 → 一次 OpenRouter Decisions 请求 → 有限动作与人物范围检查 → 本地角色继续执行。日常动作不逐帧调用模型；失效或过期的回答不会覆盖新状态。</p><p>可以试：“让风慢一点，雨停一会儿，乐手歇一歇。” 或 “红衣小孩沿街走走，巷口送信的人停下来。” 也可以打开小镇手记直接点选。撤回恢复上一组意愿，人物不会倒带或瞬移。</p><h2>测试结果与实际限制</h2><table><tr><th>检查</th><th>结果</th><th>范围</th></tr><tr><td>逻辑/状态测试</td><td>11 项通过</td><td>含 30 分钟连续模拟、存档、暂停、避让和撤回</td></tr><tr><td>实际身体几何</td><td>2,400 姿态样本无相交</td><td>4 分钟轨迹，每 0.5 秒采样；不是所有动作的连续证明</td></tr><tr><td>语言调试集</td><td>16 / 16</td><td>参与过修订，不能当作泛化准确率</td></tr><tr><td>新表达留出集</td><td>OpenAI 5 / 8</td><td>仍有漏判；全部失败记录保留</td></tr><tr><td>Jev 后续比较</td><td>5 / 8</td><td>同一组已见句子，不能推出普遍优劣</td></tr><tr><td>真实网页性能</td><td>约 {fps:.0f} FPS</td><td>本机 M2 Pro / Chromium / 1600×1000 / DPR 1；不代表其它设备</td></tr></table><p>所有 {len(runs)} 次本轮接口调用和原始响应已归档，实际费用合计 ${cost:.6f}。OpenAI 继续作为默认；Jev 保留替换入口。新句子测试没有被“调到全对”后冒充独立验证。</p><h2>天气与天空</h2><div class="pair"><div><img src="02-paper-snow.png" loading="lazy"><small>纸片雪：按屋顶和地面高度结束下落。</small></div><div><img src="03-paper-fireworks.png" loading="lazy"><small>纸花火：第一版效果小样，尚未完成主打演出的艺术打磨。</small></div></div><details><summary>对照 CP16 已认可的静态美术图</summary><p>这张仍然是目标。网页里的光影和材质不会被默认算作已经达到同等质量。</p><img src="../art-checkpoint-16/01-overview.png" loading="lazy"></details><h2>项目记录</h2><p><a href="检查点说明.txt">检查点说明与启动方法</a> · <a href="后续决策与动作路线.txt">后续动作顺序及测试要求</a> · <a href="runtime-capabilities.json">199 个对象的能力清单</a> · <a href="browser-qa.json">浏览器检查</a> · <a href="runtime-body-check.json">身体姿态检查</a> · <a href="holdout-evaluation.json">留出集失败详情</a></p><small>原模型 SHA256 已核对不变。没有上线、没有全天候服务、没有把密钥放进网页。固定视角保持 2.5D；拖动和缩放用于看清动作。</small></main></html>''';(O/'review.html').write_text(page)
print(json.dumps({'summary':summary,'review':str(O/'review.html')},ensure_ascii=False))
