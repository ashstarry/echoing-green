// Narrow, whole-utterance reliability contract. Never infer rain from a substring:
// conditions, quotes, negation, song names and multi-clause requests stay with Jev.
export function explicitWeather(text){
 const t=String(text).normalize('NFKC').trim().replace(/[。.!！,，、\s]+$/u,'');
 const patterns={
  rain:/^(?:(?:请|让)?(?:小镇|这里|这儿|全镇))?(?:开始)?(?:下(?:一场|点|一点|场)?雨(?:了|吧|啦)?|雨来了|来(?:一场|点|一点)雨)(?:吧)?$/u,
  snow:/^(?:(?:请|让)?(?:小镇|这里|这儿|全镇))?(?:开始)?(?:下(?:一场|点|一点|场)?(?:纸片|纸)?雪(?:了|吧|啦)?|雪来了)(?:吧)?$/u,
  clear:/^(?:(?:请|让)?(?:小镇|这里|这儿|全镇))?(?:雨停了|雪停了|雨雪停了|停雨|停雪|停雨停雪|停止下雨|停止下雪|别下雨了|别下雪了|不要下雨了|不要下雪了|让雨停(?:下来)?|让雪停(?:下来)?)(?:吧)?$/u
 };
 for(const[action,pattern]of Object.entries(patterns))if(pattern.test(t))return{action,rule:'explicit-weather-v1'};
 return null;
}
