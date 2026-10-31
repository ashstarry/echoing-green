import {FIREWORK_FOCUS} from './event-design.mjs?v=cp36-freewords-007e6e30821d';
import {advanceSceneEvent,requestSceneEvent,sceneTask} from './scene-events.mjs?v=cp36-freewords-007e6e30821d';
import {CADENCE,varied,stableUnit} from './cadence.mjs?v=cp36-freewords-007e6e30821d';
export const ACTIVITIES={
 hop:{label:'找一块空地跳两下',range:[3,6],zone:'playground'},follow:{label:'跟着孩子换个位置',range:[4,8],zone:'family'},
 play:{label:'给街坊弹一段琴',range:[18,35]},
 stroll:{label:'沿街散步',range:CADENCE.stroll,zone:'street'},browse:{label:'看看摊上的东西',range:[8,19],zone:'market'},chat:{label:'和邻居聊一会儿',range:CADENCE.chat,zone:'chat'},lotus:{label:'看荷花和游鱼',range:CADENCE.watch,zone:'pond'},listen:{label:'在树下听琴',range:[10,24],zone:'music'},mail:{label:'沿街查看门牌',range:[7,15],zone:'post'},rest:{label:'停下来歇一会儿',range:CADENCE.rest,zone:'street'},shelter:{label:'回到门前避雨',range:[18,35],zone:'home'},fireworks:{label:'找空位看花火',range:[18,35],zone:'view'},applaud:{label:'为花火轻轻鼓掌',range:[3,6],zone:'view'},snow:{label:'看看落下的纸片雪',range:[8,18],zone:'street'},serve:{label:'招呼客人、整理餐具',range:CADENCE.work},garden:{label:'照料花草',range:CADENCE.work},inspect:{label:'看看花叶长得怎么样',range:CADENCE.watch},read:{label:'读几页书',range:[16,30]},wait:{label:'等候下一班电车',range:[15,32]},signal:{label:'向到站电车示意',range:[3,5]},kite:{label:'迎着风走几步，再牵一牵线',range:[3,7],zone:'kite'},dine:{label:'慢慢用餐',range:CADENCE.meal},inside:{label:'在帘后的茶间歇息',range:CADENCE.inside},tidy:{label:'照看柜台和餐具',range:[12,22]}
};
const data={
 assistant_gardener:['花房的帮手','garden',['garden','inspect'],[6.4,3.4,1.2],'gardener'],gardener:['照料花草的居民','garden',['garden','inspect'],[5.2,3.8,1.1],'assistant_gardener'],garden_child:['花园边玩耍的小孩','walker',['hop','lotus','hop'],[7.8,-1.2,.7]],child_listener:['听琴的小孩','listen',['listen','chat'],[-2.5,-1.5,1.3],'listener'],listener:['树下的听众','listen',['listen','chat'],[-2.5,-1.5,1.3],'child_listener'],child_parent:['陪孩子的家长','walker',['follow','chat'],[2.4,-.8,1.2],'kite_child'],kite_child:['放风筝的孩子','walker',['kite','kite','rest'],[2.4,-.9,3.5],'child_parent'],child_runner:['广场上玩耍的小孩','walker',['hop','stroll','listen'],[0,0,1]],courier:['巷口的送信人','walker',['mail','chat','stroll'],[-5,-1,1]],postman:['邮局的邮差','walker',['mail','chat','rest'],[-5.5,-2,1]],customer_one:['餐厅门前的客人','walker',['browse','listen','chat'],[-2,2,1]],customer_two:['穿灰衣的客人','walker',['browse','chat','lotus'],[-1,3,1]],customer_three:['穿黄衣的客人','walker',['browse','chat','stroll'],[1,4,1]],market_browser:['逛集市的居民','walker',['browse','lotus','chat'],[2,2,1]],strolling_parent:['散步的家长','walker',['stroll','chat','listen'],[-3,0,1]],cyclist:['骑车的居民','cycle',['stroll','rest'],[0,0,1]],elder:['门边的长者','rest',['rest','chat'],[-7,-1,1.2],'porch_resident'],porch_resident:['阳台上的邻居','watch',['rest','chat'],[-9,-2,1.4],'elder'],quiet_reader:['露台上的读者','read',['read','rest'],[4,7,2.3]],returning_resident:['楼梯上的红衣居民','watch',['rest','kite'],[2.4,-.9,3.4]],station_attendant:['车站值守的人','station',['wait','rest'],[-.6,-6.9,1.4]],station_traveler:['准备出行的旅客','station',['wait','rest'],[-.6,-6.9,1.4]],waiting_passenger:['坐着候车的人','station',['wait','chat'],[-.6,-6.9,1.4],'waiting_passenger_2'],waiting_passenger_2:['候车的邻居','station',['wait','chat'],[-.6,-6.9,1.4],'waiting_passenger'],water_companion:['桥边持伞的同伴','watch',['lotus','chat'],[8.2,-1.5,.7],'water_visitor'],water_visitor:['桥边红衣居民','watch',['lotus','chat'],[8.2,-1.5,.7],'water_companion'],vendor_bread:['酒楼的面点师','vendor',['serve','tidy'],[-3,1,1]],vendor_flower:['酒楼的招待','vendor',['serve','tidy'],[-1.5,1.5,1]],vendor_lamp:['柜台边的店员','vendor',['serve','tidy'],[.5,3,1]],musician:['树下的乐手','musician',['listen','rest'],[-1,-1,1]],upper_diner_0:['二楼左边的客人','diner',['dine'],[-2,3,3]],upper_diner_1:['二楼右边的客人','diner',['dine'],[0,4,3]]
};
export const PROFILES=Object.fromEntries(Object.entries(data).map(([id,[label,role,routine,look,buddy]])=>['resident.'+id,{label,role,routine,look,buddy:buddy?'resident.'+buddy:null}]));
export const OCCASIONS={ordinary:'各自的日常',market:'热闹晚市',supper:'晚餐时间',reunion:'邻里相聚',delivery:'送信时光',quiet:'安静晚风'};
export function createCommunity(nav){return Object.fromEntries(Object.entries(PROFILES).map(([id,p])=>[id,{activity:p.routine[0],reason:'按自己的习惯过晚间生活',started:0,until:varied(ACTIVITIES[p.routine[0]].range,id),cycle:0,lookTarget:p.look,lookYaw:0,gesture:0,gesturePhase:0,umbrellaOpen:0,needs:{social:stableUnit(id),curiosity:.4,rest:.3}}]));}
export function requestFestival(s){if(s.worldEvent?.phase==='show'){s.worldEvent.until=Math.max(s.worldEvent.until,s.time+18);s.festivalUntil=s.worldEvent.until;s.planRevision++;return;}s.worldEvent={kind:'festival',phase:s.weather==='rain'?'postponed':'prepare',started:s.time,until:s.time+varied(CADENCE.festivalPrepare,'festival',s.revision),revision:(s.worldEvent?.revision||0)+1};s.planRevision++;s.festivalUntil=0;}
export function updateDirector(s,dt,emit,nav){
 advanceSceneEvent(s,nav,dt,emit);
 if(s.festivalAuto&&!s.sceneEvent&&['dusk','night'].includes(s.day_phase)&&s.time>=s.festivalNextAt)requestSceneEvent(s,{festival:'fireworks'},emit,{automatic:true});
 s.effectiveMusic=s.sceneEvent?.kind==='music'&&!s.sceneEvent.silentMusic&&['gather','active'].includes(s.sceneEvent.phase)?'play':s.weather==='rain'&&!s.musicManual||s.sceneEvent?.kind==='festival'&&s.sceneEvent.phase==='active'?'rest':s.music;
 for(const[id,d]of Object.entries(s.diners)){const festival=s.sceneEvent?.kind==='festival'&&['gather','active'].includes(s.sceneEvent.phase);const policy=d.manualPolicy||(s.dining!=='auto'?s.dining:s.weather==='rain'?'inside':festival||s.occasion==='supper'?'dine':'auto');if(d.effectivePolicy!==policy){d.effectivePolicy=policy;d.policy=policy;d.wait=Math.min(d.wait,varied([1,4],id,s.planRevision));}}
}
export function wantedTask(s,a){
 const foreground=sceneTask(s,a);if(foreground)return foreground;
 if(a.manual)return a.intent==='quiet'?'rest':a.intent==='gather'?'listen':'stroll';
 if(s.weather==='rain')return 'shelter';
 if(a.manualActivity&&s.time<a.activityUntil)return a.manualActivity;
 if(a.responseTask&&s.time<a.responseUntil)return a.responseTask;
 if(s.worldEvent.kind==='festival')return s.worldEvent.phase==='linger'?'chat':'fireworks';
 if(s.time<s.afterRainUntil)return 'shelter';
 if(s.weather==='snow')return 'snow';
 if(s.occasion==='market'||s.occasion==='supper')return 'browse';
 if(s.occasion==='reunion')return a.id==='resident.postman'?'mail':'chat';
 if(s.occasion==='delivery'&&['resident.postman','resident.courier'].includes(a.id))return 'mail';
 if(s.occasion==='quiet')return ['resident.market_browser','resident.strolling_parent','resident.child_runner'].includes(a.id)?'lotus':a.id.includes('customer')?'listen':'rest';
 if(s.time<s.musicGatherUntil&&stableUnit(a.id)<.55)return 'listen';
 if(s.street==='gather')return 'listen';if(s.street==='quiet')return 'rest';
 return null;
}
export function routineTask(s,a){const r=s.residents[a.id],p=PROFILES[a.id];if(r.cycle===0){r.cycle++;return p.routine[0];}let best=p.routine[0],score=-1;for(const task of p.routine){const need=task==='chat'?r.needs.social:task==='rest'?r.needs.rest:r.needs.curiosity;const value=.35+need*.55+stableUnit(a.id+task,r.cycle)*.24-(task===r.activity?.15:0);if(value>score){best=task;score=value;}}r.cycle++;return best;}
export function setResidentTask(s,id,activity,reason){const r=s.residents[id];if(!r)return;r.activity=activity;r.reason=reason;r.started=s.time;r.until=s.time+varied(ACTIVITIES[activity]?.range||CADENCE.rest,id,r.cycle++);}
export function updateResidents(s,nav,dt){
 for(const [id,r]of Object.entries(s.residents)){
  const p=PROFILES[id],a=s.actors.find(x=>x.id===id);r.needs.social=Math.min(1,r.needs.social+dt*.003);r.needs.curiosity=Math.min(1,r.needs.curiosity+dt*.004);r.needs.rest=Math.min(1,r.needs.rest+dt*.002);
  if(!a?.mobile&&p.role!=='diner'){
   let next=null,reason='按自己的习惯过晚间生活';
   if(s.roleOverrides?.[id]?.until>s.time){next=s.roleOverrides[id].activity;reason='正在试一试这个活动';}
   else if(s.weather==='rain'){next=p.role==='vendor'?'tidy':p.role==='musician'?'rest':'shelter';reason=p.role==='vendor'?'下雨了，先照看摊上的东西':'等雨小一些，留意身边的人';}
   else if(s.worldEvent.kind==='festival'&&['prepare','show','linger'].includes(s.worldEvent.phase)){next=s.worldEvent.phase==='linger'?'applaud':'fireworks';reason='听见花火的动静，在自己的位置看夜空';}
   else if(s.train.mode==='dwell'&&s.time-s.train.arrivedAt<4&&p.role==='station'){next='signal';reason='电车进站，和车上的人打个招呼';}
   else if(p.role==='vendor'&&s.sceneEvent?.phase==='closing'&&['market','supper'].includes(s.sceneEvent.kind)){next='tidy';reason='收好餐具，和最后的客人道别';}
   else if(p.role==='vendor'){const guest=s.actors.find(a=>a.workstation===id&&a.task==='browse'&&!a.path.length&&Math.hypot(a.p[0]-(nav.activities.spaces.residents[id]?.position[0]||0),a.p[1]-(nav.activities.spaces.residents[id]?.position[1]||0))<2.6);next=guest?'serve':'tidy';reason=guest?'正在招呼'+PROFILES[guest.id].label:'趁没有客人，看看柜台和餐具';if(guest)r.lookTarget=guest.p.slice();}
   else if(p.role==='listen'&&s.effectiveMusic==='rest'){next='chat';reason='琴声歇了，和身边的人聊几句';}
   else if(p.role==='musician'){next=s.effectiveMusic==='play'?'play':'rest';reason=s.effectiveMusic==='play'?'给树下的人弹一段琴':'歇一会儿，听听街上的声音';}
   else if(s.weather==='snow'){next='snow';reason='雪花落下，停一会看看';}
   if(next&&next!==r.activity)setResidentTask(s,id,next,reason);
   else if(!next&&s.time>=r.until){const candidate=p.routine[Math.floor(stableUnit(id,r.cycle)*p.routine.length)];setResidentTask(s,id,candidate,reason);}
  }
  if(a?.mobile&&a.task==='chat'&&!a.path.length){
   let partner=s.actors.find(b=>b.id===a.chatPartner&&b.task==='chat'&&!b.path.length&&Math.hypot(b.p[0]-a.p[0],b.p[1]-a.p[1])<2.4);
   if(!partner){a.chatPartner=null;partner=s.actors.filter(b=>b!==a&&b.task==='chat'&&!b.path.length&&!b.chatPartner&&Math.hypot(b.p[0]-a.p[0],b.p[1]-a.p[1])<2.0).sort((b,c)=>Math.hypot(b.p[0]-a.p[0],b.p[1]-a.p[1])-Math.hypot(c.p[0]-a.p[0],c.p[1]-a.p[1]))[0];if(partner){a.chatPartner=partner.id;partner.chatPartner=a.id;r.needs.social=.05;s.residents[partner.id].needs.social=.05;const hold=varied(CADENCE.chat,a.id,s.tick);a.wait=partner.wait=Math.max(hold,a.wait,partner.wait);}}
   if(partner){r.needs.social=Math.max(0,r.needs.social-dt*.04);r.activity='chat';a.lookTarget=partner.p.slice();r.reason='和'+PROFILES[partner.id].label+'聊几句';}else{r.activity='rest';r.reason='在街角歇一会儿，等熟人走近';}
  }
  if(a?.mobile&&a.task==='listen'&&s.effectiveMusic==='rest'&&!a.path.length){r.activity='rest';r.reason='琴声暂歇，在树下等一会儿';}
  if(a?.mobile&&s.worldEvent.kind==='festival'&&s.worldEvent.phase==='linger'&&!a.path.length){r.activity=s.time-s.worldEvent.started<3.5?'applaud':a.chatPartner?'chat':'rest';r.reason='花火结束，和身边的人分享刚才看到的景色';}
  if(p.role==='diner'){const d=s.diners[id];r.activity=d.phase==='dine'?'dine':d.phase==='inside'?'inside':'stroll';r.reason=d.phase==='dine'?'坐下来用餐，吃完再走动':d.phase==='inside'?'在暖和的茶间歇一会儿':'推好椅子，经过门帘';}
  let target=p.role==='vendor'&&r.activity==='serve'?r.lookTarget:p.look;
  if(r.activity==='chat'&&p.buddy){const b=s.actors.find(x=>x.id===p.buddy);target=b?.p||nav.activities.spaces.residents[p.buddy]?.position||target;}
  if(r.activity==='lotus')target=[8.2,-1.5,.7];if(r.activity==='fireworks'||r.activity==='applaud')target=FIREWORK_FOCUS.slice();if(r.activity==='listen')target=[-2.47,-1.45,1.2];if(r.activity==='kite')target=[2.35,-.94,3.5];if(r.activity==='signal'||r.activity==='wait')target=[-.6,-6.9,1.4];
  if(r.activity==='follow'){target=s.actors.find(b=>b.id==='resident.kite_child')?.p||target;if(a)a.lookTarget=target.slice();}
  else if(a?.lookTarget)target=a.lookTarget;
  r.lookTarget=target;const origin=s.localWalkers?.[id]?.root||a?.p||nav.activities.spaces.residents[id]?.position||[0,0,0],yaw=s.localWalkers?.[id]?.root?.[3]??a?.yaw??nav.activities.spaces.residents[id]?.yaw??0;const desired=Math.atan2(target[1]-origin[1],target[0]-origin[0])+Math.PI/2-yaw;r.lookYaw=Math.max(-.33,Math.min(.33,Math.atan2(Math.sin(desired),Math.cos(desired))));
  const phase=s.time-r.started;r.gesturePhase=phase;r.gesture=Math.sin(Math.min(1,((phase+stableUnit(id)*9)%varied([6,13],id))/2.8)*Math.PI);
  if(['garden','inspect','lotus','read'].includes(r.activity))r.gesture=Math.sin(Math.min(1,((phase+stableUnit(id)*3)%5.5)/3.5)*Math.PI);
  if(r.activity==='kite')r.gesture=(.5-.5*Math.cos(phase*3.5))*Math.min(1,phase);
  if(r.activity==='chat'){const buddy=a?.chatPartner||p.buddy;if(!buddy)r.gesture=0;else{const turn=(s.time%7)<3.5;if((id<buddy)!==turn)r.gesture*=.12;}}
  const safe=a?.mobile&&!a.atHome?nav.activities.spaces.nodes[a.node]?.umbrellaClear:nav.activities.spaces.residents[id]?.umbrellaClear;const covered=a?.mobile&&!a.atHome?nav.activities.spaces.nodes[a.node]?.covered:nav.activities.spaces.residents[id]?.covered;
  const eligible=p.role==='walker'||['garden','watch'].includes(p.role);const want=eligible&&!s.localWalkers?.[id]&&s.weather==='rain'&&safe&&!covered&&!a?.path?.length&&!['resident.water_visitor','resident.water_companion','resident.kite_child'].includes(id);r.umbrellaOpen+=(Number(want)-r.umbrellaOpen)*Math.min(1,dt*3.5);
 }
}
