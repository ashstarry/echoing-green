// Generic finite action recipes. Travel, pose and object transfers are adapters;
// this executor knows neither the town scene name nor any particular paper mesh.
export const INTERACTION_PRIMITIVES=Object.freeze({
 approach:{kind:'move'},take:{kind:'pose',seconds:1.2},write:{kind:'pose',seconds:4.8},fold:{kind:'pose',seconds:2.1},hang:{kind:'pose',seconds:2.7},offer:{kind:'pose',seconds:3},read:{kind:'pose',seconds:3.2},collect:{kind:'pose',seconds:1.6},stow:{kind:'pose',seconds:1.6},receive:{kind:'pose',seconds:3.2}
});
export const INTERACTION_RECIPES=Object.freeze({
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
