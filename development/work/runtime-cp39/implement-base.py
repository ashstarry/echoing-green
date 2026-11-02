from pathlib import Path
import json
base=Path('app/runtime-cp39')
p=base/'src/interaction-sequence.mjs';s=p.read_text().replace("receive:{kind:'pose',seconds:3.2}","receive:{kind:'pose',seconds:3.2},carry:{kind:'move'},place:{kind:'pose',seconds:2.4},wipe:{kind:'pose',seconds:4.4},open:{kind:'pose',seconds:1.7},welcome:{kind:'pose',seconds:4.2},wait_for:{kind:'pose',seconds:.2},unfold:{kind:'pose',seconds:3.2},admire:{kind:'pose',seconds:3.6},pack:{kind:'pose',seconds:2.5}")
s=s.replace(' hang_note:[',""" home_host:[{action:'approach',target:'destination'},{action:'open'},{action:'wait_for',waitFor:'partner'},{action:'welcome'},{action:'offer'},{action:'admire'}],
 home_arrive:[{action:'approach',target:'destination'},{action:'wait_for',waitFor:'door'},{action:'welcome'},{action:'receive'},{action:'admire'}],
 carry_place:[{action:'approach',target:'supply'},{action:'take'},{action:'carry',target:'destination'},{action:'place'},{action:'admire'}],
 carry_give:[{action:'approach',target:'supply'},{action:'take'},{action:'carry',target:'destination'},{action:'offer'},{action:'place'}],
 wipe_place:[{action:'approach',target:'destination'},{action:'take'},{action:'wipe'},{action:'stow'},{action:'unfold'},{action:'admire'}],
 plant_flower:[{action:'approach',target:'supply'},{action:'take'},{action:'carry',target:'destination'},{action:'place'},{action:'unfold'},{action:'admire'}],
 hang_note:[""")
p.write_text(s)
p=base/'src/catalog.mjs';s=p.read_text();line="DOMAINS.neighborhood={label:'街坊一起做的事',choices:{keep:'保持街坊当前安排',homecoming:'留一盏灯等晚归的人：居民走向家门、开门迎接、暖窗亮起',prepare:'一起筹备庆祝：搬小凳、摆点心、递纸灯，准备好后邻居相聚',reopen:'雨后重新开始：收伞、擦椅、重新摆回商品，自行车与小动物恢复活动',spring:'把春天带到街角：搬花盆、折纸花展开、孩子牵风筝、居民扶帽，风铃轻响',rest:'停止新的街坊协作，收好手里的东西，保留已经摆好的小物'}};\n"
s=s.replace('export const KEEP={};',line+'export const KEEP={};');s+="\nCHOICE_LABELS.neighborhood={homecoming:'留灯迎归人',prepare:'一起筹备庆祝',reopen:'雨后重新开张',spring:'让春天走进街角',rest:'收好手里的东西'};\n";p.write_text(s)
p=base/'semantic-contract.json';r=json.loads(p.read_text());r['fields']['neighborhood']={'label':'街坊协作与小镇变化','kind':'macro','available':True,'choices':{'keep':'保持当前安排','homecoming':'留灯等晚归、回家有人迎接、门打开暖窗变化','prepare':'为欢庆做准备：搬凳、点心、纸灯，之后相聚','reopen':'雨后重新生活：收伞擦拭摆回商品，街道恢复活动','spring':'春风花开：搬盆与纸花展开、牵风筝、扶帽、风铃','rest':'不要或停止新的街坊协作'}};p.write_text(json.dumps(r,ensure_ascii=False,indent=2))
p=base/'src/atmosphere.mjs';s=p.read_text().replace("changes:{occasion:'reunion',music:'play',light:'warm',breeze:'lively'}","changes:{neighborhood:'prepare',music:'play',light:'warm',breeze:'lively'}").replace("hopeful:{label:'让街巷亮起来，把新的好心情传开。',changes:{occasion:'market',light:'bright',breeze:'gentle'}}","hopeful:{label:'把春天带进街角，让花和晚风先动起来。',changes:{neighborhood:'spring',light:'warm',breeze:'gentle'}}").replace("['weather','festival','occasion','paper']","['weather','festival','occasion','paper','neighborhood']")
s=s.replace("const paperOff=", "const neighborhoodOff=answers.neighborhood?.choice==='rest'&&(answers.neighborhood.probabilities?.rest||0)>.5;if(neighborhoodOff&&['celebration','hopeful'].includes(mood.choice))preset=ATMOSPHERES.together;const paperOff=")
p.write_text(s)
p=base/'src/quick-wishes.mjs';s=p.read_text().replace(' paper:{'," homecoming:{label:'留一盏灯，等晚归的人',decisions:{neighborhood:'homecoming',light:'warm'}},\n prepare:{label:'一起准备一个值得开心的晚上',decisions:{neighborhood:'prepare'}},\n reopen:{label:'雨停了，日子重新开始',decisions:{weather:'clear',neighborhood:'reopen'}},\n spring:{label:'让春天走进每个角落',decisions:{neighborhood:'spring',breeze:'gentle'}},\n paper:{");p.write_text(s)
p=base/'decision-api.mjs';s=p.read_text().replace('普通人不能任意进屋；不能以相似动作替代。','普通人不能任意进屋，但邮居门前留灯、开门、回家迎接已经通过neighborhood.homecoming实现；不能以相似动作替代。');s=s.replace(" questions.paper.instructions=", " questions.neighborhood.instructions='街坊协作是现有真实流程，不是新造无限能力。晚归、家门、留灯等人、有人迎接的诗意邀请选homecoming；值得开心的晚上、准备聚会、搬凳摆点心递灯选prepare（不自动放烟花）；雨后重新开始、重新开张、收伞擦椅摆回东西选reopen；春天走进街角、花展开、搬盆牵风筝扶帽选spring。只谈一般思念而不涉及回家选keep，由纸笺承担；仅风速改变选keep，由breeze承担。明确不要/停止这些协作选rest；过去赞美、假设、保持不变选keep。可以不点名角色。';\n questions['scope:neighborhood'].instructions='有归家迎接/准备庆祝/雨后重开/春风花开的直接或诗意愿望选yes；不要求命令句，情绪和意象有实质关联即可。单纯纸笺、既往评价、假设、否定保持则no，明确停止该流程则yes。';\n questions.paper.instructions=")
p.write_text(s)
print('Shared primitives, finite neighborhood choices and semantic contract added')
