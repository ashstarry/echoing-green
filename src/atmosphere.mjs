export const ATMOSPHERE_QUESTIONS={
  "intent": {
    "type": "choice",
    "instructions": "User speaks to an artistic miniature town. Emotional wishes, moods and poetic evocations are invitations even without imperative verbs. Emotion transformed into imagery is a metaphor, not a demand to manufacture its imaginary objects. Pure compliments, past recollections, keep-as-is and hypothetical questions are not invitations. Choose literal if a concrete supported activity/time/weather/person/object is the meaning of the wish; poetic adjectives alone do not make it mixed. Choose mixed for a concrete request PLUS a separately desired town-wide feeling. Choose mood for a feeling or evocative metaphor without a concrete supported command.",
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
    "instructions": "Choose ONE artistic interpretation of the feeling the speaker wants the town to evoke. You may interpret poetic imagery. Do not invent objects, people or new physical capabilities. This is a mood choice, not an exact-command detector. Pure praise/memory/hypothetical/keep-as-is chooses keep.",
    "criteria": {
      "keep": "No new atmosphere requested",
      "tender": "Soft, warm, welcoming, emotionally held",
      "together": "Companionship, reunion, human closeness, less loneliness",
      "celebration": "A little joy, festive surprise or a reason to celebrate",
      "dream": "Weightless, hushed, gently unreal, dreamlike",
      "quiet": "Rest, a slow exhale, less bustle, release of tiredness",
      "hopeful": "Freshness, hope, a new beginning, a touch of spring"
    }
  }
};
export const ATMOSPHERES={
 tender:{label:'让街巷暖一点，让彼此靠近一点。',changes:{light:'warm',breeze:'gentle',occasion:'reunion'}},
 together:{label:'让邻居们慢慢找到彼此。',changes:{occasion:'reunion',light:'warm'}},
 celebration:{label:'把这份小小的欢喜，化成一场夜空里的花。',changes:{day_phase:'night',festival:'fireworks'}},
 dream:{label:'让夜色、灯火和晚风一起放轻。',changes:{day_phase:'night',light:'soft',breeze:'calm',occasion:'quiet'}},
 quiet:{label:'让脚步和风都慢一点，留一会儿安静。',changes:{occasion:'quiet',light:'soft',breeze:'calm'}},
 hopeful:{label:'让街巷亮起来，把新的好心情传开。',changes:{occasion:'market',light:'bright',breeze:'gentle'}}
};
export function atmospherePlan(answers){const intent=answers.mood_intent,mood=answers.atmosphere;if(!['mood','mixed'].includes(intent?.choice)||!ATMOSPHERES[mood?.choice]||((intent.probabilities?.mood||0)+(intent.probabilities?.mixed||0))<.6||(mood.probabilities?.[mood.choice]||0)<.5)return null;const preset=ATMOSPHERES[mood.choice];return{status:'change',items:Object.entries(preset.changes).map(([target,action])=>({kind:'macro',target,action,field:target,label:preset.label,target_label:'氛围'})),skipped:[],summary:preset.label,resolution:{source:'jev-atmosphere',choice:mood.choice,confidence:mood.probabilities[mood.choice]}};}

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
