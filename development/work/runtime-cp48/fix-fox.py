from pathlib import Path
p=Path('app/runtime-cp48/src/fox-view.mjs');s=p.read_text().replace("[k,p.quaternion.clone()]", "[k,{q:p.quaternion.clone(),p:p.position.clone()}]").replace('p.quaternion.copy(b).multiply','p.quaternion.copy(b.q).multiply')
s=s.replace("const displayed={headPitch", "let gaitWeight=0;let lastLegs=[];let locomoting=false;\n const displayed={headPitch")
s=s.replace("const p=displayed;if(s.foxBehavior?.suspended&&s.musicCircle?.phase!=='listen')return;", """const p=displayed,m=s.movers?.[id],f=s.foxBehavior;
 // One final owner for the four legs. A fading grooming/paw pose must never
 // replace a travelling fox's gait with its rest transforms.
 locomoting=!!m&&m.speed>.02&&(f?.phase==='walk'||f?.suspended&&s.musicCircle?.phase==='approach');
 const wanted=locomoting?Math.min(1,m.strideWeight??1):0;gaitWeight+=(wanted-gaitWeight)*alpha;if(gaitWeight<.00001)gaitWeight=0;
 const phase=(m?.distance||0)*19,amplitude=.34+.07*Math.min(1,(m?.speed||0)*.52/.55),poses=locomoting?[0,0,0,0]:[p.front+p.paw,p.back,p.front,p.back];lastLegs=[];
 for(let leg=0;leg<4;leg++){
  const name='leg_'+leg,node=parts.get(id+'/'+name),rest=base.get(id+'/'+name),cycle=phase+(leg===0||leg===3?0:Math.PI),step=Math.sin(cycle)*amplitude*gaitWeight,gesture=poses[leg]*(1-Math.min(1,gaitWeight));
  rotate(name,PITCH,step+gesture);if(node&&rest){node.position.copy(rest.p);node.position.y+=.045*Math.max(0,Math.sin(cycle))*gaitWeight;}
  lastLegs.push({angle:step+gesture,lift:node&&rest?node.position.y-rest.p.y:0});
 }
 if(f?.suspended&&s.musicCircle?.phase!=='listen')return;""")
s=s.replace(" // A clear one-paw greeting; the other three feet remain planted.\n if(p.front||p.paw||p.groom){rotate('leg_0',PITCH,p.front+p.paw);rotate('leg_2',PITCH,p.front);for(const i of[1,3])rotate('leg_'+i,PITCH,p.back);}\n if(p.lift)"," // Only the stationary play bounce may lift the root; walking and the\n // one-paw greeting keep the body supported by the other feet.\n if(!locomoting&&f?.phase==='play'&&p.lift)")
s=s.replace("pose:{...displayed}", "pose:{...displayed},walking:locomoting,gaitWeight,legs:lastLegs.map(x=>({...x}))")
p.write_text(s)
p=Path('app/runtime-cp48/src/life-view.mjs');s=p.read_text().replace("if(clip.motion==='creature_walk'){for(let leg=0;leg<4;leg++)", "if(clip.motion==='creature_walk'){if(id!=='animal.garden_fox')for(let leg=0;leg<4;leg++)")
s=s.replace("return {kiteHandGap:start.distanceTo(hand),", "return {foxAnimation:foxView.snapshot(),kiteHandGap:start.distanceTo(hand),")
p.write_text(s)
p=Path('app/runtime-cp48/src/fox-behavior.mjs');s=p.read_text()
s=s.replace("&&!s.residentActions?.[a.id]?.requested&&!a.id.includes('vendor')", "&&Math.abs(a.p[2]-m.p[2])<.5&&!a.id.includes('vendor')")
s=s.replace("(a.id.includes('child')?.65:0)", "(a.id.includes('child')?.45:0)+(s.residentActions?.[a.id]?.requested?.65:0)").replace("(b.id.includes('child')?.65:0)", "(b.id.includes('child')?.45:0)+(s.residentActions?.[b.id]?.requested?.65:0)")
s=s.replace("D(x.p,near.p)<2.05", "D(x.p,near.p)<1.5")
s=s.replace("for(const handle of[.38,.62,.90])", "for(const handle of[.27,.38,.62,.90])")
s=s.replace("s.time-(f.lastBackAt??-100)>25", "(goalMode==='greet'?(f.greetingBacksteps||0)<3&&s.time-(f.lastBackAt??-100)>.9:s.time-(f.lastBackAt??-100)>25)")
s=s.replace("if(chosen.reverse)f.lastBackAt=s.time;", "if(chosen.reverse){f.lastBackAt=s.time;if(goalMode==='greet')f.greetingBacksteps=(f.greetingBacksteps||0)+1;}")
s=s.replace("f.immediateGreeting=false;if(c?.action", "f.immediateGreeting=false;f.wasClearing=false;f.greetingBacksteps=0;if(c?.action")
s=s.replace("if(clearing&&D(m.p", "// A fresh local wish owns the fox over an older ambient gathering.\n clearing=clearing&&!(c&&c.started>=(s.sceneEvent?.started??Infinity)&&f.completedControl!==key);\n if(clearing&&D(m.p")
s=s.replace("D(m.p,a.p)<2.4&&!a.id.includes('vendor')&&!a.actor.interactionLock", "D(m.p,a.p)<1.65&&Math.abs(delta(m.yaw,Math.atan2(a.p[1]-m.p[1],a.p[0]-m.p[0])+Math.PI))<1.1&&!a.id.includes('vendor')&&!a.actor.interactionLock")
s=s.replace("f.command==='greet'&&neighbor&&f.routeDistance>.25", "f.command==='greet'&&!route.reverse&&neighbor&&f.routeDistance>.25")
p.write_text(s)
p=Path('app/runtime-cp48/src/music-circle.mjs');s=p.read_text().replace("const e=s.sceneEvent,m=s.movers[FOX];if(!m)return false;", "const e=s.sceneEvent,m=s.movers[FOX];if(!m)return false;const control=s.objectControls?.[FOX];if(e?.kind==='music'&&control&&control.started>=e.started){if(s.musicCircle?.eventId===e.id)s.musicCircle.phase='done';return false;}")
p.write_text(s)
p=Path('app/runtime-cp48/src/main.mjs');s=p.read_text().replace("小狐狸:state.foxBehavior,", "小狐狸:state.foxBehavior,狐狸步态:life.diagnostics().foxAnimation,")
p.write_text(s)
p=Path('app/runtime-cp48/src/i18n-en.mjs');p.write_text(p.read_text()+"\nObject.assign(EN,{'狐狸步态':'Fox walking animation'});\n")
