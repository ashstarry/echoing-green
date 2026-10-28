// Only complete, unambiguous scene requests. Not substring or poetry matching.
export function explicitScene(text){
 const value=String(text??'').trim().replace(/[。！!\.]+$/u,'').trim();
 if(/^(?:请)?(?:(?:来|办|开)(?:一场|一个|个)?|举办(?:一场)?|开启|开始)?(?:夜间集市|夜市|晚市|夜间市场)(?:吧|了)?$/u.test(value)||/^(?:逛逛|逛一逛)(?:晚市|夜市)$/u.test(value)||/^(?:please\s+)?(?:(?:open|start|hold|begin)\s+(?:(?:an?|the)\s+)?)?(?:night market|evening market)(?:,?\s+please)?$/i.test(value))return {rule:'explicit-scene-v1',kind:'market',changes:{day_phase:'night',occasion:'market'}};
 if(/^(?:请)?(?:放(?:一场|点)?|来(?:一场|个)?|办(?:一场|个)?|举办(?:一场)?|开启|开始)?(?:烟花|花火(?:大会)?)(?:吧|了)?$/u.test(value)||/^(?:please\s+)?(?:set off|launch|show|start|light)\s+(?:(?:some|the|a)\s+)?fireworks(?:\s+show)?(?:,?\s+please)?$/i.test(value))return {rule:'explicit-scene-v1',kind:'festival',changes:{day_phase:'night',festival:'fireworks'}};
 return null;
}
