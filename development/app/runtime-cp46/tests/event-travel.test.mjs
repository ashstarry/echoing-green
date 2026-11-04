import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createWorld,step,serialize,restore} from '../src/simulation.mjs';
import {queueIntent} from '../src/life-plans.mjs';
import {objectCatalog} from '../src/object-actions.mjs';
const read=n=>JSON.parse(readFileSync(new URL('../public/assets/'+n+'.json',import.meta.url)));
function setup(){const nav=read('navigation');nav.activities=read('motion-activities');for(const[k,n]of Object.entries({rail:'rail-path',diners:'diner-clips',spaces:'activity-spaces',localRoutes:'local-routes',boarding:'boarding-config',eventTrips:'event-trips',seatedRigs:'seated-rigs'}))nav.activities[k]=read(n);nav.activities.objectCatalog=objectCatalog(read('runtime-registry'));return{nav,s:createWorld(nav)};}
const run=(s,nav,t)=>{for(let i=0;i<t*20;i++)step(s,nav);};
const wish=(s,target,action)=>queueIntent(s,[{kind:'macro',target,action}]);
test('A bicycle that has not reached its stop cannot indefinitely hold distant residents at home',()=>{
 const{s,nav}=setup();run(s,nav,10);wish(s,'occasion','market');let leftBridge=false;
 for(let i=0;i<500;i++){const bike=s.movers['bicycle.street_bicycle'];bike.tripState='ride';bike.stopWait=0;step(s,nav);leftBridge ||=s.eventGuests['resident.water_companion'].phase==='entry_out';}
 assert(leftBridge);
});
test('Far residents really leave, attend the market and return to their former places',()=>{
 const{s,nav}=setup();run(s,nav,10);wish(s,'occasion','market');const ids=['resident.quiet_reader','resident.water_visitor','resident.water_companion'];const reached=new Set(),distance={};let peak=0;
 for(let i=0;i<4800;i++){const before=Object.fromEntries(ids.map(id=>[id,s.eventGuests[id].p.slice()]));step(s,nav);for(const id of ids){const g=s.eventGuests[id],home=nav.activities.eventTrips[id].home;distance[id]=Math.max(distance[id]||0,Math.hypot(g.p[0]-home[0],g.p[1]-home[1]));if(g.phase==='hold')reached.add(id);assert(Math.hypot(g.p[0]-before[id][0],g.p[1]-before[id][1])<.18,'continuous walking: '+id+' '+s.time+' '+g.phase);}const e=s.sceneEvent;if(e)peak=Math.max(peak,s.actors.filter(a=>a.node===e.slots[a.id]&&a.reservation===a.node&&!a.path.length).length);}
 assert.equal(reached.size,3);assert(peak>=13);for(const id of ids){assert(distance[id]>4);assert.equal(s.eventGuests[id].active,false);}assert.equal(s.sceneEvent,null);
});
test('Saving during a stair/bridge journey preserves the next footsteps and eventual return',()=>{
 const{s,nav}=setup();run(s,nav,10);wish(s,'festival','fireworks');run(s,nav,38);assert(Object.values(s.eventGuests).some(g=>g.active));const copy=restore(serialize(s),nav);run(s,nav,6);run(copy,nav,6);assert.deepEqual(copy,s);
 wish(s,'weather','snow');run(s,nav,260);if(Object.values(s.eventGuests).some(g=>g.active))writeFileSync(new URL('../../../work/runtime-cp30/interrupted-state.json',import.meta.url),JSON.stringify(s));assert(Object.values(s.eventGuests).every(g=>!g.active));assert.equal(s.sceneEvent,null);assert.equal(s.weather,'clear');
});
test('The published CP29 town save migrates without resetting time or resident positions',async()=>{
 const old=await import('../../runtime-cp29/src/simulation.mjs');
 const oldRead=n=>JSON.parse(readFileSync(new URL('../../runtime-cp29/public/assets/'+n+'.json',import.meta.url)));
 const oldNav=oldRead('navigation');oldNav.activities=oldRead('motion-activities');for(const[k,n]of Object.entries({rail:'rail-path',diners:'diner-clips',spaces:'activity-spaces',localRoutes:'local-routes',boarding:'boarding-config'}))oldNav.activities[k]=oldRead(n);
 const prior=old.createWorld(oldNav);for(let i=0;i<200;i++)old.step(prior,oldNav);const{nav}=setup();const resumed=restore(old.serialize(prior),nav);assert.equal(resumed.time,prior.time);for(const a of prior.actors)assert.deepEqual(resumed.actors.find(b=>b.id===a.id).p,a.p);assert.equal(Object.keys(resumed.eventGuests).length,12);run(resumed,nav,5);assert(resumed.time>prior.time);
});
