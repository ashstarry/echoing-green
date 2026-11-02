from pathlib import Path
import json,math
A=Path('app/runtime-cp32/public/assets');nav=json.loads((A/'navigation.json').read_text());sock=json.loads((A/'actor-sockets.json').read_text());old=list(nav['nodes']);grid=nav['grid'];new=[]
fixed=['resident.musician','resident.vendor_bread','resident.vendor_flower','resident.vendor_lamp']
for x in range(15,73):
 for y in range(0,47):
  key=f'{x},{y}'
  if key in grid:continue
  ns=[old[grid[f'{x+dx},{y+dy}']]for dx,dy in[(-1,0),(1,0),(0,-1),(0,1)]if f'{x+dx},{y+dy}'in grid]
  if not ns:continue
  px=round(nav['origin'][0]+x*nav['step'],4);py=round(nav['origin'][1]+y*nav['step'],4)
  if not(-4.6<px<4.32 and -3.55<py<3.3) or math.hypot(px+.27,py+.54)<1.92:continue
  if any(math.hypot(px-sock[k]['origin'][0],py-sock[k]['origin'][1])<.60 for k in fixed):continue
  if py>1.05+.75*(px+3) and px<.7:continue
  if any(abs(p[2]-.654)>.03 for p in ns):continue
  new.append([px,py,.654,x,y])
for p in new:grid[f'{p[3]},{p[4]}']=len(nav['nodes']);nav['nodes'].append(p)
nav['radius']=.27;(A/'navigation.json').write_text(json.dumps(nav,separators=(',',':')));print('Added',len(new),'one-cell plaza edge positions; nodes',len(nav['nodes']))
