import test from 'node:test';
import assert from 'node:assert/strict';
import {makeRequest,parsePlan,contract} from '../decision-api.mjs';
import {DOMAINS} from '../src/catalog.mjs';
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

import {t,setLocale} from '../src/i18n.mjs';
test('Every semantic choice shown in a receipt has an English translation',()=>{setLocale('en');const values=[...new Set(Object.values(contract.fields).flatMap(d=>[d.label,...Object.values(d.choices)]))];assert.deepEqual(values.filter(s=>/[\u3400-\u9fff]/u.test(t(s))),[]);setLocale('zh');});

test('A highly confident existing neighborhood workflow survives a conflicting scope answer; no-change still wins',()=>{const p=plan('雨停了，日子重新开始吧。',{neighborhood:'reopen','scope:neighborhood':'no',mood_intent:'mood',atmosphere:'hopeful'});assert.deepEqual(p.items.map(x=>[x.target,x.action]),[['neighborhood','reopen']]);assert.equal(p.items[0].resolution,'bounded-neighborhood-confidence-v1');const kept=plan('只是设想，不要改变',{intent_status:'no_change',neighborhood:'reopen','scope:neighborhood':'no',mood_intent:'no_change',atmosphere:'keep'});assert.deepEqual(kept.items,[]);});

test('A global rest request corroborated by the mood question is not erased by a contradictory scope',()=>{const p=plan('安静一点，别放烟花，也别下雨。',{weather:'clear','scope:weather':'yes',occasion:'quiet','scope:occasion':'no',mood_intent:'literal',atmosphere:'quiet'});assert(p.items.some(i=>i.target==='occasion'&&i.action==='quiet'));assert(p.items.some(i=>i.target==='weather'&&i.action==='clear'));assert(!p.items.some(i=>i.target==='festival'&&i.action==='fireworks'));});
test('Explicitly leaving other residents alone prevents inferred atmosphere from escaping a local request',()=>{const p=plan('只有风车慢下来，其他人不用理我。',{'object.windmill':'slow','scope:object.windmill':'group',mood_intent:'mixed',atmosphere:'quiet'});assert(p.items.length>0);assert(p.items.every(i=>i.kind==='object'));assert.equal(p.resolution.scopeGuard,'explicit-others-unchanged');const mixed=plan('风车慢下来，整个小镇也温柔一些',{'object.windmill':'slow','scope:object.windmill':'group',mood_intent:'mixed',atmosphere:'tender'});assert(mixed.items.some(i=>i.kind==='object'));assert(mixed.items.some(i=>i.target==='occasion'&&i.action==='reunion'));});
test('A negative weather constraint can coexist with an independently requested quiet mood',()=>{const p=plan('不下雨，想安静一下',{weather:'clear','scope:weather':'yes',mood_intent:'mixed',atmosphere:'quiet'});assert(p.items.some(i=>i.target==='weather'&&i.action==='clear'));assert(p.items.some(i=>i.target==='occasion'&&i.action==='quiet'));});

test('Tram welcomes and sendoffs remain one local journey instead of duplicating a house or town gathering',()=>{const p=plan('让列车上的这一程有温暖的告别和归来',{journey:'welcome','scope:journey':'yes',neighborhood:'homecoming','scope:neighborhood':'yes',occasion:'reunion','scope:occasion':'yes','resident.station_traveler':'ride_once','scope:resident.station_traveler':'yes',mood_intent:'mixed',atmosphere:'tender'});assert(p.items.some(i=>i.target==='journey'));assert(!p.items.some(i=>['neighborhood','occasion','resident.station_traveler'].includes(i.target)));});

test('A fox greeting is local unless the user actually asks the whole town to gather',()=>{const choices={'object.fox':'greet','scope:object.fox':'group',occasion:'reunion','scope:occasion':'yes',mood_intent:'literal',atmosphere:'together'};const p=plan('让狐狸认识身边的街坊',choices);assert.deepEqual(p.items.map(i=>i.target),['animal.garden_fox']);const all=plan('让狐狸认识街坊，大家都来相聚',choices);assert(all.items.some(i=>i.target==='occasion'));});
test('Stopping new trips does not stop the train against an explicit negative instruction',()=>{const p=plan('暂停新的行程，不要停整列电车',{journey:'rest','scope:journey':'no',train:'hold','scope:train':'yes',mood_intent:'literal',atmosphere:'keep'});assert(p.items.some(i=>i.target==='journey'&&i.action==='rest'));assert(!p.items.some(i=>i.target==='train'&&i.action==='hold'));const later=plan('不要停整列电车，还是让电车到站等一会',{train:'hold','scope:train':'yes',mood_intent:'literal',atmosphere:'keep'});assert(later.items.some(i=>i.target==='train'&&i.action==='hold'));});

test('A fox can greet without commanding its neighbor when others are explicitly left alone',()=>{const p=plan('小狐狸去打个招呼，其他人不用理它。',{'object.fox':'greet','scope:object.fox':'group',mood_intent:'mixed',atmosphere:'tender'});assert.equal(p.resolution.scopeGuard,'explicit-others-unchanged');assert.deepEqual(p.items.map(i=>i.target),['animal.garden_fox']);});
