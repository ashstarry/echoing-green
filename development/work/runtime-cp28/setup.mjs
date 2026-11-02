import{readFile,writeFile}from'node:fs/promises';
import{createWorld,step,serialize,restore}from'../../app/runtime-cp28/src/simulation.mjs';
import{queueIntent}from'../../app/runtime-cp28/src/life-plans.mjs';
const read=async n=>JSON.parse(await readFile('app/runtime-cp28/public/assets/'+n,'utf8'));
export async function setup(seed=62417){const nav=await read('navigation.json');nav.activities=await read('motion-activities.json');Object.assign(nav.activities,{rail:await read('rail-path.json'),diners:await read('diner-clips.json'),spaces:await read('activity-spaces.json'),localRoutes:await read('local-routes.json'),boarding:await read('boarding-config.json')});return{nav,s:createWorld(nav,seed)};}
export const command=(s,d)=>queueIntent(s,Object.entries(d).map(([target,action])=>({kind:'macro',target,action})));
