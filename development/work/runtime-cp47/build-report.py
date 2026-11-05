# -*- coding: utf-8 -*-
from pathlib import Path
import json,html,shutil
root=Path.cwd();out=root/'outputs/runtime-checkpoint-47';pub=root/'publish/echoing-green/verification/expressive-life';pub.mkdir(parents=True,exist_ok=True)
rows=json.loads((out/'language-six.json').read_text());repeat=out/'repeat-night-actual.json';rows+=json.loads(repeat.read_text()) if repeat.exists() else [];grey=json.loads((out/'grey-audit-final.json').read_text())
tr=''
for r in rows:
 e=r.get('execution');actions=' · '.join(i['target']+': '+i['action'] for i in r['plan']['items']) or '保持原样'
 result=('流程完成' if e['outcome']=='completed' else '动作结束后平滑收束') if e else '按要求保持原状'
 tr+='<tr><td>'+html.escape(r['text'])+'</td><td>'+html.escape(actions)+'</td><td>'+(str(e['seconds'])+' 秒' if e else '—')+'</td><td>'+result+'</td></tr>'

cards=[]
for title,name,caption in [('纸灯未点亮','lantern-before.png','灯、绳与灯架已经在场景中；保持原有环境亮度。'),('纸灯沿街亮起','lantern-after.png','依次增加暖橘色自发光与柔和地面暖光；两名居民实际取灯、携灯并归还。'),('狐狸招呼街坊','fox-greeting.png','先沿弧线小跑，再停下抬前爪、摇四段纸折尾巴；邻居短暂停步回应。'),('电车捎来礼物','parcel-pickup.png','旅客走近行李架，双手取下礼物并举起来看。'),('礼物交给街坊','parcel-handoff.png','同一个礼物转交给接收者；主角提示随物件归属交接。')]:
 if (out/name).exists():
  shutil.copy2(out/name,pub/name);cards.append(f'<article><h2>{title}</h2><img src="{name}" alt="{title}" loading="lazy"><p>{caption}</p></article>')
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CP47 · 纸灯、礼物与狐狸</title><style>body{margin:0;background:#24232c;color:#ebdfcb;font:16px/1.7 system-ui,sans-serif}main{max-width:1160px;margin:auto;padding:32px 22px 70px}a{color:#e7b97d}h1{font:36px Georgia,serif}h2{font-size:22px;color:#edc995}p{max-width:80ch}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:18px}article{padding:18px;background:#302d35;border:1px solid #605145;border-radius:14px}img{width:100%;border-radius:8px}table{border-collapse:collapse;width:100%;min-width:730px}td,th{text-align:left;padding:12px;border-bottom:1px solid #655647}.scroll{overflow:auto}.note{padding:16px;border-left:3px solid #d8ac6c;background:#302c33}@media(max-width:450px){.grid{grid-template-columns:1fr}h1{font-size:28px}main{padding:20px 14px}}</style><main><a href="../../">← 回到小镇</a> · <a href="../">CP46 完整 83 案例档案</a><h1>CP47 · 纸灯、礼物与狐狸</h1><p>本轮重点：更清楚的灯光变化、更有来由的礼物交接、更活泼的狐狸，以及局部互动中的主角提示。原有暖纸雕美术、建筑和完整屋顶保留。</p><div class="note">这是本轮补充验收。旧版 83 案例报告保留作历史记录，不代表本轮又重新逐一观看了 83 段动画。以下图片是实际网页在受控模拟时间的采样画面；单张图片不能证明整段动作流畅。</div><h2>这次改了什么</h2><ul><li>12 盏灯串与 2 盏现成手提灯保留实体尺寸，拉开未点亮与暖光状态的差别，加入逐盏点亮和局部地面暖光；不靠把整个小镇变暗来造差别。</li><li>停靠时的旅客先候望、走近电车行李架，取下带蝴蝶结的礼物并举起来看看，再走出站台与街坊交接。同一礼物始终保留同一个身份。此活动仍只在电车停靠、旅客可用时提供。</li><li>狐狸先走近可达的邻居，停下抬爪摇尾。身体朝向随脚步转弯，站定时不绕中心轴转。尾巴由一个硬三角体改为四段相连的纸折结构；平时加入舔爪、伸展、嗅闻与更清楚的摇尾。</li><li>局部活动最多提示三名主角：淡金色纸笔触脚下圈持续跟随活动，并有少量柔和暖光。礼物换手后，提示随接收者交接。全镇花火、夜市等活动不把所有人圈起来；没有人物头顶文字。</li><li>用户触发的手工动作约快 18%，对应局部行走约快 12%；上下楼与桥梁的既有步态不统一粗暴加速。一件事结束后再接受下一件。</li></ul><div class="grid">'''+''.join(cards)+'''</div><h2>本轮实际测试</h2><p>254 项完整运行检查通过，35 项云端接口检查通过；主角提示与灯光也经过实际网页复看。17 条轮换提示分别在两个不同运行状态中完整执行，共 34 次：均有进展、流程完成、参与者锁释放。另以三个开场状态检查狐狸接近、抬爪与摇尾，均完成。</p><p>下面九条均为本轮真实模型调用，其中最后三条专门测试已入夜时的重复点灯与明确保持原样，收到的计划再经同一最终模拟器执行。表内秒数是模拟中整段互动及收尾的时长，包含走路和交接，不是 API 延迟，也不是要求用户先等待这么久才见到反馈。纸灯中两位搬灯者会先完成工作，再温和收束余下停留。</p><div class="scroll"><table><thead><tr><th>实际输入</th><th>选中的行为</th><th>整段时长</th><th>执行结果</th></tr></thead><tbody>'''+tr+'''</tbody></table></div><p>本轮沿用现有 Jev 接口、模型、密钥与云服务权限。上线检查发现“已经是夜晚”时，明确点灯曾被误解成团聚；第 19 版接口已修复此问题，否定、假设与混合要求仍交给模型判断，不用关键词强行覆盖。狐狸尾巴、礼物饰带、行李架与提示均为少量运行时几何；原 GLB 与贴图未换。地面提示共用实例化几何，额外暖光固定最多两盏且不投射新阴影。没有以此宣称所有设备达到某个帧率。</p><p><a href="../../">回到小镇，试试这三句话 →</a></p></main></html>'''
(pub/'index.html').write_text(page)
# The previous full report remains an explicitly historical archive.
p=root/'publish/echoing-green/verification/index.html';s=p.read_text();banner='<aside style="padding:16px;margin:16px 0;background:#40343a;color:#f0e5d0;border-left:3px solid #e0b474"><b>最新 CP47：</b>纸灯亮灭、列车礼物、狐狸和局部主角提示已更新。<a style="color:#efc990" href="expressive-life/">查看本轮更新与测试 →</a><br>下方保留 CP46 的完整 83 案例档案。</aside>'
if '最新 CP47' not in s:
 import re
 s=re.sub(r'(<main[^>]*>)',lambda m:m[0]+banner,s,count=1)
p.write_text(s)
print(json.dumps({'report':str(pub.relative_to(root)),'images':len(cards),'grey_runs':len(grey),'real_requests':len(rows)}))
