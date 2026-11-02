from pathlib import Path
from html.parser import HTMLParser
import re,json,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-06';PRE=ROOT/'outputs/modeling-checkpoint-05'
shutil.copy2(PRE/'approved-reference.png',OUT/'approved-reference.png');shutil.copy2(PRE/'01-overview.png',OUT/'cp05-comparison.png')
for name in ['build_revision.py','refine_paths.py','finalize_layout.py','check_circulation.py','validate_checkpoint.py','render_checkpoint.py','package_review.py']:shutil.copy2(Path(__file__).parent/name,OUT/'source'/name)
for src,dst in [('work/modeling-cp01/build_town.py','cp01_geometry_helpers_origin.py'),('work/modeling-cp02/refine_and_present.py','cp02_material_aliases_origin.py'),('work/modeling-cp05/revise_restaurant_terrace.py','cp05_slab_helpers_origin.py')]:shutil.copy2(ROOT/src,OUT/'source'/dst)
old=(PRE/'review.html').read_text();style=re.search(r'<style>(.*?)</style>',old,re.S).group(1)
style+=' .sequence{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.sequence img{display:block;width:100%;height:auto}.sequence figure{background:#0e1925;padding:8px}.sequence figcaption{padding:0 5px}.legend{display:flex;gap:18px;flex-wrap:wrap;margin:12px 0;color:#c0c7cb}@media(max-width:700px){.sequence{grid-template-columns:1fr}}'
items={
 'model':{'label':'CP06 总览','src':'01-overview.png','alt':'CP06真实模型正常全景，完整屋顶','caption':'真实 Blender 渲染：保留完整屋顶和原主镜头，补上侧档口，扩大露台并接通二楼至露台的实际空间。'},
 'stall':{'label':'饭店侧档口','src':'03-side-stall.png','alt':'新增的饭店侧面档口近景','caption':'雨棚、柜台和服务口已建出，入口与接近位置分别安排；附近树冠让出顾客接近路线。'},
 'terrace':{'label':'可活动的露台','src':'04-terrace.png','alt':'扩大后的露台与长椅、楼梯和连接步道','caption':'楼梯口先有转身空间，再接到主通道；长椅、花盆和灯柱沿边缘布置。左侧新连廊通往二楼。'},
 'cutaway':{'label':'动线检查（揭顶）','src':'05-circulation-cutaway.png','alt':'仅用于检查的揭顶动线图','caption':'检查视图：青色为通行预留，橙色为起身/转身等短时动作区域。A起身入走道、B门口、C连廊、D转身、E长椅起身过渡。正常画面仍保留完整屋顶。'},
 'door':{'label':'门口进出检查','src':'door-sequence/01.png','alt':'门口的连续位置检查','caption':'同一个未绑定骨骼的比例人的4个相邻位置，屋顶完整、人物未切换隐藏状态。用于检查真实遮挡中的进出过程；不是正式行走动画。'},
 'reference':{'label':'认可参考图','src':'approved-reference.png','alt':'用户认可的柔光小镇参考','caption':'认可的v3参考继续是艺术目标；新增功能空间不等于整体画面已1:1还原。'},
 'previous':{'label':'上版 CP05','src':'cp05-comparison.png','alt':'CP05模型的历史总览','caption':'CP05历史版本：可比较侧档口、露台地面和二楼连接的变化。旧模型没有覆盖。'},
 'plan':{'label':'俯视布局','src':'02-plan.png','alt':'CP06真实模型俯视布局','caption':'同一模型的俯视辅助图，用于检查建筑、台阶与平台的实际位置。'}
}
buttons='\n'.join('<button type="button" data-view="'+k+'" aria-pressed="'+str(k=='model').lower()+'">'+v['label']+'</button>' for k,v in items.items())
cards=''.join('<figure><img src="door-sequence/%02d.png" alt="门口位置检查%d"><figcaption>%d · %s</figcaption></figure>'%(i,i,i,text) for i,text in enumerate(['门口内侧','开始走出','过门中段','门外平台'],1))
html='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>借风町 · CP06 侧档口与连续活动空间</title><style>'''+style+'''</style></head><body><main>
<h1>CP06 · 侧档口与连续活动空间</h1><p>已停在检查点等待审阅。通行、停留和操作分别留空间；正常观看保留完整屋顶。</p>
<div class="controls" role="group" aria-label="选择检查画面">'''+buttons+'''</div>
<figure id="single-view"><div class="stage"><img id="main-image" src="01-overview.png" width="1672" height="941" alt="CP06真实模型正常全景"></div></figure>
<div id="door-view" class="sequence" hidden>'''+cards+'''</div><p id="caption" aria-live="polite">'''+items['model']['caption']+'''</p>
<div class="links"><a id="original" href="01-overview.png" target="_blank" rel="noopener">打开当前原图</a><a href="borrowed-wind-town-cp06.blend">可编辑 Blender 工程</a><a href="空间与行为说明.txt">各位置的活动逻辑</a><a href="检查点说明.txt">检查点说明</a><a href="validation.json">模型核验</a></div>
<div class="notes"><p>重点查看：侧档口是否到位；楼梯口和长椅前是否有可活动空间；二楼—门口—连廊—露台的去向是否清楚。</p><p>本轮检查固定构件、地面支撑与局部视线。完整起身/走路动画、多人避让、寻路和网页运行尚未实现。正常屋顶内允许真实遮挡，室外主路线按可连续观察来检查。</p></div>
</main><script>'use strict';
const items='''+json.dumps(items,ensure_ascii=False)+''';
const main=document.getElementById('main-image'),single=document.getElementById('single-view'),door=document.getElementById('door-view'),caption=document.getElementById('caption'),link=document.getElementById('original');
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{const k=b.dataset.view,v=items[k];single.hidden=k==='door';door.hidden=k!=='door';main.src=v.src;main.alt=v.alt;caption.textContent=v.caption;link.href=v.src;document.querySelectorAll('[data-view]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));}));
</script></body></html>'''
(OUT/'review.html').write_text(html);(Path(__file__).parent/'review-script.js').write_text(re.search(r'<script>(.*?)</script>',html,re.S).group(1))
class Check(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  for k in ['href','src']:
   if k in a:self.links.append(a[k])
c=Check();c.feed(html);targets=set(c.links+[v['src'] for v in items.values()]);missing=[p for p in targets if not(OUT/p).exists()];assert not missing;assert len(c.ids)==len(set(c.ids))
(OUT/'review-static-check.json').write_text(json.dumps({'local_targets_checked':len(targets),'missing_files':missing,'duplicate_ids':False,'views':len(items),'browser_visual_qa':False,'scope':'Local links, HTML IDs, JavaScript syntax only'},ensure_ascii=False,indent=2));print('CP06_REVIEW_READY',len(targets))
