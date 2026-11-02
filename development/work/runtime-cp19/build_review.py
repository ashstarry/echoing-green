# -*- coding: utf-8 -*-
from pathlib import Path
import json
R=Path.cwd();O=R/'outputs/runtime-checkpoint-19'
perf=json.loads((O/'performance-final.json').read_text())['profiles'][0]
collision=json.loads((O/'browser-full-cast-final.json').read_text())
records=json.loads((O/'video-records.json').read_text())
leads={x['mode']:x['lead_in_seconds']for x in records}
page='''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>借风町 · CP19 生活节奏与共同事件</title>
<style>
:root{color-scheme:dark;--ink:#f0e3cf;--muted:#afbfca;--gold:#e7b775;--line:#345064}*{box-sizing:border-box}body{margin:0;color:var(--ink);background:radial-gradient(ellipse at 10% 0%,#284356,#0b1929 65%);font:16px/1.75 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}main{max-width:1320px;margin:auto;padding:48px 26px 75px}h1{font-size:clamp(34px,5vw,58px);font-weight:550;letter-spacing:.06em;line-height:1.3;margin:12px 0 18px}h2{font-size:26px;font-weight:550;margin:0 0 12px}h3{font-size:20px;font-weight:550;margin:0 0 10px}p{margin:0 0 14px}.eyebrow{font-size:12px;color:var(--gold);letter-spacing:.16em}.lead{max-width:920px;font-size:18px;color:#bfcbd4}.muted{color:var(--muted)}.links{display:flex;gap:12px;flex-wrap:wrap;margin:25px 0}a{color:#efc188;text-decoration:none}a:hover{text-decoration:underline}.button{border:1px solid #82725d;padding:9px 20px;border-radius:24px;background:#233849}.primary{background:var(--gold);color:#142739}.card{border:1px solid var(--line);background:#14283add;border-radius:22px;overflow:hidden}.pad{padding:26px}section{margin-top:28px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.two{display:grid;grid-template-columns:1fr 1fr;gap:20px}video,img{display:block;width:100%;background:#12314b}video{max-height:80vh;object-fit:contain}figure{margin:0}figcaption{padding:16px 22px;font-size:14px;color:var(--muted)}.tag{font-size:12px;display:inline-block;border:1px solid #526575;border-radius:12px;padding:1px 10px;margin-bottom:12px}.number{font-size:29px;color:var(--gold)}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:14px 12px;border-bottom:1px solid var(--line);vertical-align:top}th{color:#d9bd95;font-weight:500}details{border:1px solid var(--line);padding:18px 22px;border-radius:16px;margin-top:18px}summary{cursor:pointer;color:#e0c49f}details p{margin-top:14px}.small{font-size:14px}.chapters{padding:14px 22px;display:flex;gap:10px;flex-wrap:wrap}.chapters button{background:#264255;border:1px solid #4b697b;color:#e8d7bd;font:inherit;font-size:14px;border-radius:18px;padding:5px 13px;cursor:pointer}.footer{margin-top:30px;color:#90a7b9;font-size:13px}@media(max-width:760px){main{padding:28px 16px 50px}.grid,.two{grid-template-columns:1fr}.pad{padding:21px}video{max-height:none}td,th{padding:10px 7px;font-size:14px}}
</style></head><body><main>
<div class="eyebrow">借风町 / CP19 / 真实网页运行</div>
<h1>生活有节奏，也有理由。</h1>
<p class="lead">小镇的时间比现实轻快一些。有人聊几句，有人看花、等车、照料盆栽；客人坐一会儿再走进门帘。不同的人错峰行动，雨和花火也会改变这一晚的生活。</p>
<div class="links"><a class="button primary" href="#life">看小镇日常</a><a class="button" href="#rain">看雨来雨停</a><a class="button" href="../../app/runtime-cp19/打开借风町.command" download>本地启动器</a><a class="button" href="../runtime-checkpoint-18/review.html">对比 CP18</a></div>
<section id="life" class="card">
<video id="mainVideo" controls muted playsinline preload="metadata" poster="02-festival.png" src="town-life.webm"></video>
<div class="chapters"><button data-at="0">从日常开始</button><button data-at="30">街道与用餐</button><button data-at="56">花火与观众</button><button data-at="78">结束后的余韵</button></div>
<figcaption>实际网页录像，未经加速。日常、进站、用餐和偶尔的花火自主运行；没有把所有人编排成同一段循环。</figcaption>
</section>
<section class="grid">
<article class="card pad"><span class="tag">更顺滑</span><h3>把每一步接起来</h3><p class="muted">狐狸和居民的位置、朝向平滑衔接。小动物会走走闻闻，遇人先让路，停下来也有原因。</p></article>
<article class="card pad"><span class="tag">更有意图</span><h3>静下来，也在做事</h3><p class="muted">露台读书、桥边看荷花、园丁照料花草、店家招呼客人。可以点选居民，看看他正在做什么、为什么这么做。</p></article>
<article class="card pad"><span class="tag">更有变化</span><h3>错峰，而不是整齐划一</h3><p class="muted">聊天约8–20秒，用餐约32–72秒，电车停靠约12–20秒。每个人和每一轮都有变化，不等待现实中的漫长几分钟。</p></article>
</section>
<section id="rain" class="card">
<div class="pad"><h2>一阵雨，改变了大家的安排。</h2><p class="muted">雨来后陆续找位置、撑伞，店家照看柜台，二楼客人回帘后。雨停后先收伞，再慢慢恢复日常。</p></div>
<video controls muted playsinline preload="metadata" poster="04-rain-shelter.png" src="town-rain.webm"></video>
<figcaption>实际事件演示。当前避雨位置是可到达的屋檐或门前纸伞位；普通住宅的自由进屋还没有实现。</figcaption>
</section>
<section class="card pad"><h2>同一个小镇，可以过不同的一晚。</h2>
<table><thead><tr><th>心愿</th><th>居民的回应</th></tr></thead><tbody>
<tr><td>等一场花火</td><td>找空位 → 看演出 → 鼓掌、停留 → 各自散开；遇雨会等待。</td></tr>
<tr><td>唤醒热闹晚市</td><td>客人逛摊，店家回应真实来到面前的客人，没有客人时整理柜台。</td></tr>
<tr><td>邻里聊聊今天</td><td>寻找附近伙伴、面对彼此、轮流说话，保留通路。</td></tr>
<tr><td>晚饭时间到了</td><td>食客走向柜台，二楼客人回到自己的餐位。</td></tr>
<tr><td>安静看看风景</td><td>更多居民看水、听琴、歇息；风车和电车仍按自己的节奏运行。</td></tr>
</tbody></table></section>
<section class="card"><div class="pad"><h2>走近一点，看帘后与花园。</h2><p class="muted">完整屋顶和门帘保留。帘后增加真正的纸屏风、木格和茶具，让经过门口的一瞬间也有空间层次。</p></div>
<video controls muted playsinline preload="metadata" poster="06-interior-open.png" src="town-detail.webm"></video>
</section>
<section class="two"><figure class="card"><img loading="lazy" src="06-interior-open.png" alt="酒楼门帘与真实茶间"><figcaption>客人真实经过门帘；室内仍然受屋顶自然遮挡。</figcaption></figure><figure class="card"><img loading="lazy" src="07-garden-actions.png" alt="园丁与纸雕狐狸的网页近景"><figcaption>书、水壶和雨伞都是模型或受控组件，跟随居民身份和动作。</figcaption></figure></section>
<section><h2>这一轮怎样检查</h2><div class="grid">
<article class="card pad"><div class="number">28 项</div><p>行为与控制测试通过</p><p class="small muted">包括连续运行、不同事件组合、错峰、存档恢复、撤回与输入拒绝。</p></article>
<article class="card pad"><div class="number">__POSES__</div><p>真实浏览器姿态检查</p><p class="small muted">320秒内每0.5秒采样，复查全体人物、车辆、动物、雨伞和动态环境。最终未检测到意外相交。</p></article>
<article class="card pad"><div class="number">约 __FPS__ FPS</div><p>本机浏览器实测</p><p class="small muted">1600×1000、渲染比例1、无录屏。流畅衔接与帧率分别检查；不代表所有设备的性能。</p></article>
</div></section>
<details><summary>实现范围与检查记录</summary>
<p>32位居民都有角色和意图；当前8位可在地面路线行走，两位二楼客人有餐位与门帘往返，骑车居民随车移动，其余居民在各自工作或休息位置活动。尚未实现任意房间、楼梯、登车和完整社会关系。</p>
<p>碰撞检查是离散样本验证，不是对所有未来决策、所有时刻的绝对证明。另有1288个步行居民脚底支撑样本通过。语言功能小样本不能作为普遍准确率。</p>
<p><a href="行为设计与节奏.txt">行为与节奏说明</a> · <a href="制作与测试记录.txt">制作与测试记录</a> · <a href="调研与设计依据.txt">游戏行为设计调研</a> · <a href="browser-full-cast-final.json">模型接触报告</a> · <a href="performance-final.json">性能报告</a></p>
</details>
<p class="footer">仍然是独立的浏览器小镇：打开时生活，关闭后暂停。自然语言只调用一次决策接口，日常行为在本地运行。CP18保留，本页是CP19的验收候选。</p>
</main><script>
const lead=__LEAD__;document.querySelectorAll('[data-at]').forEach(b=>b.onclick=()=>{const v=document.querySelector('#mainVideo');v.currentTime=lead+Number(b.dataset.at);v.play();});
</script></body></html>'''
page=page.replace('__FPS__',str(round(perf['mean_fps']))).replace('__POSES__',f"{collision['body_poses']:,}").replace('__LEAD__',str(leads['life']))
(O/'review.html').write_text(page)
print('REVIEW_WRITTEN')
