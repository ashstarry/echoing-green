import {actionSubjects} from './action-subjects.mjs?v=cp52-living-variations-0f9817dcf3a8';

// Keep the overview unless the user chooses a closer view. For a small paper
// or neighborhood task, that view should follow a real worker, not a landmark.
export function liveWishFocus(s,fallback=null){
 const q=s.inputSession;
 if(q?.phase!=='running')return fallback;
 if(s.sceneEvent?.kind==='music'&&s.sceneEvent.id===q.sceneId)return 'resident.musician';
 const local=q.items?.some(i=>i.kind==='macro'&&(i.target==='paper'&&['hang','share','read','collect'].includes(i.action)||i.target==='neighborhood'&&['spring','prepare','reopen'].includes(i.action)));
 return local?actionSubjects(s)[0]||fallback:fallback;
}
