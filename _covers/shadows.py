# The figures whose shadows fall across some of the covers. Drawn here as white shapes on black (white
# blocks the light), at a size where a soft shadow keeps them readable. Run once; writes tex/shadows/.
import math, os
from PIL import Image, ImageDraw, ImageFilter
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'tex','shadows')
S=2000
def canvas(w=S,h=S): im=Image.new('L',(w,h),0); return im, ImageDraw.Draw(im)
def limb(d,a,b,r): d.line([a,b],fill=255,width=int(2*r)); [d.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=255) for p in (a,b)]
def body(d,pts,r): [limb(d,pts[i],pts[i+1],r) for i in range(len(pts)-1)]
def head(d,c,r): d.ellipse([c[0]-r,c[1]-r*1.12,c[0]+r,c[1]+r*1.12],fill=255)
def save(im,name): im.filter(ImageFilter.GaussianBlur(3)).save(os.path.join(OUT,name)); print(name, im.size)

# A golfer at the top of the backswing, seen side on: club up behind the head, weight on the back foot.
im,d=canvas(1500,2000)
d.polygon([(560,560),(880,540),(900,640),(860,900),(830,1120),(560,1130),(540,900),(520,650)],fill=255)   # chest to hips, turned
d.ellipse([500,1000,880,1260],fill=255)                       # hips
d.ellipse([735,470,815,580],fill=255)                         # neck
head(d,(790,420),98)
body(d,[(600,1180),(560,1540),(540,1920)],88)                  # back leg, straight
body(d,[(800,1180),(900,1520),(900,1920)],84)                  # front leg, knee in
d.ellipse([430,1880,680,1975],fill=255); d.ellipse([820,1880,1060,1975],fill=255)
body(d,[(600,640),(420,560),(410,330)],62)                     # back arm, elbow out, hands up
body(d,[(820,640),(640,470),(440,330)],58)                     # front arm across to the hands
d.ellipse([380,290,500,400],fill=255)                          # the hands together
limb(d,(450,330),(1020,90),14)                                 # the club, over the shoulder
d.polygon([(1005,70),(1095,45),(1105,95),(1025,115)],fill=255)
save(im,'golfer.png')

# A small team standing together, seen from the front: three people, shoulder to shoulder.
im,d=canvas(2600,1800)
def person(x,top,k):
    head(d,(x,top+150*k),118*k)
    d.rectangle([x-52*k,top+250*k,x+52*k,top+330*k],fill=255)                         # neck
    d.rounded_rectangle([x-300*k,top+300*k,x+300*k,1900],radius=int(210*k),fill=255)  # shoulders and body
for x,top,k in ((620,140,0.97),(1300,40,1.03),(1980,170,0.95)): person(x,top,k)
save(im,'team.png')

# Someone leaning in over a desk, seen from the side: head forward, back curved, a forearm reaching.
im,d=canvas(2000,1400)
d.polygon([(300,1400),(330,900),(450,640),(700,520),(900,560),(980,700),(940,900),(900,1400)],fill=255)
d.ellipse([820,420,900,560],fill=255)
head(d,(930,380),140)
body(d,[(860,760),(1200,980),(1650,1040)],80)
d.ellipse([1610,990,1760,1090],fill=255)
save(im,'leaning.png')

# A window: the frame and its bars block the light, the panes let it through.
im,d=canvas(2000,2400)
d.rectangle([0,0,2000,2400],fill=255)
for x0 in (180,1040):
    for y0 in (200,1240):
        d.rectangle([x0,y0,x0+780,y0+960],fill=0)
save(im,'window.png')

# A bicycle's front: the wheel with its spokes, the fork, and the handlebar.
im,d=canvas(2000,2000)
c=(1000,1250); R=620
d.ellipse([c[0]-R,c[1]-R,c[0]+R,c[1]+R],outline=255,width=70)
for k in range(18):
    a=k*math.pi/9; d.line([c,(c[0]+R*math.cos(a),c[1]+R*math.sin(a))],fill=255,width=9)
limb(d,c,(1000,470),34); limb(d,(1000,470),(1000,330),30)
limb(d,(640,300),(1360,300),30); limb(d,(640,300),(560,380),28); limb(d,(1360,300),(1440,380),28)
save(im,'bike.png')

# A man walking past, side on, mid-stride: one arm forward, one back.
im,d=canvas(1300,2000)
head(d,(700,180),100)
d.ellipse([650,260,740,360],fill=255)                                            # neck
d.polygon([(540,330),(830,320),(860,520),(820,980),(560,990),(520,560)],fill=255)  # coat, shoulders to hips
d.ellipse([540,900,840,1100],fill=255)                                           # hips
body(d,[(650,1050),(470,1480),(330,1900)],78)                                     # back leg, behind
body(d,[(740,1050),(880,1460),(1000,1880)],80)                                    # front leg, reaching
d.ellipse([230,1860,450,1960],fill=255); d.ellipse([940,1840,1160,1940],fill=255)
body(d,[(600,420),(470,700),(400,940)],56)                                       # arm swinging back
body(d,[(800,420),(920,700),(1010,920)],56)                                      # arm swinging forward
save(im,'walker.png')

# The bicycle again, bolder: fewer, thicker spokes and a heavier rim, so it reads as a bike when soft.
im,d=canvas(2000,2000)
c=(1000,1250); R=620
d.ellipse([c[0]-R,c[1]-R,c[0]+R,c[1]+R],outline=255,width=110)
for k in range(8):
    a=k*math.pi/4+0.2; d.line([c,(c[0]+R*math.cos(a),c[1]+R*math.sin(a))],fill=255,width=26)
d.ellipse([c[0]-70,c[1]-70,c[0]+70,c[1]+70],fill=255)
limb(d,c,(1000,470),46); limb(d,(1000,470),(1000,320),40)
limb(d,(600,290),(1400,290),42); limb(d,(600,290),(500,400),38); limb(d,(1400,290),(1500,400),38)
save(im,'bike-bold.png')
