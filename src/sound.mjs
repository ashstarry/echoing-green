import {createEventSfx} from './event-sfx.mjs?v=cp33-stability-cf73c211622a';
import {writeText} from './i18n.mjs?v=cp33-stability-cf73c211622a';

// User-approved loop master, played unchanged. Keep the same track across events.
export function createSound(button){
 const effects=createEventSfx();
 let enabled=true,audio=null,worldPaused=false,blocked=false,pending=null,shouldPlay=false;
 try{enabled=localStorage.getItem('echoing-green.sound.v1')!=='off';}catch{}
 function wanted(){return enabled&&!worldPaused&&!document.hidden;}
 function stop(){audio?.pause();effects.setEnabled(false);effects.stop();}
 function start(fromGesture=false){
  if(!wanted())return;
  if(fromGesture)blocked=false;
  effects.arm(fromGesture);
  effects.setEnabled(true);
  if(blocked||pending)return;
  if(!audio){audio=new window.Audio(new URL('../assets/lanterns-awake-loop.wav',import.meta.url).href);audio.loop=true;audio.preload='auto';audio.playbackRate=1;}
  if(!audio.paused)return;
  try{pending=Promise.resolve(audio.play()).then(()=>{blocked=false;if(!wanted())stop();}).catch(error=>{blocked=error?.name==='NotAllowedError';}).finally(()=>{pending=null;});}catch(error){blocked=error?.name==='NotAllowedError';}
 }
 function show(){writeText(button,enabled?'声音开':'声音关');button.setAttribute('aria-pressed',String(enabled));}
 button.onclick=()=>{enabled=!enabled;try{localStorage.setItem('echoing-green.sound.v1',enabled?'on':'off');}catch{}show();shouldPlay=wanted();if(shouldPlay)start(true);else stop();};
 function unlock(event){if(event.target?.closest?.('#sound'))return;if(wanted())start(true);}
 document.addEventListener('pointerdown',unlock,{passive:true});document.addEventListener('keydown',unlock);
 document.addEventListener('visibilitychange',()=>{shouldPlay=wanted();if(shouldPlay)start();else stop();});
 show();shouldPlay=wanted();if(shouldPlay)start();
 return{
  sync(s){worldPaused=!!s.paused;const next=wanted();if(next!==shouldPlay){shouldPlay=next;if(next)start();else stop();}},
  update(s){effects.update(s);},
  muteNow(){shouldPlay=false;stop();},
  status:()=>({enabled,state:!audio?'not_started':blocked?'awaiting_gesture':audio.paused?'paused':'playing',title:'灯火未眠',loop:true,playbackRate:1,currentTime:audio?.currentTime||0,theme:'lanterns-awake-game-loop',bgmIndependentOfGuitar:true,eventSounds:effects.status()})
 };
}
