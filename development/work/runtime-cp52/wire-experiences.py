# -*- coding: utf-8 -*-
from pathlib import Path
import json
base=Path('app/runtime-cp52')
def edit(name,old,new):
 p=base/name;s=p.read_text();assert old in s,(name,old[:80]);p.write_text(s.replace(old,new,1))
edit('decision-api.mjs',"import {REPLY_QUESTION", "import {EXPRESSION_QUESTION,normalizeExperienceContext,varyMoodPlan} from './src/experience-choices.mjs';\nimport {REPLY_QUESTION")
edit('decision-api.mjs',"s.individual_overrides={light:","s.experience_context=normalizeExperienceContext(input.experience_context);\n s.individual_overrides={light:")
edit('decision-api.mjs',"questions.mood_intent=structuredClone", "questions.mood_expression=structuredClone(EXPRESSION_QUESTION);\n if(!current.experience_context)delete questions.craft.criteria.company;\n questions.craft.instructions+=' 两位街坊无须借伞、一起散步聊天、结伴走过水边属于company。只邀请陪伴但没有指定做法，仍可由氛围问题选择。';\n questions['scope:craft'].instructions+=' 明确一起散步、结伴走一小段也选yes。';\n questions.mood_intent=structuredClone")
edit('decision-api.mjs',"return explicit?literal:withGentleReply(composeAtmosphere(literal,raw.answers,{utterance:input.user_utterance}),raw.answers,input.user_utterance);", "return explicit?literal:varyMoodPlan(withGentleReply(composeAtmosphere(literal,raw.answers,{utterance:input.user_utterance}),raw.answers,input.user_utterance),raw.answers,state);")
# Each request owns its criteria, so old-client filtering cannot mutate the contract.
edit('decision-api.mjs',"criteria:d.choices};", "criteria:{...d.choices}};")
p=base/'semantic-contract.json';data=json.loads(p.read_text());data['fields']['craft']['choices']['company']='两位街坊结伴走过一段水边，停下来招呼、交谈，不需要借伞';p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
edit('src/catalog.mjs',"DOMAINS.craft={label:'街边的小日子',choices:{keep:","DOMAINS.craft={label:'街边的小日子',choices:{company:'两位街坊相互招呼，结伴走过水边，停下来聊一会儿',keep:")
edit('src/catalog.mjs',"CHOICE_LABELS.craft={", "CHOICE_LABELS.craft={company:'结伴走一段',")
edit('src/craft-design.mjs',"new Set(['tea_service'", "new Set(['company_walk','tea_service'")
edit('src/craft-design.mjs',"export const CRAFT_TIMING={", "export const CRAFT_TIMING={company_walk:{gather:22,active:40,closing:6},")
edit('src/craft-design.mjs',"export const CRAFT_NAMES={", "export const CRAFT_NAMES={company_walk:'一起走过一段晚风',")
edit('src/scene-events.mjs',"const craft={tea:'tea_service'", "const craft={company:'company_walk',tea:'tea_service'")
edit('src/interaction-sequence.mjs',"export const INTERACTION_RECIPES=Object.freeze({", "export const INTERACTION_RECIPES=Object.freeze({\n company_companion:[{action:'approach',target:'supply'},{action:'welcome',waitFor:'recipient',seconds:2.2},{action:'pair_walk',target:'destination'},{action:'welcome',seconds:3.5},{action:'admire',seconds:1.6}],")
edit('src/craft-world.mjs',"import {rainingAt}","import {recentParticipationPenalty} from './wish-memory.mjs';\nimport {rainingAt}")
edit('src/craft-world.mjs',"D(a.p,where)-D(b.p,where)","D(a.p,where)+recentParticipationPenalty(s,a.id)-D(b.p,where)-recentParticipationPenalty(s,b.id)")
edit('src/craft-world.mjs',"}else if(e.kind==='umbrella_walk'){", """}else if(e.kind==='company_walk'){
  const route=pairRoute(s,nav);if(route){const first=route[0],last=route.at(-1),p0=nav.nodes[first[0]],p1=nav.nodes[first[1]];
   const a=job('company_companion',p0,nav.nodes[last[0]],{context:{routeSide:0}}),b=job('company_companion',p1,nav.nodes[last[1]],{context:{routeSide:1}});
   if(a&&b){a.context.supplyNode=first[0];a.context.destinationNode=last[0];b.context.supplyNode=first[1];b.context.destinationNode=last[1];a.context.partner=b.actor;b.context.partner=a.actor;a.context.look=p1.slice(0,3);b.context.look=p0.slice(0,3);w.pair={ids:[a.actor,b.actor],route,at:1,done:false,kind:'company'};lock(s,a,e,'supply');lock(s,b,e,'supply');}
  }else emit('水边暂时没有合适的并肩位置，街坊先各自歇一会儿。');
 }else if(e.kind==='umbrella_walk'){""")
edit('src/craft-world.mjs',"enter(step){if(step.target)","enter(step){if(j.recipe==='company_companion'&&step.action==='welcome'){const other=s.actors.find(a=>a.id===j.context.partner);if(other){j.context.look=other.p.slice();j.context.supplyLook=other.p.slice();}}if(step.target)")
edit('src/craft-world.mjs',"if(j.recipe.startsWith('umbrella_'))return;", "if(j.recipe.startsWith('umbrella_')||j.recipe==='company_companion')return;")
edit('src/input-session.mjs',"['paper_','memory_','laundry_','tea_','umbrella_','leaf_','parcel_']", "['paper_','memory_','laundry_','tea_','umbrella_','company_','leaf_','parcel_']")
edit('src/life-plans.mjs',"import {eventKind}","import {beginExperience} from './wish-memory.mjs';\nimport {eventKind}")
edit('src/life-plans.mjs',"s.intentRuntime.lastReceipt=receipt;s.revision++;", "s.intentRuntime.lastReceipt=receipt;beginExperience(s,items,receipt);s.revision++;")
edit('src/simulation.mjs',"import {ensureCraft", "import {ensureWishMemory,advanceWishMemory,validateWishMemory} from './wish-memory.mjs';\nimport {ensureCraft")
edit('src/simulation.mjs',"ensureBoat(s,nav.activities?.boatRoute);", "ensureWishMemory(s);ensureBoat(s,nav.activities?.boatRoute);")
edit('src/simulation.mjs',"syncGuestActors(s);advanceInput(s,nav);", "syncGuestActors(s);advanceInput(s,nav);advanceWishMemory(s);")
edit('src/simulation.mjs',"recoverInput(s);return s;", "recoverInput(s);validateWishMemory(s);return s;")
edit('src/main.mjs',"import {liveWishFocus}","import {experienceContext} from './wish-memory.mjs';\nimport {liveWishFocus}")
edit('src/main.mjs',"const current={individual_overrides:","const current={experience_context:experienceContext(state),individual_overrides:")
edit('src/main.mjs',"['craft',['tea','snack'", "['craft',['company','tea','snack'")
# Follow an actual walker for the new prop-free scene instead of a restaurant landmark.
edit('src/main.mjs',"action==='umbrella'?'resident.child_runner'", "['umbrella','company'].includes(action)?'resident.child_runner'")
# Prefer a recently less-used worker when the new expressive policy is active.
edit('src/neighborhood-world.mjs',"import {LANTERN_STATIONS}","import {recentParticipationPenalty} from './wish-memory.mjs';\nimport {LANTERN_STATIONS}")
edit('src/neighborhood-world.mjs',"cost(a)-cost(b)","cost(a)+recentParticipationPenalty(s,a.id)-cost(b)-recentParticipationPenalty(s,b.id)")
edit('src/paper-world.mjs',"import {createInteraction", "import {recentParticipationPenalty,returnKindness} from './wish-memory.mjs';\nimport {createInteraction")
edit('src/paper-world.mjs',"const count=e.kind==='paper_share'", "const care=e.kind==='paper_share'?returnKindness(s,candidates):null;\n const count=e.kind==='paper_share'")
edit('src/paper-world.mjs',"const actor=candidates.filter(a=>!used.has(a.id)).sort((a,b)=>D(a.p,nav.nodes[writingNode])-D(b.p,nav.nodes[writingNode]))[0];", "const actor=(care&&candidates.find(a=>a.id===care.to&&D(a.p,nav.nodes[writingNode])<6))||candidates.filter(a=>!used.has(a.id)).sort((a,b)=>D(a.p,nav.nodes[writingNode])+recentParticipationPenalty(s,a.id)-D(b.p,nav.nodes[writingNode])-recentParticipationPenalty(s,b.id))[0];")
edit('src/paper-world.mjs',"recipient=candidates.filter(a=>!used.has(a.id)).sort", "recipient=(care&&actor.id===care.to&&candidates.find(a=>a.id===care.from&&!used.has(a.id)))||candidates.filter(a=>!used.has(a.id)).sort")
print('Wired experiences, memory, and the two-person walk.')
