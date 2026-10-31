export const ATMOSPHERE_QUESTIONS={
  "intent": {
    "type": "choice",
    "instructions": "User speaks to an artistic miniature town. Present feelings, sensory impressions, loose associations and poetic fragments are soft invitations, even without imperative verbs or a request to change the town. Interpret generously when there is any meaningful emotional link. A current personal feeling is enough; do not demand a named action. Emotion transformed into imagery is a metaphor, not a demand to manufacture its imaginary objects. Pure praise of the interface or a completed event, hypothetical questions, and explicit keep-as-is are not invitations. A memory used to evoke a feeling now can be an invitation. Personal needs such as hunger or wanting company are mood invitations, not literal object manipulation. A wish to hear human voices evokes social company; it does not require new speech synthesis. Choose literal if a concrete supported activity/time/weather/person/object is the meaning of the wish; poetic adjectives alone do not make it mixed. Choose mixed for a concrete request PLUS a separately desired town-wide feeling. A separate clause expressing relief, breathing room, personal space, reduced pressure, or companionship is an independent mood even when another clause precisely controls a vehicle or person; do not let that concrete clause erase the emotional one. Choose mood for a feeling or evocative metaphor without a concrete supported command.",
    "criteria": {
      "mood": "An implied or explicit invitation to evoke an atmosphere",
      "literal": "A specific action, communal activity, time, weather or object request, including poetic phrasing",
      "mixed": "Both specific actions AND an independent invitation for the whole town to evoke a mood",
      "no_change": "Only praise, memory, hypothetical or explicit leave unchanged",
      "unclear": "No coherent direction can be inferred"
    }
  },
  "atmosphere": {
    "type": "choice",
    "instructions": "Choose ONE artistic interpretation of the feeling the speaker wants the town to evoke. You may interpret poetic imagery. Do not invent objects, people or new physical capabilities. This is a mood choice, not an exact-command detector. Use the closest feeling for a meaningful present sensory or emotional fragment. Use keep only for interface praise, purely retrospective event comments, hypothetical questions or explicit keep-as-is. Loneliness suggests togetherness; fatigue suggests rest; food aromas or hunger suggest a warm meal.",
    "criteria": {
      "keep": "No new atmosphere requested",
      "tender": "Soft, warm, welcoming, emotionally held",
      "together": "Companionship, reunion, human closeness, less loneliness",
      "celebration": "A little joy, festive surprise or a reason to celebrate",
      "dream": "Weightless, hushed, gently unreal, dreamlike",
      "quiet": "Rest, a slow exhale, less bustle, release of tiredness",
      "hopeful": "Freshness, hope, a new beginning, a touch of spring",
      "hearth": "Hunger, food aromas, warm meals, the comfort of a kitchen",
      "drizzle": "Soft rain, damp evening air, raindrops on eaves",
      "snowfall": "Winter, falling snow, soft white flakes; not emotional loneliness"
    }
  }
};
export const ATMOSPHERES={
 tender:{label:'让街巷暖一点，让彼此靠近一点。',changes:{light:'warm',breeze:'gentle',occasion:'reunion'}},
 together:{label:'让邻居们慢慢找到彼此。',changes:{occasion:'reunion',light:'warm'}},
 celebration:{label:'把这份欢喜带到树下，让街坊和琴声一起热闹起来。',changes:{occasion:'reunion',music:'play',light:'warm',breeze:'lively'}},
 dream:{label:'让夜色、灯火和晚风一起放轻。',changes:{day_phase:'night',light:'soft',breeze:'calm',occasion:'quiet'}},
 quiet:{label:'让脚步和风都慢一点，留一会儿安静。',changes:{occasion:'quiet',light:'soft',breeze:'calm'}},
 hearth:{label:'把热食摆上柜台，让街坊来吃点东西。',changes:{occasion:'supper',light:'warm'}},
 drizzle:{label:'细雨落在屋檐边，街坊收好手里的东西。',changes:{weather:'rain'}},
 snowfall:{label:'让纸片雪飘下来，给小镇换一个冬日。',changes:{weather:'snow'}},
 hopeful:{label:'让街巷亮起来，把新的好心情传开。',changes:{occasion:'market',light:'bright',breeze:'gentle'}}
};
export function atmospherePlan(answers){const intent=answers.mood_intent,mood=answers.atmosphere;if(!['mood','mixed'].includes(intent?.choice)||!ATMOSPHERES[mood?.choice]||((intent.probabilities?.mood||0)+(intent.probabilities?.mixed||0))<.45||(mood.probabilities?.[mood.choice]||0)<.28)return null;let preset=ATMOSPHERES[mood.choice];const explicitOff=answers.festival?.choice==='quiet'&&(answers.festival.probabilities?.quiet||0)>=.5&&(answers['scope:festival']?.probabilities?.yes||0)>=.4;
 if(mood.choice==='celebration'&&explicitOff)preset={label:'让街坊聚起一些欢笑，保持安静的夜空。',changes:{occasion:'reunion',light:'warm',breeze:'lively'}};
 return{status:'change',items:Object.entries(preset.changes).map(([target,action])=>({kind:'macro',target,action,field:target,label:preset.label,target_label:'氛围'})),skipped:[],summary:preset.label,resolution:{source:'jev-atmosphere',choice:mood.choice,confidence:mood.probabilities[mood.choice],...(explicitOff?{constraint:'explicit-fireworks-off'}:{})}};}

// Concrete choices cannot be erased by the less-specific mood interpretation.
// Only an independently requested mood may add compatible, unmentioned fields.
export function composeAtmosphere(literal, answers){
 const mood=atmospherePlan(answers);if(!mood)return literal;
 if(!literal.items.length){
  const unresolved=literal.skipped?.some(x=>!['已经是这个状态','没有明确要求改变这个对象'].includes(x.reason));
  if(['clarify','partial'].includes(literal.status)||answers.mood_intent.choice==='mixed'&&(literal.status!=='change'||unresolved))return literal;
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
