import json
from PIL import Image,ImageDraw
n=json.load(open('app/runtime-cp17/public/assets/navigation.json'));im=Image.new('RGB',(1000,650),'#162b3a');d=ImageDraw.Draw(im)
def xy(p):return(50+(p[0]+7.2)*60,590-(p[1]+3.6)*60)
for p in n['nodes']:
 x,y=xy(p);d.rectangle((x-4,y-4,x+4,y+4),fill='#87ab80')
for a in n['actors']:
 x,y=xy(a['position']);d.ellipse((x-7,y-7,x+7,y+7),fill='#ff9e73');d.text((x+9,y),a['id'].split('.')[1],fill='white')
im.save('outputs/runtime-checkpoint-17/nav-debug.png')
