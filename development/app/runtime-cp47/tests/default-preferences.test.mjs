import test from 'node:test';
import assert from 'node:assert/strict';
import {createSound} from '../src/sound.mjs';

test('First visit defaults to English and saved explicit Chinese remains respected',async()=>{
 globalThis.localStorage={getItem:()=>null};
 const fresh=await import('../src/i18n.mjs?default-en');assert.equal(fresh.getLocale(),'en');
 globalThis.localStorage={getItem:()=> 'zh'};
 const saved=await import('../src/i18n.mjs?saved-zh');assert.equal(saved.getLocale(),'zh');
 delete globalThis.localStorage;
});
test('The user-provided loop is the default, while a saved mute blocks gesture playback',async()=>{
 let saved=null,players=[],handlers={};globalThis.localStorage={getItem:()=>saved,setItem:(k,v)=>saved=v};globalThis.document={hidden:false,addEventListener:(type,fn)=>handlers[type]=fn};
 class Audio{constructor(src){this.src=src;this.paused=true;this.currentTime=0;this.plays=0;players.push(this);}play(){this.plays++;this.paused=false;return Promise.resolve();}pause(){this.paused=true;}}
 globalThis.window={Audio};const button={dataset:{},setAttribute(){}};const sound=createSound(button);await Promise.resolve();assert.equal(sound.status().enabled,true);assert.equal(players[0].loop,true);assert.equal(players[0].playbackRate,1);assert(players[0].src.endsWith('/assets/lanterns-awake-loop.wav'));button.onclick();assert.equal(saved,'off');const count=players[0].plays;handlers.pointerdown({target:{closest:()=>null}});assert.equal(players[0].plays,count);assert(players[0].paused);const muted=createSound({dataset:{},setAttribute(){}});assert.equal(muted.status().enabled,false);assert.equal(players.length,1);delete globalThis.localStorage;delete globalThis.document;delete globalThis.window;
});
