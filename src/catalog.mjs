// Executable choices only. Authoring wishes remain in runtime-registry.json.
export const DOMAINS={
 weather:{label:'天气',choices:{keep:'保持当前天气',clear:'雨雪慢慢停下，云仍留在水边',rain:'小镇落下纸雨，街上居民回门前或檐下避雨，店家整理东西，二楼客人回帘后',snow:'小镇飘起疏朗的纸片雪花'}},
 breeze:{label:'晚风',choices:{keep:'保持风速',calm:'比当前柔风更弱；风慢一点、再轻一些、风小一些都选此项，风车和风铃轻轻摆动',gentle:'恢复柔和晚风',lively:'更有精神的风，风车加速但不狂乱'}},
 light:{label:'灯火',choices:{keep:'保持灯光',warm:'灯火更橘暖，街道仍然看得清',soft:'灯火柔和收敛，保留安全可见度',bright:'灯火稍亮，仍保留橘色与明暗层次'}},
 music:{label:'琴声',choices:{keep:'保持乐手状态',play:'树下的乐手轻轻弹琴，听众点头',rest:'乐手停下拨弦，安静歇一会儿'}},
 street:{label:'街道',choices:{keep:'保持居民当前目标',wander:'可行走居民各自散步，不同时冲向同一点',gather:'可行走居民靠近树下空闲位置听琴，不挤在一起',quiet:'居民走完当前安全路段后停下看风景'}},
 birds:{label:'纸鸟',choices:{keep:'保持鸟群状态',fly:'纸鸟在各自清晰的空中范围飞行',rest:'只适用于停留空中或悬停的明确要求；绝不用于归巢/回窝/落地/栖息（这些未实现，应选 keep）'}},
 festival:{label:'夜空',choices:{keep:'保持夜空状态',fireworks:'居民先寻找空位，再举行红金花火；下雨时延期，结束后停留交谈并散开',auto:'恢复小镇偶尔自动举行的花火大会',quiet:'停止新增花火，让已有花火自然散去'}}
};
Object.assign(DOMAINS,{
 occasion:{label:'小镇的集体活动',choices:{keep:'保持当前事件安排；下雨下雪和烟火属于其它领域，不必重复改变本项',ordinary:'恢复各自的日常，居民按兴趣交替散步聊天看花',market:'让晚市热闹起来：有人逛摊买东西，店家招呼客人',supper:'到了晚餐时间，街上的食客走向柜台，二楼客人用餐',reunion:'让邻里找空位相聚聊天，保留通路',delivery:'邮差和送信人沿街查看门牌，其他人继续日常',quiet:'安静的晚风，更多人停下看水、看花、休息'}} ,
 train:{label:'环镇电车',choices:{keep:'保持电车运行安排',auto:'电车自动绕镇，进站减速、停靠后再次出发',hold:'电车到达车站后多停留，已在行驶时先安全进站，不在轨道中间突然停止'}},
 dining:{label:'二楼两位客人',choices:{keep:'保持二楼客人当前安排',auto:'客人轮流用餐、起身进入门帘，再出来坐回座位',inside:'二楼客人完成当前安全动作后走进门帘休息',dine:'二楼客人从门帘回来，坐在自己的座位用餐'}},
 pond:{label:'池塘里的鸭子和鱼',choices:{keep:'保持水中动物的状态',swim:'鸭子和鱼沿池塘内各自的路线缓缓游动',rest:'鸭子和鱼放慢并停留在当前位置，不跳到别处'}},
 animals:{label:'小猫和小狐狸',choices:{keep:'保持小猫小狐狸的当前状态',wander:'小猫和小狐狸在各自安全区域走动、嗅闻',rest:'小猫和小狐狸慢慢停下休息'}},
 cycling:{label:'骑车的居民',choices:{keep:'保持骑车人的状态',ride:'骑车人沿街道慢行，遇到行人会停下来让路',rest:'骑车人走完当前路段，到下一处停留点落脚歇息；转弯中不急停'}}
});
DOMAINS.day_phase={label:'日夜',choices:{keep:'保留当前时段',dawn:'晨曦渐亮',day:'明亮白昼',dusk:'温暖黄昏',night:'灯火夜晚，街巷仍清楚'}};
DOMAINS.paper={label:'纸笺',choices:{keep:'保持纸笺的安排',hang:'写下思念或祝愿，折好纸笺，挂到树边留下',share:'写一张感谢或心意，折好后亲手递给邻居',read:'走到树边，读一读最近留下的纸笺',collect:'走到树边，取下一张纸笺，读过后折好收起',rest:'停止新的纸笺活动，收好手里的纸，保留已经挂好的纸笺'}};
export const KEEP={};
export function validateDecision(input){if(!input||typeof input!=='object'||Array.isArray(input))throw Error('决策格式无效');for(const [k,v]of Object.entries(input))if(!Object.hasOwn(DOMAINS,k)||typeof v!=='string'||!Object.hasOwn(DOMAINS[k].choices,v))throw Error('决策包含未开放的动作');return {...KEEP,...input};}
export const labels={'resident.customer_two':'二号餐厅客人','resident.customer_three':'三号餐厅客人','resident.postman':'邮局的邮差','resident.child_runner':'小跑的孩子','resident.market_browser':'逛集市的居民','resident.customer_one':'餐厅门前的客人','resident.courier':'巷口的送信人','resident.garden_child':'花园里的孩子','resident.strolling_parent':'散步的家长'};
export const ACTOR_DOMAINS={child:'resident.child_runner',courier:'resident.courier',shopper:'resident.customer_one',browser:'resident.market_browser',parent:'resident.strolling_parent',customer2:'resident.customer_two',customer3:'resident.customer_three',postman:'resident.postman'};
const actorTitles={customer2:'餐厅中间穿灰衣的客人',customer3:'餐厅右边穿黄色衣服的客人',postman:'邮局门前拿着信的邮差',child:'广场前方穿红衣的小孩',courier:'餐厅左边巷口的送信人',shopper:'餐厅门前穿红衣的成年客人',browser:'花园旁穿蓝灰衣的逛集市居民',parent:'邮局右侧散步的家长'};
for(const [key,id]of Object.entries(ACTOR_DOMAINS))DOMAINS[key]={label:actorTitles[key],entity:id,choices:{keep:'没有针对这个人的独立要求，保持他的当前目标；指全体居民时交给街道问题',wander:'这个人沿当前允许的街道散步',gather:'这个人走向树下附近当前可用的空位，停留听琴',quiet:'这个人走完当前短路段后停下来，其他人不受影响'}};
export const CHOICE_LABELS={weather:{clear:'雨雪停一会儿',rain:'小镇细雨',snow:'轻轻下雪'},breeze:{calm:'风轻一点',gentle:'柔和晚风',lively:'风车轻快些'},light:{warm:'暖橘灯火',soft:'柔和一些',bright:'明亮一些'},music:{play:'轻轻弹琴',rest:'歇一会儿'},street:{wander:'各自散步',gather:'去树下听琴',quiet:'停下看风景'},birds:{fly:'缓缓飞行',rest:'空中悬停'},festival:{fireworks:'开一场花火',auto:'偶尔自动举行',quiet:'夜空安静下来'}};

Object.assign(CHOICE_LABELS,{occasion:{ordinary:'各自的日常',market:'逛逛晚市',supper:'晚餐时间',reunion:'邻里聊一会',delivery:'送信时光',quiet:'安静看看风景'},train:{auto:'继续环镇行驶',hold:'到站多停一会'},dining:{auto:'自在用餐休息',inside:'进门帘休息',dine:'出来用餐'},pond:{swim:'自在游动',rest:'停下来歇息'},animals:{wander:'走走闻闻',rest:'休息一会'},cycling:{ride:'沿街骑行',rest:'暂时停一停'}});
Object.assign(KEEP,Object.fromEntries(Object.keys(DOMAINS).map(k=>[k,'keep'])));

CHOICE_LABELS.paper={hang:'挂一张纸笺',share:'递一张心意',read:'读一读纸笺',collect:'收起一张纸笺',rest:'先收好纸笔'};
