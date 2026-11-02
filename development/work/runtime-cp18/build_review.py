# -*- coding: utf-8 -*-
from pathlib import Path
import json,html
R=Path.cwd();O=R/'outputs/runtime-checkpoint-18';caps=json.loads((O/'runtime-capabilities.json').read_text());qa=json.loads((O/'browser-final-qa.json').read_text());perf=json.loads((O/'performance-final.json').read_text())['profiles'][0];retina=json.loads((O/'performance-final.json').read_text())['profiles'][1]['mean_fps'];lead=json.loads((O/'video-record.json').read_text())['lead_in_seconds'];fps=perf['mean_fps']
page='''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>借风町 · CP18 动态与花火验收</title>
<style>
:root{color-scheme:dark;--bg:#0c1b2b;--panel:#142a3c;--ink:#eee3cf;--muted:#a1b6c7;--line:#314b5c;--gold:#e7ba79}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 12% 0%,#233e53,transparent 60%),var(--bg);color:var(--ink);font:16px/1.7 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}main{max-width:1320px;margin:auto;padding:52px 28px 80px}h1{font-size:clamp(34px,5vw,58px);font-weight:550;letter-spacing:.06em;line-height:1.25;margin:12px 0 18px}h2{font-size:25px;font-weight:550;margin:0 0 12px}h3{font-size:19px;font-weight:550;margin:0 0 10px}p{margin:0 0 15px}.eyebrow{color:var(--gold);letter-spacing:.18em;font-size:12px}a{color:#f1c58a;text-decoration:none}a:hover{text-decoration:underline}.lead{max-width:840px;color:#bbcad4;font-size:18px}.links{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0 28px}.button{border:1px solid #7d7058;border-radius:24px;padding:10px 20px;background:#263b47}.primary{background:var(--gold);color:#182737;border-color:var(--gold)}section{margin-top:32px}.card{border:1px solid var(--line);background:#14283bdd;border-radius:22px;overflow:hidden}.pad{padding:26px}video,img{display:block;width:100%;background:#10283c}video{max-height:78vh;object-fit:contain}figure{margin:0}figcaption{padding:15px 22px;color:var(--muted);font-size:14px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.two{display:grid;grid-template-columns:1fr 1fr;gap:20px}.muted{color:var(--muted)}.small{font-size:14px}.chapters{display:flex;flex-wrap:wrap;gap:8px;padding:16px 22px}.chapters button{font:inherit;font-size:14px;border:1px solid #456276;border-radius:18px;padding:6px 14px;background:#213c50;color:#e7d8be;cursor:pointer}.number{font-size:29px;color:var(--gold);line-height:1.2;margin-bottom:7px}details{margin-top:16px;padding:19px 22px;border:1px solid var(--line);border-radius:16px}summary{cursor:pointer;color:#dcc8a5}details p,details ul{margin-top:15px}ul{padding-left:23px}li{margin:6px 0}.tag{display:inline-block;font-size:12px;border:1px solid #496172;border-radius:12px;padding:1px 9px;margin-bottom:14px;color:#bdced6}.note{border-left:2px solid #ad895a;padding-left:18px}.footer{margin-top:36px;font-size:13px;color:#8fa7b8}@media(max-width:760px){main{padding:32px 16px 50px}.grid,.two{grid-template-columns:1fr}.pad{padding:21px}video{max-height:none}h1{letter-spacing:.03em}}
</style>
</head>
<body>
<main>
<div class="eyebrow">借风町 / CP18 / 实时网页验收</div>
<h1>小镇，开始过日子。</h1>
<p class="lead">电车会进站，也会再次回来。居民沿街走动，客人推开椅子走进门帘，纸鸟、鸭子、游鱼和风车各有自己的节奏。夜空里，是一场红金色的花火大会。</p>
<div class="links">
<a class="button primary" href="#live">看完整运行</a>
<a class="button" href="#details">看动作近景</a>
<a class="button" href="../../app/runtime-cp18/打开借风町.command" download>本地启动器</a>
<a class="button" href="../runtime-checkpoint-17/review.html">对比上一版 CP17</a>
</div>
<section id="live" class="card">
<video id="mainVideo" controls muted playsinline preload="metadata" poster="03-dining-and-streets.png" src="town-live.webm">
</video>
<div class="chapters">
<button data-at="0">从开始看</button>
<button data-at="4">减速进站</button>
<button data-at="17">花火大会</button>
<button data-at="26">客人回来用餐</button>
<button data-at="84">电车再次到站</button>
</div>
<figcaption>实际网页录制，未经加速。模型、行走、停靠和花火均在浏览器中实时运行。完整录像约 100 秒。</figcaption>
</section>
<section class="grid">
<article class="card pad">
<span class="tag">街道与交通</span>
<h3>从摆动，到真正移动</h3>
<p class="muted">8 位居民沿可走街道选择目标、走动和让路；骑车人缓缓滑行。电车沿真实轨道绕镇，进站减速，停靠约 6.5 秒后再出发。</p>
</article>
<article class="card pad">
<span class="tag">酒楼与水边</span>
<h3>动作有来有回</h3>
<p class="muted">两位二楼客人各自推椅、起身、穿过门帘，再回来用餐。屋顶保持完整。动物沿独立路线活动，船、水灯、风筝和花草也有细微变化。</p>
</article>
<article class="card pad">
<span class="tag">花火与晚风</span>
<h3>一场能看清的大花火</h3>
<p class="muted">红色为主、金色穿插，有升空、绽放、拖尾和短暂的映光。花火可以偶尔自动举行，也能响应一句心愿，结束后回到安静的小镇。</p>
</article>
</section>
<section id="details" class="card">
<div class="pad">
<h2>靠近一点，看动作。</h2>
<p class="muted">前半段看二楼客人，后半段看池塘与骑车人。视角朝向保持不变，只平移和放大画面。</p>
</div>
<video controls muted playsinline preload="metadata" poster="08-dining-detail.png" src="town-details.webm">
</video>
</section>
<section class="two">
<figure class="card">
<img loading="lazy" src="08-dining-detail.png" alt="酒楼二楼的真实网页近景">
<figcaption>门帘仍然保留；只在客人经过时折开。人物在屋内受到屋顶和建筑的真实遮挡。</figcaption>
</figure>
<figure class="card">
<img loading="lazy" src="09-pond-detail.png" alt="池塘和木桥的真实网页近景">
<figcaption>水面保留蓝色纸感。鸭子、游鱼与浮灯分别运动，前景栏杆会产生自然遮挡。</figcaption>
</figure>
</section>
<section class="card pad">
<h2>现在可以怎样影响小镇？</h2>
<p class="muted">启动网页后，可以写自己的话，也可以打开「小镇手记」直接选动作。</p>
<div class="two">
<div>
<p>「让红色小电车到站后，多等一会儿。」<br>「楼上的客人吃饱啦，回门帘后歇一歇。」<br>「今晚想看一场火红的花火大会。」</p>
</div>
<div>
<p>「池塘里的鱼和鸭子歇一会儿。」<br>「邮局门前拿信的邮差，沿街走走吧。」<br>「风轻一点，下些纸片雪，让乐手歇一会儿。」</p>
</div>
</div>
<p class="small muted">自然语言仍是一次 OpenRouter Decisions 请求。日常活动在网页本地运行，不会持续调用模型。关闭网页后暂停，回来读取本机存档。</p>
</section>
<section>
<h2>这一版怎样验收过</h2>
<div class="grid">
<article class="card pad">
<div class="number">20 / 20</div>
<p>控制与模拟检查通过</p>
<p class="small muted">包括连续运行、目标切换、暂停、存档恢复、撤回和损坏输入。</p>
</article>
<article class="card pad">
<div class="number">10,455</div>
<p>实际网页姿态复查</p>
<p class="small muted">102 秒内每 0.5 秒采样，包含动态环境与物体之间的接触；未检测到意外相交。</p>
</article>
<article class="card pad">
<div class="number">2,400 + 1,200</div>
<p>整圈电车密集检查</p>
<p class="small muted">车身与转向车轮 2,400 个姿态、车厢之间 1,200 个位置，均通过。</p>
</article>
</div>
<details>
<summary>查看性能、测试范围与当前限制</summary>
<p>本机 Apple M2 Pro、Chromium、1600 × 1000、像素比 1 的独立测试，平均约 <b>__FPS__ FPS</b>；像素比 1.25 时约 <b>__RETINA__ FPS</b>。这是一台设备上的结果，不代表所有浏览器和手机。网页控制、实际接口、错误恢复、声音和移动布局均另行检查。</p>
<p>碰撞结果来自当前动作范围的离散网格表面采样。水面与水纹属于允许的液体接触；安装在一起的部件按装配关系处理。后续新增动作、路线和姿态仍需重新验收。</p>
<ul>
<li>8 位地面居民可寻路；目前不包含楼梯、任意室内通行和所有居民的完整行为。</li>
<li>骑车人当前是滑行和让路，尚未制作踩踏板与下车；小船是系泊轻晃，尚无自由航行或上下客。</li>
<li>纸鸟可飞行和悬停，尚无落地、归巢。网页灯光仍是对认可模型的实时转译，并非与离线渲染逐像素一致。</li>
</ul>
<p>
<a href="检查点说明.txt">完整说明</a> · <a href="browser-full-cast-final.json">姿态检查</a> · <a href="browser-train-full-loop-check.json">整圈电车检查</a> · <a href="browser-final-qa.json">网页检查</a> · <a href="performance-final.json">性能实测</a> · <a href="runtime-capabilities.json">实际动作范围</a>
</p>
</details>
</section>
<section class="card pad">
<h2>保留的工程与记录</h2>
<p>模型、源代码、原始接口记录、成功与失败的检查轮次均已保存在项目里。CP16 认可模型和 CP17 保留。</p>
<div class="links">
<a class="button" href="borrowed-wind-town-cp18.blend">可编辑模型</a>
<a class="button" href="../../app/runtime-cp18/public/assets/town.glb">网页模型</a>
<a class="button" href="制作与测试记录.txt">制作与测试记录</a>
<a class="button" href="../ecosystem-v3-lighting/borrowed-wind-town-soft-light.png">认可的美术参考</a>
</div>
<p class="small muted">本页与录像可以直接打开。要实际交互，请在本机双击「本地启动器」；它启动网页和按需接口，小镇的模拟仍在浏览器里。Blender 工程保存模型与控制支点，动作由网页代码执行。</p>
</section>
<p class="footer">CP18 是新的动态验收版，等待你的体验反馈。保留纸雕风格、完整屋顶与固定 43° 朝向。</p>
</main>
<script>const video=document.querySelector('#mainVideo');const lead=__LEAD__;document.querySelectorAll('[data-at]').forEach(b=>b.addEventListener('click',()=>{video.currentTime=lead+Number(b.dataset.at);video.play();video.scrollIntoView({behavior:'smooth',block:'center'});}));</script>
</body>
</html>'''.replace('__FPS__',str(round(fps,1))).replace('__LEAD__',str(round(lead,3))).replace('__RETINA__',str(round(retina,1)))
(O/'review.html').write_text(page)
