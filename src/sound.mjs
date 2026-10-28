import {writeText,t,initializeI18n} from './i18n.mjs?v=cp28-1336fccff9e2';
import {scoreStep,musicMood,MUSIC_TITLES,STEP_SECONDS} from './chiptune-score.mjs?v=cp28-1336fccff9e2';
const waves=new WeakMap();
export function scheduleTone(context,destination,note,time){const osc=context.createOscillator(),env=context.createGain(),length=note.beats*STEP_SECONDS;
 if(note.voice==='lead'){let wave=waves.get(context);if(!wave){const real=new Float32Array(8),imag=new Float32Array(8);imag[1]=1;imag[3]=.12;imag[5]=.035;imag[7]=.012;wave=context.createPeriodicWave(real,imag);waves.set(context,wave);}osc.setPeriodicWave(wave);}else osc.type='triangle';
 osc.frequency.setValueAtTime(440*2**((note.midi-69)/12),time);if(note.voice==='drum')osc.frequency.exponentialRampToValueAtTime(48,time+length);
 const attack=Math.min(.085,length*.18);env.gain.setValueAtTime(.0001,time);env.gain.linearRampToValueAtTime(note.gain,time+attack);env.gain.linearRampToValueAtTime(note.gain*.68,time+length*.60);env.gain.exponentialRampToValueAtTime(.0001,time+length+.10);osc.connect(env);env.connect(destination);osc.start(time);osc.stop(time+length+.12);osc.onended=()=>{osc.disconnect();env.disconnect();};return osc;
}
// Music defaults on; browsers may wait for a trusted gesture before playing.
// Two arrangement buses crossfade over 3.2 seconds.
export function createSound(button){
 let context=null,enabled=true,master,nextAt=0,active=false,mood='town',scheduled=0,current=null,transitionCount=0;
 try{enabled=localStorage.getItem('echoing-green.sound.v1')!=='off';}catch{}
 const voices=new Set(),buses=[];
 function initialize(){const Audio=window.AudioContext||window.webkitAudioContext;if(!Audio)return false;context=new Audio();master=context.createGain();master.gain.value=0;master.connect(context.destination);return true;}
 function change(next){const now=context.currentTime;if(current){current.gain.gain.cancelScheduledValues(now);current.gain.gain.setValueAtTime(current.gain.gain.value,now);current.gain.gain.linearRampToValueAtTime(0,now+3.2);current.end=now+3.35;transitionCount++;}
  const gain=context.createGain(),filter=context.createBiquadFilter();gain.gain.value=0;gain.gain.linearRampToValueAtTime(1,now+3.2);filter.type='lowpass';filter.frequency.value=next==='rain'||next==='night'?1450:1900;filter.Q.value=.25;filter.connect(gain);gain.connect(master);current={gain,filter,mood:next,index:0,end:Infinity};buses.push(current);mood=next;
 }
 function showPreference(){writeText(button,enabled?'声音开':'声音关');button.setAttribute('aria-pressed',String(enabled));}
 function resume(){if(!enabled)return;if(!context&&!initialize())return;try{Promise.resolve(context.resume()).then(()=>{nextAt=context.currentTime+.04;}).catch(()=>{});}catch{}}
 button.onclick=()=>{enabled=!enabled;try{localStorage.setItem('echoing-green.sound.v1',enabled?'on':'off');}catch{}showPreference();if(enabled)resume();else{active=false;if(master)master.gain.setTargetAtTime(0,context.currentTime,.04);}};
 function unlock(event){if(event.target?.closest?.('#sound'))return;if(enabled&&context?.state!=='running')resume();}
 document.addEventListener('pointerdown',unlock,{passive:true});document.addEventListener('keydown',unlock);
 showPreference();resume();
 function play(bus,note,time){const osc=scheduleTone(context,bus.filter,note,time);voices.add(osc);scheduled++;osc.addEventListener('ended',()=>voices.delete(osc));}
 return{sync(s){if(!context)return;const audible=enabled&&context.state==='running'&&!s.paused&&!document.hidden;if(audible&&!active)nextAt=context.currentTime+.04;active=audible;const next=musicMood(s);if(active&&(!current||next!==mood))change(next);master.gain.setTargetAtTime(active?.42:0,context.currentTime,.20);},
 update(){if(!context||!active)return;const now=context.currentTime;for(let i=buses.length-1;i>=0;i--)if(now>buses[i].end){buses[i].filter.disconnect();buses[i].gain.disconnect();buses.splice(i,1);}if(nextAt<now-.25)nextAt=now+.02;while(nextAt<now+.12){for(const bus of buses)if(nextAt<bus.end)for(const note of scoreStep(bus.index++,bus.mood))play(bus,note,nextAt);nextAt+=STEP_SECONDS;}},
 muteNow(){active=false;if(master)master.gain.setTargetAtTime(0,context.currentTime,.04);},status:()=>({enabled,state:context?.state||'not_started',mood,title:MUSIC_TITLES[mood],scheduled,activeVoices:voices.size,arrangements:buses.length,transitionCount,crossfadeSeconds:3.2,theme:'six-original-soft-handheld-pieces',bgmIndependentOfGuitar:true})};
}
