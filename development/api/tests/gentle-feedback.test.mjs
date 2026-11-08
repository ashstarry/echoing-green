import test from 'node:test';
import assert from 'node:assert/strict';
import {makeRequest,parsePlan,contract} from '../server/decision-core.mjs';
function response(request,choices){return {answers:Object.fromEntries(Object.entries(request.questions).map(([k,q])=>{const choice=choices[k]??(k.startsWith('scope:')?'no':Object.hasOwn(q.criteria,'keep')?'keep':Object.keys(q.criteria)[0]);return[k,{type:'choice',choice,probabilities:Object.fromEntries(Object.keys(q.criteria).map(c=>[c,Number(c===choice)]))}]}))};}
function plan(text,choices){const request=makeRequest(text);return parsePlan(response(request,{intent_status:'change',...choices}),request);}
test('Unsupported construction is acknowledged without a substitute town celebration',()=>{
 for(const reply of ['celebrate','reunion','market']){
  const p=plan('Build a new tower above the town',{intent_status:'unsupported',mood_intent:'literal',atmosphere:'celebration',gentle_reply:reply});
  assert.deepEqual(p.items.map(i=>[i.target,i.action]),[['resident.vendor_flower','greet']]);
  assert.match(p.summary,/暂时做不到/);
 }
});
test('A hand-to-hand expression of gratitude uses the existing two-person note exchange',()=>{
 const p=plan('Pass a little appreciation to another person',{mood_intent:'literal',atmosphere:'gratitude',gentle_reply:'share'});
 assert.deepEqual(p.items.map(i=>[i.target,i.action]),[['paper','share']]);
});
test('An emotionally meaningful metaphor can still be interpreted when its literal imagery is unsupported',()=>{
 const p=plan('Let my tangled thoughts find somewhere to rest',{intent_status:'unsupported',mood_intent:'mood',atmosphere:'quiet',gentle_reply:'quiet'});
 assert(p.items.some(i=>i.target==='occasion'&&i.action==='quiet'));
});
test('Local wishes protect people described as 别人、旁人 or the others carrying on',()=>{
 for(const text of ['只有狐狸想找个朋友，别人照常就好。','小狐狸有点孤单，旁人不用回应。','The little fox seems lonely; let the others carry on.']){
  for(const intent of ['mood','literal']){
   const p=plan(text,{mood_intent:intent,atmosphere:'together',gentle_reply:'fox'});
   assert.deepEqual(p.items.map(i=>[i.target,i.action]),[['animal.garden_fox','greet']]);
   assert.equal(p.resolution.scopeGuard,'explicit-others-unchanged');
  }
 }
});
