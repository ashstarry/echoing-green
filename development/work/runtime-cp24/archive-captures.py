from pathlib import Path
import gzip,hashlib,json
R=Path.cwd();O=R/'outputs/runtime-checkpoint-24/captures';O.mkdir(exist_ok=True);records=[]
for n in range(1,7):
 src=R/f'work/runtime-cp24/capture-round{n}/browser-mesh-motion.json';dst=O/f'round-{n}.json.gz';h=hashlib.sha256()
 with src.open('rb')as source,gzip.open(dst,'wb',compresslevel=5)as target:
  for chunk in iter(lambda:source.read(1048576),b''):h.update(chunk);target.write(chunk)
 original=h.hexdigest();v=hashlib.sha256()
 with gzip.open(dst,'rb')as source:
  for chunk in iter(lambda:source.read(1048576),b''):v.update(chunk)
 assert v.hexdigest()==original
 records.append({'round':n,'original':str(src.relative_to(R)),'original_bytes':src.stat().st_size,'original_sha256':original,'archive':str(dst.relative_to(R)),'archive_bytes':dst.stat().st_size,'lossless_verified':True})
 print(n,src.stat().st_size,dst.stat().st_size,flush=True)
(O.parent/'capture-archive-index.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
