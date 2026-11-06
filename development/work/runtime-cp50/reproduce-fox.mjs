import{writeFileSync}from'node:fs';import{setup,step,runInput,queueIntent,inputBusy,execute}from'./audit-utils.mjs';import{applyDecision}from'../../app/runtime-cp50/src/simulation.mjs';
const rows=[];for(const name of['fresh','warm-10','warm-60','warm-120','ambient-market','ambient-music','after-market','after-music','after-paper','retreat-edge']){
 if(process.argv[3]&&name!==process.argv[3])continue;
 const warm=name.startsWith('warm-')?Number(name.slice(5)):2,{s,nav}=setup(62417,warm);
 if(name==='ambient-market'||name==='ambient-music'){applyDecision(s,name.endsWith('market')?{occasion:'market'}:{music:'play',street:'gather'});for(let i=0;i<200;i++)step(s,nav);}
 if(name.startsWith('after-')){execute(s,nav,name==='after-market'?[{kind:'macro',target:'occasion',action:'market'}]:name==='after-music'?[{kind:'macro',target:'music',action:'play'},{kind:'macro',target:'street',action:'gather'}]:[{kind:'macro',target:'paper',action:'hang'}]);}
 if(name==='retreat-edge'){Object.assign(s.movers['animal.garden_fox'],{p:[5.15,1.7,.624],yaw:Math.PI});Object.assign(s.foxBehavior,{phase:'look',duration:999,lastBackAt:s.time-.5,route:null,clock:0});}
 const start=s.time,origin=s.movers['animal.garden_fox'].p.slice(),phases=[],trace=[];let first=null,span=0,greeted=false;
 runInput(s,[{kind:'object',target:'animal.garden_fox',action:'greet'}],()=>queueIntent(s,[{kind:'object',target:'animal.garden_fox',action:'greet'}],{},nav.activities.objectCatalog));
 for(let i=0;i<1000&&inputBusy(s);i++){step(s,nav);const m=s.movers['animal.garden_fox'],f=s.foxBehavior,d=Math.hypot(m.p[0]-origin[0],m.p[1]-origin[1]);if(d>.01&&first===null)first=s.time-start;span=Math.max(span,d);if(phases.at(-1)!==f.phase)phases.push(f.phase);greeted||=!!f.greeted;if(i%10===0)trace.push({t:+(s.time-start).toFixed(2),phase:f.phase,clock:f.clock,p:m.p,command:f.command,neighbor:f.neighbor,greeted:f.greeted,wasClearing:f.wasClearing,scene:s.sceneEvent?.kind,scenePhase:s.sceneEvent?.phase,routeLength:f.route?.length,failedPlans:f.failedPlans,lastBackAt:f.lastBackAt});}
 rows.push({name,seconds:s.time-start,first,span,greeted,outcome:s.inputSession.outcome,phases,trace});console.log(JSON.stringify(rows.at(-1),null,0));writeFileSync('outputs/runtime-checkpoint-50/reproduce-'+(process.argv[2]||'before')+'.json',JSON.stringify(rows,null,2));
}
