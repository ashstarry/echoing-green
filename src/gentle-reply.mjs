import {eventKind} from './scene-events.mjs?v=cp52-living-variations-0f9817dcf3a8';
import {keepsOtherActivity} from './atmosphere.mjs?v=cp52-living-variations-0f9817dcf3a8';
// A bounded interpretation or a visible greeting, never an invented capability.
export const REPLY_QUESTION={type:'choice',instructions:'Choose the closest honest response when the main action selection cannot express the user. Present feelings and sensory fragments should produce a coherent small town action. Use preserve for explicit keep-everything-unchanged, explicit no-action, quoted or hypothetical events without a wish to enact them. Never enact a negated effect. Use greeting for greetings, interface praise, incoherent text, questions without a change request, or impossible literal construction/travel/boat sailing. Do not pretend to perform impossible requests. Use a concrete interpretation for a meaningful atmosphere, not greeting by default. Use share for appreciation, thanks or kindness deliberately passed to another person, including hand-to-hand metaphors without a named physical gift. Use paper for a wish or memory kept by the tree, especially longing for someone far away. These are different existing actions.',criteria:{preserve:'No physical change was wanted',greeting:'A nearby neighbor briefly waves hello',music:'Children listen beside the guitarist and the fox joins them',tea:'Warm hands with hot tea',paper:'Leave a paper wish or memory in the tree',share:'Write a small note of appreciation and hand it to one neighbor',spring:'Bring flowers and a fresh beginning',quiet:'Slow down in a quiet corner',reunion:'Warm human companionship',night:'Take real paper lamps from their stands into the evening',rain:'A passing rain with shelter and umbrellas',snow:'Paper snow and residents reacting',market:'Stall queues and warm food',celebrate:'Prepare a happy evening together',fox:'A little fox greeting',pond:'A neighbor feeds fish'}};
const macro=(target,action)=>({kind:'macro',target,action});
export const GENTLE_REPLIES={
 greeting:{label:'街坊听见了，向你挥挥手。',items:[{kind:'resident',target:'resident.vendor_flower',action:'greet'}]},
 music:{label:'把这份心情化成孩子们围坐听琴的小片刻。',items:[macro('music','play'),macro('street','gather')]},
 tea:{label:'把这份心情化成一杯递到手里的热茶。',items:[macro('craft','tea')]},
 paper:{label:'把这份心意写成纸笺，留在树边。',items:[macro('paper','hang')]},
 share:{label:'写下一点谢意，亲手交给一位街坊。',items:[macro('paper','share')]},
 spring:{label:'让几盆花和一阵春风回应这句话。',items:[macro('neighborhood','spring'),macro('breeze','gentle')]},
 quiet:{label:'给这份心情留一处安静的角落。',items:[macro('occasion','quiet')]},
 reunion:{label:'让街坊走近彼此，陪这一刻待一会。',items:[macro('occasion','reunion')]},
 night:{label:'让街坊拿起纸灯，把暖光带到街边。',items:[macro('day_phase','night'),macro('light','warm')]},
 rain:{label:'用一阵雨和街坊的雨伞回应这句话。',items:[macro('weather','rain')]},
 snow:{label:'让纸片雪和街坊的抬头回应这句话。',items:[macro('weather','snow')]},
 market:{label:'让摊前的热食和等候的街坊回应这句话。',items:[macro('occasion','market')]},
 celebrate:{label:'街坊搬来点心和小凳，准备一个开心的晚上。',items:[macro('neighborhood','prepare')]},
 fox:{label:'小狐狸摇摇尾巴，和附近的街坊打招呼。',items:[{kind:'object',target:'animal.garden_fox',action:'greet'}]},
 pond:{label:'让一位街坊走近水边，喂喂池塘的鱼。',items:[{kind:'resident',target:'resident.water_visitor',action:'feed_pond'}]}
};
function replyPlan(plan,answers,text){
 if(!plan.items.length&&/(?:什么都不要(?:改变|做)|(?:不要|别)(?:改变|改动)任何(?:东西|事情)|保持(?:现状|原样|现在这样)|do not change anything|don't change anything|change nothing|keep everything unchanged)/i.test(text))return {...plan,status:'no_change',summary:'小镇会保持现在的安排，继续自己的生活。'};

 const namedFox=/(?:狐狸|小狐|小狗|橘色.{0,5}(?:家伙|动物)|fox|little dog|orange little (?:one|creature))/i.test(text);
 const inferred=plan.resolution?.source==='jev-atmosphere';
 if(namedFox&&keepsOtherActivity(text)&&/(?:别|不要).{0,4}打扰|(?:do not|don't).{0,6}disturb/i.test(text))return {...plan,status:'no_change',items:[],summary:'不打扰小狐狸，街坊继续各自的生活。',resolution:{source:'local-preserve'}};
 if(namedFox&&inferred&&['together','tender'].includes(answers.atmosphere?.choice)&&!/(?:全镇|所有人|大家一起|whole town|everyone together)/i.test(text))return {...plan,status:'change',items:GENTLE_REPLIES.fox.items.map(i=>({...i,label:GENTLE_REPLIES.fox.label,target_label:'小狐狸'})),summary:GENTLE_REPLIES.fox.label,resolution:{source:'named-local-feeling',...(keepsOtherActivity(text)?{scopeGuard:'explicit-others-unchanged'}:{})}};
 const weather=plan.items.find(i=>i.target==='weather'&&['rain','snow'].includes(i.action));
 if(weather){const secondary=plan.items.filter(i=>i.kind==='macro'&&['occasion','festival','paper','neighborhood','craft'].includes(i.target)&&!['ordinary','quiet','rest','keep'].includes(i.action));if(secondary.length){plan={...plan,items:plan.items.filter(i=>!secondary.includes(i)),skipped:[...plan.skipped,...secondary.map(i=>({...i,reason:'先回应天气，让居民安顿好；这次不同时展开另一场活动。'}))],summary:weather.action==='rain'?'先落一阵雨，让街坊撑伞或避雨；这次不同时开另一场活动。':'先让纸雪落下、街坊安顿好；这次不同时开另一场活动。',resolution:{...plan.resolution,foreground:'weather-first'}};}}
 if(plan.items.some(i=>i.target==='street'&&i.action==='gather')&&!keepsOtherActivity(text))plan={...plan,items:plan.items.filter(i=>!(i.kind==='resident'&&i.action==='listen_music'&&['resident.child_runner','resident.garden_child'].includes(i.target)))};
 if(plan.items.some(i=>i.target==='music'&&i.action==='play')&&answers.gentle_reply?.choice==='music'&&!keepsOtherActivity(text)&&!plan.items.some(i=>i.kind==='macro'&&['street','occasion','weather','festival','neighborhood','craft'].includes(i.target)))return {...plan,items:[...plan.items,macro('street','gather')]};
 if(!plan.items.length){const missing=plan.skipped?.find(i=>/还没有纸笺|纪念角暂时还是空的/.test(i.reason));if(missing)return {...plan,status:'change',items:GENTLE_REPLIES.greeting.items.map(i=>({...i,label:GENTLE_REPLIES.greeting.label,target_label:'回应'})),summary:plan.summary+GENTLE_REPLIES.greeting.label,resolution:{source:'missing-object-acknowledgement'}};}
 if(plan.items.length)return plan;
 const rawChoice=answers.gentle_reply?.choice;
 // A failed concrete request is acknowledged without inventing an unrelated event.
 // Meaningful emotional wishes can still use the model's mood interpretation.
 const unsupportedLiteral=plan.status==='unsupported'&&answers.mood_intent?.choice==='literal';
 const selected=unsupportedLiteral?'greeting':rawChoice==='preserve'&&plan.status==='unsupported'&&!/(?:别|不要|保持|不改|if|what if|don't|do not|leave|keep|hypothetical)/i.test(text)?'greeting':rawChoice;
 if(!selected||selected==='preserve'||/(?:什么|任何东西|所有东西|整个小镇).{0,4}(?:都)?(?:别|不要)(?:动|改)|保持(?:一切|所有|全部|现状|原样).{0,3}不变|什么都不要做|do not change anything|don't change anything|change nothing|leave everything (?:alone|unchanged)|keep everything (?:as it is|unchanged)/i.test(text))return plan;
 const withdrawnBoat=/(?:船|舟|boat).*(?:自行|自己|开动|航|开到|离岸|sail|travel|cruise)|(?:sail|row|cruise).*(?:boat)/i.test(text);const fallback=withdrawnBoat?GENTLE_REPLIES.greeting:GENTLE_REPLIES[selected]||GENTLE_REPLIES.greeting;
 const prefix=withdrawnBoat?'小舟系在岸边，没有船夫，不会自行航行。':['unsupported','partial'].includes(plan.status)?'这件事小镇暂时做不到。':'';
 return {...plan,status:'change',items:fallback.items.map(i=>({...i,label:fallback.label,target_label:'回应'})),summary:prefix+fallback.label,resolution:{...plan.resolution,source:'jev-gentle-reply',choice:selected,original_status:plan.status}};
}

function episodeOf(i){if(i.kind!=='macro')return null;if(i.target==='journey'&&i.action!=='rest')return 'journey';if(i.target==='cloud'&&i.action!=='rest')return 'cloud';if(['weather','festival','craft','neighborhood','paper','occasion'].includes(i.target))return eventKind({[i.target]:i.action});if(i.target==='street'&&i.action==='gather')return 'music';return null;}
export function withGentleReply(plan,answers,text){
 let p=replyPlan(plan,answers,text);
 const feed=/(?:喂.{0,6}鱼|\bfeed\b.{0,30}\b(?:fish|pond))/i.test(text)&&!/(?:不要|别).{0,4}喂|(?:don't|do not).{0,8}feed/i.test(text);
 if(p.status==='change'&&feed&&!keepsOtherActivity(text)&&!p.items.some(i=>i.target==='resident.water_visitor'&&i.action==='feed_pond')){p={...p,items:[...p.items,{kind:'resident',target:'resident.water_visitor',action:'feed_pond',label:GENTLE_REPLIES.pond.label,target_label:'回应'}],summary:GENTLE_REPLIES.pond.label,resolution:{...p.resolution,feeding:'person-and-fish'}};}
 const macros=Object.fromEntries(p.items.filter(i=>i.kind==='macro').map(i=>[i.target,i.action]));
 let primary=macros.journey&&macros.journey!=='rest'?'journey':eventKind(macros)|| (macros.cloud&&macros.cloud!=='rest'?'cloud':null);
 if(primary!=='rain'&&primary!=='snow'&&primary!=='festival'&&macros.neighborhood==='prepare'&&/(?:大家|街坊|一起|everyone|together).{0,12}(?:准备|筹备|prepare)|prepare.{0,35}(?:together|everyone)/i.test(text))primary='prepare';
 const removed=primary?p.items.filter(i=>episodeOf(i)&&episodeOf(i)!==primary):[];
 if(removed.length){const items=p.items.filter(i=>!removed.includes(i));p={...p,items,skipped:[...p.skipped,...removed.map(i=>({...i,reason:'用这一场具体活动表达心愿，不同时启动另一场活动。'}))],summary:[...new Set(items.map(i=>i.label).filter(Boolean))].slice(0,3).join('；'),resolution:{...p.resolution,primaryScene:primary}};}
 if(p.items.length&&keepsOtherActivity(text))p={...p,resolution:{...p.resolution,scopeGuard:'explicit-others-unchanged'}};
 return p;
}
