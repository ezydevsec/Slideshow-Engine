#!/usr/bin/env python3
"""3D story scenes for @quiet.reps4 (founder 2026-11-18: remake @neuronvisuals' 3D videos for EARND, shot for shot).
Real Blender (bpy) scenes with the mannequin3d stick figures; text and the EARND end card are added in 2D afterwards.

  python3 scenes3d.py <set_dir>        # reads <set_dir>/scene3d.json, writes <set_dir>/<out>

scene3d.json: {"scene": "bricks" | "crowd" | "rooms", "out": "x.mp4", "text": {...}, "endcard": [...], "accent": [255,196,120]}
Frames render at 15 fps (Cycles, 540x960) and are doubled to 30 fps; every frame is cached in <set_dir>/3d/<scene>/.
"""
import json, math, os, random, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FPS_R = 15
RES = (540, 960)


# ------------------------------------------------------------------ custom poses (joint dicts, feet at origin, metres)
def upright(lean=0.0, zh=0.95):
    sh = (0, -math.sin(lean) * 0.5, zh + math.cos(lean) * 0.5)
    J = {"pelvis": (0, 0, zh), "neck": sh, "chest": (0, sh[1] * 0.6, zh + (sh[2] - zh) * 0.62),
         "head": (0, sh[1] - math.sin(lean) * 0.22, sh[2] + 0.22 * math.cos(lean))}
    for s, k in ((-1, "l"), (1, "r")):
        J["hip_" + k] = (s * 0.10, 0, zh); J["shoulder_" + k] = (s * 0.21, sh[1], sh[2] - 0.03)
    return J, sh


def legs_stand(J, zh=0.95):
    for s, k in ((-1, "l"), (1, "r")):
        J["knee_" + k] = (s * 0.12, 0, (zh + 0.08) / 2); J["ankle_" + k] = (s * 0.12, 0, 0.08); J["toe_" + k] = (s * 0.13, -0.14, 0.03)


def arms_down(J, sh):
    for s, k in ((-1, "l"), (1, "r")):
        J["elbow_" + k] = (s * 0.25, sh[1], sh[2] - 0.31); J["hand_" + k] = (s * 0.26, sh[1], sh[2] - 0.62)


def walk_x(ph, direction=1, slump=0.0):
    """Walking along x (side view friendly). direction -1 walks towards -x."""
    J, sh = upright(lean=0.0)
    sw = math.sin(ph * 2 * math.pi) * 0.22
    for s, k in ((-1, "l"), (1, "r")):
        f = s * sw * direction
        J["ankle_" + k] = (f, s * 0.10, 0.08 + max(0, -f) * 0.15); J["toe_" + k] = (f + 0.14 * direction, s * 0.10, 0.03)
        J["knee_" + k] = (f * 0.5 + 0.04 * direction, s * 0.10, 0.5)
        J["elbow_" + k] = (-f * 0.4, s * 0.24, sh[2] - 0.31); J["hand_" + k] = (-f * 0.7 + 0.05 * direction, s * 0.25, sh[2] - 0.6)
    if slump:   # head and shoulders drop forward
        for k in ("neck", "head", "shoulder_l", "shoulder_r", "chest", "elbow_l", "elbow_r", "hand_l", "hand_r"):
            x, y, z = J[k]; J[k] = (x + 0.12 * slump * direction * (z - 0.95) / 0.8, y, z - 0.06 * slump * (z - 0.95) / 0.8)
    return J


def kneel(ph):
    """One knee down, leaning over the bricks in front (towards +x), hands moving a level back and forth."""
    zh = 0.55; lean = 0.9
    J = {"pelvis": (0, 0, zh)}
    sh = (0.36, 0, zh + 0.36); J["neck"] = sh; J["chest"] = (0.2, 0, zh + 0.24); J["head"] = (0.52, 0, zh + 0.46)
    for s, k in ((-1, "l"), (1, "r")):
        J["hip_" + k] = (0, s * 0.10, zh); J["shoulder_" + k] = (0.34, s * 0.18, sh[2] - 0.02)
    J["knee_l"] = (-0.05, -0.12, 0.06); J["ankle_l"] = (-0.42, -0.12, 0.07); J["toe_l"] = (-0.52, -0.12, 0.03)
    J["knee_r"] = (0.32, 0.12, 0.42); J["ankle_r"] = (0.30, 0.12, 0.08); J["toe_r"] = (0.44, 0.12, 0.03)
    dx = math.sin(ph * 2 * math.pi) * 0.05
    for s, k in ((-1, "l"), (1, "r")):
        J["elbow_" + k] = (0.56, s * 0.2, 0.55); J["hand_" + k] = (0.78 + dx, s * 0.12, 0.22)
    return J


def reach(target, ph):
    """Standing, placing a brick: right hand reaches to target (x, y, z) relative to the feet."""
    J, sh = upright(); legs_stand(J)
    J["elbow_l"] = (-0.25, sh[1], sh[2] - 0.31); J["hand_l"] = (-0.26, sh[1], sh[2] - 0.62)
    tx, ty, tz = target
    dx_, dz_ = tx - 0.21, tz - sh[2]; L = math.hypot(dx_, dz_)
    if L > 0.62: tx, tz = 0.21 + dx_ * 0.62 / L, sh[2] + dz_ * 0.62 / L      # arm length
    a = 0.5 - 0.5 * math.cos(ph * 2 * math.pi)
    hx, hz = 0.26 + (tx - 0.26) * a, (sh[2] - 0.55) + (tz - (sh[2] - 0.55)) * a
    J["hand_r"] = (hx, ty, hz); J["elbow_r"] = ((0.21 + hx) / 2 + 0.03, ty * 0.5, (sh[2] + hz) / 2 + 0.06)
    return J


def stand_phone(tilt=0.0):
    J, sh = upright(lean=0.12 + tilt); legs_stand(J)
    for s, k in ((-1, "l"), (1, "r")):
        J["elbow_" + k] = (s * 0.18, sh[1] - 0.12, sh[2] - 0.32); J["hand_" + k] = (s * 0.05, sh[1] - 0.32, sh[2] - 0.22)
    return J


def supine(top=0.55):
    """Lying on the back along x (head at -x), phone held above the face."""
    J = {"head": (-0.72, 0, top + 0.13), "neck": (-0.55, 0, top + 0.12), "chest": (-0.32, 0, top + 0.13), "pelvis": (0.0, 0, top + 0.12)}
    for s, k in ((-1, "l"), (1, "r")):
        y = s * 0.11
        J["hip_" + k] = (0.0, y, top + 0.12); J["knee_" + k] = (0.42, y, top + 0.14); J["ankle_" + k] = (0.82, y, top + 0.1); J["toe_" + k] = (0.86, y, top + 0.24)
        J["shoulder_" + k] = (-0.52, y * 1.7, top + 0.12); J["elbow_" + k] = (-0.42, y * 2.2, top + 0.3); J["hand_" + k] = (-0.62, y * 0.6, top + 0.5)
    return J


def deadlift_j(p):
    import mannequin3d as M
    return M.joints("deadlift", p)


# ------------------------------------------------------------------ scene helpers
def setup(res=RES, samples=12):
    import mannequin3d as M
    sc = M.reset(res); sc.cycles.samples = samples
    return M, sc


def box(bpy, loc, size, material, name=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object
    o.scale = size; o.data.materials.append(material); return o


def cam_at(bpy, loc, target, lens=40):
    from mathutils import Vector
    bpy.ops.object.camera_add(location=loc); cam = bpy.context.object; cam.data.lens = lens
    d = Vector(target) - Vector(loc); cam.rotation_mode = "QUATERNION"; cam.rotation_quaternion = d.to_track_quat("-Z", "Y")
    bpy.context.scene.camera = cam; return cam


def spot(bpy, loc, energy=900, size=40, color=(1, 0.97, 0.92)):
    bpy.ops.object.light_add(type="SPOT", location=loc); L = bpy.context.object
    L.data.energy = energy; L.data.spot_size = math.radians(size); L.data.spot_blend = 0.6; L.data.color = color
    return L


def render_loop(bpy, sc, out_dir, n, update):
    os.makedirs(out_dir, exist_ok=True)
    only = os.environ.get("ONLY")
    for i in range(n):
        if only and i not in [int(v) for v in only.split(",")]: continue
        fp = os.path.join(out_dir, f"f{i:05d}.png")
        if os.path.exists(fp): continue
        update(i, i / FPS_R); sc.render.filepath = fp; bpy.ops.render.render(write_still=True)


# ------------------------------------------------------------------ scene 1: perfectionist vs action taker (bricks)
def scene_bricks(out_dir, dur, acc):
    import bpy
    M, sc = setup()
    floor = M.mat("floor", (0.03, 0.032, 0.04, 1), rough=0.2)
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 5, 0)); bpy.context.object.data.materials.append(floor)
    brick_m = M.mat("brick", (0.78, 0.74, 0.66, 1), rough=0.8)
    gold = M.mat("gold", tuple(c / 255 for c in acc) + (1,), rough=0.3, emit=0.6)
    spot(bpy, (-1.0, -0.5, 4.5), 700, 34); spot(bpy, (1.0, -0.5, 4.8), 900, 40)
    bpy.ops.object.light_add(type="AREA", location=(0, -4, 3)); A = bpy.context.object; A.data.energy = 90; A.data.size = 6; A.rotation_euler = (math.radians(60), 0, 0)
    cam_at(bpy, (0.35, -6.4, 2.3), (0.35, 0.2, 0.95), lens=32)
    BW, BD, BH = 0.26, 0.13, 0.1
    # perfectionist: one row of 3 bricks; action taker: a growing wall
    p_bricks = [box(bpy, (-1.05 + i * (BW + 0.01), 0.0, BH / 2), (BW, BD, BH), brick_m) for i in range(3)]
    level = box(bpy, (-0.78, 0, BH + 0.03), (0.42, 0.04, 0.04), gold)
    cols, rows = 6, 16
    wall_x0 = 0.55
    slots = []
    for r in range(rows):
        off = (BW / 2) if r % 2 else 0
        for c in range(cols):
            slots.append((wall_x0 + off + c * (BW + 0.01), 0.0, BH / 2 + r * (BH + 0.005)))
    bricks = [box(bpy, (s[0], s[1], -5), (BW, BD, BH), brick_m) for s in slots]
    pf = M.Mannequin(-1.62, tuple(c / 255 for c in acc) + (1,), "stand", style="stick")
    at = M.Mannequin(0.2, tuple(c / 255 for c in acc) + (1,), "stand", style="stick")
    T0, T1 = 1.2, dur - 4.0                   # wall builds from T0 to T1, then he climbs on top
    n_b = len(slots)
    def update(i, t):
        # perfectionist: fixes the same brick forever
        pf.pose(0, 0, J=kneel(t / 1.6))
        level.location.x = -0.80 + math.sin(t / 1.6 * 2 * math.pi) * 0.05
        lift = max(0.0, math.sin(t * 1.3)) * 0.04 if int(t) % 4 == 2 else 0.0
        p_bricks[1].location.z = BH / 2 + lift
        # action taker: bricks pop into place one by one
        k = int(n_b * max(0.0, min(1.0, (t - T0) / (T1 - T0))))
        for j, b in enumerate(bricks):
            if j < k:
                x, y, z = slots[j]; age = (t - (T0 + (T1 - T0) * j / n_b))
                b.location = (x, y, z + max(0.0, 0.15 - age * 0.9))
            else:
                b.location = (slots[j][0], slots[j][1], -5)
        top = slots[min(k, n_b - 1)]
        if t < T1:
            at.pose(0, 0.0, dx=0.0, J=reach((top[0] - 0.2, 0.0, min(top[2] + 0.05, 1.5)), (t * 1.4) % 1.0))
            at.root.location.z = 0
        else:
            h = rows * (BH + 0.005); a = min(1.0, (t - T1) / 1.0)
            at.root.location.x = 0.2 + (1.05 - 0.2) * a; at.root.location.z = h * a
            J, sh = upright(); legs_stand(J); arms_down(J, sh); at.pose(0, 0.0, dx=0.85 * a, J=J); at.root.location.z = h * a
    render_loop(bpy, sc, out_dir, int(dur * FPS_R), update)


# ------------------------------------------------------------------ scene 2: don't follow blindly (crowd and the cliff)
def scene_crowd(out_dir, dur, acc):
    import bpy
    M, sc = setup()
    ground = M.mat("ground", (0.05, 0.052, 0.06, 1), rough=0.35)
    box(bpy, (-4.5, 1.5, -0.5), (12.0, 8.0, 1.0), ground)               # the cliff top ends at x = 1.5
    bandm = M.mat("band", tuple(c / 255 for c in acc) + (1,), rough=0.3, emit=0.8)
    spot(bpy, (0.5, -1.5, 6), 1600, 60); spot(bpy, (-3, 1, 6), 900, 60)
    bpy.ops.object.light_add(type="AREA", location=(2, -5, 3)); A = bpy.context.object; A.data.energy = 140; A.data.size = 8; A.rotation_euler = (math.radians(65), 0, math.radians(20))
    cam_at(bpy, (3.4, -5.0, 2.2), (-0.4, 0.9, 0.7), lens=30)
    random.seed(7)
    people = []
    for r in range(4):
        for c in range(5):
            x0 = -5.6 + c * 1.05 + r * 0.35 + random.uniform(-0.15, 0.15); y0 = -0.2 + r * 0.8
            m = M.Mannequin(x0, (0.8, 0.8, 0.8, 1), "stand", style="stick")
            m.root.location.y = y0
            bpy.ops.mesh.primitive_cylinder_add(radius=0.118, depth=0.045, vertices=24); band = bpy.context.object; band.data.materials.append(bandm)
            people.append(dict(m=m, x0=x0, y0=y0, band=band, ph=random.random(), hero=False, fall=None))
    hero = people[3]; hero["hero"] = True; hero["x0"] = -1.0
    SPEED = 0.55
    def update(i, t):
        for P in people:
            m = P["m"]
            if P["hero"] and t > 3.4:
                tt = t - 3.4
                if tt < 1.2:                                       # stops, takes the band off
                    x = P["x0"] + SPEED * 3.4
                    J, sh = upright(); legs_stand(J)
                    up = min(1.0, tt / 0.8)
                    for s, k in ((-1, "l"), (1, "r")):
                        J["elbow_" + k] = (s * 0.3, -0.05, sh[2] - 0.05 + 0.2 * up); J["hand_" + k] = (s * 0.12, -0.05, sh[2] + 0.18 + 0.1 * up)
                    m.pose(0, 1.2, dx=x - m.x0, J=J); m.root.rotation_euler = (0, 0, 0)
                    P["band"].location = (x, P["y0"], 1.70 + 0.5 * up); P["band"].rotation_euler = (0, 0, 0)
                    if tt > 0.9: P["band"].location = (x + 0.3 * (tt - 0.9) * 4, P["y0"] - 0.4, 2.4 - (tt - 0.9) * 6)
                else:                                              # turns around and walks the other way
                    x = P["x0"] + SPEED * 3.4 - 0.5 * (tt - 1.2)
                    m.pose(0, 1.5, dx=x - m.x0, J=walk_x((t * 1.3) % 1.0, direction=-1))
                    P["band"].location = (x, P["y0"], -5)
                continue
            x = P["x0"] + SPEED * t
            if x < 1.6:
                m.pose(0, 0.0, dx=x - m.x0, J=walk_x((t * 1.3 + P["ph"]) % 1.0)); m.root.location.z = 0; m.root.rotation_euler = (0, 0, 0)
                P["band"].location = (x, P["y0"], 1.68); P["band"].rotation_euler = (0, 0, 0)
            else:
                tf = (x - 1.6) / SPEED
                z = -0.5 * 9.8 * tf * tf * 0.35
                m.pose(0, 0.0, dx=x - m.x0, J=walk_x(P["ph"])); m.root.location.z = z; m.root.rotation_euler = (0, min(1.4, tf * 2.2), 0)
                P["band"].location = (x + 0.4 * min(1, tf * 2.2), P["y0"], 1.68 + z - 0.3 * min(1, tf))
    render_loop(bpy, sc, out_dir, int(dur * FPS_R), update)


# ------------------------------------------------------------------ scene 3: 45 minutes vs no time (two rooms, then the city)
def scene_rooms(out_dir, dur, acc):
    import bpy
    M, sc = setup()
    wallm = M.mat("wall", (0.16, 0.16, 0.19, 1), rough=0.9); floorm = M.mat("rfloor", (0.10, 0.09, 0.09, 1), rough=0.6)
    warm = M.mat("sun", (1.0, 0.72, 0.42, 1), rough=0.5, emit=6.0); night = M.mat("moon", (0.35, 0.45, 0.9, 1), rough=0.5, emit=2.5)
    bedm = M.mat("bed", (0.18, 0.2, 0.32, 1), rough=0.8); metal = M.mat("steel", (0.7, 0.7, 0.75, 1), rough=0.3, metal=1.0)
    kit = M.mat("kit", tuple(c / 255 for c in acc) + (1,), rough=0.35)
    H2 = 3.2                                                   # top room sits H2 above the bottom room
    for zb, win in ((H2, warm), (0.0, night)):
        box(bpy, (0, 1.2, zb - 0.05), (5.0, 3.0, 0.1), floorm)
        box(bpy, (0, 2.7, zb + 1.3), (5.0, 0.1, 2.7), wallm)
        box(bpy, (-2.5, 1.2, zb + 1.3), (0.1, 3.0, 2.7), wallm)
        box(bpy, (0.7, 2.62, zb + 1.55), (0.9, 0.04, 0.8), win)
        bpy.ops.object.light_add(type="AREA", location=(0.7, 2.3, zb + 1.55)); L = bpy.context.object
        L.data.energy = 220 if win is warm else 60; L.data.size = 1.2; L.data.color = (1, 0.75, 0.5) if win is warm else (0.45, 0.55, 1)
        L.rotation_euler = (math.radians(-90), 0, 0)
    box(bpy, (0.9, 1.4, 0.3), (1.9, 1.0, 0.45), bedm); box(bpy, (0.15, 1.4, 0.6), (0.4, 0.8, 0.12), M.mat("pillow", (0.8, 0.8, 0.82, 1)))
    phone2 = box(bpy, (0, 0, -9), (0.08, 0.01, 0.15), M.mat("screen", (0.6, 0.75, 1, 1), emit=3))
    top = M.Mannequin(-0.5, tuple(c / 255 for c in acc) + (1,), "deadlift", style="stick"); top.root.location.y = 1.0
    bot = M.Mannequin(0.0, (0.8, 0.8, 0.8, 1), "stand", style="stick"); bot.root.location.y = 1.4
    phone1 = box(bpy, (0, 0, -9), (0.08, 0.01, 0.15), M.mat("screen1", (0.95, 0.95, 1, 1), emit=2))
    cam_at(bpy, (0.3, -4.6, 3.0), (0.3, 1.2, 3.0), lens=26)
    for m_ in (top, bot): m_.root.scale = (1.25, 1.25, 1.25)
    TA = dur * 0.6                                              # rooms until TA, then the city
    def update(i, t):
        top.root.location.z = H2
        seg = int(t / (TA / 3))
        if seg == 0:   # train
            top.pose(0.5 - 0.5 * math.cos(t * 2 * math.pi / 1.4), 0.4)
        elif seg == 1: # log it
            top.pose(0, 0.4, J=stand_phone()); top.bar.location.z = -9
            for w in top.plates: w.location.z = -9
            phone1.location = (-0.5, 1.0 - 0.3, H2 + 1.25)
        else:          # stretch
            top.pose(0, 0.4, J=kneel(t / 2.0)); phone1.location.z = -9; top.bar.location.z = -9
            for w in top.plates: w.location.z = -9
        bot.pose(0, 0.0, J=supine(0.55)); bot.root.location.x = 0.15
        phone2.location = (0.15 - 0.62, 1.4, 0.55 + 0.56)
    nA = int(TA * FPS_R)
    render_loop(bpy, sc, out_dir, nA, update)
    # ---------------- the city at dusk: both walk the same street
    M, sc = setup()
    w = sc.world.node_tree.nodes["Background"]; w.inputs["Color"].default_value = (0.09, 0.05, 0.14, 1)
    street = M.mat("street", (0.06, 0.06, 0.08, 1), rough=0.3)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 10, 0)); bpy.context.object.data.materials.append(street)
    random.seed(3)
    winm = M.mat("windows", (1.0, 0.78, 0.5, 1), emit=4.0); bld = M.mat("bld", (0.05, 0.05, 0.08, 1), rough=0.9)
    for k in range(16):
        x = -9 + k * 1.2; h = random.uniform(2.5, 9.0); wdt = random.uniform(0.8, 1.1)
        box(bpy, (x, 9, h / 2), (wdt, 1.2, h), bld)
        for r in range(int(h / 0.6)):
            for c in range(2):
                if random.random() < 0.35: box(bpy, (x - 0.2 + c * 0.4, 8.38, 0.5 + r * 0.6), (0.16, 0.02, 0.2), winm)
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 10)); S_ = bpy.context.object; S_.data.energy = 1.2; S_.data.color = (1, 0.6, 0.5); S_.rotation_euler = (math.radians(70), 0, math.radians(-30))
    spot(bpy, (0, -1, 5), 600, 60, (1, 0.85, 0.7))
    a = M.Mannequin(-1.0, tuple(c / 255 for c in acc) + (1,), "stand", style="stick"); b = M.Mannequin(-1.8, (0.75, 0.75, 0.78, 1), "stand", style="stick")
    b.root.location.y = 0.6
    cam_at(bpy, (0.0, -6.0, 1.4), (0.0, 0.5, 1.2), lens=32)
    def update2(i, t):
        a.pose(0, 0.9, dx=0.45 * t, J=walk_x((t * 1.2) % 1.0))
        b.pose(0, 0.0, dx=0.28 * t, J=walk_x((t * 0.8) % 1.0, slump=1.0))
    render_loop(bpy, sc, out_dir + "-city", int((dur - TA) * FPS_R), update2)


SCENES = {"bricks": scene_bricks, "crowd": scene_crowd, "rooms": scene_rooms}

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--render":   # internal: runs inside a fresh process
        job = json.load(open(sys.argv[2]))
        SCENES[job["scene"]](job["out_dir"], job["dur"], job["accent"]); sys.exit(0)
    set_dir = sys.argv[1]
    sp = json.load(open(os.path.join(set_dir, "scene3d.json")))
    out_dir = os.path.join(set_dir, "3d", sp["scene"]); os.makedirs(out_dir, exist_ok=True)
    jf = os.path.join(out_dir, "job.json"); json.dump(dict(scene=sp["scene"], out_dir=out_dir, dur=sp["dur"], accent=sp.get("accent", [255, 196, 120])), open(jf, "w"))
    subprocess.run([sys.executable, os.path.abspath(__file__), "--render", jf], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import compose3d; compose3d.compose(set_dir, sp)
