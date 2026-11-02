from pathlib import Path
import json,subprocess,time
rows=[]
for name,text,expected,count in [('hang','让风替我保管这份思念。','hang',0),('share','把迟来的谢谢放到邻居手里。','share',3),('read','读一读树边刚挂的纸笺。','read',3),('empty','读一读树边刚挂的纸笺。',None,0),('keep','刚才的纸笺很漂亮，不要再改动。',None,3)]:
 body={'poem':text,'state':{'weather':'clear','day_phase':'dusk','paper_count':count}}
 cmd=['curl','-sS','--max-time','35','-w','\n%{http_code}','https://echoing-green-api.dongyuanshun.chatgpt.site/api/decision','-H','Origin: https://ashstarry.github.io','-H','Content-Type: application/json','--data-binary','@-']
 started=time.monotonic();raw=subprocess.run(cmd,input=json.dumps(body).encode(),capture_output=True,check=True).stdout.decode();payload,status=raw.rsplit('\n',1);r=json.loads(payload);items=r.get('plan',{}).get('items',[]);passed=status=='200'and (any(i['target']=='paper'and i['action']==expected for i in items)if expected else not items);rows.append({'case':name,'request':body,'status':status,'result':r,'pass':passed,'roundtrip_ms':round((time.monotonic()-started)*1000)});Path('outputs/runtime-checkpoint-37/cloud-verification.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(json.dumps({'case':name,'status':status,'pass':passed,'items':[(i['target'],i['action'])for i in items]},ensure_ascii=False))
