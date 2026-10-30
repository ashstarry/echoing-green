import {FIREWORK_BURSTS,FIREWORK_FLIGHT,AUDIBLE_BURSTS} from './firework-score.mjs?v=cp35-lantern-f3a6f95a814b';

// Event edges only: no footsteps, continuous crowd noise or sound per resident.
export function createCueTracker(){
 let previous=null;const seen=new Set();
 function remember(key){seen.add(key);if(seen.size>160)seen.delete(seen.values().next().value);}
 return{rebase(){previous=null;},update(s,audible=true){
  const e=s.sceneEvent,now={time:s.time,event:e?.id,phase:e?.phase,festival:s.festivalStarted},cues=[];
  const continuous=previous&&s.time>=previous.time&&s.time-previous.time<.75;
  const emit=(key,type,variant=0)=>{if(seen.has(key))return;remember(key);if(audible&&continuous)cues.push({type,variant,key});};
  if(e&&['market','supper'].includes(e.kind)){
   if(['gather','active'].includes(e.phase)&&(previous?.event!==e.id||!previous))emit(e.id+':open','market_open',e.kind==='supper'?1:0);
   if(e.phase==='closing'&&(previous?.event!==e.id||previous?.phase!=='closing'))emit(e.id+':close','market_close');
  }
  if(s.festivalUntil>s.time){
   const start=s.festivalStarted,stop=s.festivalStop??Infinity;
   for(const i of AUDIBLE_BURSTS){const burst=start+FIREWORK_BURSTS[i],launch=burst-FIREWORK_FLIGHT;if(launch>stop)continue;
    for(const [at,type]of [[launch,'firework_launch'],[burst,'firework_bloom']]){
     // Consume old accents silently on reload/resume; never play a backlog.
     if(at<=s.time&&(previous?.festival!==start||!previous||at>previous.time))emit('firework:'+start+':'+i+':'+type,type,i);
    }
   }
  }
  previous=now;return cues;
 }};
}
