import {renderFirework} from './firework-timbre.mjs?v=cp37-paper-0036492e3f36';
import {createCueTracker} from './sound-cues.mjs?v=cp37-paper-0036492e3f36';

const fireworkCache=new WeakMap();
function fireworkBuffer(ctx,cue){
 let cache=fireworkCache.get(ctx);if(!cache){cache=new Map();fireworkCache.set(ctx,cache);}
 const key=cue.type+':'+(cue.variant%3);if(!cache.has(key)){
  const rendered=renderFirework(cue.type,cue.variant,ctx.sampleRate),buffer=ctx.createBuffer(2,rendered.channels[0].length,ctx.sampleRate);
  rendered.channels.forEach((data,i)=>buffer.getChannelData(i).set(data));cache.set(key,buffer);
 }return cache.get(key);
}

// Original soft market bells and spacious fireworks; no changes to the BGM.
// All voices have soft attacks and finite tails; this also works in OfflineAudioContext.
export function scheduleCue(ctx,destination,cue,at=ctx.currentTime){
 const voices=[],nodes=[];
 if(cue.type.startsWith('firework')){
  const source=ctx.createBufferSource(),gain=ctx.createGain();source.buffer=fireworkBuffer(ctx,cue);gain.gain.value=cue.type==='firework_launch'?1.6:1.15;source.connect(gain);gain.connect(destination);source.start(at);source.stop(at+source.buffer.length/ctx.sampleRate+.03);source.onended=()=>{source.disconnect();gain.disconnect();};
  return{voices:[source],stop(){gain.gain.cancelScheduledValues(ctx.currentTime);gain.gain.setTargetAtTime(0,ctx.currentTime,.015);try{source.stop(ctx.currentTime+.08);}catch{}}};
 }
 function envelope(source,volume,delay,duration,attack=.025,filter=null){
  const start=at+delay,gain=ctx.createGain();gain.gain.setValueAtTime(0,start);gain.gain.linearRampToValueAtTime(volume,start+attack);gain.gain.exponentialRampToValueAtTime(.0001,start+duration);gain.gain.linearRampToValueAtTime(0,start+duration+.025);
  if(filter){source.connect(filter);filter.connect(gain);nodes.push(filter);}else source.connect(gain);gain.connect(destination);nodes.push(gain);voices.push(source);source.start(start);source.stop(start+duration+.035);source.onended=()=>{source.disconnect();gain.disconnect();filter?.disconnect();};return source;
 }
 function tone(frequency,volume,delay,duration,type='sine',end=frequency){const o=ctx.createOscillator();o.type=type;o.frequency.setValueAtTime(frequency,at+delay);o.frequency.exponentialRampToValueAtTime(end,at+delay+duration*.85);return envelope(o,volume,delay,duration);}
 if(cue.type==='market_open'){
  tone(523.25,.15,0,.68);tone(1046.5,.025,0,.38);tone(783.99,.115,.22,.82);tone(1567.98,.016,.22,.4);
 }else if(cue.type==='market_close'){
  tone(392,.12,0,.58);tone(784,.018,0,.28);
 }
 return{voices,stop(){for(const o of voices){try{o.stop(ctx.currentTime+.035);}catch{}}for(const n of nodes)if(n.gain){n.gain.cancelScheduledValues(ctx.currentTime);n.gain.setTargetAtTime(0,ctx.currentTime,.008);}}};
}

export function createEventSfx({contextFactory=()=>{const C=window.AudioContext||window.webkitAudioContext;return C?new C({latencyHint:'interactive'}):null;}}={}){
 let ctx=null,master=null,unlocked=false,enabled=false,lastAccent=-Infinity,played=0,lastCue=null;const active=new Set(),tracker=createCueTracker();
 function arm(fromGesture=true){try{if(!ctx||ctx.state==='closed'){active.clear();lastAccent=-Infinity;unlocked=false;ctx=contextFactory();if(!ctx)return;master=ctx.createGain();master.gain.value=.30;const soft=ctx.createBiquadFilter();soft.type='lowpass';soft.frequency.value=3800;soft.Q.value=.5;master.connect(soft);soft.connect(ctx.destination);}if(ctx.state==='running')unlocked=true;else if(fromGesture||unlocked)Promise.resolve(ctx.resume()).then(()=>{unlocked=ctx.state==='running';}).catch(()=>{});}catch{/* BGM and the town remain usable without Web Audio. */}}
 function stop(){for(const group of active)group.stop();active.clear();tracker.rebase();}
 return{
  arm,
  setEnabled(value){if(enabled===value)return;enabled=value;if(!enabled)stop();else if(unlocked&&ctx&&ctx.state!=='running'&&ctx.state!=='closed')Promise.resolve(ctx.resume()).catch(()=>{});},
  stop,
  update(s){
   const audible=enabled&&ctx?.state==='running';const cues=tracker.update(s,audible);
   for(const cue of cues){const time=ctx.currentTime;
    // A launch and its bloom are one phrase. Bell accents never stack into chatter.
    if(cue.type.startsWith('market')&&time-lastAccent<1.8)continue;
    if(active.size>=2)continue;
    const group=scheduleCue(ctx,master,cue,time+.008);active.add(group);let remaining=group.voices.length;
    for(const source of group.voices){const cleanup=source.onended;source.onended=()=>{cleanup?.();if(--remaining===0)active.delete(group);};}
    if(cue.type!=='firework_launch')lastAccent=time;played++;lastCue=cue.type;
   }
  },
  status:()=>({ready:!!ctx&&ctx.state==='running',enabled,played,lastCue,activePhrases:active.size})
 };
}
