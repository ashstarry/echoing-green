import {EN} from './i18n-en.mjs?v=cp29-283b7ff62208';
let locale='en';try{const saved=localStorage.getItem('afterwords.locale.v1');if(saved==='zh'||saved==='en')locale=saved;}catch{}
const cache=new Map(),keys=Object.keys(EN).sort((a,b)=>b.length-a.length),listeners=new Set();
export const getLocale=()=>locale;
export function t(value){const source=String(value??'');if(locale==='zh'||!/[\u3400-\u9fff]/u.test(source))return source;if(cache.has(source))return cache.get(source);
 let result=EN[source];if(result===undefined){
  const timestamp=source.match(/^(\d+:\d+\s+)([\s\S]*)$/);if(timestamp)result=timestamp[1]+t(timestamp[2]);
  else if(/^展开模型 \d+%$/.test(source))result=source.replace('展开模型','Unfolding the model');
  else if(/^\d+ 位居民正在换位置。$/.test(source))result=source.match(/^\d+/)[0]+' residents are moving to new places.';
  else if(/^和.+聊几句$/.test(source))result='Chatting with '+t(source.slice(1,-3));
  else {result=source;for(const key of keys)if(key&&result.includes(key))result=result.split(key).join(EN[key]);result=result.replaceAll('。','. ').replaceAll('；','; ').replaceAll('：',': ').replaceAll('，',', ');}
 }
 cache.set(source,result);if(cache.size>600)cache.delete(cache.keys().next().value);return result;
}
export function writeText(node,source){const text=String(source??'');node.dataset.copy=text;node.textContent=t(text);}
export function writeAttribute(node,name,source){node.dataset['copy'+name.replace(/(^|-)([a-z])/g,(_,a,b)=>b.toUpperCase())]=source;node.setAttribute(name,t(source));}
export function setLocale(next){if(!['zh','en'].includes(next))throw Error('Unknown language');locale=next;try{localStorage.setItem('afterwords.locale.v1',next);}catch{};if(typeof document!=='undefined'){document.documentElement.lang=next==='en'?'en':'zh-CN';for(const node of document.querySelectorAll('[data-copy]'))node.textContent=t(node.dataset.copy);for(const node of document.querySelectorAll('[data-copy-title],[data-copy-placeholder],[data-copy-aria-label]'))for(const[name,key]of [['title','copyTitle'],['placeholder','copyPlaceholder'],['aria-label','copyAriaLabel']])if(node.dataset[key]!==undefined)node.setAttribute(name,t(node.dataset[key]));document.title=next==='en'?'Echoing Green — a little world that responds to your words':'言外 · 说一句话，让小镇回应你';const toggle=document.querySelector('#language');if(toggle){toggle.textContent=next==='zh'?'English':'中文';toggle.setAttribute('aria-label',next==='zh'?'Switch to English':'切换到中文');toggle.lang=next==='zh'?'en':'zh-CN';}}for(const fn of listeners)fn(next);}
export function onLocaleChange(fn){listeners.add(fn);return()=>listeners.delete(fn);}
export function initializeI18n(){const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);const nodes=[];while(walker.nextNode()){const n=walker.currentNode,p=n.parentElement;if(n.textContent.trim()&&p&&!p.children.length&&!['SCRIPT','STYLE','INPUT','TEXTAREA'].includes(p.tagName))nodes.push(p);}for(const p of new Set(nodes))writeText(p,p.textContent);for(const p of document.querySelectorAll('[title],[placeholder],[aria-label]'))for(const name of ['title','placeholder','aria-label'])if(p.hasAttribute(name))writeAttribute(p,name,p.getAttribute(name));const button=document.querySelector('#language');if(button)button.onclick=()=>setLocale(locale==='zh'?'en':'zh');setLocale(locale);}
