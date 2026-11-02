
'use strict';
const items={model:{src:'01-overview.png',alt:'CP02模型的45度正交主视角渲染',caption:'真实Blender渲染：固定45°俯角与正交投影。建筑位置、进深和活动面已重新校准，细部与材质尚未完成。'},reference:{src:'approved-reference.png',alt:'用户认可的柔光小镇参考图',caption:'认可参考图：空间、建筑关系与氛围的目标。此图不是CP02模型渲染。'},overlay:{src:'01-overview.png',alt:'CP02模型与参考图叠加对照',caption:'叠图：下层为真实模型，上层为参考图。移动滑杆观察位置、轮廓和尺度偏差；不是整体相似度评分。'},previous:{src:'cp01-comparison.png',alt:'上一次CP01模型渲染',caption:'上版CP01，原件保留。可比较建筑遮挡、站台和整镇占屏变化。'},plan:{src:'02-plan.png',alt:'CP02同一模型的俯视布局',caption:'CP02俯视辅助图，用于看建筑占地和道路连接。产品主视角仍固定为45°正交。'}};
const main=document.getElementById('main-image'),overlay=document.getElementById('overlay-image'),controls=document.getElementById('overlay-controls'),slider=document.getElementById('opacity'),caption=document.getElementById('caption'),link=document.getElementById('original');
function opacity(){overlay.style.opacity=Number(slider.value)/100;document.getElementById('opacity-value').textContent=slider.value+'%';}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{const k=b.dataset.view,v=items[k];main.src=v.src;main.alt=v.alt;overlay.hidden=k!=='overlay';controls.hidden=k!=='overlay';caption.textContent=v.caption;link.href=v.src;document.querySelectorAll('[data-view]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));opacity();}));
slider.addEventListener('input',opacity);opacity();
