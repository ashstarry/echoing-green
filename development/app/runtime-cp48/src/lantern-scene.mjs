export const LANTERN_STATIONS=[{stand:[-3.04,.88],anchor:[-3.04,1.20,1.38],destination:[-3.8,-.24]},{stand:[1.76,2.64],anchor:[1.76,2.96,1.38],destination:[1.28,-2.0]}];
const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
export const LANTERN_CARRIERS=['quiet_reader','returning_resident','water_visitor','water_companion','customer_one','customer_two','customer_three','market_browser','child_listener','strolling_parent'].map(x=>'resident.'+x);
export const LANTERN_STEP_SECONDS=.85;
export const LANTERN_FADE_SECONDS=1.1;
// A finite, simulation-clock-driven display. The ordinary night stays readable afterwards.
export function lanternDisplay(s,index=0){
 const e=s.sceneEvent;if(e?.kind!=='lantern'||e.phase==='release')return 0;
 const opening=smooth(((e.phase==='closing'?e.phaseAt:s.time)-(e.illuminationAt??e.started)-index*LANTERN_STEP_SECONDS)/LANTERN_FADE_SECONDS);
 const closing=e.phase==='closing'?1-smooth((s.time-e.phaseAt)/7.4):1;
 return opening*closing;
}
export function lanternLightFactor(s,position=[0,0,0]){
 const e=s.sceneEvent;if(e?.kind!=='lantern')return 1;
 const zone=Math.max(0,Math.min(11,Math.round((position[0]+8)*.65))),amount=lanternDisplay(s,zone);
 const clock=s.time-(e.illuminationAt??e.started)-zone*LANTERN_STEP_SECONDS;
 const wave=clock>0?Math.exp(-(((clock-1.2)/1.1)**2)):0;
 return 1+amount*(.38+.10*wave);
}
