// Original synthetic fireworks: breathy ascent, rounded bloom and a diffuse tail.
// No sharp crackle train. Short, deterministic stereo buffers are cached by the player.
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
   // The bloom grows over ~100ms; removing the impulsive edge avoids a paper slap.
   const attack=1-Math.exp(-t/.055),body=attack*Math.exp(-t/ .40),air=attack*Math.exp(-t/.74);
   rumblePhase+=2*Math.PI*(57+40*Math.exp(-t*5))*v/sampleRate;
   const rounded=Math.sin(rumblePhase)*.30+Math.sin(rumblePhase*.503)*.14;
   const shimmer=(mid-low)*(.7+.3*Math.sin(t*19+variant))*Math.min(1,t/.19)*Math.exp(-t/.95);
   dry[i]=rounded*body+low*2.5*air+shimmer*.30;
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
