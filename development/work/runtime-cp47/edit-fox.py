from pathlib import Path
p=Path('app/runtime-cp47/src/fox-behavior.mjs');s=p.read_text()
s=s.replace("const ps=people(s),near=goalMode==='greet'?ps.filter(a=>D(m.p,a.p)<4.5", "const ps=people(s),near=goalMode==='greet'?ps.filter(a=>D(m.p,a.p)<4.8")
s=s.replace(".sort((a,b)=>D(m.p,a.p)-D(m.p,b.p))[0]:null;", ".sort((a,b)=>(D(m.p,a.p)-(a.id.includes('child')?.65:0))-(D(m.p,b.p)-(b.id.includes('child')?.65:0)))[0]:null;")
s=s.replace("x.d>.44&&x.d<2.5", "x.d>(near?.75:.44)&&x.d<(near?3.3:2.5)")
s=s.replace("Math.abs(x.d-1.25)", "Math.abs(x.d-(near?1.7:1.25))")
start=s.index("else if(c?.action==='greet'){const neighbor=")
end=s.index("else if(c?.action==='stretch')",start)
s=s[:start]+"else if(c?.action==='greet'){beginWalk(s,data,m,f,'greet');}"+s[end:]
s=s.replace("f.goalMode==='play'?.52:.36", "['play','greet'].includes(f.goalMode)?.55:.40")
s=s.replace("dt*.35", "dt*.65")
s=s.replace("f.goalMode==='play'?'trot':'explore'", "['play','greet'].includes(f.goalMode)?'trot':'explore'")
s=s.replace("goal==='greet'?7:goal==='play'?5:varied([9,16]", "goal==='greet'?4.2:goal==='play'?4:varied([3,6]")
s=s.replace("pause(f,'look',varied([8,13]", "pause(f,'look',varied([2,4]")
s=s.replace("if(f.cycle%7===0)pause(f,'stretch',5.5);else beginWalk", "if(f.cycle%5===1)pause(f,'groom',3.4);else if(f.cycle%5===3)pause(f,'stretch',2.8);else beginWalk")
s=s.replace("'greet','play','bow'].includes(f.phase)", "'greet','play','bow','groom'].includes(f.phase)")
start=s.index('export function foxPose(s)')
end=s.index('export function validateFox',start)
s=s[:start]+'''export function foxPose(s){
 const f=s.foxBehavior,m=s.movers?.[ID],zero={headPitch:0,headTurn:0,tail:0,front:0,back:0,lift:0,paw:0,groom:0};
 if(s.musicCircle?.phase==='listen'&&s.sceneEvent?.kind==='music')return {...zero,headPitch:-.12,headTurn:clamp(delta(m.yaw,Math.atan2(-1.4537-m.p[1],-2.4684-m.p[0])+Math.PI),-1.45,1.45),tail:Math.sin(s.time*3.8)*.24};
 if(!f||f.suspended)return zero;
 const t=f.clock,held=['look','sniff','rest'].includes(s.objectControls?.[ID]?.action)||s.animals==='rest',soft=clamp(Math.min(t/.45,f.phase==='walk'||held?1:(f.duration-t)/.5),0,1),friendly=['greet','play'].includes(f.phase),stretch=['stretch','bow'].includes(f.phase),groom=f.phase==='groom';
 const neighbor=people(s).find(a=>a.id===f.neighbor),look=neighbor&&f.phase==='greet'?clamp(delta(m.yaw,Math.atan2(neighbor.p[1]-m.p[1],neighbor.p[0]-m.p[0])+Math.PI),-.6,.6):f.phase==='look'?Math.sin(t*.9)*.16:0;
 // The body keeps its foot-driven heading. Greeting and grooming use the neck,
 // individual front paws and articulated tail, never a spin about the root.
 return {headPitch:(f.phase==='sniff'?.24+.05*Math.sin(t*2.2):groom?.42+.10*Math.sin(t*6):stretch?.24:friendly?-.24:0)*soft,headTurn:(groom?-.25:look)*soft,
 tail:(friendly?Math.sin(t*6.8)*.48:f.phase==='walk'?Math.sin(s.time*4)*.12:f.phase==='rest'?.025*Math.sin(t):Math.sin(s.time*2.4)*.16)*soft,
 front:stretch?.28*Math.sin(Math.PI*clamp(t/f.duration,0,1)):0,back:stretch?-.07*Math.sin(Math.PI*clamp(t/f.duration,0,1)):0,
 paw:(friendly?.82*Math.pow(Math.max(0,Math.sin(t*3.4)),2):groom?.9:0)*soft,groom:Number(groom)*soft,lift:friendly?.025*Math.max(0,Math.sin(t*3.4))*soft:0};
}
''' + s[end:]
s=s.replace("stretch:'伸展前爪，舒展身体'", "groom:'抬起前爪，低头舔一舔',stretch:'伸展前爪，舒展身体'")
p.write_text(s)
