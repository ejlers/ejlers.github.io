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
    if PEOPLE:   # light in the room: sun through leaves outside, dappled across the table
        figure_shadow('dapples', T+'shadows/dapples.png', (0.02, 0.0, top+0.001), az=-19, el=44, width=1.0, dist=0.6, spread=2.2, strength=float(os.environ.get('SUN','0.9')))
RES['donkey']=(1920,1280)

# --- Light in the room, one setting per case -------------------------------------------------------
# Every version of a case (cover, small-screen cut, header shot) takes its light from here, so the light
# can never drift apart between them. Values are figure_shadow's.
TV2_WINDOW=dict(az=70, el=40, spread=3.8, shade=0.7, strength=0.6)
TV2_NEAR=float(os.environ.get('NEAR','0.52'))   # matched by measurement: the shade's contrast on the floor equals the wide shot's

def tv2():
    # D: lying on the floor, from straight above, a panel's soft shadow across the floor
    # (the lamp stands further off for the header shot, as in tv2s below, and for the same reason)
    far=1.7 if os.environ.get('HEADER') else 1.0
    gf,gw=base_set(side=1, key=(1.5*far,-0.5*far,0.75*far), key_size=0.35*far, key_power=34*far*far)
    box('floor', (3.0,3.0,0.03), (0,0,0.015), gf['fill'], bevel=0.0015)
    pnl=box('panel', (0.035,1.6,0.9), (0.36,0.62,0.48), gw['hover'], bevel=0.0015, rot=(0,0,math.radians(28)))
    rig,H,Tk,scr=phone(T+'tv2.png'); rig.rotation_euler=Euler((math.radians(-90),0,math.radians(-18)),'XYZ'); rig.location=(0.0,0.0,0.03+Tk/2)
    camera((0.0,-0.08,0.60),(0.0,0.0,0.03), lens=85, fstop=8); sheen(scr, slide=(-0.7,0.3,0))
    if PEOPLE:   # morning: the window's light across the floor, the phone in one pane of it
        hd=bool(os.environ.get('HEADER'))   # the wide shot needs a larger cut-out further off to cover its floor; the light it makes is the same
        L_=dict(TV2_WINDOW); L_['strength']=float(os.environ.get('SUN',L_['strength']))
        if hd: L_['spread']=0.45   # further off, so a smaller sun makes the same softness on the floor
        else: L_['shade']*=TV2_NEAR   # close up, the same cut-out darkens the floor about twice as much as in the wide shot
        figure_shadow('window', T+'shadows/window.png', (0.10, 0.09, 0.031), width=1.0 if hd else 0.55, dist=0.85 if hd else 0.10, only_sun=False, **L_)
        pnl.visible_shadow=False   # the window gives the light; the panel's shadow would end abruptly in the wide shot, and the tall cover matches it
RES['tv2']=(1440,1800)

def ok():
    # E: lying on a large slab, from above at an angle. FLIP=1 mirrors the whole set-up about the phone,
    # so the camera looks at it from the other side (the screen itself is not mirrored).
    m=-1 if os.environ.get('FLIP') else 1; X=lambda x: 0.10+(x-0.10)*m
    gf,gw=base_set(side=-1*m)
    box('slab', (1.6,1.1,0.06), (X(0.45),0.25,0.03), gf['fill'], bevel=0.002, rot=(0,0,math.radians(-12*m)))
    box('under', (3.0,3.0,0.02), (0,0,0.01), gf['rule'], bevel=0.002)
    rig,H,Tk,scr=phone(T+'ok.png'); rig.rotation_euler=Euler((math.radians(-90),0,math.radians(16*m)),'XYZ'); rig.location=(0.10,0.06,0.06+Tk/2)
    camera((X(-0.020),-0.285,0.40),(X(0.112),0.058,0.06), lens=85, fstop=8); sheen(scr, slide=(-0.6*m,0.2,0))
    # a sun, the room's lamps turned down to match so the picture keeps its brightness
    sun('crisp', az=float(os.environ.get('CRISPAZ',180+10*m)), el=float(os.environ.get('CRISPEL','32')), strength=float(os.environ.get('CRISP','1.0')), spread=3.0, dim_room=float(os.environ.get('CRISPROOM','0.79')))   # from behind: the phone's shadow falls in front of it
RES['ok']=(1440,1800)

def theorg():
    # The dashboard on a tablet on a table, seen from straight above so nothing is skewed.
    # The whole tablet is in the frame. It is turned a few degrees, and its lower left corner
    # hangs just over the table's edge (Carl's call: an exception to "never on an edge", and only a little).
    # lit from high overhead, so the thin tablet throws only a short, soft shadow
    gf,gw=base_set(side=-1, key=(-0.40,-0.50,2.55), key_size=float(os.environ.get('KEYSZ','0.55')), key_power=20)   # a smaller key than before (1.1): the tablet's shadow visible
    top=0.42; yaw=math.radians(5); th=math.radians(-9); D=1.3; over=0.014
    rig,W,H,Tk,scr=tablet(T+'theorg.png')
    px,py=0.030,0.034
    phi=yaw-th; low=(W/2)*math.sin(phi)+(H/2)*math.cos(phi); off=D/2-(low-over)
    box('table', (3.0,D,0.045), (px-off*math.sin(th), py+off*math.cos(th), top-0.0225), gf['fill'], bevel=0.002, rot=(0,0,th))
    box('floor', (5.0,5.0,0.02), (0,0,0.01), gf['rule'], bevel=0.002)
    rig.rotation_euler=Euler((math.radians(-90),0,yaw),'XYZ'); rig.location=(px,py,top+Tk/2)
    camera((0.0,-0.035,top+0.90),(0.0,0.0,top), lens=70, fstop=8); sheen(scr, power=0.6, slide=(-0.6,0.2,0))
    if PEOPLE:   # light in the room: a soft, wide band of sun across the table's far corner, the tablet half in it.
        # From the key lamp's own direction (high, front left), so it agrees with the tablet's shadow.
        figure_shadow('edge', T+'shadows/edge.png', (float(os.environ.get('EX','-0.10')), float(os.environ.get('EY','-0.02')), top+0.001), az=-39, el=float(os.environ.get('EL','58')), width=2.0, dist=0.8, spread=float(os.environ.get('SPREAD','12.0')), strength=float(os.environ.get('SUN','0.9')), roll=float(os.environ.get('ROLL','220')))
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
    if PEOPLE:   # light in the room: a long patch of low sun across the floor in front of the screen
        figure_shadow('opening', T+'shadows/opening.png', (0.10, -0.30, 0.041), az=-62, el=30, width=2.4, dist=0.8, spread=1.5, strength=float(os.environ.get('SUN','2.4')), roll=0)
RES['trackman']=(2400,1350)

def economic():
    # wide: the laptop on the floor seen a little from above, the wall filling the frame behind it
    gf,gw=base_set(side=1)
    box('floor', (3.8,1.2,0.04), (0,0.0,0.02), gf['fill'], bevel=0.0015)
    box('wall', (3.8,0.035,1.8), (0,0.52,0.94), gw['rule'], bevel=0.0015)
    rig,W,D,scr=laptop(T+'economic-lap.png', open_deg=106)
    rig.location=(-0.02,0.10,0.04); rig.rotation_euler=Euler((0,0,math.radians(12)))
    camera((0.38,-0.97,0.36),(-0.02,0.12,0.150), lens=62, fstop=8, shift=(0,-0.052)); sheen(scr, power=0.5, slide=(0.9,0,0.3))
    if PEOPLE:   # light in the room, from the key lamp's side (front right), so it agrees with the laptop's own shadow
        v=os.environ.get('LIGHT','edge')
        if v=='edge':     # one soft edge of shade across the wall, the laptop in the light
            figure_shadow('edge', T+'shadows/edge.png', (-0.30, 0.5025-0.002, 0.55), az=19, el=44, width=2.0, dist=0.6, spread=2.5, strength=float(os.environ.get('SUN','0.9')), roll=-25)
        elif v=='window': # a window's soft light on the wall behind, as on TV2's floor
            figure_shadow('window', T+'shadows/window.png', (0.10, 0.5025-0.002, 0.45), az=19, el=44, width=0.9, dist=0.6, spread=1.2, strength=float(os.environ.get('SUN','0.9')), shade=0.6)
        elif v=='opening':# a single patch of sun on the wall and floor, no frame
            figure_shadow('opening', T+'shadows/opening.png', (0.15, 0.40, 0.25), az=19, el=44, width=1.6, dist=0.6, spread=2.5, strength=float(os.environ.get('SUN','1.2')), roll=10)
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
    pnl=box('panel', (0.035,1.6,0.9), (0.36,0.62,0.48), gw['hover'], bevel=0.0015, rot=(0,0,math.radians(28)))
    if PEOPLE: pnl.visible_shadow=False   # as in tv2(): the window gives the light
    rig,H,Tk,scr=phone(T+'tv2.png'); rig.rotation_euler=Euler((math.radians(-90),0,math.radians(-18)),'XYZ'); rig.location=(0.0,0.0,0.03+Tk/2)
    camera((0.0,-0.09,0.03+0.70),(0.0,0.0,0.03), lens=85, fstop=8); sheen(scr, slide=(-0.7,0.3,0))
    if PEOPLE:   # morning: the window's light across the floor, the phone in one pane of it
        L_=dict(TV2_WINDOW); L_['strength']=float(os.environ.get('SUN',L_['strength'])); L_['shade']*=TV2_NEAR
        figure_shadow('window', T+'shadows/window.png', (0.10, 0.09, 0.031), width=0.55, dist=0.10, only_sun=False, **L_)
RES['tv2s']=(1600,1200)

def oks():
    gf,gw=base_set(side=-1)
    box('slab', (1.6,1.1,0.06), (0.45,0.25,0.03), gf['fill'], bevel=0.002, rot=(0,0,math.radians(-12)))
    box('under', (3.0,3.0,0.02), (0,0,0.01), gf['rule'], bevel=0.002)
    rig,H,Tk,scr=phone(T+'ok.png'); rig.rotation_euler=Euler((math.radians(-90),0,math.radians(16)),'XYZ'); rig.location=(0.10,0.06,0.06+Tk/2)
    camera((-0.053,-0.337,0.455),(0.100,0.062,0.06), lens=85, fstop=8); sheen(scr, slide=(-0.6,0.2,0))
    # a sun from the key lamp's own direction, the room's lamps turned down to match: the phone's shadow a little crisper
    sun('crisp', az=float(os.environ.get('CRISPAZ',190)), el=float(os.environ.get('CRISPEL','32')), strength=float(os.environ.get('CRISP','1.0')), spread=3.0, dim_room=float(os.environ.get('CRISPROOM','0.79')))   # as ok()
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
# Where a scene's sun would lift it, the room's lamps are turned down to make up for it, not the exposure:
# exposure would dim the device's screen with everything else. (Screens light themselves.)
ROOM={'donkey':0.88,'theorg':float(os.environ.get('ROOMK','0.8')),'economic':float(os.environ.get('ROOMK','0.74'))}.get(which) if PEOPLE else None
if ROOM:
    for o in bpy.context.scene.objects:
        if o.type=='LIGHT' and o.data.type!='SUN' and not o.name.startswith('sheen'): o.data.energy*=ROOM
EXPOSURE=float(os.environ.get('EXPO', {'economic':0.0,'trackman':-0.45,'donkey':0.0,'theorg':0.0,'ok':-0.2}.get(which,0))) if PEOPLE else 0.0   # a sun added to a scene lifts it; this brings it back to the cover's own level
w,h=RES[which]; k,spp={'test':(3/8,32),'mid':(0.7,80),'final':(1,150)}[quality]
render(out, res=(int(w*k),int(h*k)), samples=spp, exposure=EXPOSURE)
# the lens and the film: a faint glow around the brightest parts and a fine grain over everything
from PIL import Image, ImageFilter
import numpy as np
im=Image.open(out).convert('RGB'); a=np.asarray(im).astype('float32')
hi=np.clip((a-225)/30,0,1)*255; glow=np.asarray(Image.fromarray(hi.astype('uint8')).filter(ImageFilter.GaussianBlur(im.width/160))).astype('float32')
a=a+glow*0.07; rng=np.random.default_rng(7); g=rng.normal(0,1.5,a.shape[:2])[...,None]; a=np.clip(a+g,0,255)
Image.fromarray(a.astype('uint8')).save(out.replace('.png','.jpg'), quality=93)
print('saved',out)
