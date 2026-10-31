import {requestResidentAction} from './resident-actions.mjs?v=cp39-neighborhood-18b2d8344ad8';
const definitions={
 kite:{fly:['牵稳线放风筝',1],calm:['让风筝平稳下来',.12]},
 windmill:{slow:['慢慢转',.20],brisk:['轻快地转',.70],stop:['慢慢停住',0],follow_wind:['跟随晚风',null]},
 plant:{sway:['随晚风摆动',1],rustle:['轻轻抖动叶片',1.2],still:['叶片安静下来',0]},
 tree:{sway:['随晚风摆动',1],rustle:['轻轻抖动枝叶',1.2],still:['枝叶安静下来',0]},
 hanging_ornament:{sway:['轻摆吊饰',1],rustle:['轻快摆动',1.2],still:['安静垂下',0]},
 bird:{fly:['循着空中路线飞',1],hover:['放慢并悬停',0],glide:['舒展翅膀滑翔',.75],flap:['轻快拍翼',1]},
 fish:{swim:['继续游动',1],nibble:['放慢觅食',.12],rest:['缓缓停留',0]},
 animal:{explore:['沿熟悉的地方走走',1],sniff:['停下嗅闻',0],look:['抬头留意周围',0],rest:['安静歇息',0]},
 duck:{swim:['沿水面游动',1],nibble:['低头啄食',.12],look:['抬头张望',.15],rest:['安静浮着',0]},
 boat:{bob:['系泊轻摇',1],row:['摆动船桨',1],rest:['船与桨放轻动作',0]},
 water_lantern:{float:['在水上轻浮',1],still:['缓缓停稳',0],shine:['灯心更明亮',1]},
 light:{warm:['橘暖灯火',1],soft:['柔和灯火',.55],dark:['熄下这盏灯',0]},
 star:{glow:['稳定发亮',1],twinkle:['轻轻闪烁',1],dim:['光芒淡下来',.35]},
 celestial:{glow:['月光明亮',1],dim:['月光柔和',.55]},
 door:{open:['滑开站门',1],close:['关上站门',0]},
 curtain:{open:['把门帘拨向两侧',1],close:['让门帘垂下',0],sway:['门帘随风轻摆',null]},
 parked_bicycle:{freewheel:['轻拨车轮',1],settle:['让车轮停下',0]}
};
const coupled={
 book:[['read_pages','翻阅书页','resident.quiet_reader'],['close_book','合书休息','resident.quiet_reader']],
 umbrella:[['umbrella_open','撑开纸伞','resident.water_companion'],['umbrella_close','收拢纸伞','resident.water_companion']],
 letter:[['check_letter','让邮差核对信件','resident.postman']],
 instrument:[['play','弹奏琴弦',null],['rest','放下拨弦动作',null]],
 watering_can:[['pour','抬壶浇水',null],['rest','把水壶放稳',null]],
 weather:[['rain','让雨落下来',null],['snow','让纸片雪落下',null],['clear','让雨雪收住',null]],
 tram:[['run','到站后继续环镇',null],['hold','到站停候',null]],
 bicycle:[['ride','骑去下一处',null],['rest','到下一处停脚',null]]
};
export function objectCatalog(registry){return Object.fromEntries(registry.entities.filter(e=>e.kind!=='resident').map(e=>{
 let kind=e.id==='bicycle.cp07_parked_bicycle'?'parked_bicycle':e.id.startsWith('animal.duck_')?'duck':e.kind;
 let actions=Object.entries(definitions[kind]||{}).map(([id,[label,value]])=>({id,label,value,executor:'object'}));
 if(['cup','food'].includes(kind))actions=[{id:kind==='cup'?'sip_tea':'taste_food',label:kind==='cup'?'端起喝茶再放回':'拿起品尝再放回',owner:e.state.owner,executor:'coupled'}];
 if(coupled[kind])actions=coupled[kind].map(([id,label,owner])=>({id,label,owner,executor:'coupled'}));
 if(e.kind==='seat'&&e.id.includes('dining_chair'))actions=[{id:'pull_out',label:'随客人起身拉开椅子',executor:'seat'},{id:'sit_back',label:'随客人坐回收椅',executor:'seat'}];
 if(e.kind==='workstation')actions=e.id.includes('upper_dining')?[{id:'sip_tea',label:'客人端茶',executor:'coupled',owner:'resident.upper_diner_'+e.id.at(-1)},{id:'taste_food',label:'客人用餐',executor:'coupled',owner:'resident.upper_diner_'+e.id.at(-1)}]:[{id:'inspect_leaf',label:'园丁检查花叶',executor:'coupled',owner:'resident.gardener'}];
 return[e.id,{id:e.id,kind,actions,coupled:actions.some(a=>a.executor!=='object'),fixed:!actions.length}];}));}
export function requestObjectAction(s,id,action,catalog,apply){const item=catalog[id],def=item?.actions.find(a=>a.id===action);if(!def)throw Error('这个物件没有这项可执行动作');
 if(def.owner)return requestResidentAction(s,def.owner,action);
 if(def.executor==='seat'){const diner=id.endsWith('0')?'resident.upper_diner_0':'resident.upper_diner_1';const d=s.diners[diner];d.manualPolicy=action==='pull_out'?'inside':'dine';d.policy=d.manualPolicy;d.effectivePolicy=d.policy;d.wait=0;s.revision++;return;}
 if(def.executor==='workstation'){const people=['resident.vendor_bread','resident.vendor_flower','resident.vendor_lamp'],n=Number(id.at(-1))||0;return requestResidentAction(s,people[n%3],action==='serve'?'offer_food':'wipe_counter');}
 if(def.executor==='coupled'){
  if(item.kind==='weather')apply(s,{weather:action});
  if(item.kind==='instrument')apply(s,{music:action==='play'?'play':'rest'});
  if(item.kind==='tram')apply(s,{train:action==='run'?'auto':'hold'});
  if(item.kind==='bicycle')apply(s,{cycling:action==='ride'?'ride':'rest'});
  if(item.kind==='watering_can')return requestResidentAction(s,'resident.gardener',action==='pour'?'water_plants':'inspect_leaf');
  if(item.kind==='kite')apply(s,{breeze:action==='fly'?'gentle':'calm'});
  return;
 }
 const old=s.objectControls[id];s.objectControls[id]={kind:item.kind,action,target:def.value,value:old?.value??(item.kind==='windmill'?s.windSpeed:item.kind==='parked_bicycle'||item.kind==='curtain'?0:item.kind==='door'?(s.train.doorOpen||0):1),phase:old?.phase??(item.kind==='windmill'?s.windPhase:0),started:s.time};s.revision++;
}
export function advanceObjectControls(s,dt){for(const c of Object.values(s.objectControls)){const target=c.target??s.windSpeed;c.value+=(target-c.value)*Math.min(1,dt*3);c.phase+=c.value*dt*3.1;}}
export function validateObjectControls(s){if(!s.objectControls||typeof s.objectControls!=='object')throw Error('物件动作存档不完整');for(const c of Object.values(s.objectControls))if(!definitions[c.kind]?.[c.action]||!Number.isFinite(c.value)||!Number.isFinite(c.phase)||!Number.isFinite(c.started))throw Error('物件动作存档无效');}
export function describeObjectAction(c){return definitions[c.kind]?.[c.action]?.[0]||'';}
