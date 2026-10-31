// Generic finite action recipes. Travel, pose and object transfers are adapters;
// this executor knows neither the town scene name nor any particular paper mesh.
export const INTERACTION_PRIMITIVES=Object.freeze({
 approach:{kind:'move'},take:{kind:'pose',seconds:1.2},write:{kind:'pose',seconds:4.8},fold:{kind:'pose',seconds:2.1},hang:{kind:'pose',seconds:2.7},offer:{kind:'pose',seconds:3},read:{kind:'pose',seconds:3.2},collect:{kind:'pose',seconds:1.6},stow:{kind:'pose',seconds:1.6},receive:{kind:'pose',seconds:3.2},carry:{kind:'move'},place:{kind:'pose',seconds:2.4},wipe:{kind:'pose',seconds:4.4},open:{kind:'pose',seconds:1.7},welcome:{kind:'pose',seconds:4.2},wait_for:{kind:'pose',seconds:.2},unfold:{kind:'pose',seconds:3.2},admire:{kind:'pose',seconds:3.6},pack:{kind:'pose',seconds:2.5}
});
export const INTERACTION_RECIPES=Object.freeze({
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
 else{if(step.waitFor&&!adapter.condition(step.waitFor,job))return;job.clock=Math.min(primitive.seconds,job.clock+dt);if(job.clock<primitive.seconds)return;}
 adapter.commit?.(step,job);job.history.push(step.action);job.step++;job.clock=0;job.entered=false;
 if(job.step>=INTERACTION_RECIPES[job.recipe].length){job.status='done';adapter.finish?.(job);}
}
