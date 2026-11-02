from pathlib import Path
import json,time,subprocess
out=Path('outputs/runtime-checkpoint-36');rows=[]
cases=[('music','让琴声把散落在街角的人慢慢牵到一起。'),('boundary','想多点欢笑，但不要放烟花，也别下雪。'),('roles','小孩玩起来，大人慢慢散步，花房也忙一点。'),('quiet','Give everyone a little room to breathe, and let the tram wait.')]
for id,text in cases:
 body={'poem':text,'state':{'weather':'clear','day_phase':'dusk','occasion':'ordinary','light':'warm','music':'play','street':'wander','festival':'quiet','train':'auto'}};started=time.monotonic()
 command=['curl','-sS','--max-time','35','-w','\n%{http_code}','https://echoing-green-api.dongyuanshun.chatgpt.site/api/decision','-H','Origin: https://ashstarry.github.io','-H','Content-Type: application/json','--data-binary','@-']
 response=subprocess.run(command,input=json.dumps(body).encode(),capture_output=True,check=True).stdout.decode();payload,status=response.rsplit('\n',1)
 if status!='200':raise RuntimeError('Public API returned '+status)
 result=json.loads(payload)
 items=result['plan']['items'];pairs={(x['target'],x['action'])for x in items}
 passed=(('music','play')in pairs and ('street','gather')in pairs)if id=='music'else bool(items)and ('festival','fireworks')not in pairs and ('weather','snow')not in pairs if id=='boundary'else any(t.startswith('resident.child_')or t=='resident.garden_child' for t,a in pairs)and any(t in ['resident.gardener','resident.assistant_gardener']for t,a in pairs)if id=='roles'else ('train','hold')in pairs and ('occasion','quiet')in pairs
 row={'id':id,'text':text,'pass':passed,'request':body,'result':result,'roundtrip_ms':round((time.monotonic()-started)*1000)};rows.append(row);(out/'cloud-verification.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(json.dumps({'id':id,'pass':passed,'items':list(pairs),'ms':result['ms']},ensure_ascii=False))
