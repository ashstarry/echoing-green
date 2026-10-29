import {requestResidentAction} from './resident-actions.mjs?v=cp30-life-e7bb14ab832f';
// Executable local action trials; semantic expansion waits for reviewed behavior.
export const ACTION_LIBRARY=[
 {id:'children_play',label:'孩子玩起来',description:'花园小孩走到空地，停稳后跳两下，再换个位置。',entities:['resident.garden_child','resident.child_runner'],activities:['hop'],decisions:{}},
 {id:'kite_walk',label:'迎风放风筝',description:'小孩换位置牵线、收放，家长跟着看看。',entities:['resident.kite_child','resident.child_parent','kite.plaza_kite'],activities:['kite','follow'],decisions:{}},
 {id:'garden_work',label:'照料花草',description:'园丁抬壶、倾倒、收回；帮手探身查看花叶。',entities:['resident.gardener','resident.assistant_gardener','watering_can.garden_can'],activities:['garden','inspect'],decisions:{}},
 {id:'pond_watch',label:'桥边看看鱼',description:'两人探身看水、抬头交流，再回头看鱼。',entities:['resident.water_visitor','resident.water_companion'],activities:['lotus','chat'],decisions:{}},
 {id:'market_visit',label:'逛摊买东西',description:'客人走到摊前，店员招呼、整理，之后客人离开。',entities:['resident.customer_one','resident.vendor_bread'],activities:['browse','serve'],decisions:{occasion:'market'}},
 {id:'cycle_trip',label:'骑车去下一站',description:'沿较长街道出发，车站旁或池塘边停脚再走。',entities:['bicycle.street_bicycle','resident.cyclist'],activities:['cycle_trip'],decisions:{cycling:'ride'}},
 {id:'diner_inside',label:'吃好回茶间',description:'二楼客人推椅起身，真实经过门帘。',entities:['resident.upper_diner_0','resident.upper_diner_1'],activities:['inside'],decisions:{dining:'inside'}},
 {id:'diner_return',label:'出来坐下用餐',description:'从门帘走出，坐回自己的餐位。',entities:['resident.upper_diner_0','resident.upper_diner_1'],activities:['dine'],decisions:{dining:'dine'}},
 {id:'rain',label:'一阵雨来了',description:'陆续找位置避雨、撑伞，二楼回茶间。',entities:[],activities:['shelter'],decisions:{weather:'rain'}},
 {id:'clear',label:'雨停继续玩',description:'收好雨具，再恢复街巷的活动。',entities:[],activities:[],decisions:{weather:'clear',occasion:'ordinary'}},
 {id:'festival',label:'一起看花火',description:'找位置、观看、余韵，再恢复日常。',entities:[],activities:['fireworks'],decisions:{weather:'clear',festival:'fireworks'}}
];
export function beginAction(s,id,apply){const action=ACTION_LIBRARY.find(x=>x.id===id);if(!action)throw Error('未开放的动作');if(s.weather==='rain'&&['children_play','kite_walk','garden_work','cycle_trip'].includes(id))throw Error('雨还在下，先点“雨停继续玩”，再试这个活动。');if(id==='cycle_trip'&&s.worldEvent.kind==='festival')throw Error('骑车人正在等花火结束，之后再试下一段骑行。');apply(s,action.decisions);s.roleOverrides??={};const assign=(actor,task)=>{const a=s.actors.find(x=>x.id===actor);if(a){a.manualActivity=task;a.activityUntil=s.time+38;a.manual=false;a.path=[];a.reservation=null;a.taskRevision=-1;a.wait=.3;a.mode='idle';}};
 if(id==='children_play'){assign('resident.garden_child','hop');assign('resident.child_runner','hop');}
 if(id==='kite_walk'){assign('resident.kite_child','kite');assign('resident.child_parent','follow');}
 if(id==='garden_work')for(const[id,activity]of [['resident.gardener','garden'],['resident.assistant_gardener','inspect']])s.roleOverrides[id]={activity,until:s.time+24};
 if(id==='pond_watch')for(const id of ['resident.water_visitor','resident.water_companion'])s.roleOverrides[id]={activity:'lotus',until:s.time+16};
 if(id==='cycle_trip'){const m=s.movers['bicycle.street_bicycle'];m.restUntil=s.time;m.stopWait=0;}
 if(id==='garden_work'){requestResidentAction(s,'resident.gardener','water_plants');requestResidentAction(s,'resident.assistant_gardener','inspect_leaf');}if(id==='pond_watch'){requestResidentAction(s,'resident.water_visitor','look_pond');requestResidentAction(s,'resident.water_companion','converse');}
 s.actionTrial={id,started:s.time};s.planRevision++;return action;
}
