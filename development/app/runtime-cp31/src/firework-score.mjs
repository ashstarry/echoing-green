// Visual and audio accents share this simulation clock; never use wall timers.
export const FIREWORK_BURSTS=Object.freeze([1.2,2.9,5.3,6.8,9.2,11.0,13.0,15.4,17.0,17.4,18.1]);
export const FIREWORK_FLIGHT=.95;
// Only the larger phrases receive sound. The finale is one accent, not three bangs.
export const AUDIBLE_BURSTS=Object.freeze([0,2,4,6,8]);
