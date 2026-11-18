# Put the rendered covers on the Work page (working copy only): a desk version and a 4:3 small-screen version of each.
import re, sys, os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.dirname(HERE)+'/'; O=HERE+'/out/'
q=sys.argv[1] if len(sys.argv)>1 else 'mid'
def src(n):
    for qq in (q,'mid','test'):
        for ext in ('jpg','png'):
            f=O+f'{n}-mix-{qq}.{ext}'
            if os.path.exists(f): return Image.open(f).convert('RGB'), qq
    raise SystemExit('missing '+n)
# small-screen 4:3: a window cut from the desk version (left edge as a share of the width), or its own photograph
SMALL={'economic':0.105,'trackman':0.118,'donkey':0.02,'theorg':0.111,'tv2':'tv2s','ok':'oks'}
p=R+'work/index.html'; s=open(p).read()
for slug in ['economic','trackman','donkey','tv2','ok','theorg']:
    im,q1=src(slug); big=f'img/work/{slug}/cover-set.jpg'; im.save(R+big,quality=88,optimize=True,progressive=True)
    sm=SMALL[slug]
    if isinstance(sm,str): small,q2=src(sm)
    else:
        w,h=im.size; cw=round(h*4/3); x=max(0,min(round(sm*w),w-cw)); small=im.crop((x,0,x+cw,h)); q2=q1
    if small.width>1600: small=small.resize((1600,1200),Image.LANCZOS)
    sp=f'img/work/{slug}/cover-set-small.jpg'; small.save(R+sp,quality=88,optimize=True,progressive=True)
    pat=re.compile(r'(<a class="case [^"]*case--%s"[^>]*>\s*)<span class="case__cover[^"]*">.*?</span>(\s*<span class="case__caption">)'%slug, re.S)
    new=(r'\1<span class="case__cover"><picture><source media="(max-width: 1100px)" srcset="../%s" width="%d" height="%d">'
         r'<img %s decoding="async" src="../%s" alt="" width="%d" height="%d"></picture></span>\2')%(sp,small.width,small.height,'fetchpriority="high"' if slug=='economic' else 'loading="lazy"',big,im.width,im.height)
    s,n=pat.subn(new,s); assert n==1,(slug,n); print(slug, im.size, q1, '| small', small.size, q2)
open(p,'w').write(s)

# The header shots: each case page opens on the wide shot of its scene, in three widths for three sizes
# of window. The pages name these files themselves; nothing in the HTML is rewritten here.
HEADER={'economic':'economic','trackman':'trackman','donkey':'donkey','theorg':'theorg','tv2':'tv2s','ok':'oks'}
for slug,scene in HEADER.items():
    f=next((O+f'{scene}-mix-{qq}-header.jpg' for qq in (q,'mid','test') if os.path.exists(O+f'{scene}-mix-{qq}-header.jpg')), None)
    if not f: print(slug,'header: no shot in out/, left as it is'); continue
    im=Image.open(f).convert('RGB')
    for w,name in ((3200,'header.jpg'),(2400,'header-2400.jpg'),(1600,'header-1600.jpg')):
        v=im if im.width==w else im.resize((w,w//2),Image.LANCZOS)
        v.save(R+f'img/work/{slug}/{name}',quality=84,optimize=True,progressive=True)
        v.save(R+f'img/work/{slug}/{name[:-4]}.webp',quality=84,method=6)      # a third of the weight; the JPEG stays for browsers without it
    print(slug,'header from',os.path.basename(f))
