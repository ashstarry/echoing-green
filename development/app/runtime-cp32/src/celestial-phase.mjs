const clamp=x=>Math.max(0,Math.min(1,x));
export function celestialVisibility(weights){
 const daylight=clamp((weights.day||0)+.85*(weights.dawn||0));
 // A brief handover gap prevents the crescent showing through the paper sun.
 return {sun:clamp((daylight-.52)/.32),moon:clamp((.48-daylight)/.32),stars:Math.max(.08,1-daylight)};
}
