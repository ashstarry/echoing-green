from pathlib import Path
from html.parser import HTMLParser
import json,re,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-04';PRE=ROOT/'outputs/modeling-checkpoint-03'
for src,dst in [(PRE/'approved-reference.png','approved-reference.png'),(PRE/'01-overview.png','cp03-comparison.png'),(ROOT/'outputs/modeling-checkpoint-02/01-overview.png','cp02-comparison.png')]:shutil.copy2(src,OUT/dst)
for name in ['revise_two_faces.py','refine_clearance.py','finish_checkpoint.py','render_saved.py','validate_checkpoint.py','package_review.py']:shutil.copy2(Path(__file__).parent/name,OUT/'source'/name)
shutil.copy2(ROOT/'work/modeling-cp01/build_town.py',OUT/'source/cp01_geometry_helpers_origin.py');shutil.copy2(ROOT/'work/modeling-cp02/refine_and_present.py',OUT/'source/cp02_material_aliases_origin.py')
old=(PRE/'review.html').read_text();style=re.search(r'<style>(.*?)</style>',old,re.S).group(1);events=re.search(r'(const main=document.*)</script>',old,re.S).group(1)
items={
 'model':{'label':'CP04 模型','src':'01-overview.png','alt':'CP04真实模型全景，茶屋和左上住宅同时显露两面','caption':'实际模型渲染：主镜头沿用CP03；茶屋和左上住家以约45°的水平转角呈现，并补充可见侧面的窗格、木构和阳台转角。'},
 'detail':{'label':'两面建筑近景','src':'03-architecture-detail.png','alt':'茶屋、左上住宅和圆顶望楼的真实模型近景','caption':'同一模型、同一观察方向的近景。重点看两面的窗光、转角木构和檐下阴影。整体纸材与夜市光影仍待精修。'},
 'reference':{'label':'认可参考图','src':'approved-reference.png','alt':'认可的柔光纸雕小镇参考','caption':'认可参考继续作为美术目标；当前模型仍有轮廓、构件、材质和光影差距。参考不是模型渲染。'},
 'overlay':{'label':'参考叠图','src':'01-overview.png','alt':'CP04与认可参考叠加','caption':'下层是CP04模型，上层是参考。检查转角、体量及其对市场排布的影响；叠图不代表整体已经1:1还原。'},
 'previous':{'label':'上版 CP03','src':'cp03-comparison.png','alt':'保留的CP03真实模型全景','caption':'CP03：相同主镜头，可直接比较之前偏正面的建筑和现在的双立面呈现。'},
 'older':{'label':'更早 CP02','src':'cp02-comparison.png','alt':'保留的CP02真实模型全景','caption':'CP02历史版本：镜头为45°俯角，尚未完成本轮朝向与高台等修订。'},
 'plan':{'label':'俯视布局','src':'02-plan.png','alt':'CP04模型俯视图','caption':'实际模型俯视图，可看到茶屋与左上住家在地面上的转向；主镜头没有随之旋转。'},
 'space':{'label':'活动空间预留','src':'04-reserved-space.png','alt':'CP04活动空间辅助图','caption':'青色为步行空间预留，橙色为交互预留。市场预留带随立面更新；这些仍是设计辅助，不是已通过导航、碰撞或动作测试的空间。'}
}
buttons='\n'.join('<button type="button" data-view="'+k+'" aria-pressed="'+str(k=='model').lower()+'">'+v['label']+'</button>' for k,v in items.items())
html='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>借风町 · CP04 双立面建筑</title><style>'''+style+'''</style></head><body><main>
<h1>CP04 · 同时读到建筑的两面</h1><p>这一版已停下等待审阅。主镜头保持43°俯角；调整的是建筑在地面上的朝向，以及实际露出的侧面构件。</p>
<div class="controls" role="group" aria-label="选择对照画面">'''+buttons+'''</div>
<div class="controls" id="overlay-controls" hidden><label for="opacity">参考图透明度</label><input id="opacity" type="range" min="0" max="100" value="50"><output id="opacity-value">50%</output></div>
<figure><div class="stage"><img id="main-image" src="01-overview.png" width="1672" height="941" alt="CP04真实模型全景"><img id="overlay-image" class="overlay" src="approved-reference.png" alt="" hidden></div><figcaption id="caption" aria-live="polite">'''+items['model']['caption']+'''</figcaption></figure>
<div class="links"><a id="original" href="01-overview.png" target="_blank" rel="noopener">打开当前原图</a><a href="borrowed-wind-town-cp04.blend">可编辑 Blender 工程</a><a href="检查点说明.txt">检查点说明</a><a href="revision-record.json">修订记录</a><a href="validation.json">模型核验</a></div>
<div class="notes"><p>本轮重点：茶屋与左上住家的正面、侧面是否都足够清楚；两面露出的比例及屋脊斜率是否更接近你想要的效果。</p><p>24名人物仍是比例占位，头部与上半身中心的静态采样均可见；全身动作和通行仍待以后验证。原有住家/附属小屋的体块连接、纸材和整体氛围尚未完成。</p></div>
</main><script>'use strict';\nconst items='''+json.dumps(items,ensure_ascii=False)+';\n'+events+'</script></body></html>'
(OUT/'review.html').write_text(html)
(Path(__file__).parent/'review-script.js').write_text(re.search(r'<script>(.*?)</script>',html,re.S).group(1))
class Check(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.append(d['id'])
  for k in ['src','href']:
   if k in d:self.links.append(d[k])
c=Check();c.feed(html);targets=set(c.links+[v['src'] for v in items.values()]);missing=[p for p in targets if not(OUT/p).exists()];assert not missing,missing;assert len(c.ids)==len(set(c.ids))
(OUT/'review-static-check.json').write_text(json.dumps({'local_targets_checked':len(targets),'missing_files':missing,'duplicate_ids':False,'view_count':len(items),'browser_visual_qa':False,'verification_scope':'Local links, HTML IDs and separate JavaScript syntax check only'},ensure_ascii=False,indent=2))
print('CP04_REVIEW_READY',len(targets))
