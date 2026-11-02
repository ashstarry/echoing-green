const button=document.querySelector('#run'),status=document.querySelector('#status'),frame=document.querySelector('#town');
button.onclick=async()=>{button.disabled=true;try{const t=frame.contentWindow.__town;if(!t?.ready)throw Error('小镇尚未加载');t.setCaptureMode(true);const results=[];
 for(const quality of ['smooth','fine','smooth']){frame.contentDocument.querySelector(`[data-quality="${quality}"]`).click();t.reset();t.apply({festival:'quiet'});t.advance(500);const gl=t.renderer.getContext();for(let i=0;i<8;i++){t.render();gl.finish();}const samples=[];
  for(let i=0;i<60;i++){const before=performance.now();t.stepOnly();t.renderer.info.reset();t.render();gl.finish();samples.push(performance.now()-before);if(i%10===9){status.textContent=`${quality} ${i+1}/60`;await new Promise(r=>setTimeout(r,0));}}
  const sorted=samples.slice().sort((a,b)=>a-b);results.push({quality,pixelRatio:t.renderer.getPixelRatio(),canvas:[t.renderer.domElement.width,t.renderer.domElement.height],mean_ms:samples.reduce((a,b)=>a+b,0)/samples.length,median_ms:sorted[30],p95_ms:sorted[56],calls:t.renderer.info.render.calls,triangles:t.renderer.info.render.triangles,samples});
 }
 const data={date:new Date().toISOString(),viewport:[frame.clientWidth,frame.clientHeight],results,scope:'Same seeded world, one simulation step and full rendering per sample; GPU finish included. 60 samples per mode in smooth/fine/smooth order. This is render-cost measurement, not browser animation FPS or phone hardware performance.'};
 const r=await fetch('/qa-perf-result',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});if(!r.ok)throw Error(await r.text());status.textContent=JSON.stringify(data,null,2);
}catch(e){status.textContent=e.message;button.disabled=false;}};
