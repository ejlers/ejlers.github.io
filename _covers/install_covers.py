# Put the rendered covers on the Work page (working copy only): a desk version and a 4:3 small-screen version of each.
import re, sys, os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.dirname(HERE)+'/'; O=HERE+'/out/'
# A render is looked for in out/ first (what was just made here), then in masters/ (the finished renders
# kept in the repository), so the site's pictures can be rebuilt without rendering anything.
M=HERE+'/masters/'
def find(name): return next((d+name for d in (O,M) if os.path.exists(d+name)), None)
q=sys.argv[1] if len(sys.argv)>1 else 'mid'
def src(n):
    for qq in (q,'mid','test'):
        for ext in ('jpg','png'):
            f=find(f'{n}-mix-{qq}.{ext}')
            if f: return Image.open(f).convert('RGB'), qq
    raise SystemExit('missing '+n)
# small-screen 4:3: a window cut from the desk version (left edge as a share of the width), or its own photograph
SMALL={'economic':0.105,'trackman':0.118,'donkey':0.02,'theorg':0.111,'tv2':'tv2s','ok':'oks'}
p=R+'work/index.html'; s=open(p).read()
for slug in ['economic','trackman','donkey','tv2','ok','theorg']:
    im,q1=src(slug); big=f'img/work/{slug}/cover-set.jpg'; im.save(R+big,quality=88,optimize=True,progressive=True)
    im.save(R+big[:-4]+'.webp',quality=84,method=6)                # every cover also as a WebP, about a third of the weight; the JPEG is the fallback
    sm=SMALL[slug]
    if isinstance(sm,str): small,q2=src(sm)
    else:
        w,h=im.size; cw=round(h*4/3); x=max(0,min(round(sm*w),w-cw)); small=im.crop((x,0,x+cw,h)); q2=q1
    if small.width>1600: small=small.resize((1600,1200),Image.LANCZOS)
    sp=f'img/work/{slug}/cover-set-small.jpg'; small.save(R+sp,quality=88,optimize=True,progressive=True)
    small.save(R+sp[:-4]+'.webp',quality=84,method=6)
    pat=re.compile(r'(<a class="case [^"]*case--%s"[^>]*>\s*)<span class="case__cover[^"]*">.*?</span>(\s*<span class="case__caption">)'%slug, re.S)
    new=(r'\1<span class="case__cover"><picture>'
         r'<source media="(max-width: 1100px)" type="image/webp" srcset="../%s" width="%d" height="%d">'
         r'<source media="(max-width: 1100px)" srcset="../%s" width="%d" height="%d">'
         r'<source type="image/webp" srcset="../%s" width="%d" height="%d">'
         r'<img %s decoding="async" src="../%s" alt="" width="%d" height="%d"></picture></span>\2')%(
         sp[:-4]+'.webp',small.width,small.height, sp,small.width,small.height, big[:-4]+'.webp',im.width,im.height,
         'fetchpriority="high"' if slug=='economic' else 'loading="lazy"',big,im.width,im.height)
    s,n=pat.subn(new,s); assert n==1,(slug,n); print(slug, im.size, q1, '| small', small.size, q2)
open(p,'w').write(s)

# The header shots: each case page opens on the wide shot of its scene, in three widths for three sizes
# of window. The pages name these files themselves; nothing in the HTML is rewritten here.
CARD_X={'theorg':0.03}        # a card's window slid sideways, as a share of the shot's width, where the device sits off the middle
HEADER={'economic':'economic','trackman':'trackman','donkey':'donkey','theorg':'theorg','tv2':'tv2','ok':'ok'}
for slug,scene in HEADER.items():
    f=next((find(f'{scene}-mix-{qq}-header.jpg') for qq in (q,'mid','test') if find(f'{scene}-mix-{qq}-header.jpg')), None)
    if not f: print(slug,'header: no shot in out/ or masters/, left as it is'); continue
    im=Image.open(f).convert('RGB')
    for w,name in ((3200,'header.jpg'),(2400,'header-2400.jpg'),(1600,'header-1600.jpg')):
        v=im if im.width==w else im.resize((w,w//2),Image.LANCZOS)
        v.save(R+f'img/work/{slug}/{name}',quality=84,optimize=True,progressive=True)
        v.save(R+f'img/work/{slug}/{name[:-4]}.webp',quality=84,method=6)      # a third of the weight; the JPEG stays for browsers without it
    # The share card: the picture a link to the case shows in a message or a feed (1200 by 630). It is the
    # header shot seen closer, because a card is read small: the middle 78% of its height.
    ch=round(im.height*0.78); cw=round(ch*1200/630); x=round((im.width-cw)/2+CARD_X.get(slug,0)*im.width); y=(im.height-ch)//2
    im.crop((x,y,x+cw,y+ch)).resize((1200,630),Image.LANCZOS).save(R+f'img/work/{slug}/card.jpg',quality=88,optimize=True,progressive=True)
    print(slug,'header from',os.path.basename(f))

# The front page's shots: the same scenes pulled further back (SUFFIX=-far in scenes.py, PULL in the
# table below), so the device stands small in open ground and the page can place it clear of the claim
# and the rows. Written as WebP only: every browser that shows the front page's backdrop reads it.
# Also prints where the device's middle is in each shot, as shares of width and height, which is what
# js/site.js needs in its SHOTS table.
FRONT={'economic':'economic','trackman':'trackman','donkey':'donkey','theorg':'theorg','tv2':'tv2','ok':'ok'}
import numpy as np
def device_middle(im):
    a=np.asarray(im.convert('RGB').resize((800,400))).astype(int)
    g=a.mean(axis=2); sat=a.max(axis=2)-a.min(axis=2)
    m=(g<110)|(sat>45)
    ys,xs=np.nonzero(m)
    if len(xs)<50: return 0.5,0.5
    lo=lambda v:np.percentile(v,2); hi=lambda v:np.percentile(v,98)
    return float(round((lo(xs)+hi(xs))/2/800,3)), float(round((lo(ys)+hi(ys))/2/400,3))
for slug,scene in FRONT.items():
    f=next((find(f'{scene}-mix-{qq}-far-header.jpg') for qq in (q,'mid','test') if find(f'{scene}-mix-{qq}-far-header.jpg')), None)
    if not f: print(slug,'front: no shot, left as it is'); continue
    im=Image.open(f).convert('RGB')
    for w,name in ((3200,'front.webp'),(2400,'front-2400.webp')):
        (im if im.width==w else im.resize((w,w//2),Image.LANCZOS)).save(R+f'img/work/{slug}/{name}',quality=84,method=6)
    print(slug,'front from',os.path.basename(f),'device middle',device_middle(im))
