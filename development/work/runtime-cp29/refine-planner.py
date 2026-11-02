from pathlib import Path
import json
p=Path('app/runtime-cp29/semantic-contract.json');d=json.loads(p.read_text());d['fields']['occasion']['choices']['delivery']='送信时刻，邮差与送信人沿街核对门牌、分送信件，街坊留意来信';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=Path('app/runtime-cp29/src/atmosphere.mjs');s=p.read_text().replace('Concrete action commands belong to the literal controller.','Specific meals, postal rounds, time of day, weather, people and object actions belong to the literal controller even when phrased poetically. An adjective describing that concrete request does not make a separate mood invitation. Choose mixed only for BOTH an independently requested town-wide mood AND specific actions.').replace('"literal": "A concrete action/weather/object request",','"literal": "A specific action, communal activity, time, weather or object request, including poetic phrasing",\n      "mixed": "Both specific actions AND an independent invitation for the whole town to evoke a mood",')
s=s.replace("intent?.choice!=='mood'", "!['mood','mixed'].includes(intent?.choice)").replace('(intent.probabilities?.mood||0)<.6','(intent.probabilities?.[intent.choice]||0)<.6')
s+='''
// Concrete choices cannot be erased by the less-specific mood interpretation.
// Only an independently requested mood may add compatible, unmentioned fields.
export function composeAtmosphere(literal, answers){
 const mood=atmospherePlan(answers);if(!mood)return literal;
 if(!literal.items.length){
  if(answers.mood_intent.choice==='mixed'||['no_change','clarify','partial'].includes(literal.status))return literal;
  return {...mood,literalPlan:literal};
 }
 if(answers.mood_intent.choice!=='mixed')return literal;
 const foreground=new Set(['weather','festival','occasion']);
 const targets=new Set(literal.items.filter(i=>i.kind==='macro').map(i=>i.target));
 const hasScene=[...targets].some(t=>foreground.has(t));
 const additions=mood.items.filter(i=>!targets.has(i.target)&&!(hasScene&&foreground.has(i.target)));
 if(!additions.length)return literal;
 return {...literal,items:[...literal.items,...additions],resolution:{...mood.resolution,source:'jev-composed'},summary:literal.summary+'；'+mood.summary};
}
''';p.write_text(s)
p=Path('app/runtime-cp29/decision-api.mjs');s=p.read_text().replace('ATMOSPHERE_QUESTIONS,atmospherePlan','ATMOSPHERE_QUESTIONS,composeAtmosphere');s=s.replace("questions.occasion.instructions='全镇/集体活动；个别人休息、工作不等于全镇quiet/market。';", "questions.occasion.instructions='选择具体的集体生活主题：吃饭/聚餐/热食=supper；邻里相聚聊天=reunion；送信时刻/邮路工作=delivery；市集买卖=market；休息放慢=quiet。即使带温馨等修饰，也优先具体活动。只安排某个人做事则keep；赞美回忆假设或保持现状keep。';\n questions['scope:occasion'].instructions='是否安排一段集体生活，包括聚餐、邻里聚会、邮差送信时光、市集或全镇放慢休息？不要求所有人都参与。独立点名一个人的动作才no；肯定的集体活动愿望yes。';")
s=s.replace('Overall mood invitations and poetic atmosphere belong to mood_intent/atmosphere;', 'Specific meanings such as meals, postal rounds and time of day still belong to the literal questions even if phrased poetically. Independently requested overall moods belong to mood_intent/atmosphere;')
s=s.replace(" const moodPlan=!explicit?atmospherePlan(raw.answers):null;if(moodPlan)return {...moodPlan,literalPlan:{status,items,skipped}};\n return{status,items,skipped,", " const literal={status,items,skipped,")
s=s.replace("换个说法或点选一个对象。'};\n}","换个说法或点选一个对象。'};\n return explicit?literal:composeAtmosphere(literal,raw.answers);\n}")
p.write_text(s)
