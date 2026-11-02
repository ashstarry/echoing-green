import test from 'node:test';
import assert from 'node:assert/strict';
import {makeRequest,parsePlan,contract} from '../server/decision-core.mjs';
import {DOMAINS} from '../runtime/catalog.mjs';
function response(request,choices){return {answers:Object.fromEntries(Object.entries(request.questions).map(([k,q])=>{const choice=choices[k]??(k.startsWith('scope:')?'no':Object.hasOwn(q.criteria,'keep')?'keep':Object.keys(q.criteria)[0]);return[k,{type:'choice',choice,probabilities:Object.fromEntries(Object.keys(q.criteria).map(c=>[c,Number(c===choice)]))}]}))};}
function plan(text,choices){const request=makeRequest(text);return parsePlan(response(request,{intent_status:'change',...choices}),request);}
test('All implemented communal episodes are exposed to language decisions',()=>{assert.deepEqual(Object.keys(contract.fields.occasion.choices).sort(),Object.keys(DOMAINS.occasion.choices).sort());});
test('Poetic supper and dawn remain concrete requests even when mood classification disagrees',()=>{
 for(const [target,action,mood]of[['occasion','supper','together'],['day_phase','dawn','hopeful']]){
  const p=plan('A poetic but concrete wish',{[target]:action,['scope:'+target]:'yes',mood_intent:'mood',atmosphere:mood});
  assert.deepEqual(p.items.map(i=>[i.target,i.action]),[[target,action]]);
 }
});
test('Independent atmosphere can accompany a personal action in one decision without replacing it',()=>{
 const p=plan('照料花草，整个小镇也温柔一些',{'resident.gardener':'water_plants','scope:resident.gardener':'yes',mood_intent:'mixed',atmosphere:'tender'});
 assert(p.items.some(i=>i.target==='resident.gardener'&&i.action==='water_plants'));
 assert(p.items.some(i=>i.target==='occasion'&&i.action==='reunion'));
 assert.equal(p.resolution.source,'jev-composed');
});
test('Mood never adds a conflicting foreground scene or replaces explicit ambient settings',()=>{
 const p=plan('聚餐时温柔一些',{occasion:'supper','scope:occasion':'yes',light:'soft','scope:light':'yes',lighting_coverage:'global',mood_intent:'mixed',atmosphere:'celebration'});
 assert(p.items.some(i=>i.target==='occasion'&&i.action==='supper'));
 assert(!p.items.some(i=>i.target==='festival'));
 assert.equal(p.items.find(i=>i.target==='light').action,'soft');
});
test('An incomplete mixed request is not silently substituted with a mood performance',()=>{
 const p=plan('Unsupported action with a mood',{intent_status:'partial',mood_intent:'mixed',atmosphere:'tender'});
 assert.deepEqual(p.items,[]);assert.equal(p.status,'partial');
});
