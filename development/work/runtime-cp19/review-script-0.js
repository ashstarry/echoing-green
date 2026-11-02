
const lead=1.339;document.querySelectorAll('[data-at]').forEach(b=>b.onclick=()=>{const v=document.querySelector('#mainVideo');v.currentTime=lead+Number(b.dataset.at);v.play();});
