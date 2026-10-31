import {requestLocalDestination} from './local-walkers.mjs?v=cp37-paper-c8fccf30daca';
import {PROFILES} from './community.mjs?v=cp37-paper-c8fccf30daca';
import {stableUnit,varied} from './cadence.mjs?v=cp37-paper-c8fccf30daca';
// Counts refer to distinct, executable intentions, not interpolation frames or body parts.
export const RESIDENT_ACTIONS={
 walk_street:{label:'沿街走到另一处',duration:60,navTask:'stroll'},
 visit_market:{label:'走到摊前逛一逛',duration:60,navTask:'browse'},
 listen_music:{label:'走去树下听琴',duration:60,navTask:'listen'},
 seek_neighbor:{label:'走去找邻居聊天',duration:60,navTask:'chat'},
 watch_pond:{label:'换到能看见池塘的位置',duration:60,navTask:'lotus'},
 seek_shelter:{label:'走去可避雨的位置',duration:60,navTask:'shelter'},
 greet:{label:'抬手招呼',duration:5,pose:'wave'},
 converse:{label:'用手势交谈',duration:8,pose:'talk'},
 stretch:{label:'舒展肩臂',duration:7,pose:'stretch'},
 warm_hands:{label:'搓手取暖',duration:6,pose:'warm'},
 watch_sky:{label:'抬手望向天空',duration:7,pose:'sky'},
 applaud:{label:'拍手回应',duration:5,pose:'clap'},
 sip_tea:{label:'端杯喝茶',duration:8,pose:'sip',prop:'cup'},
 taste_food:{label:'拿点心吃一口',duration:8,pose:'eat',prop:'snack'},
 offer_food:{label:'托起点心招呼',duration:7,pose:'offer',prop:'snack'},
 wipe_counter:{label:'擦拭柜台',duration:8,pose:'wipe',prop:'cloth'},
 cover_food:{label:'拿起整理餐布',duration:7,pose:'cover',prop:'cloth'},
 water_plants:{label:'抬壶浇花',duration:9,pose:'water'},
 look_pond:{label:'转身指给同伴看游鱼',duration:7,pose:'pond'},
 inspect_leaf:{label:'扶起花叶查看',duration:7,pose:'inspect'},
 read_pages:{label:'捧书翻页',duration:11,pose:'read'},
 close_book:{label:'合书放低休息',duration:8,pose:'close'},
 check_letter:{label:'举起信件核对',duration:7,pose:'letter'},
 feed_pond:{label:'向池塘投喂',duration:9,pose:'feed',prop:'feed_bag'},
 shade_eyes:{label:'遮眉眺望',duration:6,pose:'shade'},
 brush_coat:{label:'掸掉衣上的雨雪',duration:6,pose:'brush'},
 check_time:{label:'看看时间再候车',duration:6,pose:'time'},
 signal_train:{label:'抬臂示意电车',duration:5,pose:'signal'},
 tap_music:{label:'用脚打拍子',duration:8,pose:'tap'},
 stair_round:{internal:true,label:'沿楼梯换一处停留',duration:45,route:'stairs'},
 go_terrace:{label:'走上观景露台',duration:45,route:'stairs',destination:'terrace'},
 go_street:{label:'走下楼梯到街边',duration:45,route:'stairs',destination:'street'},
 return_landing:{label:'回到楼梯平台',duration:45,route:'stairs',destination:'landing'},
 bridge_walk:{label:'沿桥换个观察位置',duration:17,route:'bridge'},
 go_window:{label:'沿阳台走到窗边',duration:20,route:'porch',destination:'window'},
 return_porch:{label:'回到阳台原位',duration:20,route:'porch',destination:'porch'},
 porch_walk:{internal:true,label:'沿阳台走走再回身',duration:14,route:'porch'},
 umbrella_open:{label:'撑开纸伞',duration:4,propAction:'open'},
 umbrella_close:{label:'收拢纸伞',duration:4,propAction:'close'}
};
const common=['greet','converse','warm_hands','watch_sky','brush_coat'];
const families={
 walker:['walk_street','visit_market','listen_music','seek_neighbor','watch_pond','seek_shelter',...common,'stretch','applaud','shade_eyes'],
 garden:[...common,'inspect_leaf','stretch'],
 listen:[...common,'applaud','tap_music','sip_tea'],
 rest:[...common,'stretch','sip_tea','tap_music'],
 watch:[...common,'shade_eyes'],
 read:['read_pages','close_book','sip_tea','greet','watch_sky','tap_music','warm_hands'],
 station:[...common,'check_time','signal_train','tap_music'],
 vendor:['greet','converse','offer_food','wipe_counter','cover_food','warm_hands'],
 musician:['greet','converse','tap_music'],
 diner:['sip_tea','taste_food','converse','watch_sky'],
 cycle:['greet','watch_sky','check_time']
};
export const RESIDENT_CAPABILITIES=Object.fromEntries(Object.entries(PROFILES).map(([id,p])=>{
 let actions=[...(families[p.role]||common)];
 if(id==='resident.quiet_reader')actions=families.read.slice();
 if(id==='resident.returning_resident')actions.push('stair_round','go_terrace','go_street','return_landing');
 if(id==='resident.porch_resident')actions.push('porch_walk','go_window','return_porch');
 if(id==='resident.water_visitor')actions.push('feed_pond','look_pond','bridge_walk');
 if(id==='resident.gardener')actions=['water_plants','inspect_leaf','greet','converse','watch_sky','brush_coat'];
 if(id==='resident.water_companion')actions=['greet','converse','watch_sky','shade_eyes','umbrella_open','umbrella_close'];
 if(id==='resident.postman')actions.push('check_letter');
 // Carrying a kite/letter/instrument takes precedence over free two-hand motions.
 if(id==='resident.kite_child')actions=actions.filter(a=>!['warm_hands','applaud','stretch','visit_market','listen_music','seek_neighbor','watch_pond','seek_shelter'].includes(a));
 if(id==='resident.postman')actions=actions.filter(a=>!['warm_hands','applaud'].includes(a));
 return[id,[...new Set(actions)]];
}));
export function createResidentActions(){return Object.fromEntries(Object.entries(PROFILES).map(([id,p],i)=>[id,{action:null,clock:0,cycle:0,nextAt:1.6+(i%7)*.54,queued:null,queuedByUser:false,requested:false,cancelRemaining:0,contextWeather:'clear',completed:0,lastAction:null,reason:'自己的晚间习惯',bookOpen:1,bookTarget:1,bookManualUntil:0,umbrella:1,umbrellaTarget:1}]));}
export function requestResidentAction(s,id,action){if(!RESIDENT_CAPABILITIES[id]?.includes(action))throw Error('这个角色没有这项已实现动作');
 if(RESIDENT_ACTIONS[action].navTask&&RESIDENT_ACTIONS[action].navTask!=='shelter'&&s.weather==='rain')throw Error('雨还在下，先到避雨的位置，雨停后再安排外出。');
 if(action==='read_pages'&&s.weather==='rain')throw Error('雨还在下，先把书收好。');
 if(action==='feed_pond'&&s.weather==='rain')throw Error('先等雨停，再投喂池塘。');
 if(RESIDENT_ACTIONS[action].route&&!s.availableRoutes?.includes(id))throw Error('这条路线还没有完成空间验证');
 if(RESIDENT_ACTIONS[action].destination&&s.localWalkers?.[id]?.anchor===RESIDENT_ACTIONS[action].destination&&!s.localWalkers[id].clip)throw Error('他已经在这个位置了。');
 if(PROFILES[id].role==='diner'&&s.diners[id].phase==='inside'){const d=s.diners[id];d.manualPolicy='dine';d.policy='dine';d.effectivePolicy='dine';d.wait=0;}
 const r=s.residentActions[id];if(['read_pages','close_book'].includes(action)){r.bookTarget=action==='read_pages'?1:0;r.bookManualUntil=s.time+45;}r.queued=action;r.queuedByUser=true;if(r.action&&!RESIDENT_ACTIONS[r.action].route&&!RESIDENT_ACTIONS[r.action].navTask&&PROFILES[id].role!=='diner'&&!['sip_tea','taste_food','feed_pond','look_pond'].includes(r.action))r.cancelRemaining=.65;r.reason='接到你的安排';r.nextAt=s.time;s.revision++;return {id,action};
}
function canAct(s,id,action){if(s.passengers?.[id]&&s.passengers[id].phase!=='waiting')return false;if(s.localWalkers?.[id]?.clip)return false;const a=s.actors.find(a=>a.id===id),p=PROFILES[id];if(a&&['walk','yield','fold_umbrella'].includes(a.mode))return false;if(a?.mobile&&!(s.residentActions[id].requested||s.residentActions[id].queuedByUser)&&(a.reservation===null||a.taskRevision!==s.planRevision))return false;if(RESIDENT_ACTIONS[action].navTask&&RESIDENT_ACTIONS[action].navTask!=='shelter'&&s.weather==='rain')return false;if(a?.task==='hop'&&s.time-s.residents[id].started<2)return false;
 // Keep several street residents travelling instead of everybody settling into
 // long automatic gestures at once. Explicit wishes and shelter/show stops win.
 if(a?.mobile&&!s.residentActions[id].queuedByUser&&!s.residentActions[id].requested&&!a.manual&&s.weather!=='rain'&&s.worldEvent.kind!=='festival'&&s.occasion!=='quiet'&&s.street!=='quiet'&&!a.manualActivity&&s.actors.filter(x=>x.mobile&&x.path.length&&['walk','yield'].includes(x.mode)).length<4){a.wait=Math.min(a.wait,.35);return false;}
 if((s.residents[id]?.umbrellaOpen||0)>.08)return false;
 if(p.role==='diner'&&s.diners[id]?.phase!=='dine')return false;
 if(p.role==='cycle'&&s.movers['bicycle.street_bicycle'].tripState!=='parked')return false;
 if(RESIDENT_ACTIONS[action].navTask&&RESIDENT_ACTIONS[action].navTask!=='shelter'&&s.weather==='rain')return false;
 if(action==='read_pages'&&s.weather==='rain')return false;
 if(action==='feed_pond'&&s.weather==='rain')return false;
 return true;
}
function choose(s,id,r){const p=PROFILES[id],cap=RESIDENT_CAPABILITIES[id];let candidates;
 if(s.weather==='rain')candidates=p.role==='read'?['close_book','warm_hands','watch_sky']:p.role==='vendor'?['cover_food','wipe_counter']:id==='resident.water_companion'?['umbrella_open']:['brush_coat','warm_hands','converse'];
 else if(s.weather==='snow')candidates=['warm_hands','watch_sky','brush_coat'];
 else if(s.worldEvent?.phase==='show')candidates=['watch_sky'];
 else if(['market','supper'].includes(s.sceneEvent?.kind)&&s.sceneEvent.phase!=='release'&&(p.role==='vendor'||s.actors.some(a=>a.id===id&&a.mobile)))candidates=s.sceneEvent.phase==='closing'?(p.role==='vendor'?['wipe_counter','greet']:['greet','converse']):p.role==='vendor'?['offer_food','greet','wipe_counter']:['taste_food','converse','greet'];
 else if(s.sceneEvent?.kind==='lantern'&&s.sceneEvent.phase!=='release')candidates=['greet','converse','tap_music'];
 else if(p.role==='station'&&s.train.mode==='dwell')candidates=['signal_train','greet'];
 else if(p.role==='read')candidates=r.bookManualUntil>s.time&&r.bookTarget===0?['sip_tea','watch_sky','greet','tap_music']:['read_pages','read_pages','close_book','sip_tea'];
 else if(id==='resident.returning_resident')candidates=['stair_round','stair_round','shade_eyes','greet'];
 else if(id==='resident.water_visitor')candidates=['feed_pond','feed_pond','bridge_walk','converse'];
 else if(id==='resident.water_companion')candidates=r.umbrella>.5?['umbrella_close','converse']:['shade_eyes','greet','watch_sky'];
 else if(p.role==='vendor')candidates=s.residents[id].activity==='serve'?['offer_food','greet','converse']:['wipe_counter','cover_food','stretch'];
 else if(id==='resident.gardener')candidates=['water_plants','inspect_leaf','greet'];else if(p.role==='garden')candidates=['inspect_leaf','greet','stretch'];
 else if(id==='resident.porch_resident')candidates=['porch_walk','converse','greet'];
 else if(p.role==='station')candidates=['check_time','tap_music','greet'];else if(p.role==='listen')candidates=s.effectiveMusic==='play'?['tap_music','sip_tea','greet']:['converse','sip_tea','greet'];else if(p.role==='rest')candidates=['sip_tea','stretch','greet'];else candidates=cap.filter(a=>!RESIDENT_ACTIONS[a].navTask&&!['warm_hands','brush_coat','signal_train'].includes(a));
 candidates=candidates.filter(a=>(!RESIDENT_ACTIONS[a].route||!(s.localWalkers?.[id]?.holdUntil>s.time))&&cap.includes(a)&&a!==r.lastAction&&(!RESIDENT_ACTIONS[a].route||s.availableRoutes?.includes(id)));if(!candidates.length)candidates=cap.filter(a=>!RESIDENT_ACTIONS[a].route);return candidates[Math.floor(stableUnit(id,r.cycle)*candidates.length)];
}
export function advanceResidentActions(s,dt,routes={}){for(const[id,r]of Object.entries(s.residentActions)){
 r.bookOpen+=(r.bookTarget-r.bookOpen)*Math.min(1,dt*2.6);
 r.umbrella+=(r.umbrellaTarget-r.umbrella)*Math.min(1,dt*2.6);
 if(s.actors.find(a=>a.id===id)?.interactionLock||s.eventGuests?.[id]?.active||s.sceneEvent?.slots?.[id]!==undefined&&['gather','active','closing'].includes(s.sceneEvent.phase)&&!r.requested&&!r.queuedByUser){r.action=null;r.clock=0;r.nextAt=s.time+.5;continue;}
 if(r.action){const def=RESIDENT_ACTIONS[r.action];if(r.contextWeather!==s.weather){r.contextWeather=s.weather;if(def.navTask&&s.weather==='rain'&&def.navTask!=='shelter'){r.queued=r.action;r.queuedByUser=r.requested;r.action=null;r.nextAt=s.time+.25;continue;}if(id==='resident.quiet_reader'&&s.weather==='rain')r.bookTarget=0;if(!def.route&&!def.navTask&&PROFILES[id].role!=='diner'&&!['sip_tea','taste_food','feed_pond','look_pond'].includes(r.action))r.cancelRemaining=.65;}
  // Finish the small gesture before switching. Walking always owns the limbs.
  const cancelling=r.cancelRemaining>0;if(cancelling)r.cancelRemaining=Math.max(0,r.cancelRemaining-dt);else r.clock=Math.min(def.duration,r.clock+dt);const walker=s.localWalkers?.[id];const actor=s.actors.find(a=>a.id===id);const finished=cancelling&&r.cancelRemaining===0?true:def.route?walker&&!walker.clip&&walker.anchor===walker.goal:def.navTask?actor?.task===def.navTask&&actor.reservation!==null&&!actor.path.length&&actor.mode==='idle'&&(def.navTask!=='chat'||!!actor.chatPartner)&&(def.navTask!=='listen'||s.effectiveMusic==='play'):r.clock>=def.duration;if(finished){const holder=s.actors.find(a=>a.id===id);if(holder){holder.localActionUntil=Math.min(holder.localActionUntil||0,s.time);if(cancelling)holder.wait=Math.min(holder.wait,varied([.25,1.4],id,r.cycle));}if(def.route&&r.requested)walker.holdUntil=s.time+varied([18,30],id,r.cycle);r.lastAction=r.action;r.completed++;r.action=null;r.clock=0;r.nextAt=s.time+(cancelling?.25:varied([2,5],id,r.cycle));if(r.requested)r.requested=false;}continue;
 }
 if(s.sceneEvent?.kind==='festival'&&['gather','active'].includes(s.sceneEvent.phase)&&s.actors.some(a=>a.id===id&&a.mobile)&&!r.queuedByUser&&!r.requested){r.nextAt=Math.max(r.nextAt,s.time+.5);continue;}
 if(s.time<r.nextAt)continue;const action=r.queued||choose(s,id,r);if(!canAct(s,id,action)){r.nextAt=s.time+.4;continue;}
 r.action=action;r.clock=0;r.requested=!!r.queuedByUser;r.queuedByUser=false;r.queued=null;r.cycle++;r.cancelRemaining=0;r.contextWeather=s.weather;if(RESIDENT_ACTIONS[action].route){const walker=s.localWalkers[id],target=RESIDENT_ACTIONS[action].destination||({landing:'terrace',terrace:'street',street:'landing'}[walker.anchor]||Object.keys(routes[id].anchors).find(k=>k!==walker.anchor));requestLocalDestination(s,id,target,routes);}
 r.reason=r.requested?'接到你的安排':s.weather==='rain'?'雨来了，换一种合适的活动':s.weather==='snow'?'下雪了，先暖暖手再看看雪':s.worldEvent?.phase==='show'?'听见花火，回应夜空里的热闹':'按自己的兴趣做一会儿';if(id==='resident.quiet_reader'&&action==='sip_tea')r.bookTarget=0;if(action==='read_pages')r.bookTarget=1;if(action==='close_book')r.bookTarget=0;
 if(RESIDENT_ACTIONS[action].propAction)r.umbrellaTarget=RESIDENT_ACTIONS[action].propAction==='open'?1:0;
 const a=s.actors.find(a=>a.id===id);if(a&&RESIDENT_ACTIONS[action].navTask){a.manual=false;a.manualActivity=RESIDENT_ACTIONS[action].navTask;a.activityUntil=s.time+90;a.path=[];a.reservation=null;a.target=null;a.taskRevision=-1;a.wait=.1;a.localActionUntil=0;}else if(a){a.wait=Math.max(a.wait,RESIDENT_ACTIONS[action].duration+.4);a.localActionUntil=s.time+RESIDENT_ACTIONS[action].duration;}
 if(action==='feed_pond'){s.pondFeeding={owner:id,started:s.time+2.5,until:s.time+11,target:[8.7,-1.6,.62]};}
 }}
export function validateResidentActions(s){if(!s.residentActions||Object.keys(s.residentActions).length!==Object.keys(PROFILES).length)throw Error('角色动作存档不完整');for(const[id,r]of Object.entries(s.residentActions)){if(!RESIDENT_CAPABILITIES[id]||r.action&&!RESIDENT_CAPABILITIES[id].includes(r.action)||r.queued&&!RESIDENT_CAPABILITIES[id].includes(r.queued)||!['clock','cycle','nextAt','completed','umbrella','umbrellaTarget','bookOpen','bookTarget'].every(k=>Number.isFinite(r[k]))||r.clock<0||r.umbrella<0||r.umbrella>1)throw Error('角色动作存档无效');}}

export function availableResidentActions(id,routes={}){return (RESIDENT_CAPABILITIES[id]||[]).filter(a=>!RESIDENT_ACTIONS[a].internal&&(!RESIDENT_ACTIONS[a].route||routes[id]));}
