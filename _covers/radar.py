# Place the TrackMan radar cut-out on the floor of the finished TrackMan render, in 2D (no re-render).
import sys, os
from PIL import Image, ImageFilter
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))+'/'
O=HERE+'out/'; base_name=sys.argv[1]; relscale=float(sys.argv[2]); relleft=float(sys.argv[3]); relfoot=float(sys.argv[4]); out_name=sys.argv[5]
pull=float(sys.argv[6]) if len(sys.argv)>6 else None                          # given for the header shot: the same PULL the scene was rendered with
os.makedirs(O, exist_ok=True)
base=Image.open(next(d+base_name for d in (O,HERE+'masters/') if os.path.exists(d+base_name))).convert('RGB')    # the raw render, before glow and grain: just made (out/) or kept (masters/)
W,H=base.size
# Size and place are given as on the wall cover (a 16:9 frame). The header shot is the same view pulled
# back in a wider frame, so the wall cover's frame sits in its middle, smaller: Wref by Href.
Href=pull*H if pull else H; Wref=Href*16/9 if pull else W
scale=relscale*Wref/2400; left=round(W/2+(relleft-0.5)*Wref); foot=round(H/2+(relfoot-0.5)*Href)
r=Image.open(HERE+'tex/radar-src.png').convert('RGBA')
a=np.asarray(r).astype('float32'); al=a[...,3]
soft=al<200; al[soft]=np.minimum(255,al[soft]*1.25)                                               # the cut-out's own soft shadow, a little lighter to sit with the scene's
a[...,3]=al; r=Image.fromarray(a.astype('uint8'),'RGBA')
# Put the cut-out into the room's perspective. The radar stands parallel to the wall, so its top and bottom
# edges have to aim at the same vanishing point as the screen's edges. The product picture was taken at the
# radar's own eye level; here the camera stands above it, so both edges must rise towards the right.
x0=round(left-416*scale); y0=round(foot-875*scale)
SHIFT=0.09                                                                # the render's frame is slid this share of its width, so everything sits further right
VP=(W/2+(6.719+SHIFT-0.5)*Wref, 0.5*H-0.165*Wref)                                               # where the wall's horizontal lines meet, from the camera
src=[(435,116),(999,149),(934,676),(415,725)]                            # the radar's back face, measured in the picture: TL, TR, BR, BL
def aim(p_fixed, p_move):
    fx,fy=x0+p_fixed[0]*scale, y0+p_fixed[1]*scale; mx=x0+p_move[0]*scale
    return (p_move[0], ((fy+(VP[1]-fy)*(mx-fx)/(VP[0]-fx))-y0)/scale)
TL=src[0]; TR=aim(TL,src[1]); BL=src[3]
# The two sides lean back together: the bottom left goes left until the left side runs parallel to the right one.
for _ in range(4):
    BR=aim(BL,src[2]); t=(src[3][1]-TL[1])/(BR[1]-TR[1]); BL=(TL[0]+t*(BR[0]-TR[0]), src[3][1])
dst=[TL,TR,BR,BL]
def homography(frm,to):
    M=[];b=[]
    for (x,y),(u,v) in zip(frm,to):
        M.append([x,y,1,0,0,0,-u*x,-u*y]); b.append(u); M.append([0,0,0,x,y,1,-v*x,-v*y]); b.append(v)
    return np.linalg.solve(np.array(M,float),np.array(b,float))
# Room around the picture before it is warped, so the soft shadow is never cut by the picture's own edge,
# and a fade to nothing along the border for good measure.
PAD=200
big=Image.new('RGBA',(r.width+2*PAD,r.height+2*PAD),(0,0,0,0)); big.paste(r,(PAD,PAD)); r=big
P=lambda pts:[(x+PAD,y+PAD) for x,y in pts]
r=r.transform(r.size, Image.PERSPECTIVE, tuple(homography(P(dst),P(src))), Image.BICUBIC)   # PIL wants output->input
A_=np.asarray(r).astype('float32'); hh,ww=A_.shape[:2]; yy,xx=np.mgrid[0:hh,0:ww]
edge=np.minimum.reduce([xx,yy,ww-1-xx,hh-1-yy]); A_[...,3]*=np.clip(edge/120.0,0,1); r=Image.fromarray(A_.astype('uint8'),'RGBA')
x0-=round(PAD*scale); y0-=round(PAD*scale)
print('corners moved (source px): top right up', round(src[1][1]-dst[1][1]), ', bottom right up', round(src[2][1]-dst[2][1]), ', bottom left to the left', round(src[3][0]-dst[3][0]))
w,h=round(r.width*scale),round(r.height*scale); r=r.resize((w,h),Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.9*Wref/2400))   # the floor here is just in front of the focus
im=base.convert('RGBA'); im.alpha_composite(r,(x0,y0)); im=im.convert('RGB')
# the same lens glow and film grain as every other cover
A=np.asarray(im).astype('float32'); hi=np.clip((A-225)/30,0,1)*255
glow=np.asarray(Image.fromarray(hi.astype('uint8')).filter(ImageFilter.GaussianBlur(im.width/160))).astype('float32')
A=A+glow*0.07; g=np.random.default_rng(7).normal(0,1.5,A.shape[:2])[...,None]; A=np.clip(A+g,0,255)
out=Image.fromarray(A.astype('uint8')); out.save(O+out_name,quality=93)
print('radar placed at', (x0,y0), 'size', (w,h))
