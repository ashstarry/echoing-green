from pathlib import Path
p=Path('app/runtime-cp42/decision-api.mjs')
s=p.read_text().replace('小船不能离岸','小船只能在已有池塘内离岸再回泊，不能出海或载人').replace('船不能离岸','船只能在已有池塘内航行，不能远航或载人')
s=s.replace("if(Number.isInteger(input.paper_count)","if(Number.isInteger(input.memory_count)&&input.memory_count>=0&&input.memory_count<=6)s.memory_count=input.memory_count;\n if(Number.isInteger(input.paper_count)")
needle=" questions['object.fox'].instructions="
insert=""" questions.craft.instructions='现有街边生活有真实动作流程，不要求用户逐字点名：一杯茶、让一双手被热气暖一暖、给客人递杯热的=tea；揭蒸笼、递点心=snack；借伞、分一把伞、陪人走过小雨=umbrella；让落叶铺一小段路再整理/扫秋叶=leaves；把刚才的心情/片刻留作小纪念=remember；拿起/看看已留下的纪念=recall；收起纪念=putaway；让布巾/衣物晒晒风、晾晒=laundry；把布收回来/下雨前收衣=bring_in；停止当前小活动=rest。每种只安排合适的一两个人，不需要全镇。不自动解释为晚市、全体聚餐、全镇降雨。已经有纸笺要挂树或分享心意由paper负责；纪念角的保留/回看才是remember/recall。只称赞过去、假设、明确不改=keep。';
 questions['scope:craft'].instructions='具体或诗意地邀请热茶点心、借伞同行、扫落叶、留下/回看纪念物、晾晒收布时yes；不必说命令式词语。纯天气、泛泛热闹/想念而无这些关系、过去称赞、假设保持则no。';
 questions.cloud.instructions='这里只控制已有小雨云。想它沿街散步、把雨带到几个街角、挪动这朵云=wander；仅给花园/花草下雨=garden；让小云去集市附近=market；收住局部雨/让小云回去=rest。这些是局部雨，不应同时全镇rain。不提小云/特定局部而泛指下雨，cloud=keep由weather负责。';
 questions['scope:cloud'].instructions='明确或诗意邀请这朵小云移动、只给某个角落一小片雨、局部雨停=yes。只说全镇下雨、雨停=no。';
 questions.weather.instructions+=' 小雨云只在一个角落/花园/集市下雨或沿街移动属于cloud，weather=keep。局部雨不等于全镇天气。';
 questions['scope:weather'].instructions+=' Only a small cloud moving or raining on one named corner/garden is local cloud, choose no for global weather.';
 questions.journey.instructions+=' 把包裹/礼物托现有电车捎一程，或希望列车带一件小物回来交给街坊，选deliver。已有真实包裹装车、随车、下车和交接；没有跨世界目的地或新增人。';
 questions['scope:journey'].instructions+=' 电车捎来包裹/托列车带小礼物也选yes。';
 questions['object.boat'].instructions='现有小木船可cruise：收桨、松绳，在池塘内走一小程再回泊；dock：提前回泊；rest：先平稳停下；row只在原处摆桨；bob系泊轻摇。想让船看看池塘另一边/水路带它出去一小程可以cruise，不能出海、离开池塘或乘人。';
 questions.intent_status.instructions+=' 热茶点心、借伞同行、落叶整理、有限纪念角、晾晒收布、现有雨云移动与局部降雨、现有船在池塘内离岸回泊、电车带包裹交接都已经实现；这些相关诗意愿望属于change，不是新造物件。';
"""
s=s.replace(needle,insert+needle)
# intent_status is reassigned later, so append the capability clarification there too.
s=s.replace(" questions.lighting_coverage=", " questions.intent_status.instructions+=' 支持街边热茶点心、借伞同行、落叶整理、保留回看纪念物、晾晒收布、小云移动并局部下雨、小船在池塘内离岸回泊、电车托包裹。';\n questions.lighting_coverage=")
s=s.replace("['neighborhood','journey'].includes(key)","['neighborhood','journey','craft','cloud'].includes(key)")
s=s.replace("['depart','welcome'].includes(trip.action)","['depart','welcome','deliver'].includes(trip.action)")
needle=" const executionKey=item=>"
guard=""" const localCloud=items.find(i=>i.kind==='macro'&&i.target==='cloud'&&i.action!=='rest');
 const small=items.find(i=>i.kind==='macro'&&i.target==='craft'&&i.action!=='rest');
 for(let i=items.length-1;i>=0;i--){const x=items[i];if(!allTown&&(localCloud&&x.target==='weather'&&x.action==='rain'||small&&['occasion','street'].includes(x.target)&&['supper','market','reunion','quiet','gather'].includes(x.action)||small?.action==='umbrella'&&x.target==='weather'&&x.action==='rain'||trip?.action==='deliver'&&x.target==='occasion'&&x.action==='delivery')){skipped.push({...x,reason:'让这段局部生活保持自己的参与范围'});items.splice(i,1);}}
"""
s=s.replace(needle,guard+needle)
p.write_text(s)
p=Path('app/runtime-cp42/src/atmosphere.mjs');s=p.read_text().replace("'neighborhood','journey'","'neighborhood','journey','craft','cloud'").replace("journey:['rest','keep']","journey:['rest','keep'],craft:['rest','keep'],cloud:['rest','keep']");p.write_text(s)
# Freeze selected keepsake when the request is queued, not when it eventually executes.
p=Path('app/runtime-cp42/src/life-plans.mjs');s=p.read_text().replace("sourceText='',preserveOthers=false","sourceText='',preserveOthers=false,selectedMemory=null").replace("source,preserveOthers:!!preserveOthers","source,selectedMemory,preserveOthers:!!preserveOthers").replace("sourceText:jobs[0].sourceText||''","sourceText:jobs[0].sourceText||'',selectedMemory:jobs[0].selectedMemory||null");p.write_text(s)
p=Path('app/runtime-cp42/src/simulation.mjs');s=p.read_text().replace("eventPolicy=true,sourceText=''","eventPolicy=true,sourceText='',selectedMemory=null").replace("text=>event(s,text),{sourceText}","text=>event(s,text),{sourceText,selectedMemory}");p.write_text(s)
p=Path('app/runtime-cp42/src/scene-events.mjs');s=p.read_text().replace("{sourceText=''}={}","{sourceText='',selectedMemory=null}={}").replace("selectedMemory:s.selectedMemory||null","selectedMemory:selectedMemory||null");p.write_text(s)
