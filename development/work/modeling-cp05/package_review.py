from pathlib import Path
from html.parser import HTMLParser
import json,re,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-05';PRE=ROOT/'outputs/modeling-checkpoint-04'
shutil.copy2(PRE/'approved-reference.png',OUT/'approved-reference.png');shutil.copy2(PRE/'01-overview.png',OUT/'cp04-comparison.png')
for name in ['revise_restaurant_terrace.py','finish_checkpoint.py','validate_checkpoint.py','package_review.py']:shutil.copy2(Path(__file__).parent/name,OUT/'source'/name)
shutil.copy2(ROOT/'work/modeling-cp01/build_town.py',OUT/'source/cp01_geometry_helpers_origin.py');shutil.copy2(ROOT/'work/modeling-cp02/refine_and_present.py',OUT/'source/cp02_material_aliases_origin.py')
old=(PRE/'review.html').read_text();style=re.search(r'<style>(.*?)</style>',old,re.S).group(1);events=re.search(r'(const main=document.*)</script>',old,re.S).group(1)
items={
 'model':{'label':'CP05 总览','src':'01-overview.png','alt':'CP05真实模型全景，饭店长立面与两段式露台','caption':'实际 Blender 渲染：饭店相对镜头的水平转角从45°收回到25°；右上露台改为两段楼梯。主镜头与其他核心建筑保持。'},
 'restaurant':{'label':'核心饭店近景','src':'03-restaurant-detail.png','alt':'核心饭店长立面、侧入口和纸灯笼近景','caption':'长立面为主，保留侧面厚度；整理侧入口、门帘、阳台、纸灯笼和边缘花箱。外围全部装饰与最终光影仍待后续精修。'},
 'terrace':{'label':'两段式露台近景','src':'04-terrace-detail.png','alt':'两段楼梯、中间平台、住家连接和上层座椅的近景','caption':'下段5级 → 转折平台 → 上段5级 → 观景座椅。补入支撑、铺地、石墙、栏杆和边缘种植；灯柱与座椅避让落脚空间。'},
 'reference':{'label':'认可参考图','src':'approved-reference.png','alt':'认可的柔光纸雕小镇参考','caption':'认可的v3柔光参考继续是建筑关系与氛围目标；这张是概念参考，不是模型渲染。'},
 'overlay':{'label':'参考叠图','src':'01-overview.png','alt':'CP05真实模型与认可参考叠加对照','caption':'下层CP05，上层参考。观察长立面、屋脊和露台关系的剩余差异，不代表整体已经1:1复原。'},
 'previous':{'label':'上版 CP04','src':'cp04-comparison.png','alt':'CP04真实模型历史全景','caption':'上版CP04：饭店45°转角更强，露台仍是单跑楼梯。原模型保持不变。'},
 'plan':{'label':'俯视布局','src':'02-plan.png','alt':'CP05同一模型的俯视布局','caption':'俯视辅助图：检查饭店朝向和两段楼梯的真实空间关系。'},
 'space':{'label':'活动空间预留','src':'05-reserved-space.png','alt':'CP05步行和交互设计预留层','caption':'青色为步行/入口设计预留，橙色为交互预留。该辅助层在主画面隐藏；尚不是完成导航或动作验证的区域。'}
}
buttons='\n'.join('<button type="button" data-view="'+k+'" aria-pressed="'+str(k=='model').lower()+'">'+v['label']+'</button>' for k,v in items.items())
html='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>借风町 · CP05 饭店与露台</title><style>'''+style+'''</style></head><body><main>
<h1>CP05 · 饭店长立面与两段式露台</h1><p>本轮已停下等待审阅。集中修订饭店和右上露台，其余已认可的核心建筑保持。</p>
<div class="controls" role="group" aria-label="选择检查画面">'''+buttons+'''</div>
<div class="controls" id="overlay-controls" hidden><label for="opacity">参考图透明度</label><input id="opacity" type="range" min="0" max="100" value="50"><output id="opacity-value">50%</output></div>
<figure><div class="stage"><img id="main-image" src="01-overview.png" width="1672" height="941" alt="CP05真实模型全景"><img id="overlay-image" class="overlay" src="approved-reference.png" alt="" hidden></div><figcaption id="caption" aria-live="polite">'''+items['model']['caption']+'''</figcaption></figure>
<div class="links"><a id="original" href="01-overview.png" target="_blank" rel="noopener">打开当前原图</a><a href="borrowed-wind-town-cp05.blend">可编辑 Blender 工程</a><a href="检查点说明.txt">检查点说明</a><a href="revision-record.json">修订记录</a><a href="validation.json">模型核验</a></div>
<div class="notes"><p>本轮重点：饭店是否以长立面为主、仍有侧面厚度；两段楼梯与平台是否更清楚、合理，是否留出停留位置。</p><p>24名人物的头部及上半身中心采样、30个踏面采样均通过。这些是静态局部检查，完整动作、全镇通行与碰撞仍待后续验证。人物仍为未绑定骨骼的比例占位，整体美术尚未达到参考图最终品质。</p></div>
</main><script>'use strict';\nconst items='''+json.dumps(items,ensure_ascii=False)+';\n'+events+'</script></body></html>'
(OUT/'review.html').write_text(html);(Path(__file__).parent/'review-script.js').write_text(re.search(r'<script>(.*?)</script>',html,re.S).group(1))
class Check(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.append(d['id'])
  for key in ['src','href']:
   if key in d:self.links.append(d[key])
c=Check();c.feed(html);targets=set(c.links+[v['src'] for v in items.values()]);missing=[v for v in targets if not(OUT/v).exists()];assert not missing;assert len(c.ids)==len(set(c.ids))
(OUT/'review-static-check.json').write_text(json.dumps({'local_targets_checked':len(targets),'missing_files':missing,'duplicate_ids':False,'view_count':len(items),'browser_visual_qa':False,'verification_scope':'Local links, HTML IDs and separate JavaScript syntax check only'},ensure_ascii=False,indent=2));print('CP05_REVIEW_READY',len(targets))
