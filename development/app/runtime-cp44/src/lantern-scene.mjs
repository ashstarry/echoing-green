const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
export const LANTERN_CARRIERS=['quiet_reader','returning_resident','water_visitor','water_companion','customer_one','customer_two','customer_three','market_browser','child_listener','strolling_parent'].map(x=>'resident.'+x);
// A finite, simulation-clock-driven display. The ordinary night stays readable afterwards.
export function lanternDisplay(s,index=0){
 const e=s.sceneEvent;if(e?.kind!=='lantern'||e.phase==='release')return 0;
 const opening=smooth((s.time-e.started-index*.26)/1.8);
 const closing=e.phase==='closing'?1-smooth((s.time-e.phaseAt)/7.4):1;
 return opening*closing;
}
export function lanternLightFactor(s,position=[0,0,0]){
 const e=s.sceneEvent;if(e?.kind!=='lantern')return 1;
 const zone=Math.max(0,Math.min(7,(position[0]+8)*.45)),amount=lanternDisplay(s,zone);
 const clock=s.time-(e.illuminationAt??e.started)-zone*.35;
 const wave=clock>0?Math.exp(-(((clock-1.2)/1.1)**2)):0;
 return 1+amount*(.22+.16*wave);
}
