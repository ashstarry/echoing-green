// Visual and audio accents share this simulation clock; never use wall timers.
export const FIREWORK_BURSTS=Object.freeze([1.2,5.0,8.8,12.6,16.4,20.2,24.0,27.8,31.6,35.4,39.2,43.0,46.8,50.6,54.4,58.2]);
export const FIREWORK_FLIGHT=.95;
// Only the larger phrases receive sound. The finale is one accent, not three bangs.
export const AUDIBLE_BURSTS=Object.freeze([0,3,6,9,12]);
