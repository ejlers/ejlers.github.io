# A contact sheet of all six covers at one quality, for looking at them together.
import sys, os
from PIL import Image, ImageDraw, ImageFont
q=sys.argv[1]; out=sys.argv[2]; d=os.path.dirname(os.path.abspath(__file__))+'/out/'
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',26)
names=[('economic','Visma e-conomic'),('trackman','TrackMan'),('donkey','Donkey Republic'),('theorg','The Org'),('tv2','TV2 Regionerne'),('ok','OK')]
H=560; cap=50; pad=14; rows=[names[:2],names[2:4],names[4:]]
def load(n):
    im=Image.open(d+f'{n}-mix-{q}.'+('jpg' if q!='test' else 'png')).convert('RGB'); return im.resize((int(im.width*H/im.height),H),Image.LANCZOS)
sized={n:load(n) for n,_ in names}
W=max(sum(sized[n].width for n,_ in r)+pad*(len(r)-1) for r in rows)+2*pad
s=Image.new('RGB',(W,len(rows)*(H+cap+pad)+pad),'white'); dr=ImageDraw.Draw(s); y=pad
for r in rows:
    x=pad
    for n,l in r: s.paste(sized[n],(x,y)); dr.text((x,y+H+10),l,fill=(40,40,40),font=f); x+=sized[n].width+pad
    y+=H+cap+pad
s.save(d+out,quality=90); print(s.size)
