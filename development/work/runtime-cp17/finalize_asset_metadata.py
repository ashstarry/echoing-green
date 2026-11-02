import json,struct,hashlib
from pathlib import Path
root=Path.cwd();assets=root/'app/runtime-cp17/public/assets';p=assets/'town.glb';raw=p.read_bytes();size,typ=struct.unpack_from('<II',raw,12);data=json.loads(raw[20:20+size]);caps=json.loads((assets/'runtime-capabilities.json').read_text());by={e['id']:e for e in caps['entities']}
for n in data.get('nodes',[]):
 e=n.get('extras',{});eid=e.get('entity_id')
 if eid in by:e['runtime_status']='CP17 bounded executors; see runtime-capabilities.json';e['implemented_actions']=by[eid]['enabled']
 if 'rig_status'in e:e['rig_status']='Rest-pose geometry; CP17 runtime animates selected rigid pivots'
for s in data.get('scenes',[]):
 e=s.get('extras',{});e['asset_status']='CP17 rigid-part runtime derivative; no skeletal animation clips';e['source_checkpoint']='CP16 approved geometry'
js=json.dumps(data,separators=(',',':')).encode();js+=b' '*((-len(js))%4);rest=raw[20+size:];new=struct.pack('<4sII',b'glTF',2,12+8+len(js)+len(rest))+struct.pack('<II',len(js),typ)+js+rest;p.write_bytes(new)
r=json.loads((assets/'web-export-record.json').read_text());r.update({'unrigged':False,'skeletal_rigs':False,'rig_type':'Rigid part transforms, procedural motion in browser','logical_nodes_and_parts':434,'web_fps_measured':True,'performance_record':'outputs/runtime-checkpoint-17/browser-qa.json'});(assets/'web-export-record.json').write_text(json.dumps(r,indent=2))
accept=json.loads((root/'outputs/runtime-checkpoint-17/acceptance.json').read_text());master=root/'outputs/art-checkpoint-16/borrowed-wind-town-cp16.blend';sha=hashlib.sha256(master.read_bytes()).hexdigest();print('CP16_SHA256',sha);print('ACCEPTANCE',accept)
