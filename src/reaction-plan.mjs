import {ACTOR_DOMAINS} from './catalog.mjs?v=cp37-paper-c8fccf30daca';
import {PROFILES} from './community.mjs?v=cp37-paper-c8fccf30daca';
const role=id=>PROFILES[id]?.label||'这位居民';
const moving=a=>a&&['walk','yield','fold_umbrella'].includes(a.mode);
const reached=a=>a&&a.reservation!==null&&!moving(a)&&a.path.length===0;
const primaryOrder=['day_phase','weather','festival','train','dining','music','occasion','street','cycling','pond','animals','breeze','light','birds'];
const targets={day_phase:['moon.paper_crescent'],weather:['weather.cp02_paper_cloud'],festival:['tree.lantern_tree'],train:['tram.tram_car_front','door.station_entry_door'],dining:['curtain.restaurant_upper_noren'],music:['resident.musician'],occasion:['resident.customer_one','resident.gardener'],street:['resident.child_runner','resident.postman','resident.market_browser'],cycling:['bicycle.street_bicycle'],pond:['fish.pond_fish_0','animal.duck_0'],animals:['animal.garden_fox','animal.doorstep_cat'],breeze:['windmill.hill_windwheel','ornament.restaurant_wind_chime'],light:['tree.lantern_tree','light.hanging_light_cp04_tea_side_lantern_washi'],birds:['bird.paper_bird_0','bird.paper_bird_1']};
const titles={day_phase:{dawn:'晨曦落在小镇',day:'纸雕小镇迎来白天',dusk:'回到温暖黄昏',night:'夜色与灯火'},weather:{rain:'雨落进小镇',clear:'让雨雪歇一会儿',snow:'纸片雪来了'},festival:{fireworks:'准备一场花火',quiet:'让夜空安静下来',auto:'恢复偶尔的花火'},train:{hold:'电车到站多等一会儿',auto:'电车继续环镇行驶'},dining:{inside:'楼上客人回茶间',dine:'楼上客人出来用餐',auto:'客人自在用餐与休息'},music:{play:'树下再响起琴声',rest:'让乐手歇一会儿'},street:{wander:'大家沿街走走',gather:'有人去树下听琴',quiet:'街上的脚步慢下来'},cycling:{ride:'骑车人继续下一程',rest:'骑车人找地方歇脚'},pond:{swim:'池塘里继续游动',rest:'鸭子和鱼歇一会儿'},animals:{wander:'小动物走走闻闻',rest:'小动物歇一会儿'},breeze:{calm:'风再轻一点',gentle:'柔和的晚风回来',lively:'风车转得轻快些'},light:{warm:'灯火更橘暖',soft:'灯火柔和下来',bright:'灯火明亮一些'},birds:{fly:'纸鸟继续飞行',rest:'纸鸟停留在空中'},occasion:{ordinary:'回到各自的日常',market:'晚市热闹起来',supper:'闻着饭香去用餐',reunion:'邻里聊聊今天',delivery:'沿街看看门牌',quiet:'安静看看风景'}};
function previous(s,k){if(ACTOR_DOMAINS[k])return s.actors.find(a=>a.id===ACTOR_DOMAINS[k])?.intent;if(k==='train')return s.trainPolicy;if(k==='festival')return s.worldEvent.kind==='festival'?'fireworks':s.festivalAuto?'auto':'quiet';return s[k];}
export function makeReaction(before,after,decision,{trial=null,source='words'}={}){
 const requested=Object.entries(decision||{}).filter(([,v])=>v!=='keep');
 let changed=requested.filter(([k,v])=>previous(before,k)!==v||k==='music'&&before.effectiveMusic!==v||ACTOR_DOMAINS[k]&&!before.actors.find(a=>a.id===ACTOR_DOMAINS[k])?.manual);
 changed.sort((a,b)=>(primaryOrder.indexOf(a[0])<0?99:primaryOrder.indexOf(a[0]))-(primaryOrder.indexOf(b[0])<0?99:primaryOrder.indexOf(b[0])));
 const items=changed.slice(0,3).map(([key,value])=>({key,value,id:ACTOR_DOMAINS[key]||null,title:ACTOR_DOMAINS[key]?role(ACTOR_DOMAINS[key])+(value==='quiet'?'停一会儿':value==='gather'?'去树下听琴':'沿街走走'):titles[key]?.[value]||'小镇换一种安排'}));
 if(trial){items.splice(0,items.length,{key:'trial',value:trial.id,title:trial.label,trial});}
 const trialTargets={children_play:['resident.garden_child','resident.child_runner'],kite_walk:['resident.kite_child','resident.child_parent'],garden_work:['resident.gardener','resident.assistant_gardener'],pond_watch:['resident.water_visitor'],market_visit:['resident.customer_one','resident.vendor_bread'],cycle_trip:['bicycle.street_bicycle'],diner_inside:targets.dining,diner_return:targets.dining,rain:targets.weather,clear:targets.weather,festival:targets.festival};
 const ids=[...new Set(items.flatMap(x=>x.key==='trial'?trialTargets[x.value]||[]:x.id?[x.id]:targets[x.key]||[]))].slice(0,3);
 return {items,ids,source,started:after.time,before,requested,kind:items.length?'change':requested.length?'already':'unavailable',title:items[0]?.title||(requested.length?'已经是这个安排':'这句话暂时没有改变小镇'),summary:items.map(i=>i.title).slice(0,2).join('，')};
}
const done=text=>({phase:'done',text});const active=text=>({phase:'active',text});const waiting=text=>({phase:'waiting',text});
function personStatus(s,p,id,value){const a=s.actors.find(a=>a.id===id),old=p.before.actors.find(a=>a.id===id);if(!a)return waiting('这里还没有对应的行走动作。');if(value==='quiet')return !moving(a)?done(role(id)+'已经停下来。'):active(role(id)+'走完眼前这段路就会停下。');if(a.mode==='yield')return waiting(role(id)+'正在让路，空出来后继续。');if(a.mode==='fold_umbrella')return active(role(id)+'先收好伞，再继续走。');if(value==='gather'&&reached(a)&&a.task==='listen')return done(role(id)+'已经到了树下。');if(a.mode==='walk'&&a.walked-(old?.walked||0)>.12)return value==='wander'?done(role(id)+'已经沿街走起来。'):active(role(id)+'正在往树下走。');return waiting(role(id)+'正在找一个能走过去的位置。');}
function itemStatus(x,p,s,v){const elapsed=s.time-p.started;
 if(x.id)return personStatus(s,p,x.id,x.value);
 if(x.key==='day_phase')return (s.dayWeights?.[x.value]||0)>.95?done('光影已经换到这个时段。'):active('天空与光影正在柔和过渡。');
 if(x.key==='weather'){
  if(s.weather!==x.value)return waiting('天气又有了新的安排。');
  if(x.value==='clear'){if((v.rain??1)>.04||(v.snow??1)>.04)return active('雨雪正在收住。');const n=Object.values(s.residents).filter(r=>r.umbrellaOpen>.08).length;return done(n?'雨雪停了，还有人正在收伞。':'雨雪停了，街巷慢慢恢复日常。');}
  if(x.value==='rain')return(v.rain??0)>.85?done('雨已落下，居民开始各自找地方避雨。'):active('雨丝正在落进小镇。');
  return(v.snow??0)>.85?done('雪花落下来了。'):active('纸片雪正在慢慢出现。');
 }
 if(x.key==='train'){if(x.value==='hold')return s.train.mode==='dwell'?done('电车已经停在站边等候。'):waiting('电车还在途中，会到车站再多停一会儿。');return s.train.speed>.15?done('电车已经继续前行。'):active(s.train.mode==='dwell'?'电车正在站边稍作停留，随后继续前行。':'电车正在慢慢起步。');}
 if(x.key==='dining'){const ds=Object.values(s.diners),goal=x.value==='inside'?'inside':'dine';if(x.value==='auto')return done('用餐与休息的节奏已经恢复。');if(ds.every(d=>d.phase===goal))return done(goal==='inside'?'两位客人已经回到帘后的茶间。':'两位客人已经回来用餐。');if(ds.some(d=>['exit','enter','turn'].includes(d.phase)))return active(goal==='inside'?'客人正在起身、穿过门帘。':'客人正在走出门帘、回到座位。');return waiting(goal==='inside'?'客人准备起身，会先把动作做完。':'客人正准备从茶间出来。');}
 if(x.key==='festival'){if(x.value==='quiet')return(v.fireworksActive??s.festivalUntil>s.time)?active('不再升起新的花火，已有的光正在散去。'):done('夜空已经安静下来。');if(x.value==='auto')return done('小镇恢复了偶尔举行花火的安排。');const e=s.worldEvent;if(e.phase==='postponed')return waiting('雨还在下，花火会等雨停再准备。');if(e.phase==='prepare')return active('花火在准备，居民正找看得清的位置。');if(e.phase==='show')return done('花火已经升空，街坊正在一起看。');if(e.phase==='linger')return done('这一场花火已经结束，大家还在回味。');return waiting('花火的安排正在准备。');}
 if(x.key==='music')return s.effectiveMusic===x.value?done(x.value==='play'?'树下的乐手已经开始拨弦。':'乐手已经停下来歇息。'):active('乐手正在调整手上的动作。');
 if(x.key==='breeze'){const target={calm:.08,gentle:.35,lively:.8}[x.value];return Math.abs(s.windSpeed-target)<.025?done(x.value==='calm'?'风车和风铃已经放慢。':x.value==='lively'?'风车和风铃轻快起来了。':'晚风已经柔和下来。'):active('风车和风铃正在跟着晚风变化。');}
 if(x.key==='light'){const goal={warm:1,soft:.78,bright:1.18}[x.value];return Math.abs((v.light??0)-goal)<.03?done('灯火已经换成了你的安排。'):active('灯火正轻轻过渡。');}
 if(x.key==='cycling'){const m=s.movers['bicycle.street_bicycle'];if(x.value==='rest')return m.tripState==='parked'&&m.footDown>.9?done('骑车人已经落脚歇息。'):waiting('骑车人会走完当前路段，再落脚停下。');if(s.weather==='rain')return waiting('骑车人先等雨小些，再继续下一程。');if(s.worldEvent.kind==='festival')return waiting('骑车人正在看花火，结束后会继续。');if(m.blocked)return waiting('骑车人正在让行人先走。');return m.speed>.2?done('骑车人已经继续下一程。'):active('骑车人正在收脚、准备出发。');}
 if(['pond','animals','birds'].includes(x.key)){const ids=x.key==='pond'?Object.keys(s.movers).filter(i=>i.startsWith('fish.')||i.startsWith('animal.duck_')):x.key==='animals'?['animal.garden_fox','animal.doorstep_cat']:Object.keys(s.movers).filter(i=>i.startsWith('bird.'));const ms=ids.map(i=>s.movers[i]);if(x.value==='rest')return ms.every(m=>m.speed<.04)?done(x.key==='birds'?'纸鸟已停留在空中。':'它们已经慢慢停下来。'):active('它们正慢慢放轻动作。');if(ms.some(m=>m.speed>.3&&!m.blocked))return done(x.key==='birds'?'纸鸟已经舒展翅膀。':x.key==='pond'?'鸭子和鱼已经继续游动。':'小动物已经走走闻闻。');return waiting('它们在等身边空出来，再继续。');}
 if(x.key==='street'||x.key==='occasion'){
  if(s.weather==='rain'&&x.key==='street')return waiting('大家会先避雨，雨停后再按新安排活动。');
  const wanted=x.key==='street'?({gather:['listen'],wander:['stroll','hop','kite','browse','chat','lotus'],quiet:['rest']}[x.value]):({market:['browse'],supper:['browse'],reunion:['chat'],delivery:['mail'],quiet:['lotus','listen','rest'],ordinary:['stroll','hop','kite','browse','chat','lotus']}[x.value]);
  const a=s.actors.filter(a=>a.mobile&&wanted.includes(a.task)),arrived=a.filter(reached).length,walk=a.filter(a=>a.mode==='walk').length;
  if(x.value==='quiet'&&x.key==='street')return s.actors.filter(a=>a.mobile).every(a=>!moving(a))?done('街上的脚步已经慢下来。'):active('大家走完眼前这段路，就会停一会儿。');
  if(arrived>=2)return done(x.value==='market'||x.value==='supper'?'已经有客人到了摊前。':x.value==='reunion'?'已经有人找到邻居聊起来。':x.value==='delivery'?'送信的人已经沿街查看门牌。':x.value==='gather'?'已经有人到了树下。':'居民正在按新的安排活动。');
  return walk?active(`${walk} 位居民正在换位置。`):waiting('居民正找可用的位置，会陆续响应。');
 }
 if(x.key==='trial'){
  const id=x.value;
  if(id==='children_play'){const a=s.actors.filter(a=>['resident.garden_child','resident.child_runner'].includes(a.id));if(a.some(a=>a.task==='hop'&&reached(a)&&s.time-s.residents[a.id].started<1.9))return done('小孩已经到空地上玩起来。');return a.some(a=>a.mode==='walk')?active('小孩正往空地走。'):waiting('小孩在找不挡路的空位。');}
  if(id==='kite_walk'){const a=s.actors.find(a=>a.id==='resident.kite_child');return a.walked-p.before.actors.find(b=>b.id===a.id).walked>.3?done('小孩已经牵着风筝换了位置。'):waiting('小孩正牵稳线，准备换个位置。');}
  if(id==='garden_work')return v.watering?done('园丁正在倾倒水壶、照料花草。'):active('园丁正准备抬壶、查看花叶。');
  if(id==='pond_watch')return v.watching?done('桥边的人已经探身看水。'):active('桥边的人正把注意力转向池塘。');
  const map={market_visit:['occasion','market'],cycle_trip:['cycling','ride'],diner_inside:['dining','inside'],diner_return:['dining','dine'],rain:['weather','rain'],clear:['weather','clear'],festival:['festival','fireworks']};if(map[id])return itemStatus({key:map[id][0],value:map[id][1]},p,s,v);
 }
 return active('小镇正在按新的安排变化。');
}
export function reactionStatus(plan,s,visual={}){
 if(plan.kind==='unavailable')return {phase:'unavailable',title:'这句话暂时没有对应的变化',text:'可以换一句具体心愿，或先试试已有的活动。',complete:false};
 if(plan.kind==='already'){const [key,value]=plan.requested[0],item={key,value,id:ACTOR_DOMAINS[key]||null};const status=itemStatus(item,plan,s,visual);return{phase:status.phase==='done'?'already':status.phase,title:'这个安排已经记下',text:status.text,complete:status.phase==='done'};}
 if(s.paused)return {phase:'waiting',title:plan.title,text:'心愿已经记下，继续小镇后再开始。',complete:false};
 const states=plan.items.map(x=>itemStatus(x,plan,s,visual));const complete=states.every(x=>x.phase==='done');const current=states.find(x=>x.phase!=='done')||states[0];
 return {phase:complete?'done':current.phase,title:plan.items.length>1?plan.summary:plan.title,text:current.text,secondary:states.length>1&&states[0]!==current?states[0].text:states[1]?.text||'',complete};
}
