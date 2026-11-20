import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from studio import *
T=os.path.dirname(os.path.abspath(__file__))+'/tex/'
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
PEOPLE=bool(os.environ.get('PEOPLE'))   # the covers' shadow figures (see shadows.py)
which=ARGS[0]; quality=ARGS[1] if len(ARGS)>1 else 'test'; look=ARGS[2] if len(ARGS)>2 else 'mix'
FLOOR,WALL={'concrete':('concrete','concrete'),'lino':('lino','paint'),'paint':('paint','paint'),'mix':('concrete','paint'),'plain':('plain','plain')}[look]

# THE RULES OF THE SHOOT (set by Carl):
#  1. The device is never covered: nothing in front of it, no part of it sunk into anything.
#  2. It lies flat on a surface or stands against one. It never rests on a corner or an edge.
#  3. No bend in the wall behind it: one flat plane behind the device, no corner, no edge crossing behind it.
#  Also: large flat surfaces, not sculpture; the backdrop stays the backdrop; light greys close in tone,
#  so the device is the foreground; concrete floors, painted walls.
#  Phone placements chosen: A standing against a wall that fills the frame, D lying on the floor from
#  straight above, E lying on a large slab from above at an angle.

def base_set(side=-1, key=None, key_power=40, key_size=0.95, wash=17):
    reset(); world(0.10)
    cove(finish('canvas', '#d6d6d6', 'paint' if WALL!='plain' else 'plain'), depth_back=1.3)
    area('key', key or (0.60*side,-1.7,1.9), (0,0,0.15), key_size, key_power)
    area('fill', (-1.4*side,-1.6,0.9), (0,0,0.1), 2.0, 3)
    area('top', (0.2,0.5,2.3), (0,0,0), 1.5, 3)
    area('wash', (0.0,0.15,2.4), (0,1.3,0.5), 2.2, wash)
    return ({k:finish('f-'+k,v,FLOOR) for k,v in GREYS.items()}, {k:finish('w-'+k,v,WALL) for k,v in GREYS.items()})

def lean(rig, H, Tk, x, wall_y, floor_z, lean_deg=14):
    """Stand a slab on the floor and rest its top edge against a wall."""
    l=math.radians(lean_deg); rig.rotation_euler=Euler((-l,0,0))
    zc=floor_z+(H/2)*math.cos(l)+(Tk/2)*math.sin(l); yc=wall_y-0.0004-(H/2)*math.sin(l)-(Tk/2)*math.cos(l)
    rig.location=(x,yc,zc); return (x,yc,zc)

RES={}

def donkey():
    # lying on a table near its front edge, seen from the front and above; the floor far below
    gf,gw=base_set(side=-1)
    top=0.34; yaw=math.radians(24); H0,W0=0.148,0.0715
    low=(H0/2)*math.cos(yaw)+(W0/2)*math.sin(yaw); edge=-low-0.016          # the edge runs 16 mm in front of the nearest corner
    box('table', (3.4,3.0,0.05), (0,edge+1.5,top-0.025), gf['fill'], bevel=0.002)
    box('floor', (5.0,5.0,0.02), (0,0,0.01), gf['rule'], bevel=0.002)
    rig,H,Tk,scr=phone(T+'donkey.png'); rig.rotation_euler=Euler((math.radians(-90),0,yaw),'XYZ'); c=(0.0,0.0,top+Tk/2); rig.location=c
    camera((0.09,-0.25,top+0.66),(0.006,-0.012,top), lens=85, fstop=8, focus=c); sheen(scr, slide=(-0.6,0.3,0))
    if PEOPLE:   # a bicycle parked beside the table: the shadow of its front wheel and handlebar across the top
        figure_shadow('bike', T+'shadows/bike.png', (0.21, 0.03, top+0.001), az=70, el=55, width=0.34, dist=0.06, spread=1.5, strength=float(os.environ.get('SUN','0.6')))
RES['donkey']=(1920,1280)

def tv2():
    # D: lying on the floor, from straight above, a panel's soft shadow across the floor
    # (the lamp stands further off for the header shot, as in tv2s below, and for the same reason)
    far=1.7 if os.environ.get('HEADER') else 1.0
    gf,gw=base_set(side=1, key=(1.5*far,-0.5*far,0.75*far), key_size=0.35*far, key_power=34*far*far)
    box('floor', (3.0,3.0,0.03), (0,0,0.015), gf['fill'], bevel=0.0015)
    box('panel', (0.035,1.6,0.9), (0.36,0.62,0.48), gw['hover'], bevel=0.0015, rot=(0,0,math.radians(28)))
    rig,H,Tk,scr=phone(T+'tv2.png'); rig.rotation_euler=Euler((math.radians(-90),0,math.radians(-18)),'XYZ'); rig.location=(0.0,0.0,0.03+Tk/2)
    camera((0.0,-0.08,0.60),(0.0,0.0,0.03), lens=85, fstop=8); sheen(scr, slide=(-0.7,0.3,0))
    if PEOPLE:   # morning: the window's light across the floor, the phone in one pane of it
        figure_shadow('window', T+'shadows/window.png', (0.10, 0.09, 0.031), az=70, el=40, width=0.55, dist=0.10, spread=1.5, strength=float(os.environ.get('SUN','0.6')))
RES['tv2']=(1440,1800)

def ok():
    # E: lying on a large slab, from above at an angle
    gf,gw=base_set(side=-1)
    box('slab', (1.6,1.1,0.06), (0.45,0.25,0.03), gf['fill'], bevel=0.002, rot=(0,0,math.radians(-12)))
    box('under', (3.0,3.0,0.02), (0,0,0.01), gf['rule'], bevel=0.002)
    rig,H,Tk,scr=phone(T+'ok.png'); rig.rotation_euler=Euler((math.radians(-90),0,math.radians(16)),'XYZ'); rig.location=(0.10,0.06,0.06+Tk/2)
    camera((-0.020,-0.285,0.40),(0.112,0.058,0.06), lens=85, fstop=8); sheen(scr, slide=(-0.6,0.2,0))
RES['ok']=(1440,1800)

def theorg():
    # The dashboard on a tablet on a table, seen from straight above so nothing is skewed.
    # The whole tablet is in the frame. It is turned a few degrees, and its lower left corner
    # hangs just over the table's edge (Carl's call: an exception to "never on an edge", and only a little).
    # lit from high overhead, so the thin tablet throws only a short, soft shadow
    gf,gw=base_set(side=-1, key=(-0.40,-0.50,2.55), key_size=1.1, key_power=20)
    top=0.42; yaw=math.radians(5); th=math.radians(-9); D=1.3; over=0.014
    rig,W,H,Tk,scr=tablet(T+'theorg.png')
    px,py=0.030,0.034
    phi=yaw-th; low=(W/2)*math.sin(phi)+(H/2)*math.cos(phi); off=D/2-(low-over)
    box('table', (3.0,D,0.045), (px-off*math.sin(th), py+off*math.cos(th), top-0.0225), gf['fill'], bevel=0.002, rot=(0,0,th))
    box('floor', (5.0,5.0,0.02), (0,0,0.01), gf['rule'], bevel=0.002)
    rig.rotation_euler=Euler((math.radians(-90),0,yaw),'XYZ'); rig.location=(px,py,top+Tk/2)
    camera((0.0,-0.035,top+0.90),(0.0,0.0,top), lens=70, fstop=8); sheen(scr, power=0.6, slide=(-0.6,0.2,0))
    if PEOPLE:   # a team standing round the far side of the table: their heads and shoulders reach in from the top
        figure_shadow('team', T+'shadows/team.png', (0.03, 0.235, top+0.001), az=180, el=40, width=0.36, dist=0.12, spread=2.5, strength=float(os.environ.get('SUN','0.6')))
RES['theorg']=(1920,1280)

def trackman():
    # Not a device: the simulator's picture projected on a wall. Photographed the way a room is:
    # the camera is level, so every vertical stays vertical, and stands a little to one side.
    # The picture sits in the middle of the wall with air above it and a good strip of floor below.
    gf,gw=base_set(side=1, key=(0.5,-2.6,2.3), key_size=1.6, key_power=58, wash=9)
    box('floor', (7.0,3.7,0.04), (0,-0.65,0.02), gf['fill'], bevel=0.0015)
    K=1.215; CX,CY,CZ=-0.26,-1.10,0.30    # wall and picture pushed back from the camera by K and enlarged by K: the picture keeps its place and size in the frame, the floor line climbs up to its bottom edge
    box('wall', (7.0,0.035,2.0), (0,CY+1.30*K+0.0175,1.04), gw['hover'], bevel=0.0015)
    pic,h=projection('projection', T+'trackman.png', 0.455*K, strength=1.1, feather=0.0006); pic.location=(CX+0.26*K,CY+1.2996*K-0.0002,CZ-0.21*K+h/2)
    # seen from the left: the screen's left side is nearest and the wall runs away to the right, so the
    # wall faces the floor on the right, where the radar stands looking back at the screen
    camera((-0.26,-1.10,0.30),(0.10,0.20,0.30), lens=62, fstop=8, shift=(-0.09,-0.165))   # the frame slid left, so screen and radar sit centred together
    if PEOPLE:   # the shadow of a golfer at the top of the backswing, cast on the wall left of the screen
        figure_shadow('golfer', T+'shadows/golfer.png', (0.56, CY+1.30*K-0.002, 0.04+0.110), az=-35, el=16, width=0.17, dist=0.16, spread=2.5, strength=float(os.environ.get('SUN','0.6')))
RES['trackman']=(2400,1350)

def economic():
    # wide: the laptop on the floor seen a little from above, the wall filling the frame behind it
    gf,gw=base_set(side=1)
    box('floor', (3.8,1.2,0.04), (0,0.0,0.02), gf['fill'], bevel=0.0015)
    box('wall', (3.8,0.035,1.8), (0,0.52,0.94), gw['rule'], bevel=0.0015)
    rig,W,D,scr=laptop(T+'economic-lap.png', open_deg=106)
    rig.location=(-0.02,0.10,0.04); rig.rotation_euler=Euler((0,0,math.radians(12)))
    camera((0.38,-0.97,0.36),(-0.02,0.12,0.150), lens=62, fstop=8, shift=(0,-0.052)); sheen(scr, power=0.5, slide=(0.9,0,0.3))
    if PEOPLE:   # someone leaning in to look, off to the right: their shadow on the wall beside the laptop
        figure_shadow('leaning', T+'shadows/leaning.png', (0.33, 0.5025-0.002, 0.30), az=-22, el=12, width=0.38, dist=0.12, spread=2.5, strength=float(os.environ.get('SUN','0.6')), mirror=True)
RES['economic']=(2400,1350)

# --- Small-screen versions --------------------------------------------------------------------
# Below the columns every cover is the same shape (4:3) and every subject takes a similar share of
# its frame. Four of them are cut from the desk versions; the two upright phone covers cannot be
# cut to a lying shape without losing the phone, so they are photographed again, the same sets
# and light, the camera further back.

def tv2s():
    # The lamp stands low and near. In the wider header frame the table reaches closer to it and burns out,
    # so there it stands further off along the same line, larger and stronger by the same measure: the
    # light on the phone is the same, and it falls evenly across the rest.
    far=1.7 if os.environ.get('HEADER') else 1.0
    gf,gw=base_set(side=1, key=(1.5*far,-0.5*far,0.75*far), key_size=0.35*far, key_power=34*far*far)
    box('floor', (3.0,3.0,0.03), (0,0,0.015), gf['fill'], bevel=0.0015)
    box('panel', (0.035,1.6,0.9), (0.36,0.62,0.48), gw['hover'], bevel=0.0015, rot=(0,0,math.radians(28)))
    rig,H,Tk,scr=phone(T+'tv2.png'); rig.rotation_euler=Euler((math.radians(-90),0,math.radians(-18)),'XYZ'); rig.location=(0.0,0.0,0.03+Tk/2)
    camera((0.0,-0.09,0.03+0.70),(0.0,0.0,0.03), lens=85, fstop=8); sheen(scr, slide=(-0.7,0.3,0))
RES['tv2s']=(1600,1200)

def oks():
    gf,gw=base_set(side=-1)
    box('slab', (1.6,1.1,0.06), (0.45,0.25,0.03), gf['fill'], bevel=0.002, rot=(0,0,math.radians(-12)))
    box('under', (3.0,3.0,0.02), (0,0,0.01), gf['rule'], bevel=0.002)
    rig,H,Tk,scr=phone(T+'ok.png'); rig.rotation_euler=Euler((math.radians(-90),0,math.radians(16)),'XYZ'); rig.location=(0.10,0.06,0.06+Tk/2)
    camera((-0.053,-0.337,0.455),(0.100,0.062,0.06), lens=85, fstop=8); sheen(scr, slide=(-0.6,0.2,0))
RES['oks']=(1600,1200)

globals()[which]()

# --- The header shot ------------------------------------------------------------------------------
# A case page opens on its cover, edge to edge of the window, and windows come in every shape. So the
# header is the same scene in a 2:1 frame, pulled back: the device keeps clear of every edge, the extra
# is plain wall and floor, and a wide or a flat window can crop into it without touching the work.
# HEADER=1 turns it on; PULL is how far back (1 = the device as large as on the wall, per frame height).
PULL={'economic':0.80,'trackman':0.82,'donkey':0.80,'theorg':0.80,'tv2':1.0,'ok':1.0,'tv2s':0.80,'oks':0.80}
HEADER=bool(os.environ.get('HEADER'))
if HEADER:
    c=bpy.context.scene.camera.data; w,h=RES[which]; k=float(os.environ.get('PULL') or PULL.get(which,0.8))*(max(w,h)/h)/2.0
    c.lens*=k; c.shift_x*=k; c.shift_y*=k            # the lens and the frame's slide are both counted in the frame's longer side
    RES[which]=(3200,1600)

# --- Focus: measure it, and optionally set it from the display itself --------------------------
def _display():
    for o in bpy.context.scene.objects:
        if o.name.endswith('-display') or o.name=='projection': return o
def _depths(o):
    bpy.context.view_layer.update(); cam=bpy.context.scene.camera; inv=cam.matrix_world.inverted()
    pts=[o.matrix_world @ Vector(c) for c in o.bound_box]
    return sorted(-(inv @ p).z for p in pts), -(inv @ o.matrix_world.translation).z
def focus_report(tag=''):
    cam=bpy.context.scene.camera; c=cam.data; w,h=RES[which]; f=c.lens; N=c.dof.aperture_fstop; s_=c.dof.focus_distance*1000
    ds,dc=_depths(_display()); pxmm=max(w,h)/36.0
    blur=lambda d: (f*f/N)*abs(d*1000-s_)/(d*1000*(s_-f))*pxmm
    print(f"FOCUS {which:9s}{tag} f/{N:<4g} lens {f:g}mm  focus at {s_/10:6.1f} cm | display from {ds[0]*100:6.1f} to {ds[-1]*100:6.1f} cm (centre {dc*100:6.1f}) | blur in final pixels: near edge {blur(ds[0]):4.1f}, centre {blur(dc):4.1f}, far edge {blur(ds[-1]):4.1f}")
# How each cover is focused. The focus always goes on the display itself, at the depth that blurs its
# nearest and farthest part equally; the aperture follows the angle: the steeper the device lies to
# the camera, the smaller the aperture, so the work is sharp and the table still falls off like a photograph.
# Covers not listed face the camera squarely enough to stay at f/8 with their own focus.
APERTURE={'economic':11,'trackman':11,'tv2':16,'tv2s':16,'donkey':16,'ok':22,'oks':22}
if os.environ.get('FOCUS')=='display' or (which in APERTURE and os.environ.get('FOCUS')!='asbuilt'):
    ds,dc=_depths(_display()); n,fr=ds[0],ds[-1]
    bpy.context.scene.camera.data.dof.focus_distance=2*n*fr/(n+fr)      # the plane that blurs the near and far edge equally
    if which in APERTURE: bpy.context.scene.camera.data.dof.aperture_fstop=APERTURE[which]
if os.environ.get('FSTOP'): bpy.context.scene.camera.data.dof.aperture_fstop=float(os.environ['FSTOP'])
suffix=os.environ.get('SUFFIX','')+('-people' if PEOPLE else '')+('-header' if HEADER else '')
if quality=='focus':
    focus_report(' '+(os.environ.get('FOCUS','as-is')+' f/'+os.environ.get('FSTOP','-'))+' ')
    sys.exit(0)
out=os.path.dirname(os.path.abspath(__file__))+f'/out/{which}-{look}-{quality}{suffix}.png'
w,h=RES[which]; k,spp={'test':(3/8,32),'mid':(0.7,80),'final':(1,150)}[quality]
render(out, res=(int(w*k),int(h*k)), samples=spp)
# the lens and the film: a faint glow around the brightest parts and a fine grain over everything
from PIL import Image, ImageFilter
import numpy as np
im=Image.open(out).convert('RGB'); a=np.asarray(im).astype('float32')
hi=np.clip((a-225)/30,0,1)*255; glow=np.asarray(Image.fromarray(hi.astype('uint8')).filter(ImageFilter.GaussianBlur(im.width/160))).astype('float32')
a=a+glow*0.07; rng=np.random.default_rng(7); g=rng.normal(0,1.5,a.shape[:2])[...,None]; a=np.clip(a+g,0,255)
Image.fromarray(a.astype('uint8')).save(out.replace('.png','.jpg'), quality=93)
print('saved',out)
