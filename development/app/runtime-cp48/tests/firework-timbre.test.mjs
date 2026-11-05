import test from 'node:test';
import assert from 'node:assert/strict';
import {renderFirework} from '../src/firework-timbre.mjs';
test('Firework phrases have finite stereo tails, finite starts and no clipped samples',()=>{
 for(const rate of [22050,44100,48000])for(const type of ['firework_launch','firework_bloom'])for(let variant=0;variant<3;variant++){
  const s=renderFirework(type,variant,rate),[l,r]=s.channels;assert.equal(l.length,Math.ceil(s.duration*rate));assert.equal(l.length,r.length);
  assert.equal(Math.abs(l[0]),0);assert(Math.abs(l.at(-1))<.001);let stereo=0,peak=0;for(let i=0;i<l.length;i++){assert(Number.isFinite(l[i])&&Number.isFinite(r[i]));peak=Math.max(peak,Math.abs(l[i]),Math.abs(r[i]));stereo+=Math.abs(l[i]-r[i]);}assert(peak<1);assert(stereo>1);
  if(type==='firework_bloom'){const early=Math.max(...l.slice(0,Math.floor(.05*rate)).map(Math.abs));assert(early>peak*.45,'bloom needs a distinct early pressure burst');const tail=l.slice(Math.floor(rate)).reduce((a,v)=>a+v*v,0);assert(tail>.01,'bloom has an audible diffuse tail');}
 }
});
