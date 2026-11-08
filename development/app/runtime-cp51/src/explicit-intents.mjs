// A narrow literal contract for weather and its ordinary collective reaction.
// Conditions, quotes, questions, named-person actions and unrelated requests stay with Jev.
export function explicitWeather(text){
 const t=String(text).normalize('NFKC').trim().replace(/[。.!！,，、\s]+$/u,'');
 const patterns={
  rain:/^(?:(?:请|让)?(?:小镇|这里|这儿|全镇))?(?:开始)?(?:下(?:一场|点|一点|场)?雨(?:了|吧|啦)?|雨来了|来(?:一场|点|一点)雨)(?:吧)?$/u,
  snow:/^(?:(?:请|让)?(?:小镇|这里|这儿|全镇))?(?:开始)?(?:下(?:一场|点|一点|场)?(?:纸片|纸)?雪(?:了|吧|啦)?|雪来了)(?:吧)?$/u,
  clear:/^(?:(?:请|让)?(?:小镇|这里|这儿|全镇))?(?:雨停了|雪停了|雨雪停了|停雨|停雪|停雨停雪|停止下雨|停止下雪|别下雨了|别下雪了|不要下雨了|不要下雪了|让雨停(?:下来)?|让雪停(?:下来)?)(?:吧)?$/u
 };
 const english={rain:/^(?:it(?:'s| is) raining|rain(?: is here)?|let it rain)$/i,snow:/^(?:it(?:'s| is) snowing|let it snow)$/i,clear:/^(?:(?:the )?(?:rain|snow)(?: has| is)? (?:stopped|stopping)|stop (?:the )?(?:rain|snow))$/i};
 const literal=value=>Object.keys(patterns).find(action=>patterns[action].test(value)||english[action].test(value));
 const direct=literal(t);if(direct)return{action:direct,rule:'explicit-weather-v1'};
 const clauses=t.split(/[，,；;]/u).map(x=>x.trim());if(clauses.length!==2)return null;
 const action=literal(clauses[0]);if(!action)return null;
 const reaction=/^(?:(?:让)?(?:大家|大伙儿|街坊们?|居民们?|人们))?(?:(?:赶快|赶紧|一起|都|可以|快|先|继续)){0,2}(?:(?:去|找地方|找个地方|找屋檐|到屋檐下)?(?:避雨|躲雨)|(?:撑起|打起|撑|打)伞|(?:出来|出去|出门)?(?:走走|散步|逛逛|活动一下|逛街|看雪|接雪花)|出来|出门|出去)(?:吧|啦|了)?$/u;
 const englishReaction=/^(?:(?:let's|let us|everyone|the residents|the neighbors)\s+)?(?:(?:can|should)\s+)?(?:(?:go|head|come)(?:\s+back)?\s+outside(?:\s+for\s+a\s+walk)?|take\s+shelter|find\s+shelter|open\s+(?:our|their)\s+umbrellas|go\s+for\s+a\s+walk)$/i;
 if(reaction.test(clauses[1])||englishReaction.test(clauses[1]))return{action,rule:'explicit-weather-reaction-v2'};
 return null;
}
