import test from 'node:test';
import assert from 'node:assert/strict';
import {createCueTracker} from '../src/sound-cues.mjs';
import {createEventSfx} from '../src/event-sfx.mjs';
import {FIREWORK_BURSTS,AUDIBLE_BURSTS,FIREWORK_FLIGHT} from '../src/firework-score.mjs';
const world=(time,sceneEvent=null)=>({time,sceneEvent,festivalStarted:10,festivalUntil:0,festivalStop:null});
test('Market opening/repeat/closing produce two sparse cues for the whole event',()=>{
 const t=createCueTracker();t.update(world(0));const e={id:'scene-1',kind:'market',phase:'gather'};
 assert.equal(t.update(world(.05,e))[0].type,'market_open');for(let i=2;i<50;i++)assert.deepEqual(t.update(world(i*.05,e)),[]);
 assert.equal(t.update(world(2.5,{...e,phase:'closing'}))[0].type,'market_close');assert.deepEqual(t.update(world(2.55,{...e,phase:'closing'})),[]);
 assert.deepEqual(t.update(world(2.6,e)),[],'undo/repeated request must not replay the opening bell');
});
test('Every spaced visual firework gets one launch and bloom, at the same simulation times',()=>{
 const t=createCueTracker(),heard=[];t.update(world(9.95));for(let i=0;i<1300;i++){const time=10+i*.05;for(const cue of t.update({...world(time),festivalUntil:75}))heard.push({...cue,time});}
 assert.equal(heard.length,FIREWORK_BURSTS.length*2);for(const i of AUDIBLE_BURSTS){const cues=heard.filter(c=>c.variant===i);assert.equal(cues.length,2);assert(Math.abs(cues[0].time-(10+FIREWORK_BURSTS[i]-FIREWORK_FLIGHT))<.051);assert(Math.abs(cues[1].time-(10+FIREWORK_BURSTS[i]))<.051);}
});
test('Mute, page resume and a clock jump never replay old sounds',()=>{
 const t=createCueTracker(),s=time=>({...world(time),festivalUntil:75});assert.deepEqual(t.update(s(15)),[]);assert.deepEqual(t.update(s(15.3),false),[]);assert.deepEqual(t.update(s(15.35),true),[]);t.rebase();assert.deepEqual(t.update(s(25)),[]);assert.deepEqual(t.update(s(28.2)),[]);
});
test('Closing fireworks permits a rocket already in flight to bloom, but no new launch',()=>{
 const t=createCueTracker(),heard=[];t.update(world(9.95));for(let i=0;i<160;i++){const time=10+i*.05;heard.push(...t.update({...world(time),festivalUntil:18,festivalStop:10.5}));}assert.deepEqual(heard.map(c=>c.type),['firework_launch','firework_bloom']);
});
test('Muted playback never creates an audio context; active voices stop with the master sound switch',()=>{
 let created=0,stopped=0;const param=()=>({value:0,setValueAtTime(){},linearRampToValueAtTime(){},exponentialRampToValueAtTime(){},cancelScheduledValues(){},setTargetAtTime(){}}),node=()=>({gain:param(),frequency:param(),Q:param(),connect(){},disconnect(){},start(){},stop(){stopped++;}});
 const ctx={state:'running',currentTime:0,sampleRate:22050,destination:{},createGain:node,createBiquadFilter:node,createOscillator:node,createBufferSource:node,createBuffer:(n,len)=>({getChannelData:()=>new Float32Array(len)})};
 const sfx=createEventSfx({contextFactory:()=>{created++;return ctx;}});sfx.update(world(0));sfx.update(world(.05,{id:'muted',kind:'market',phase:'gather'}));assert.equal(created,0);sfx.arm();sfx.setEnabled(true);sfx.update(world(.1,{id:'open',kind:'market',phase:'gather'}));assert.equal(sfx.status().played,1);assert(sfx.status().activePhrases>0);const previous=stopped;sfx.setEnabled(false);assert(stopped>previous);assert.equal(sfx.status().activePhrases,0);
});

test('An interrupted audio context recovers on the next gesture',async()=>{let resumes=0;const param=()=>({value:0});const node=()=>({gain:param(),frequency:param(),Q:param(),connect(){}});const ctx={state:'running',destination:{},createGain:node,createBiquadFilter:node,resume(){resumes++;this.state='running';return Promise.resolve();}};const sfx=createEventSfx({contextFactory:()=>ctx});sfx.arm(false);sfx.setEnabled(true);ctx.state='interrupted';sfx.arm(true);await Promise.resolve();assert.equal(resumes,1);assert.equal(sfx.status().ready,true);});
test('Replacing a closed context clears old voices so the next burst is audible',()=>{const param=()=>({value:0,setValueAtTime(){},linearRampToValueAtTime(){},exponentialRampToValueAtTime(){},cancelScheduledValues(){},setTargetAtTime(){}}),node=()=>({gain:param(),frequency:param(),Q:param(),connect(){},disconnect(){},start(){},stop(){}}),contexts=[];const make=()=>{const c={state:'running',currentTime:0,sampleRate:22050,destination:{},createGain:node,createBiquadFilter:node,createOscillator:node,createBufferSource:node,createBuffer:(n,len)=>({getChannelData:()=>new Float32Array(len)})};contexts.push(c);return c;};const sfx=createEventSfx({contextFactory:make});sfx.arm();sfx.setEnabled(true);sfx.update(world(0));sfx.update(world(.05,{id:'market',kind:'market',phase:'gather'}));const fire=time=>({...world(time),festivalStarted:0,festivalUntil:6});sfx.update(fire(.3));assert.equal(sfx.status().activePhrases,2);contexts[0].state='closed';sfx.arm();assert.equal(contexts.length,2);assert.equal(sfx.status().activePhrases,0);for(const time of[.6,.9,1.2])sfx.update(fire(time));assert.equal(sfx.status().played,3);});
