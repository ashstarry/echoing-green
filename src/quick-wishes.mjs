// These are product controls with known intent, not model-evaluation samples.
// Free text still uses Jev; curated controls must work offline and deterministically.
export const QUICK_WISHES={
 homecoming:{label:'留一盏灯，等晚归的人',decisions:{neighborhood:'homecoming',light:'warm'}},
 prepare:{label:'一起准备一个值得开心的晚上',decisions:{neighborhood:'prepare'}},
 reopen:{label:'雨停了，日子重新开始',decisions:{weather:'clear',neighborhood:'reopen'}},
 spring:{label:'让春天走进每个角落',decisions:{neighborhood:'spring',breeze:'gentle'}},
 paper:{label:'把思念挂在树上，留一张随风的纸笺',decisions:{paper:'hang'}},
 snow:{label:'纸雪轻落，街坊换个地方看看',decisions:{weather:'snow'}},
 dawn:{label:'晨光渐亮，小镇开始新的一天',decisions:{day_phase:'dawn'}},
 night:{label:'纸灯沿街亮起，街坊提灯相聚',decisions:{day_phase:'night',light:'warm'}},
 market:{label:'晚市开张，居民逛摊、邻里招呼',decisions:{occasion:'market'}},
 festival:{label:'天色渐暗，大家找位置等花火',decisions:{day_phase:'night',festival:'fireworks'}}
};
export function quickWishItems(id){const q=QUICK_WISHES[id];if(!q)throw Error('没有这个快捷活动');return Object.entries(q.decisions).map(([target,action])=>({kind:'macro',target,action,label:q.label,target_label:'小镇'}));}
