// Original synthetic fireworks: breathy ascent, a single pressure burst and a diffuse tail.
// One impact per bloom, not a repeated crackle train. Short, deterministic stereo buffers are cached by the player.
export function renderFirework(type,variant=0,sampleRate=44100){
 const launch=type==='firework_launch',duration=launch?1.02:2.72;
 const n=Math.ceil(duration*sampleRate),left=new Float32Array(n),right=new Float32Array(n),dry=new Float32Array(n);
 let seed=(70517+(variant%3)*9173)>>>0,low=0,mid=0,phase=0,rumblePhase=0;
 const v=1+((variant%3)-1)*.045;
 for(let i=0;i<n;i++){
  const t=i/sampleRate,u=t/duration;seed=(Math.imul(seed,1664525)+1013904223)>>>0;const white=seed/4294967296*2-1;
  low+=.035*(white-low);mid+=.22*(white-mid);
  if(launch){
   const swell=Math.pow(Math.sin(Math.PI*Math.min(1,u)),1.35)*(0.48+.52*u);
   phase+=2*Math.PI*(460+1000*u*u)*v/sampleRate;
   dry[i]=swell*((mid-low)*.67+Math.sin(phase)*.038);
  }else{
   // A single pressure crack, followed by a chesty boom and diffuse fine sparks.
   // The launch branch is byte-for-byte the CP34 timbre the user approved.
   const impactRise=1-Math.exp(-t/.0035),bodyRise=1-Math.exp(-t/.012);
   rumblePhase+=2*Math.PI*(58+82*Math.exp(-t*8))*v/sampleRate;
   const crack=(white-mid)*.64*impactRise*Math.exp(-t/.028)+(mid-low)*1.12*impactRise*Math.exp(-t/.10);
   const rounded=(Math.sin(rumblePhase)*.34+Math.sin(rumblePhase*.503)*.11)*bodyRise*Math.exp(-t/.36);
   const air=low*1.8*(1-Math.exp(-t/.02))*Math.exp(-t/.68);
   const scatter=(mid-low)*(.65+.20*Math.sin(t*79+variant)+.15*Math.sin(t*127+.7))*Math.min(1,t/.10)*Math.exp(-t/.88)*.50;
   dry[i]=Math.tanh((crack+rounded+air+scatter)*1.1)/1.1;
  }
 }
 // A handful of unequal, low-level diffuse reflections creates space without a loud echo.
 const taps=launch?[[.031,.16],[.067,.09]]:[[.061,.24],[.103,.19],[.163,.15],[.239,.11],[.347,.08],[.479,.055]];
 for(let i=0;i<n;i++){
  let l=dry[i],r=dry[i];for(let j=0;j<taps.length;j++){const[d,g]=taps[j],a=i-Math.round(d*sampleRate),b=i-Math.round((d+.013+(j%2)*.009)*sampleRate);if(a>=0)l+=dry[a]*g;if(b>=0)r+=dry[b]*g;}
  const fade=Math.min(1,(n-i)/(sampleRate*.16));left[i]=l*fade*.94;right[i]=r*fade*.94;
 }
 return{sampleRate,duration,channels:[left,right]};
}
