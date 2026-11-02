import {renderFirework} from '../../app/runtime-cp35/src/firework-timbre.mjs';
import {writeFileSync} from 'node:fs';
const rate=44100,seconds=9,n=seconds*rate,channels=[new Float32Array(n),new Float32Array(n)];
for(const[time,type,variant]of [[.4,'firework_launch',0],[1.35,'firework_bloom',0],[4.2,'firework_launch',1],[5.15,'firework_bloom',1]]){
 const s=renderFirework(type,variant,rate),gain=.30*(type==='firework_launch'?1.6:1.15);
 for(let c=0;c<2;c++)for(let i=0;i<s.channels[c].length&&i+Math.round(time*rate)<n;i++)channels[c][i+Math.round(time*rate)]+=s.channels[c][i]*gain;
}
// Same master low-pass as the live player (RBJ biquad, Q=.5, 3800Hz).
const w=2*Math.PI*3800/rate,cos=Math.cos(w),alpha=Math.sin(w)/(2*.5),a0=1+alpha,b0=(1-cos)/2/a0,b1=(1-cos)/a0,b2=b0,a1=-2*cos/a0,a2=(1-alpha)/a0;
for(const ch of channels){let x1=0,x2=0,y1=0,y2=0;for(let i=0;i<n;i++){const x=ch[i],y=b0*x+b1*x1+b2*x2-a1*y1-a2*y2;x2=x1;x1=x;y2=y1;y1=y;ch[i]=y;}}
const b=Buffer.alloc(44+n*4);b.write('RIFF');b.writeUInt32LE(36+n*4,4);b.write('WAVEfmt ',8);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(2,22);b.writeUInt32LE(rate,24);b.writeUInt32LE(rate*4,28);b.writeUInt16LE(4,32);b.writeUInt16LE(16,34);b.write('data',36);b.writeUInt32LE(n*4,40);let peak=0,sum=0;
for(let i=0;i<n;i++)for(let c=0;c<2;c++){const x=channels[c][i];peak=Math.max(peak,Math.abs(x));sum+=x*x;b.writeInt16LE(Math.max(-32767,Math.min(32767,Math.round(x*32767))),44+(i*2+c)*2);}
writeFileSync('outputs/runtime-checkpoint-35/fireworks-preview.wav',b);writeFileSync('outputs/runtime-checkpoint-35/audio-metrics.json',JSON.stringify({seconds,rate,channels:2,peak,rms:Math.sqrt(sum/n/2),clipped:peak>=1,source:'Same renderFirework PCM, master gains and low-pass as the live Web Audio player; BGM excluded.'},null,2));console.log({peak,rms:Math.sqrt(sum/n/2)});
