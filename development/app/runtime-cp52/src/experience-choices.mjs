// Finite ways to perform a feeling. The model decides whether the performance
// is open; current availability and recent experience choose a suitable one.
export const EXPRESSION_QUESTION={type:'choice',instructions:'Does the speaker leave HOW the feeling is expressed open? Choose open for a personal feeling, atmosphere or evocative metaphor without specifying an activity. Choose small when they want a little/private moment or only a few neighbors. Choose town only when they explicitly want the whole town or most residents to participate. Choose fixed for a named activity, person, object, time/weather instruction, a pure negation/keep request without a positive feeling, a hypothetical, praise, or an impossible literal construction. Hunger with meals, wanting music, giving a paper note, and a fox greeting are specific activities even when poetic: fixed. Saying lonely, cared for, comforted or happy without an activity leaves the performance open. A positive open feeling with a restriction may still be open/small/town: do not let the negative clause erase the positive wish. A wish for a small comfort without bringing everyone over is small. This choice never creates new capabilities.',criteria:{fixed:'Keep the specified action and scope',open:'An open feeling; choose a suitable existing performance',small:'An open feeling expressed by a few relevant neighbors',town:'An open feeling explicitly involving most of the town'}};
export const EXPERIENCES={
 company_meet:{theme:'together',scene:'reunion',need:'gather',reach:'town',label:'街坊从不同的角落走近，找个地方陪彼此聊一会儿。',changes:{occasion:'reunion',light:'warm'}},
 company_walk:{theme:'together',scene:'company_walk',need:'company',reach:'small',label:'两位街坊相互招呼，结伴走过水边，再停下来聊一会儿。',changes:{craft:'company',light:'warm'}},
 company_tea:{theme:'together',scene:'tea_service',need:'tea',reach:'small',label:'有人走向热茶摊，接过一杯茶，和招待自己的街坊聊一会儿。',changes:{craft:'tea',light:'warm'}},
 comfort_tea:{theme:'tender',scene:'tea_service',need:'tea',reach:'small',label:'把这一刻交给一杯温热的茶，街坊慢慢走近、接过、喝下。',changes:{craft:'tea',light:'warm',breeze:'gentle'}},
 comfort_home:{theme:'tender',scene:'homecoming',need:'home',reach:'small',label:'晚归的街坊走向家门，暖窗亮起，窗边的人招呼他回来。',changes:{neighborhood:'homecoming',light:'warm'}},
 comfort_note:{theme:'tender',scene:'paper_share',need:'paper',reach:'small',label:'把温柔写成一张小纸笺，交到另一位街坊手里。',changes:{paper:'share',light:'warm'}},
 joy_prepare:{theme:'celebration',scene:'prepare',need:'prepare',reach:'small',label:'街坊分头搬来小凳、点心和纸灯，认真准备一个开心的晚上。',changes:{neighborhood:'prepare',music:'play',light:'warm',breeze:'lively'}},
 joy_music:{theme:'celebration',scene:'music',need:'music',reach:'small',label:'孩子们围到吉他手身边，小狐狸也循着琴声跑来听一段。',changes:{music:'play',street:'gather',light:'warm',breeze:'gentle'}},
 joy_snack:{theme:'celebration',scene:'tea_service',need:'tea',reach:'small',label:'摊主揭开热蒸笼，把一份点心递给走近的街坊，分享一点开心。',changes:{craft:'snack',light:'warm'}}
};
export const EXPERIENCE_THEMES=['together','tender','celebration'];
export function normalizeExperienceContext(value){
 if(value?.version!==1)return null;
 const available={};for(const k of ['gather','company','tea','home','paper','prepare','music'])if(typeof value.available?.[k]==='boolean')available[k]=value.available[k];
 const recent=Array.isArray(value.recent)?value.recent.slice(-8).filter(x=>typeof x==='string'&&Object.hasOwn(EXPERIENCES,x)):[];
 return{version:1,recent,available,lastScene:['tea_service','company_walk','paper_share','paper_hang','reunion','prepare','homecoming','music','spring'].includes(value.lastScene)?value.lastScene:null,hasCare:!!value.hasCare};
}
const signature=v=>JSON.stringify(v.changes);
export function chooseExperience(theme,context,scope='open',blocked=new Set(),phase='dusk'){
 const ctx=normalizeExperienceContext(context);if(!ctx||!EXPERIENCE_THEMES.includes(theme))return null;
 let candidates=Object.entries(EXPERIENCES).filter(([,v])=>v.theme===theme&&(scope!=='small'||v.reach==='small')&&ctx.available[v.need]!==false&&!Object.keys(v.changes).some(k=>blocked.has(k)));
 if(scope==='town')candidates=ctx.available.gather===false||blocked.has('occasion')?[]:[['company_meet',EXPERIENCES.company_meet]];
 const score=([id,v],index)=>{
  let n=1-index*.08;
  for(const [i,used]of ctx.recent.slice(-3).reverse().entries()){const previous=EXPERIENCES[used];if(id===used)n-=4/(i+1);else if(previous&&signature(previous)===signature(v))n-=3/(i+1);}
  if(ctx.lastScene===v.scene)n-=.8;
  if(theme==='tender'&&ctx.available.home===true&&id==='comfort_home')n+=phase==='night'?.4:.25;
  if(theme==='tender'&&ctx.hasCare&&id==='comfort_note')n+=1.2;
  return n;
 };
 return candidates.map((entry,i)=>({entry,score:score(entry,i)})).sort((a,b)=>b.score-a.score||a.entry[0].localeCompare(b.entry[0]))[0]?.entry||null;
}
export function varyMoodPlan(plan,answers,current={}){
 const expression=answers.mood_expression,theme=answers.atmosphere?.choice,family=expression?.choice==='small'&&['quiet','dream'].includes(theme)?'tender':theme;
 if(plan.status!=='change'||!plan.items.length||!['open','small','town'].includes(expression?.choice)||(expression.probabilities?.[expression.choice]||0)<.55||(!['mood','mixed'].includes(answers.mood_intent?.choice)&&!['small','town'].includes(expression?.choice))||!EXPERIENCE_THEMES.includes(family)||(plan.resolution?.scopeGuard&&expression?.choice!=='small')||plan.resolution?.source?.startsWith('explicit'))return plan;
 if(plan.items.some(i=>i.kind!=='macro'||['weather','festival','journey','cloud'].includes(i.target)&&!['quiet','keep','rest'].includes(i.action)))return plan;
 const requested=i=>answers['scope:'+(i.field||i.target)]?.choice!=='no';
 if(plan.items.some(i=>requested(i)&&(i.target==='paper'&&['hang','read','collect'].includes(i.action)||i.target==='occasion'&&['supper','market','delivery'].includes(i.action)||i.target==='neighborhood'&&['spring','reopen'].includes(i.action)||i.target==='craft'&&!['tea','snack','company','rest','keep'].includes(i.action))))return plan;
 // A supported concrete paper, home or food request remains authoritative.
 const blocked=new Set();for(const k of ['music','paper','craft','neighborhood','occasion'])if(['rest','quiet','ordinary'].includes(answers[k]?.choice)&&answers['scope:'+k]?.choice==='yes')blocked.add(k);
 const selected=chooseExperience(family,current.experience_context,expression.choice,blocked,current.day_phase);if(!selected)return plan;
 const [id,v]=selected,experience={theme:family,variant:id};
 const retained=plan.items.filter(i=>i.kind==='macro'&&['weather','festival','day_phase','train','light','breeze','music'].includes(i.target)&&(answers['scope:'+i.target]?.choice==='yes'||['quiet','rest'].includes(i.action)));
 const occupied=new Set(retained.map(i=>i.target));
 const items=[...retained,...Object.entries(v.changes).filter(([k])=>!occupied.has(k)).map(([target,action])=>({kind:'macro',target,action,field:target,label:v.label,target_label:'氛围',experience}))];
 if(!items.some(i=>i.experience))return plan;
 return {...plan,items,summary:v.label,resolution:{...plan.resolution,source:'jev-contextual-mood',choice:theme,variant:id,expression:expression.choice,selection:'available-performances-with-recent-history'}};
}
