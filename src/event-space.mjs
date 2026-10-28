const festivalPlaces={
 customer_one:[.2,-3.8],customer_two:[2.0,-3.6],customer_three:[3.5,-2.6],market_browser:[.6,-4.7],
 courier:[2.0,-1.7],postman:[-.9,-3.8],strolling_parent:[-3.7,-2.0],garden_child:[4.0,-.5],
 child_runner:[1.1,-2.2],child_parent:[3.1,-2.8],kite_child:[3.4,-1.15]
};
const shelterPlaces={
 customer_one:[-3.68,2.8],customer_two:[-2.24,3.9],customer_three:[-1.4,2.0],market_browser:[-4.7,1.6],
 courier:[-5.1,-2.1],postman:[-4.4,.5],strolling_parent:[-3.9,-3.0],garden_child:[4.1,1.2],
 child_runner:[1.4,2.4],child_parent:[3.8,1.5],kite_child:[3.65,.5]
};
export function eventCenter(id,task,fallback){const name=id.slice(9);return (task==='fireworks'?festivalPlaces[name]:task==='shelter'?shelterPlaces[name]:null)||fallback;}
export function eventScore(task,candidate,space,id){
 if(task!=='shelter')return 0;
 // Only the two nearest shop-side guests compete for the two separated roof slots.
 // Others use spacious umbrella sites instead of jamming the same narrow eave.
 const seekRoof=['resident.customer_one','resident.customer_two'].includes(id);
 return space.covered?(seekRoof?-8:2):0;
}
