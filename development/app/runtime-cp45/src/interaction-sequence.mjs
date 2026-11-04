// Generic finite action recipes. Travel, pose and object transfers are adapters;
// this executor knows neither the town scene name nor any particular paper mesh.
export const INTERACTION_PRIMITIVES=Object.freeze({
 approach:{kind:'move'},take:{kind:'pose',seconds:1.2},write:{kind:'pose',seconds:4.8},fold:{kind:'pose',seconds:2.1},hang:{kind:'pose',seconds:2.7},offer:{kind:'pose',seconds:3},read:{kind:'pose',seconds:3.2},collect:{kind:'pose',seconds:1.6},stow:{kind:'pose',seconds:1.6},receive:{kind:'pose',seconds:3.2},carry:{kind:'move'},place:{kind:'pose',seconds:2.4},wipe:{kind:'pose',seconds:4.4},open:{kind:'pose',seconds:1.7},welcome:{kind:'pose',seconds:4.2},wait_for:{kind:'pose',seconds:.2},unfold:{kind:'pose',seconds:3.2},admire:{kind:'pose',seconds:3.6},pack:{kind:'pose',seconds:2.5},pour:{kind:'pose',seconds:3.4},sip:{kind:'pose',seconds:4.5},taste:{kind:'pose',seconds:4.5},sweep:{kind:'pose',seconds:6},dry:{kind:'pose',seconds:1.4},pair_walk:{kind:'move'},close:{kind:'pose',seconds:2.1}
});
export const INTERACTION_RECIPES=Object.freeze({
 snack_host:[{action:'open'},{action:'take'},{action:'offer',waitFor:'recipient'},{action:'wipe'},{action:'close'}],
 snack_guest:[{action:'approach',target:'destination'},{action:'receive',waitFor:'received'},{action:'taste'},{action:'place'},{action:'welcome'}],
 tea_host:[{action:'open'},{action:'pour'},{action:'take'},{action:'offer',waitFor:'recipient'},{action:'wipe'},{action:'close'}],
 tea_guest:[{action:'approach',target:'destination'},{action:'receive',waitFor:'received'},{action:'sip'},{action:'place'},{action:'welcome'}],
 umbrella_lender:[{action:'approach',target:'supply'},{action:'take'},{action:'offer',waitFor:'recipient'},{action:'pair_walk',target:'destination'},{action:'receive',waitFor:'returned'},{action:'fold'},{action:'stow'}],
 umbrella_borrower:[{action:'approach',target:'supply'},{action:'receive',waitFor:'received'},{action:'unfold'},{action:'pair_walk',target:'destination'},{action:'close'},{action:'offer',waitFor:'lender'},{action:'welcome'}],
 sweep_leaves:[{action:'approach',target:'destination'},{action:'take'},{action:'sweep',when:'leaves_spread'},{action:'collect'},{action:'stow'},{action:'admire'}],
 keep_memory:[{action:'approach',target:'supply'},{action:'take'},{action:'read'},{action:'carry',target:'destination'},{action:'collect',when:'occupied'},{action:'stow',when:'occupied'},{action:'place'},{action:'read'}],
 read_memory:[{action:'approach',target:'destination'},{action:'take'},{action:'read'},{action:'place'}],
 putaway_memory:[{action:'approach',target:'destination'},{action:'take'},{action:'read'},{action:'fold'},{action:'stow'}],
 laundry_batch:[{action:'approach',target:'supply',propIndex:0},{action:'take',propIndex:0},{action:'unfold',propIndex:0},{action:'carry',target:'destination',propIndex:0},{action:'hang',propIndex:0},{action:'approach',target:'supply',propIndex:1},{action:'take',propIndex:1},{action:'unfold',propIndex:1},{action:'carry',target:'destination',propIndex:1},{action:'hang',propIndex:1},{action:'dry',propIndex:1},{action:'collect',propIndex:1},{action:'fold',propIndex:1},{action:'carry',target:'supply',propIndex:1},{action:'stow',propIndex:1},{action:'approach',target:'destination',propIndex:0},{action:'collect',propIndex:0},{action:'fold',propIndex:0},{action:'carry',target:'supply',propIndex:0},{action:'stow',propIndex:0}],
 collect_laundry_batch:[{action:'approach',target:'destination',propIndex:0},{action:'collect',propIndex:0},{action:'fold',propIndex:0},{action:'carry',target:'supply',propIndex:0},{action:'stow',propIndex:0},{action:'approach',target:'destination',propIndex:1,when:'has_second'},{action:'collect',propIndex:1,when:'has_second'},{action:'fold',propIndex:1,when:'has_second'},{action:'carry',target:'supply',propIndex:1,when:'has_second'},{action:'stow',propIndex:1,when:'has_second'}],
 give_parcel:[{action:'approach',target:'destination'},{action:'offer',waitFor:'recipient'},{action:'welcome'}],
 receive_parcel:[{action:'approach',target:'destination'},{action:'receive',waitFor:'received'},{action:'read'},{action:'carry',target:'supply'},{action:'place'},{action:'welcome'}],
 receive_prop:[{action:'approach',target:'destination'},{action:'receive',waitFor:'received'},{action:'place'},{action:'admire'}],
 home_host:[{action:'approach',target:'destination'},{action:'open'},{action:'wait_for',waitFor:'partner'},{action:'welcome'},{action:'offer'},{action:'admire'}],
 home_arrive:[{action:'approach',target:'supply'},{action:'wait_for',waitFor:'door'},{action:'approach',target:'destination'},{action:'welcome'},{action:'receive'},{action:'admire'}],
 carry_place:[{action:'approach',target:'supply'},{action:'take'},{action:'carry',target:'destination'},{action:'place'},{action:'admire'}],
 carry_give:[{action:'approach',target:'supply'},{action:'take'},{action:'carry',target:'destination'},{action:'offer',waitFor:'recipient'},{action:'admire'}],
 wipe_surface:[{action:'approach',target:'destination'},{action:'take'},{action:'wipe'},{action:'stow'},{action:'admire'}],
 wipe_place:[{action:'approach',target:'destination'},{action:'take'},{action:'wipe'},{action:'stow'},{action:'unfold'},{action:'admire'}],
 plant_flower:[{action:'approach',target:'supply'},{action:'take'},{action:'carry',target:'destination'},{action:'place'},{action:'unfold'},{action:'admire'}],
 hang_note:[{action:'approach',target:'writing'},{action:'take'},{action:'write'},{action:'fold'},{action:'approach',target:'destination'},{action:'collect',when:'occupied'},{action:'stow',when:'occupied'},{action:'hang'},{action:'read'}],
 share_note:[{action:'approach',target:'writing'},{action:'take'},{action:'write'},{action:'fold'},{action:'approach',target:'destination'},{action:'offer',waitFor:'recipient'},{action:'read'}],
 read_note:[{action:'approach',target:'destination'},{action:'read'}],
 collect_note:[{action:'approach',target:'destination'},{action:'collect'},{action:'read'},{action:'fold'},{action:'stow'}],
 receive_note:[{action:'approach',target:'destination'},{action:'receive',waitFor:'received'},{action:'read'},{action:'fold'},{action:'stow'}]
});
export function createInteraction({id,recipe,actor,prop,context={}}){if(!INTERACTION_RECIPES[recipe])throw Error('Unknown interaction recipe');return{id,recipe,actor,prop,context,step:0,clock:0,status:'running',entered:false,history:[]};}
export function interactionStep(job){return job?.status==='running'?INTERACTION_RECIPES[job.recipe]?.[job.step]:null;}
export function advanceInteraction(job,dt,adapter){
 if(job.status!=='running')return;const step=interactionStep(job);if(!step){job.status='done';adapter.finish?.(job);return;}
 if(step.when&&!adapter.condition(step.when,job)){job.step++;job.entered=false;job.clock=0;return;}
 const primitive=INTERACTION_PRIMITIVES[step.action];if(!job.entered){job.entered=true;adapter.enter?.(step,job);}
 if(primitive.kind==='move'){adapter.move(step.target,job);if(!adapter.arrived(step.target,job))return;}
 else{if(step.waitFor&&!adapter.condition(step.waitFor,job))return;const duration=step.seconds??primitive.seconds;job.clock=Math.min(duration,job.clock+dt);if(job.clock<duration)return;}
 adapter.commit?.(step,job);job.history.push(step.action);job.step++;job.clock=0;job.entered=false;
 if(job.step>=INTERACTION_RECIPES[job.recipe].length){job.status='done';adapter.finish?.(job);}
}
