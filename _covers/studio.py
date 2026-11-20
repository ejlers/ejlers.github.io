# A small studio: a canvas-grey cove, plain blocks in the site's greys, one device.
import bpy, bmesh, math, sys, json, os
from mathutils import Vector, Euler, Quaternion

def lin(h):
    h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return [x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4 for x in c]+[1]

GREYS={'ink':'#181818','strong':'#464646','muted':'#686868','grey':'#8b8b8b','rule':'#dfdfdf','fill':'#ececec','hover':'#f5f5f5','canvas':'#d9d9d9','paper':'#ffffff'}

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'
    return s

def mat(name, hexc, rough=0.55, metallic=0.0, coat=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=lin(hexc); b.inputs['Roughness'].default_value=rough
    b.inputs['Metallic'].default_value=metallic
    if coat: b.inputs['Coat Weight'].default_value=coat; b.inputs['Coat Roughness'].default_value=0.05
    return m

def screen_mat(name, path, strength=0.92):
    """A lit display under glass: the picture glows, and the glass over it reflects the room."""
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree
    b=nt.nodes['Principled BSDF']
    t=nt.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(path, check_existing=True); t.extension='EXTEND'; t.interpolation='Cubic'
    b.inputs['Base Color'].default_value=(0.004,0.004,0.004,1)
    nt.links.new(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value=strength
    b.inputs['Roughness'].default_value=0.25; b.inputs['Specular IOR Level'].default_value=0.5
    b.inputs['Coat Weight'].default_value=1.0; b.inputs['Coat Roughness'].default_value=0.07
    return m

def glass_mat(name='glass'):
    m=mat(name, '#050505', rough=0.25, coat=1.0); b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Coat Roughness'].default_value=0.07; b.inputs['Specular IOR Level'].default_value=0.5; return m

def tex_mat(name, path, rough=0.5, metallic=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']
    t=nt.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(path, check_existing=True)
    nt.links.new(t.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metallic
    return m

def finish(name, hexc, kind):
    """A grey with a surface: 'concrete', 'lino', 'paint', or 'plain'. Scales are in metres."""
    if kind=='plain': return mat(name, hexc, rough=0.62)
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links
    b=N['Principled BSDF']; tc=N.new('ShaderNodeTexCoord')
    def noise(scale, detail=4, rough=0.55, distortion=0.0, stretch=None):
        n=N.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=scale; n.inputs['Detail'].default_value=detail
        n.inputs['Roughness'].default_value=rough; n.inputs['Distortion'].default_value=distortion
        if stretch:
            mp=N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=stretch; L.new(tc.outputs['Object'], mp.inputs['Vector']); L.new(mp.outputs['Vector'], n.inputs['Vector'])
        else: L.new(tc.outputs['Object'], n.inputs['Vector'])
        return n.outputs['Fac']
    def rng(sock, lo, hi, a=0.0, c=1.0):
        r=N.new('ShaderNodeMapRange'); r.inputs['From Min'].default_value=a; r.inputs['From Max'].default_value=c
        r.inputs['To Min'].default_value=lo; r.inputs['To Max'].default_value=hi; L.new(sock, r.inputs['Value']); return r.outputs['Result']
    def mul(a, bb):
        x=N.new('ShaderNodeMath'); x.operation='MULTIPLY'; L.new(a, x.inputs[0]); L.new(bb, x.inputs[1]); return x.outputs['Value']
    def add(a, bb):
        x=N.new('ShaderNodeMath'); x.operation='ADD'; L.new(a, x.inputs[0]); L.new(bb, x.inputs[1]); return x.outputs['Value']
    def tint(factor):
        mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs['Factor'].default_value=1.0
        mx.inputs['A'].default_value=lin(hexc); L.new(factor, mx.inputs['B']); L.new(mx.outputs['Result'], b.inputs['Base Color'])
    def bump(height, dist):
        bp=N.new('ShaderNodeBump'); bp.inputs['Distance'].default_value=dist; bp.inputs['Strength'].default_value=1.0
        L.new(height, bp.inputs['Height']); L.new(bp.outputs['Normal'], b.inputs['Normal'])
    if kind=='concrete':
        # cast concrete: slow clouding, a sandy grain, a scatter of small pores
        cloud=rng(noise(5, 6, 0.6), 0.91, 1.05, 0.3, 0.7); grain=rng(noise(700, 3, 0.6), 0.955, 1.03)
        pores=rng(noise(230, 2, 0.5), 1.0, 0.80, 0.745, 0.79)
        tint(mul(mul(cloud, grain), pores))
        bump(add(mul(noise(420, 4, 0.65), rng(noise(9,2),0.6,1.0)), mul(rng(noise(230,2,0.5),0.0,-2.0,0.745,0.79), rng(noise(9,2),1,1))), 0.00035)
        L.new(rng(noise(40, 3), 0.72, 0.90), b.inputs['Roughness'])
    elif kind=='lino':
        # linoleum: a soft marbling drawn along one direction, a fine fleck, a low sheen
        marble=rng(noise(7, 5, 0.6, 2.2, stretch=(1.0,0.22,1.0)), 0.90, 1.055, 0.3, 0.7); fleck=rng(noise(900, 2, 0.5), 0.95, 1.04)
        tint(mul(marble, fleck)); bump(noise(1200, 2, 0.5), 0.00006)
        L.new(rng(noise(25, 3), 0.33, 0.47), b.inputs['Roughness'])
    elif kind=='paint':
        # rolled paint on board: the roller's orange peel and barely any colour change
        tint(rng(noise(3, 3, 0.5), 0.97, 1.025)); bump(noise(650, 2, 0.45), 0.00030)
        L.new(rng(noise(60, 2), 0.50, 0.62), b.inputs['Roughness'])
    return m

def link(o):
    bpy.context.scene.collection.objects.link(o); return o

def smooth(o):
    for p in o.data.polygons: p.use_smooth=True

def box(name, size, loc, material, bevel=0.004, rot=(0,0,0)):
    me=bpy.data.meshes.new(name); bm=bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co=Vector((v.co.x*size[0], v.co.y*size[1], v.co.z*size[2]))
    bm.to_mesh(me); bm.free()
    o=link(bpy.data.objects.new(name, me)); o.location=loc; o.rotation_euler=Euler(rot); o.data.materials.append(material)
    if bevel:
        smooth(o); b=o.modifiers.new('bevel','BEVEL'); b.width=bevel; b.segments=6; b.limit_method='ANGLE'; b.harden_normals=True
    return o

def cylinder(name, r, h, loc, material, bevel=0.004, rot=(0,0,0), seg=160):
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r, depth=h)
    bm.to_mesh(me); bm.free()
    o=link(bpy.data.objects.new(name, me)); o.location=loc; o.rotation_euler=Euler(rot); o.data.materials.append(material); smooth(o)
    b=o.modifiers.new('bevel','BEVEL'); b.width=bevel; b.segments=6; b.limit_method='ANGLE'; b.angle_limit=math.radians(40); b.harden_normals=True
    return o

def sphere(name, r, loc, material):
    me=bpy.data.meshes.new(name); bm=bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=96, v_segments=48, radius=r); bm.to_mesh(me); bm.free()
    o=link(bpy.data.objects.new(name, me)); o.location=loc; o.data.materials.append(material); smooth(o); return o

def rounded_slab(name, w, h, t, r, material, seg=14):
    """A slab w x h (in X,Z), thickness t (in Y), rounded outline: a phone body, a laptop half."""
    me=bpy.data.meshes.new(name); bm=bmesh.new(); vs=[]
    for cx,cz,a0 in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
        for i in range(seg+1):
            a=math.radians(a0+90*i/seg); vs.append(bm.verts.new((cx+r*math.cos(a), t/2, cz+r*math.sin(a))))
    f=bm.faces.new(vs); ext=bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=(0,-t,0), verts=[g for g in ext['geom'] if isinstance(g,bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o=link(bpy.data.objects.new(name, me)); o.data.materials.append(material); smooth(o)
    b=o.modifiers.new('bevel','BEVEL'); b.width=min(t*0.3,0.0015); b.segments=4; b.limit_method='ANGLE'; b.angle_limit=math.radians(60); b.harden_normals=True
    return o

def plane_xz(name, w, h, material):
    """A plane in X,Z facing -Y, UVs upright."""
    me=bpy.data.meshes.new(name); bm=bmesh.new(); uv=bm.loops.layers.uv.new()
    co=[(-w/2,0,-h/2),(w/2,0,-h/2),(w/2,0,h/2),(-w/2,0,h/2)]; uvs=[(0,0),(1,0),(1,1),(0,1)]
    f=bm.faces.new([bm.verts.new(c) for c in co])
    for l,u in zip(f.loops,uvs): l[uv].uv=u
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if f.normal.y>0: bmesh.ops.reverse_faces(bm, faces=[f])
    bm.to_mesh(me); bm.free()
    o=link(bpy.data.objects.new(name, me)); o.data.materials.append(material); return o

def rounded_plane_xz(name, w, h, r, material, seg=12):
    """A plane in X,Z facing -Y with rounded corners, UVs upright: a display."""
    me=bpy.data.meshes.new(name); bm=bmesh.new(); uv=bm.loops.layers.uv.new(); vs=[]
    for cx,cz,a0 in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
        for i in range(seg+1):
            a=math.radians(a0+90*i/seg); vs.append(bm.verts.new((cx+r*math.cos(a), 0, cz+r*math.sin(a))))
    f=bm.faces.new(vs)
    for l in f.loops: l[uv].uv=(l.vert.co.x/w+0.5, l.vert.co.z/h+0.5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if f.normal.y>0: bmesh.ops.reverse_faces(bm, faces=[f])
    bm.to_mesh(me); bm.free()
    o=link(bpy.data.objects.new(name, me)); o.data.materials.append(material); return o

def parent(children, name):
    e=link(bpy.data.objects.new(name, None))
    for c in children: c.parent=e
    return e

def slab_device(name, W, H, T, r, tex, frame_hex, border, lip=0.0009, frame_rough=0.32):
    """A metal frame, a sheet of black glass set into its face, and the lit display under the glass.
    Stands in X,Z facing -Y. Returns (rig, display object)."""
    frame=rounded_slab(name+'-frame', W,H,T, r, mat(name+'-metal', frame_hex, rough=frame_rough, metallic=1.0))
    frame.modifiers['bevel'].width=min(T*0.22,0.0013)
    gt=0.0008; glass=rounded_slab(name+'-glass', W-2*lip, H-2*lip, gt, r-lip, glass_mat(name+'-glass')); glass.location=(0,-T/2-0.00025+gt/2,0)
    glass.modifiers['bevel'].width=0.00025
    dw,dh=W-2*lip-2*border, H-2*lip-2*border
    scr=rounded_plane_xz(name+'-display', dw, dh, max(r-lip-border,0.0012), screen_mat(name+'-display', tex)); scr.location=(0,-T/2-0.00029,0)
    return parent([frame,glass,scr], name+'-rig'), scr

def phone(tex):
    """An iPhone of the notch years in proportion: a rounded polished steel band, glass edge to edge,
    the side button on the right, the switch and two volume buttons on the left. No marks, no logos."""
    W,H,T=0.0715,0.1480,0.0078
    rig,scr=slab_device('phone', W,H,T, 0.0105, tex, '#7a7b7e', border=0.0021, lip=0.0008, frame_rough=0.22)
    band=[o for o in rig.children if o.name.startswith('phone-frame')][0]; band.modifiers['bevel'].width=T*0.20; band.modifiers['bevel'].segments=6
    steel=band.data.materials[0]
    for x,z,h in [(W/2,0.025,0.0125),(-W/2,0.044,0.0052),(-W/2,0.031,0.0085),(-W/2,0.0195,0.0085)]:
        b=box('phone-btn', (0.0011,0.0026,h), (x,0,z), steel, bevel=0.0004); b.parent=rig
    return rig, H, T, scr

def monitor(tex):
    """A 16:9 display panel with a thin dark frame: what a simulator screen would be shown on."""
    W=0.56; H=W*9/16+0.004; T=0.011
    rig,scr=slab_device('monitor', W,H,T, 0.007, tex, '#c2c3c5', border=0.0095, lip=0.0014, frame_rough=0.36)
    return rig, H, T, scr

def tablet(tex, W=0.285):
    """A tablet: a satin aluminium frame, glass edge to edge, an even dark border round the display.
    As tall as the picture needs."""
    img=bpy.data.images.load(tex, check_existing=True); lip=0.0012; border=0.0085; T=0.0064
    H=(W-2*lip-2*border)*img.size[1]/img.size[0]+2*lip+2*border
    rig,scr=slab_device('tablet', W,H,T, 0.0125, tex, '#bdbec0', border=border, lip=lip, frame_rough=0.58)
    return rig, W, H, T, scr

def laptop(tex, open_deg=108, alu='#bdbec0'):
    W,D,T=0.3041,0.2150,0.0085; LT=0.0042; R90=math.radians(90)
    m=mat('alu', alu, rough=0.58, metallic=1.0)
    base=rounded_slab('base', W,D,T, 0.011, m); base.rotation_euler=Euler((R90,0,0)); base.location=(0,0,T/2)
    keys=plane_xz('keys', 0.2755, 0.1140, tex_mat('keys', os.path.dirname(tex)+'/keys.png', rough=0.5)); keys.rotation_euler=Euler((-R90,0,0)); keys.location=(0,D/2-0.0095-0.057,T+0.00015)
    pad=plane_xz('pad', 0.128, 0.080, mat('pad','#c6c7c9',rough=0.48,metallic=1.0)); pad.rotation_euler=Euler((-R90,0,0)); pad.location=(0,-D/2+0.0055+0.040,T+0.00015)
    # The lid is hinged behind the base, below its top surface, so the display's lower edge
    # drops down behind the machine when it is open, the way a MacBook's does.
    drop=0.0075; lip=0.0012; gt=0.0006; top=0.0042; chin=0.0100
    img=bpy.data.images.load(tex, check_existing=True); asp=img.size[0]/img.size[1]
    dw=W-2*lip-2*0.0040; dh=dw/asp
    LH=drop+chin+dh+top+lip          # the lid is as tall as the display needs, so the strip under it stays thin
    lid=rounded_slab('lid', W,LH,LT, 0.011, m); lid.location=(0,0,LH/2-drop)
    glass=rounded_slab('lid-glass', W-2*lip, LH-2*lip, gt, 0.011-lip, glass_mat('lid-glass')); glass.location=(0,-LT/2-0.0002+gt/2,LH/2-drop); glass.modifiers['bevel'].width=0.0002
    scr=plane_xz('lap-display', dw, dh, screen_mat('lap-display', tex)); scr.location=(0,-LT/2-0.00024, LH-drop-lip-top-dh/2)
    hinge=parent([lid,glass,scr],'hinge'); hinge.location=(0,D/2+LT/2+0.0012,T-0.0025); hinge.rotation_euler=Euler((math.radians(-(open_deg-90)),0,0))
    barrel=cylinder('barrel', 0.0036, W*0.80, (0,D/2+0.0010,T-0.0030), mat('barrel','#1f1f21',rough=0.45,metallic=0.6), bevel=0.0005, rot=(0,R90,0), seg=48)
    return parent([base,keys,pad,hinge,barrel],'laptop-rig'), W, D, scr

def projection(name, tex, w, strength=1.0, feather=0.004):
    """An image thrown on a wall by a projector: light on the surface, nothing more. No frame, no glass,
    no thickness; the edge is a little soft, and the picture lights the floor in front of it."""
    img=bpy.data.images.load(tex, check_existing=True); h=w*img.size[1]/img.size[0]
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links
    for n in list(N): N.remove(n)
    out=N.new('ShaderNodeOutputMaterial'); em=N.new('ShaderNodeEmission'); tr=N.new('ShaderNodeBsdfTransparent'); mix=N.new('ShaderNodeMixShader')
    t=N.new('ShaderNodeTexImage'); t.image=img; t.extension='EXTEND'; t.interpolation='Cubic'
    tc=N.new('ShaderNodeTexCoord'); sep=N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['UV'], sep.inputs['Vector'])
    def edge(sock, f):
        a=N.new('ShaderNodeMath'); a.operation='SUBTRACT'; a.inputs[0].default_value=1.0; L.new(sock, a.inputs[1])
        mn=N.new('ShaderNodeMath'); mn.operation='MINIMUM'; L.new(sock, mn.inputs[0]); L.new(a.outputs[0], mn.inputs[1])
        d=N.new('ShaderNodeMath'); d.operation='DIVIDE'; d.use_clamp=True; L.new(mn.outputs[0], d.inputs[0]); d.inputs[1].default_value=f; return d.outputs[0]
    al=N.new('ShaderNodeMath'); al.operation='MULTIPLY'; L.new(edge(sep.outputs['X'], feather), al.inputs[0]); L.new(edge(sep.outputs['Y'], feather*w/h), al.inputs[1])
    L.new(t.outputs['Color'], em.inputs['Color']); em.inputs['Strength'].default_value=strength
    L.new(al.outputs[0], mix.inputs['Fac']); L.new(tr.outputs[0], mix.inputs[1]); L.new(em.outputs[0], mix.inputs[2]); L.new(mix.outputs[0], out.inputs['Surface'])
    return plane_xz(name, w, h, m), h

def sheen(scr, power=0.9, size=1.5, dist=2.4, slide=(0.55,0.0,0.35)):
    """A big diffuser placed where the display's glass reflects it towards the camera, off to one side,
    so the glass carries a soft gradient across display and bezel alike. It lights nothing else."""
    bpy.context.view_layer.update()
    cam=bpy.context.scene.camera.matrix_world.translation; c=scr.matrix_world.translation.copy()
    n=(scr.matrix_world.to_3x3() @ Vector((0,-1,0))).normalized(); v=(cam-c).normalized(); r=(2*v.dot(n)*n-v).normalized()
    o=area('sheen', c+r*dist+Vector(slide), c, size, power); o.visible_diffuse=False; o.visible_camera=False
    # The room's own lamps are kept off the glass, the way a photographer flags them: whatever the
    # angle, the display and its bezel see only this one diffuser, so the picture is never washed out.
    glassy=[scr]+[x for x in scr.parent.children if x.name.endswith('-glass') or 'glass' in x.name]
    coll=bpy.data.collections.new('glass-only')
    for g in glassy: coll.objects.link(g)
    for co in coll.collection_objects: co.light_linking.link_state='EXCLUDE'
    for l in bpy.context.scene.objects:
        if l.type=='LIGHT' and l is not o: l.light_linking.receiver_collection=coll
    return o

def cove(material, depth_back=1.1, radius=0.7, width=14):
    me=bpy.data.meshes.new('cove'); bm=bmesh.new(); prof=[(-8,0)]
    n=40
    for i in range(n+1):
        a=math.radians(-90+90*i/n); prof.append((depth_back-radius+radius*math.cos(a), radius+radius*math.sin(a)))
    prof.append((depth_back,7))
    L=[bm.verts.new((-width/2,y,z)) for y,z in prof]; Rr=[bm.verts.new((width/2,y,z)) for y,z in prof]
    for i in range(len(prof)-1): bm.faces.new([L[i],Rr[i],Rr[i+1],L[i+1]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o=link(bpy.data.objects.new('cove', me)); o.data.materials.append(material); smooth(o); return o

def area(name, loc, target, size, power, color=(1,1,1), shape='RECTANGLE', size_y=None):
    l=bpy.data.lights.new(name,'AREA'); l.shape=shape; l.size=size
    if size_y: l.size_y=size_y
    l.energy=power; l.color=color
    o=link(bpy.data.objects.new(name,l)); o.location=loc
    o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler(); return o

def camera(loc, target, lens=85, fstop=8, focus=None, shift=(0,0)):
    c=bpy.data.cameras.new('cam'); c.lens=lens; c.sensor_width=36; c.shift_x, c.shift_y=shift
    o=link(bpy.data.objects.new('cam',c)); o.location=loc
    o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    c.dof.use_dof=True; c.dof.aperture_fstop=fstop; c.dof.focus_distance=(Vector(focus or target)-Vector(loc)).length
    bpy.context.scene.camera=o; return o

def world(strength=0.35):
    w=bpy.data.worlds.new('w'); w.use_nodes=True; bpy.context.scene.world=w
    bg=w.node_tree.nodes['Background']; bg.inputs['Color'].default_value=(1,1,1,1); bg.inputs['Strength'].default_value=strength

def render(path, res=(1800,1200), samples=160, exposure=0.0, save_only=False):
    s=bpy.context.scene; s.render.resolution_x, s.render.resolution_y=res; s.render.resolution_percentage=100
    s.cycles.samples=samples; s.cycles.use_denoising=True; s.cycles.use_adaptive_sampling=True; s.cycles.adaptive_threshold=0.02
    s.render.threads_mode='AUTO'
    s.view_settings.view_transform='Standard'; s.view_settings.look='None'; s.view_settings.exposure=exposure
    s.render.image_settings.file_format='PNG'; s.render.filepath=path
    s.cycles.max_bounces=6; s.cycles.caustics_reflective=False; s.cycles.caustics_refractive=False
    if save_only:   # a Blender file to open in the app: the scene as built, every picture packed inside it
        s.render.filepath='//'+os.path.basename(path)
        bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=save_only, compress=True); return
    bpy.ops.render.render(write_still=True)

def figure_shadow(name, png, target, az, el, width, dist, spread=2.0, strength=2.0, mirror=False, roll=0.0, only_sun=True, shade=1.0, wall=False, sun_only_cut=False):
    """A low sun, and in its path a cut-out figure the camera never sees: only its shadow lands, on the
    surface at `target`. az/el: where the sun is, in degrees (az 0 = from the camera's side, -Y; 90 = from
    +X). The cut-out stands `dist` metres from the target towards the sun, square to the light, so its
    shadow is its own shape at its own size; `spread` is the sun's angular size, which softens it."""
    a,e=math.radians(az),math.radians(el)
    to_sun=Vector((math.sin(a)*math.cos(e), -math.cos(a)*math.cos(e), math.sin(e))).normalized()
    s=bpy.data.lights.new(name+'-sun','SUN'); s.energy=strength; s.angle=math.radians(spread)
    # the studio's curved backdrop rises far behind everything; a sun from behind would only light its far side
    for o in bpy.context.scene.objects:
        if o.name.startswith('cove'): o.visible_shadow=False
    so=link(bpy.data.objects.new(name+'-sun',s)); so.rotation_euler=(-to_sun).to_track_quat('-Z','Y').to_euler()
    img=bpy.data.images.load(png, check_existing=True); h=width*img.size[1]/img.size[0]
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links
    for n in list(N): N.remove(n)
    out=N.new('ShaderNodeOutputMaterial'); mix=N.new('ShaderNodeMixShader'); tr=N.new('ShaderNodeBsdfTransparent'); df=N.new('ShaderNodeBsdfDiffuse')
    df.inputs['Color'].default_value=(0,0,0,1)
    t=N.new('ShaderNodeTexImage'); t.image=img; t.extension='EXTEND' if wall else 'CLIP'   # wall: the window's frame runs on into a wall, so no light gets round its edge
    mul=N.new('ShaderNodeMath'); mul.operation='MULTIPLY'; mul.inputs[1].default_value=shade; L.new(t.outputs['Color'], mul.inputs[0])   # shade<1: the cut-out lets some light through, so its shadow is lighter
    L.new(mul.outputs[0], mix.inputs['Fac']); L.new(tr.outputs[0], mix.inputs[1]); L.new(df.outputs[0], mix.inputs[2]); L.new(mix.outputs[0], out.inputs['Surface'])
    if wall:   # a much larger plane, the picture in its middle and its edge carried out to all sides
        tc=N.new('ShaderNodeTexCoord'); mp=N.new('ShaderNodeMapping'); mp.inputs['Location'].default_value=(-2.0,-2.0,0); mp.inputs['Scale'].default_value=(5,5,1)
        L.new(tc.outputs['UV'], mp.inputs['Vector']); L.new(mp.outputs['Vector'], t.inputs['Vector'])
        p=plane_xz(name, width*5, h*5, m)
    else:
        p=plane_xz(name, width, h, m)
    if mirror: p.scale.x=-1
    p.location=Vector(target)+to_sun*dist
    p.rotation_euler=(Quaternion(to_sun, math.radians(roll)) @ to_sun.to_track_quat('-Y','Z')).to_euler()
    for attr in ('visible_camera','visible_glossy','visible_transmission','visible_diffuse'): setattr(p, attr, False)
    # sun_only_cut: the sun's light is shaped by the cut-out alone; the device casts no shadow of its own in
    # it (a near sun gives a hard one), so the device's shadow stays the room lamps' soft one
    if sun_only_cut:
        sc=bpy.data.collections.new(name+'-sun-blocker'); sc.objects.link(p)
        for co in sc.collection_objects: co.light_linking.link_state='INCLUDE'
        so.light_linking.blocker_collection=sc
    # the cut-out stands in the sun's way and no other light's: every other lamp ignores it
    if not only_sun: return p
    coll=bpy.data.collections.new(name+'-only-sun'); coll.objects.link(p)
    for co in coll.collection_objects: co.light_linking.link_state='EXCLUDE'
    for o in bpy.context.scene.objects:
        if o.type=='LIGHT' and o is not so: o.light_linking.blocker_collection=coll
    return p

def sun(name, az, el, strength, spread=2.0, dim_room=1.0):
    """A plain sun from az/el (as figure_shadow), for a crisper shadow under a device. dim_room scales the
    room's other lamps (not the screen's sheen), so the scene keeps its brightness."""
    a,e=math.radians(az),math.radians(el)
    to_sun=Vector((math.sin(a)*math.cos(e), -math.cos(a)*math.cos(e), math.sin(e))).normalized()
    for o in bpy.context.scene.objects:
        if o.type=='LIGHT' and o.data.type!='SUN' and not o.name.startswith('sheen'): o.data.energy*=dim_room
    for o in bpy.context.scene.objects:   # the curved backdrop rises behind everything; a sun from behind would only light its far side
        if o.name.startswith('cove'): o.visible_shadow=False
    s=bpy.data.lights.new(name,'SUN'); s.energy=strength; s.angle=math.radians(spread)
    so=link(bpy.data.objects.new(name,s)); so.rotation_euler=(-to_sun).to_track_quat('-Z','Y').to_euler()
    if 'glass-only' in bpy.data.collections: so.light_linking.receiver_collection=bpy.data.collections['glass-only']   # like the room's lamps, never in the screen's glass
    return so
