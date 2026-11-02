from pathlib import Path
import json,subprocess,time
rows=[]
for name,text,expected,count in [('home','留一盏灯，等晚归的人。','homecoming',3),('prepare','给大家一个值得开心的晚上。','prepare',3),('reopen','雨停了，日子也重新开始吧。','reopen',3),('spring','让春天走进每个角落。','spring',3),('negative','如果明天春风来了再说，现在保持原样。',None,3)]:
 body={'poem':text,'state':{'weather':'clear','day_phase':'dusk','paper_count':count}}
 cmd=['curl','-sS','--max-time','35','-w','\n%{http_code}','https://echoing-green-api.dongyuanshun.chatgpt.site/api/decision','-H','Origin: https://ashstarry.github.io','-H','Content-Type: application/json','--data-binary','@-']
 started=time.monotonic();raw=subprocess.run(cmd,input=json.dumps(body).encode(),capture_output=True,check=True).stdout.decode();payload,status=raw.rsplit('\n',1);r=json.loads(payload);items=r.get('plan',{}).get('items',[]);passed=status=='200'and (any(i['target']=='neighborhood'and i['action']==expected for i in items)if expected else not items);rows.append({'case':name,'request':body,'status':status,'result':r,'pass':passed,'roundtrip_ms':round((time.monotonic()-started)*1000)});Path('outputs/runtime-checkpoint-39/cloud-verification.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(json.dumps({'case':name,'status':status,'pass':passed,'items':[(i['target'],i['action'])for i in items]},ensure_ascii=False))
