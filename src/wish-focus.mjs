import {actionSubjects} from './action-subjects.mjs?v=cp51-vibe-response-acb055878926';

// Keep the overview unless the user chooses a closer view. For a small paper
// or neighborhood task, that view should follow a real worker, not a landmark.
export function liveWishFocus(s,fallback=null){
 const q=s.inputSession;
 if(q?.phase!=='running')return fallback;
 const local=q.items?.some(i=>i.kind==='macro'&&(i.target==='paper'&&['hang','share','read','collect'].includes(i.action)||i.target==='neighborhood'&&['spring','prepare','reopen'].includes(i.action)));
 return local?actionSubjects(s)[0]||fallback:fallback;
}
