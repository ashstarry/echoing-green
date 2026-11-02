from pathlib import Path
import json,shutil,re
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-03';PRE=ROOT/'outputs/modeling-checkpoint-02'
shutil.copy2(PRE/'approved-reference.png',OUT/'approved-reference.png')
shutil.copy2(PRE/'01-overview.png',OUT/'cp02-comparison.png')
for name in ['revise_model.py','finish_checkpoint.py','clear_routes.py','validate_checkpoint.py']:
 shutil.copy2(Path(__file__).parent/name,OUT/'source'/name)
shutil.copy2(ROOT/'work/modeling-cp01/build_town.py',OUT/'source/cp01_geometry_helpers_origin.py')
shutil.copy2(ROOT/'work/modeling-cp02/refine_and_present.py',OUT/'source/cp02_material_aliases_origin.py')
style=re.search(r'<style>(.*?)</style>',(PRE/'review.html').read_text(),re.S).group(1)
items={
 'model':{'label':'CP03 模型','src':'01-overview.png','alt':'CP03真实模型的43度正交主视角渲染','caption':'实际 Blender 渲染：镜头从45°轻降至43°；修订建筑朝向与右上角高台。细部、材质和角色仍待后续完成。'},
 'reference':{'label':'认可参考图','src':'approved-reference.png','alt':'用户认可的柔光纸雕小镇参考图','caption':'认可参考继续是环境、建筑关系和氛围的目标。这张是概念参考，不是模型渲染。'},
 'overlay':{'label':'参考叠图','src':'01-overview.png','alt':'CP03真实模型与认可参考的叠加对比','caption':'下层为真实模型，上层为参考；拖动透明度查看剩余差异。叠图不代表整体还原度已经达到1:1。'},
 'previous':{'label':'上版 CP02','src':'cp02-comparison.png','alt':'保留的CP02模型渲染','caption':'上版 CP02：45°正交镜头。可比较屋脊方向、后山高差和人物遮挡变化。旧模型没有覆盖。'},
 'hill':{'label':'高台与楼梯','src':'03-hill-detail.png','alt':'真实模型高台阶梯近景','caption':'同一真实模型的局部相机：8级阶梯、落脚平台、座椅和栏杆。人物仍是未绑定骨骼的比例占位。'},
 'plan':{'label':'俯视布局','src':'02-plan.png','alt':'CP03真实模型俯视布局','caption':'同一模型的俯视布局；天空纸饰隐藏，用于核对建筑占地、通道和高台位置。主镜头仍为43°正交。'},
 'space':{'label':'活动空间预留','src':'04-reserved-space.png','alt':'模型内活动空间设计预留的俯视辅助图','caption':'青色：步行空间预留；橙色：交互位置预留。辅助层在正常画面中隐藏，不是最终美术配色，也不是已通过导航或动作测试的区域。'}
}
buttons='\n'.join('<button type="button" data-view="'+k+'" aria-pressed="'+str(k=='model').lower()+'">'+v['label']+'</button>' for k,v in items.items())
html='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>借风町 · CP03 空间修订</title><style>'''+style+'''</style></head><body><main>
<h1>CP03 · 朝向、山阶与活动空间</h1>
<p>本轮已停在检查点。保持认可参考方向，先检查镜头、建筑关系和可活动的空间。</p>
<div class="controls" role="group" aria-label="选择检查画面">'''+buttons+'''</div>
<div class="controls" id="overlay-controls" hidden><label for="opacity">参考图透明度</label><input id="opacity" type="range" min="0" max="100" value="50"><output id="opacity-value">50%</output></div>
<figure><div class="stage"><img id="main-image" src="01-overview.png" width="1672" height="941" alt="CP03真实模型的43度正交主视角渲染"><img id="overlay-image" class="overlay" src="approved-reference.png" alt="" hidden></div><figcaption id="caption" aria-live="polite">'''+items['model']['caption']+'''</figcaption></figure>
<div class="links"><a id="original" href="01-overview.png" target="_blank" rel="noopener">打开当前原图</a><a href="borrowed-wind-town-cp03.blend">可编辑 Blender 工程</a><a href="检查点说明.txt">检查点说明</a><a href="revision-record.json">本轮修订记录</a><a href="validation.json">模型核验</a></div>
<div class="notes"><p>后续细节遵循同一原则：先保留街道与交互位置，再放置花草、店铺外摆和建筑构件；每轮复查主镜头中的人物遮挡。</p><p>当前24名占位人物的头部和上半身中心视线采样均可见。这是静止摆位检查；全身动作、连续移动、导航碰撞仍待之后验证。建筑细节、植被和光影尚未达到参考品质。</p></div>
</main><script>
'use strict';
const items='''+json.dumps(items,ensure_ascii=False)+''';
const main=document.getElementById('main-image'),overlay=document.getElementById('overlay-image'),controls=document.getElementById('overlay-controls'),slider=document.getElementById('opacity'),caption=document.getElementById('caption'),link=document.getElementById('original');
function opacity(){overlay.style.opacity=Number(slider.value)/100;document.getElementById('opacity-value').textContent=slider.value+'%';}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{const k=b.dataset.view,v=items[k];main.src=v.src;main.alt=v.alt;overlay.hidden=k!=='overlay';controls.hidden=k!=='overlay';caption.textContent=v.caption;link.href=v.src;document.querySelectorAll('[data-view]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));opacity();}));
slider.addEventListener('input',opacity);opacity();
</script></body></html>'''
(OUT/'review.html').write_text(html)
script=re.search(r'<script>(.*?)</script>',html,re.S).group(1);(Path(__file__).parent/'review-script.js').write_text(script)
class Check(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.append(d['id'])
  for k in ['src','href']:
   if k in d:self.links.append(d[k])
c=Check();c.feed(html)
targets=set(c.links+[v['src'] for v in items.values()]);missing=[p for p in targets if not(OUT/p).exists()]
assert not missing,missing
assert len(c.ids)==len(set(c.ids))
(OUT/'review-static-check.json').write_text(json.dumps({'local_targets_checked':len(targets),'missing_files':missing,'duplicate_ids':False,'view_count':len(items),'browser_visual_qa':False,'verification_scope':'Local link existence, HTML IDs and separate JavaScript syntax check only'},ensure_ascii=False,indent=2))
print('REVIEW_PACKAGED',len(targets),'local targets')
