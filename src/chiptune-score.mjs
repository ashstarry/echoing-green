// Six original, related handheld-town pieces; no borrowed melodies.
// A shared slow pulse makes changes musically aligned while each theme has its own melody.
export const BPM=76,STEP_SECONDS=60/BPM/2,LOOP_STEPS=128;
const decode=s=>s.split('|').map(bar=>bar.trim().split(/\s+/).map(x=>x==='-'?null:Number(x)));
const tracks={
 town:{lead:decode('74 - - 78 76 - 74 - | 71 - 69 - 71 - - - | 74 - 76 - 78 - 81 - | 78 - - 76 74 - - - | 76 - 78 - 81 - 78 - | 74 - - 71 69 - - - | 71 - 74 - 76 - 78 - | 76 - - 73 74 - - -'),chords:[[50,[62,66,69,73]],[47,[59,62,66,69]],[43,[59,62,67,69]],[45,[57,61,64,69]]],color:0},
 night:{lead:decode('78 - - - 76 - 74 - | 71 - - - 69 - - - | 73 - - 76 78 - - - | 76 - 73 - 71 - - - | 74 - - - 78 - 76 - | 73 - - - 69 - - - | 71 - - 73 76 - - - | 74 - - - - - - -'),chords:[[47,[59,62,66,69]],[43,[55,59,62,66]],[50,[57,62,66,69]],[45,[57,61,64,71]]],color:-1},
 rain:{lead:decode('71 - - 74 73 - - - | 69 - - - 66 - - - | 69 - - 71 74 - - - | 73 - - - 69 - - - | 66 - - 69 71 - - - | 74 - - - 73 - 71 - | 69 - - 66 64 - - - | 66 - - - - - - -'),chords:[[47,[59,62,66,69]],[40,[55,59,62,66]],[43,[55,59,62,69]],[42,[57,61,66,69]]],color:-2},
 snow:{lead:decode('81 - - 83 86 - - - | 83 - 81 - 78 - - - | 79 - - 81 83 - - - | 81 - - - 74 - - - | 78 - - 81 83 - 81 - | 78 - - - 76 - - - | 74 - 76 - 78 - 81 - | 78 - - - 74 - - -'),chords:[[50,[62,66,69,76]],[43,[59,62,67,74]],[47,[59,62,66,73]],[45,[57,64,69,74]]],color:1},
 market:{lead:decode('74 - 76 78 81 - 78 - | 76 - 74 - 71 - 74 - | 78 - 81 83 81 - 78 - | 76 - - 73 74 - - - | 81 - 78 - 76 - 74 - | 71 - 74 76 78 - - - | 76 - 78 81 78 - 76 - | 73 - - 76 74 - - -'),chords:[[50,[62,66,69,73]],[43,[59,62,67,69]],[47,[59,62,66,69]],[45,[57,61,64,69]]],color:0},
 festival:{lead:decode('74 - 78 - 81 - 83 - | 86 - - 83 81 - - - | 83 - 81 78 76 - 74 - | 76 - - - 81 - - - | 78 - 81 - 83 - 86 - | 83 - - 81 78 - - - | 76 78 81 78 76 - 73 - | 74 - - - - - - -'),chords:[[50,[62,66,69,74]],[43,[59,62,67,74]],[47,[59,62,66,73]],[45,[57,61,64,71]]],color:1}
};
export const MUSIC_TITLES={town:'纸町晚风',night:'灯影里的归途',rain:'檐下听雨',snow:'纸雪轻落',market:'小街开市',festival:'今夜花开'};
export function musicMood(s){return s.weather==='rain'?'rain':s.worldEvent?.phase==='show'?'festival':s.weather==='snow'?'snow':['market','supper','reunion'].includes(s.occasion)?'market':s.day_phase==='night'?'night':'town';}
export function scoreStep(index,mood='town'){
 const step=((index%LOOP_STEPS)+LOOP_STEPS)%LOOP_STEPS,bar=Math.floor(step/8),beat=step%8,t=tracks[mood]||tracks.town,[bass,chord]=t.chords[bar%4],out=[];
 const phrase=t.lead[bar%8],lead=phrase[beat],secondHalf=bar>=8;
 if(lead!==null){let length=1;while(beat+length<8&&phrase[beat+length]===null)length++;out.push({voice:'lead',midi:lead+(secondHalf&&bar%8<2?-12:0),beats:length+.24,gain:mood==='rain'?.068:mood==='night'?.065:.082});}
 if(beat===0||beat===4)out.push({voice:'bass',midi:bass+(beat===4?7:0),beats:3.7,gain:.085});
 if(beat%2===1&&(mood!=='rain'||beat===3)&&(mood!=='night'||beat===1||beat===5))out.push({voice:'arp',midi:chord[(beat>>1)%4]+(secondHalf?0:12),beats:1.75,gain:mood==='snow'?.033:.025});
 if(mood==='festival'&&(beat===0||beat===4))out.push({voice:'drum',midi:43,beats:.55,gain:.032});
 return out;
}
