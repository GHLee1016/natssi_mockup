"""
낯씨 스탠드형 디바이스 + 앱 목업 — Blender 4.2 이상 / 5.x

만드는 것
  - 낯씨 LED 케어 디바이스(가상 제품, 스탠드형): 원형 LED 헤드, 전면 버튼·슬라이더, 원형 거치대
  - 옆에 세운 폰 1대 (다이어리 화면)
  - 카메라 2개: Cam_pair(디바이스+폰), Cam_device(디바이스 단독 3/4 뷰)

실행
  blender -b -P natssi_device_stand.py          → renders/ 에 PNG 2장
  Blender MCP / 스크립팅 탭에서는 ASSET_DIR를 바꾸고 실행(씬만 생성).
  주의: 현재 씬의 오브젝트를 모두 지웁니다.
"""
import bpy, math, os
from mathutils import Vector

try:
    ASSET_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    ASSET_DIR = os.path.expanduser("~/natssi_mockup")
SCREENS = os.path.join(ASSET_DIR, "screens")
OUT_DIR = os.path.join(ASSET_DIR, "renders")
RENDER = bool(bpy.app.background)
SAMPLES = int(os.environ.get("NATSSI_SAMPLES", 96))
PHONE_SCREEN = os.environ.get("NATSSI_PHONE_SCREEN", "screen_d_diary.png")

ORANGE = (1.0, 0.54, 0.40)


def srgb(c):
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


def reset():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def principled(name, color, rough=0.4, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*srgb(color), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k in ("Coat Weight", "Clearcoat"):
        if k in b.inputs:
            b.inputs[k].default_value = coat
            break
    return m


def emissive(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*srgb(color), 1)
    e.inputs["Strength"].default_value = strength
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


def screen_mat(name, png, strength=0.95):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexImage")
    p = os.path.join(SCREENS, png)
    if os.path.exists(p):
        tex.image = bpy.data.images.load(p)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.05
    fr = nt.nodes.new("ShaderNodeFresnel")
    fr.inputs["IOR"].default_value = 1.25
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(fr.outputs[0], mx.inputs[0])
    nt.links.new(em.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    bk = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bk.inputs["Base Color"].default_value = (0.005, 0.005, 0.006, 1)
    mx2 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tex.outputs["Alpha"], mx2.inputs[0])
    nt.links.new(bk.outputs[0], mx2.inputs[1])
    nt.links.new(mx.outputs[0], mx2.inputs[2])
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(mx2.outputs[0], o.inputs[0])
    return m


def bevel(o, w, seg=8, angle=True):
    md = o.modifiers.new("Bevel", "BEVEL")
    md.width = w
    md.segments = seg
    md.limit_method = "ANGLE" if angle else "NONE"
    bpy.ops.object.shade_smooth()


def box(name, size, bev, mat, loc=(0, 0, 0), seg=10):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    bevel(o, bev, seg, angle=False)
    o.data.materials.append(mat)
    return o


def cyl(name, r, d, mat, loc, rot=(0, 0, 0), verts=96, bev=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    if bev:
        bevel(o, bev, 8)
    else:
        bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    return o


def look_at(o, t):
    o.rotation_euler = (Vector(t) - o.location).to_track_quat("-Z", "Y").to_euler()


def camera(name, loc, target, lens, fstop=11):
    c = bpy.data.cameras.new(name)
    c.lens = lens
    c.dof.use_dof = True
    c.dof.aperture_fstop = fstop
    o = bpy.data.objects.new(name, c)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    look_at(o, target)
    c.dof.focus_distance = (Vector(target) - Vector(loc)).length
    return o


def area(name, loc, target, size, power, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, "AREA")
    d.size = size
    d.energy = power
    d.color = color
    o = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    look_at(o, target)


# ───────── 디바이스 ─────────
def subsurf(o, lv=2):
    m = o.modifiers.new("Subsurf", "SUBSURF")
    m.levels = lv
    m.render_levels = lv
    bpy.ops.object.shade_smooth()


def loft(name, rings, mat, n=48, power=3.0):
    """rings: [(z, rx, ry)] — 둥근 사각(슈퍼타원) 단면을 높이별로 이어 붙인 몸체."""
    import bmesh
    bm = bmesh.new()
    loops = []
    for z, rx, ry in rings:
        vs = []
        for i in range(n):
            t = 2 * math.pi * i / n
            c, s_ = math.cos(t), math.sin(t)
            x = rx * math.copysign(abs(c) ** (2 / power), c)
            y = ry * math.copysign(abs(s_) ** (2 / power), s_)
            vs.append(bm.verts.new((x, y, z)))
        loops.append(vs)
    for a_, b_ in zip(loops, loops[1:]):
        for i in range(n):
            bm.faces.new((a_[i], a_[(i + 1) % n], b_[(i + 1) % n], b_[i]))
    bm.faces.new(list(reversed(loops[0])))
    bm.faces.new(loops[-1])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    subsurf(o, 2)
    o.select_set(False)
    o.data.materials.append(mat)
    return o


def torus(name, R, r, mat, loc, rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=160,
                                     minor_segments=16, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    return o


def label(text, size, mat, loc, y_front=True):
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(90), 0, 0))
    t = bpy.context.active_object
    t.data.body = text
    t.data.size = size
    t.data.extrude = 0.00008
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.materials.append(mat)
    return t


def make_device(M, x=0.0, y=0.0, rot_z=0.0):
    P = []
    X90 = (math.radians(90), 0, 0)
    # ── 거치대: 넓은 받침 + 금속 띠 + 꽂는 컵
    base = cyl("Stand_base", 0.047, 0.013, M["shell"], (0, 0, 0.0065), bev=0.0055, verts=128)
    P.append(base)
    P.append(torus("Stand_band", 0.0468, 0.0011, M["metal"], (0, 0, 0.0032)))
    P.append(loft("Stand_cup", [(0.011, 0.0255, 0.0225), (0.020, 0.0235, 0.0205), (0.034, 0.0215, 0.0185),
                                (0.037, 0.0205, 0.0175)], M["shell"]))
    P.append(cyl("Stand_led", 0.0010, 0.0008, M["status"], (0, -0.0215, 0.018), X90, verts=16))
    # ── 몸체: 아래는 가늘고 위로 갈수록 넓어지는 손잡이
    rings = [(0.030, 0.0145, 0.0120), (0.036, 0.0158, 0.0134), (0.060, 0.0170, 0.0145),
             (0.100, 0.0182, 0.0145), (0.140, 0.0198, 0.0145), (0.165, 0.0218, 0.0145),
             (0.185, 0.0240, 0.0140), (0.196, 0.0240, 0.0130)]
    P.append(loft("Body", rings, M["shell"]))
    # ── 헤드
    hz = 0.203
    head = cyl("Head", 0.0375, 0.031, M["shell"], (0, -0.001, hz), X90, bev=0.011, verts=128)
    subsurf(head, 1)
    P.append(head)
    P.append(torus("Bezel", 0.0318, 0.0021, M["metal"], (0, -0.0166, hz), X90, scale=(1, 1, 0.75)))
    # 렌즈: 살짝 볼록한 스모크 커버
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=0.0302, location=(0, -0.0158, hz))
    lens = bpy.context.active_object
    lens.name = "Lens"
    lens.scale = (1, 0.085, 1)
    bpy.ops.object.shade_smooth()
    lens.data.materials.append(M["lens"])
    P.append(lens)
    # LED: 가운데 1 + 안쪽 6 + 바깥 12 (작은 돔)
    pts = [(0.0, 0.0)]
    pts += [(0.0105 * math.cos(2 * math.pi * i / 6), 0.0105 * math.sin(2 * math.pi * i / 6)) for i in range(6)]
    pts += [(0.0205 * math.cos(2 * math.pi * i / 12 + 0.26), 0.0205 * math.sin(2 * math.pi * i / 12 + 0.26)) for i in range(12)]
    for i, (px, pz) in enumerate(pts):
        rr = (px * px + pz * pz) / (0.0302 ** 2)
        yy = -0.0158 - 0.00257 * math.sqrt(max(0.0, 1 - rr)) + 0.0002
        P.append(torus(f"LED_cup{i}", 0.0021, 0.00045, M["metal_dark"], (px, yy - 0.0001, hz + pz), X90))
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.0019, location=(px, yy, hz + pz))
        d = bpy.context.active_object
        d.name = f"LED{i}"
        d.scale = (1, 0.45, 1)
        bpy.ops.object.shade_smooth()
        d.data.materials.append(M["led_dot"])
        P.append(d)
    # ── 전면 조작부: 오목한 패널 + 전원 버튼 + 강도 로커
    P.append(box("Panel", (0.0150, 0.0016, 0.064), 0.0007, M["panel"], (0, -0.01435, 0.116), seg=4))
    P.append(torus("Power_ring", 0.0056, 0.00055, M["metal"], (0, -0.0152, 0.137), X90))
    P.append(cyl("Power", 0.0050, 0.0022, M["accent"], (0, -0.0152, 0.137), X90, verts=64, bev=0.0008))
    P.append(torus("Power_icon", 0.0020, 0.00028, M["icon"], (0, -0.0164, 0.1367), X90))
    P.append(box("Power_icon_bar", (0.0006, 0.0006, 0.0026), 0.0002, M["icon"], (0, -0.0164, 0.1385), seg=2))
    P.append(box("Rocker", (0.0078, 0.0022, 0.027), 0.00105, M["rocker"], (0, -0.0152, 0.1085), seg=8))
    P.append(label("+", 0.0048, M["icon_dark"], (0, -0.01635, 0.1160)))
    P.append(label("–", 0.0048, M["icon_dark"], (0, -0.01635, 0.1012)))
    for i in range(3):   # 강도 표시등 3칸 (2칸 켜짐)
        P.append(cyl(f"Level{i}", 0.00085, 0.0008, M["status"] if i < 2 else M["off"],
                     (-0.0032 + 0.0032 * i, -0.0151, 0.1255), X90, verts=16))
    P.append(label("natssi", 0.0056, M["logo"], (0, -0.01465, 0.070)))
    # 뒷면 충전 접점(보이지 않는 각도용)
    P.append(cyl("Charge", 0.0016, 0.0008, M["metal"], (0, 0.0148, 0.050), X90, verts=24))

    root = bpy.data.objects.new("Device", None)
    bpy.context.scene.collection.objects.link(root)
    for p_ in P:
        p_.parent = root
    root.location = (x, y, 0)
    root.rotation_euler[2] = math.radians(rot_z)
    return root


def make_phone(M, png, loc, rot_z, tilt=12):
    W, H, T = 0.0715, 0.147, 0.0083
    body = box("Phone", (W, T, H), 0.0095, M["phone"], seg=12)
    bpy.ops.mesh.primitive_plane_add()
    s = bpy.context.active_object; s.name = "Phone_screen"
    s.scale = ((W - 0.0045) / 2, (H - 0.0045) / 2, 1)
    bpy.ops.object.transform_apply(scale=True)
    s.data.materials.append(screen_mat("phone_scr", png))
    s.rotation_euler = (math.radians(90), 0, 0)
    s.location = (0, -T / 2 - 0.0002, 0)
    s.parent = body
    body.location = (loc[0], loc[1], H / 2 * math.cos(math.radians(tilt)) + 0.006)
    body.rotation_euler = (math.radians(-tilt), 0, math.radians(rot_z))
    st = box("Phone_stand", (0.064, 0.05, 0.006), 0.003, M["dock"], (loc[0], loc[1] + 0.01, 0.003), seg=4)
    st.rotation_euler[2] = math.radians(rot_z)


def backdrop(M):
    bpy.ops.mesh.primitive_plane_add(size=1)
    f = bpy.context.active_object; f.name = "Backdrop"
    f.scale = (3, 3, 1); bpy.ops.object.transform_apply(scale=True)
    for v in f.data.vertices:
        v.select = v.co.y > 0.5
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 2)})
    bpy.ops.object.mode_set(mode="OBJECT")
    f.location = (0, -0.6, 0)
    md = f.modifiers.new("Bevel", "BEVEL"); md.width = 0.5; md.segments = 24; md.limit_method = "ANGLE"
    bpy.ops.object.shade_smooth()
    f.data.materials.append(M["floor"])


def setup():
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.samples = SAMPLES
    s.cycles.use_denoising = True
    try:
        s.cycles.device = "GPU"
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.get_devices()
        if not any(d.use for d in prefs.devices if d.type != "CPU"):
            s.cycles.device = "CPU"
    except Exception:
        s.cycles.device = "CPU"
    s.render.resolution_x, s.render.resolution_y = 1600, 2000   # 세로형 제품컷
    s.render.resolution_percentage = int(os.environ.get("NATSSI_SCALE", 100))
    s.view_settings.view_transform = "Standard"
    w = s.world or bpy.data.worlds.new("World")
    s.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (*srgb((0.97, 0.95, 0.93)), 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.14


reset()
M = {
    "shell": principled("Shell", (0.93, 0.925, 0.915), 0.22, 0.0, 0.45),
    "panel": principled("Panel", (0.84, 0.83, 0.82), 0.14, 0.0, 0.8),
    "metal": principled("RoseMetal", (0.96, 0.60, 0.46), 0.24, 1.0),
    "metal_dark": principled("DarkMetal", (0.20, 0.17, 0.16), 0.3, 1.0),
    "accent": principled("Accent", ORANGE, 0.38, 0.0, 0.3),
    "rocker": principled("Rocker", (0.97, 0.965, 0.96), 0.3, 0.0, 0.4),
    "lens": principled("Lens", (0.055, 0.03, 0.03), 0.06, 0.0, 1.0),
    "led_dot": emissive("LEDdot", (1.0, 0.32, 0.22), 3.2),
    "status": emissive("Status", (1.0, 0.62, 0.42), 5),
    "off": principled("Off", (0.70, 0.69, 0.68), 0.4),
    "icon": principled("Icon", (1, 1, 1), 0.4),
    "icon_dark": principled("IconDark", (0.55, 0.53, 0.52), 0.5),
    "seam": principled("Seam", (0.70, 0.69, 0.68), 0.5),
    "logo": principled("Logo", (0.48, 0.46, 0.45), 0.45),
    "dock": principled("Dock", (0.86, 0.84, 0.81), 0.55),
    "phone": principled("PhoneFrame", (0.17, 0.18, 0.2), 0.25, 0.9),
    "floor": principled("Floor", (0.80, 0.74, 0.69), 0.55),
}
setup()
backdrop(M)
make_device(M, 0.05, 0.0, rot_z=-10)
make_phone(M, PHONE_SCREEN, (-0.055, 0.03, 0), rot_z=12)
area("Key", (-0.45, -0.55, 0.65), (0.03, 0, 0.12), 0.9, 6)
area("Fill", (0.6, -0.35, 0.25), (0.03, 0, 0.12), 1.0, 2.2, (1, 0.96, 0.92))
area("Top", (0.05, -0.05, 0.75), (0.05, 0, 0.1), 0.7, 3)
area("Rim", (0.3, 0.5, 0.5), (0.05, 0, 0.15), 0.6, 5, (0.92, 0.95, 1))

cams = {
    "pair":   camera("Cam_pair", (0.0, -0.62, 0.17), (0.0, 0.01, 0.110), 50),
    "device": camera("Cam_device", (0.17, -0.50, 0.19), (0.05, 0.0, 0.118), 62, fstop=8),
    "head":   camera("Cam_head", (0.13, -0.24, 0.215), (0.045, -0.01, 0.168), 70, fstop=5.6),
}
bpy.context.scene.camera = cams["pair"]

if RENDER:
    os.makedirs(OUT_DIR, exist_ok=True)
    only = os.environ.get("NATSSI_SHOTS")
    for k, c in cams.items():
        if only and k not in only.split(","):
            continue
        bpy.context.scene.camera = c
        bpy.context.scene.render.filepath = os.path.join(OUT_DIR, f"natssi_stand_{k}.png")
        bpy.ops.render.render(write_still=True)
        print("[natssi] 렌더 완료:", bpy.context.scene.render.filepath)
