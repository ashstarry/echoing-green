export function actionAvailability(s,item){const t=s.train,p=s.passengers?.['resident.station_traveler'],atStation=t?.mode==='dwell';
 if(item.target==='journey'&&item.action!=='rest'){
  if(s.eventGuests?.['resident.station_traveler']?.active)return{available:false,reason:'The traveler is returning to the platform.'};
  if(!atStation)return{available:false,reason:'电车还在路上，靠站后再来迎送。'};
  if(item.action==='depart'&&p?.phase!=='waiting')return{available:false,reason:'旅客正在上下车，等他站稳后再试。'};
  if(item.action==='deliver'&&p?.phase!=='waiting')return{available:false,reason:'旅客正在上下车，等他站稳后再试。'};
  if(item.action==='welcome'&&p?.phase==='waiting'&&!p.completedTrips)return{available:false,reason:'这时还没有归来的旅客，先试试另一件小事。'};
 }
 if(item.kind==='resident'&&['ride_once','alight','stay'].includes(item.action)){
  if(!atStation)return{available:false,reason:'电车还在路上，靠站后再来迎送。'};
  if(item.action==='ride_once'&&p?.phase!=='waiting'||item.action==='alight'&&p?.phase==='waiting')return{available:false,reason:'旅客已经是这个状态了。'};
 }
 if((item.target==='train'&&item.action==='hold'||item.target?.startsWith('tram.')&&item.action==='hold')&&!atStation)return{available:false,reason:'电车还在路上，靠站后再来迎送。'};
 return{available:true};
}

export function resolveActionItems(items,catalog){return items.map(i=>{if(i.kind!=='object')return i;const o=catalog[i.target],a=o?.actions.find(a=>a.id===i.action);let owner=a?.owner,action=i.action;if(o?.kind==='watering_can'){owner='resident.gardener';action=i.action==='pour'?'water_plants':'inspect_leaf';}if(o?.kind==='instrument'){owner='resident.musician';action=i.action==='play'?'play_music':'rest_music';}if(o?.kind==='seat'&&i.target.includes('dining_chair')){owner='resident.upper_diner_'+i.target.at(-1);action=i.action==='pull_out'?'inside':'dine';}return owner?{...i,origin_object:i.target,kind:'resident',target:owner,action}:i;});}
