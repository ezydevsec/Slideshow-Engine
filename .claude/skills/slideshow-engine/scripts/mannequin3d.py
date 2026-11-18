"""3D wooden-artist mannequins for the study races and stickman videos (founder 2026-11-18: "make our content 3D").
Real Blender (bpy) scene: charcoal stage, glossy floor, spotlights, ivory ball-jointed mannequins, equipment per exercise.
Motion per exercise: deadlift | squat | curl | calf | press | bench | stand | walk (p = 0..1 through the rep).

  frames = render_race(sides, motion, n_frames, poses_fn, out_dir, res=(720, 1280))
Used by anim_study.py when study.json has "render": "3d".
"""
import math, os
import bpy
from mathutils import Vector

IVORY = (0.86, 0.80, 0.70, 1)


# ------------------------------------------------------------------ pose: joint positions in metres (feet centre at origin)
def joints(motion, p, side_on=False):
    """Returns dict of joint name -> (x, y, z). Front view by default; y is depth (towards camera is -y)."""
    J = {}
    z_hip, z_sh, z_head = 0.95, 1.45, 1.70
    lift = 0.0; knee_out = 0.0; hip_drop = 0.0; lean = 0.0
    if motion == "calf":
        lift = -0.04 + 0.12 * p
    if motion == "squat":
        hip_drop = 0.42 * (1 - p); knee_out = 0.08 * (1 - p)
    if motion == "deadlift":
        hip_drop = 0.30 * (1 - p); lean = 0.55 * (1 - p)
    zh = z_hip - hip_drop + lift
    # spine: hips -> shoulders, lean forward (towards -y) for deadlift
    sh = (0, -math.sin(lean) * 0.5, zh + math.cos(lean) * 0.5)
    J["pelvis"] = (0, 0, zh); J["chest"] = ((sh[0]) * 0.5, sh[1] * 0.6, zh + (sh[2] - zh) * 0.62); J["neck"] = sh
    J["head"] = (0, sh[1] - math.sin(lean) * 0.22, sh[2] + 0.22 * math.cos(lean))
    for s, k in ((-1, "l"), (1, "r")):
        hip = (s * 0.10, 0, zh); J["hip_" + k] = hip
        ankle_z = 0.08 + max(lift, 0) if motion == "calf" else 0.08
        J["ankle_" + k] = (s * 0.12, 0.0, ankle_z)
        J["toe_" + k] = (s * 0.13, -0.14, 0.03 if motion != "calf" else 0.04)
        kz = (hip[2] + ankle_z) / 2 + (0.0 if motion not in ("squat", "deadlift") else 0.0)
        ky = -0.18 * (hip_drop / 0.42) if motion == "squat" else (-0.10 * (1 - p) if motion == "deadlift" else 0.0)
        J["knee_" + k] = (s * (0.12 + knee_out), ky, kz)
        shp = (s * 0.21, sh[1], sh[2] - 0.03); J["shoulder_" + k] = shp
        if motion == "curl":
            a = math.pi * 0.85 * p
            el = (s * 0.23, sh[1] + 0.02, sh[2] - 0.30)
            ha = (s * 0.24, el[1] - 0.28 * math.sin(a), el[2] - 0.28 * math.cos(a))
        elif motion == "press":
            bar_z = sh[2] + 0.02 + 0.52 * p
            ha = (s * 0.30, sh[1] - 0.05, bar_z)
            el = (s * (0.40 - 0.12 * p), sh[1] - 0.02, (shp[2] + bar_z) / 2 - 0.08 * (1 - p))
        elif motion == "squat":
            ha = (s * 0.42, sh[1] + 0.05, sh[2] + 0.02); el = (s * 0.40, sh[1] + 0.15, sh[2] - 0.18)
        elif motion == "deadlift":
            hz = 0.22 + (zh - 0.22 + 0.0) * 0.0 + 0.55 * p
            ha = (s * 0.24, sh[1] - 0.02, max(0.22, sh[2] - 0.62)); el = ((shp[0] + ha[0]) / 2, (shp[1] + ha[1]) / 2, (shp[2] + ha[2]) / 2)
        elif motion == "walk":
            sw = math.sin(p * 2 * math.pi) * 0.25
            ha = (s * 0.24, -s * sw, sh[2] - 0.62); el = (s * 0.23, -s * sw * 0.5, sh[2] - 0.31)
            J["ankle_" + k] = (s * 0.12, s * sw, 0.08); J["toe_" + k] = (s * 0.13, s * sw - 0.14, 0.03)
            J["knee_" + k] = (s * 0.12, s * sw * 0.5 - 0.04, (hip[2] + 0.08) / 2)
        else:   # stand, calf: arms down holding dumbbells
            ha = (s * 0.26, sh[1], sh[2] - 0.62); el = (s * 0.25, sh[1], sh[2] - 0.31)
        J["elbow_" + k] = el; J["hand_" + k] = ha
    return J


def bench_joints(p):
    """Side view (x along the bench), lying on a flat bench, bar from chest (p=0) to lockout (p=1)."""
    J = {}
    top = 0.48
    J["head"] = (-0.62, 0, top + 0.13); J["neck"] = (-0.45, 0, top + 0.12); J["chest"] = (-0.22, 0, top + 0.13); J["pelvis"] = (0.12, 0, top + 0.12)
    for s, k in ((-1, "l"), (1, "r")):
        y = s * 0.12
        J["hip_" + k] = (0.12, y, top + 0.12); J["knee_" + k] = (0.48, y * 1.6, top + 0.16); J["ankle_" + k] = (0.52, y * 1.9, 0.08); J["toe_" + k] = (0.66, y * 1.9, 0.03)
        bar_z = top + 0.30 + 0.42 * p
        J["shoulder_" + k] = (-0.42, y * 1.6, top + 0.12)
        J["hand_" + k] = (-0.32, y * 2.4, bar_z)
        J["elbow_" + k] = (-0.40, y * 3.0, (top + 0.12 + bar_z) / 2 - 0.05 * (1 - p))
    return J


IDLE = {"deadlift": 1.0, "squat": 1.0, "curl": 0.0, "calf": 0.35, "press": 0.0, "bench": 1.0, "stand": 0.0, "walk": 0.0}

LIMBS = [("neck", "chest", 0.085), ("chest", "pelvis", 0.10),
         ("shoulder_l", "elbow_l", 0.045), ("elbow_l", "hand_l", 0.04), ("shoulder_r", "elbow_r", 0.045), ("elbow_r", "hand_r", 0.04),
         ("hip_l", "knee_l", 0.06), ("knee_l", "ankle_l", 0.05), ("hip_r", "knee_r", 0.06), ("knee_r", "ankle_r", 0.05),
         ("ankle_l", "toe_l", 0.035), ("ankle_r", "toe_r", 0.035), ("shoulder_l", "shoulder_r", 0.06), ("hip_l", "hip_r", 0.07)]
BALLS = ["shoulder_l", "shoulder_r", "elbow_l", "elbow_r", "hip_l", "hip_r", "knee_l", "knee_r", "neck", "hand_l", "hand_r"]


# ------------------------------------------------------------------ scene
def mat(name, rgba, rough=0.55, emit=0.0, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba; b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    b.inputs["Emission Color"].default_value = rgba; b.inputs["Emission Strength"].default_value = emit
    return m


def reset(res):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 24; sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.film_transparent = False
    sc.render.image_settings.file_format = "PNG"
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.012, 0.013, 0.017, 1)
    return sc


def stage(xs):
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 4, 0))
    bpy.context.object.data.materials.append(mat("floor", (0.03, 0.032, 0.04, 1), rough=0.22))
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 6, 0), rotation=(math.pi / 2, 0, 0))
    bpy.context.object.data.materials.append(mat("wall", (0.02, 0.022, 0.028, 1), rough=0.9))
    for x in xs:
        bpy.ops.object.light_add(type="SPOT", location=(x, 0.2, 4.2)); L = bpy.context.object
        L.data.energy = 900; L.data.spot_size = math.radians(38); L.data.spot_blend = 0.5; L.data.color = (0.95, 0.96, 1.0)
        L.rotation_euler = (math.radians(3), 0, 0)
    bpy.ops.object.light_add(type="AREA", location=(0, -4, 2.5)); A = bpy.context.object
    A.data.energy = 120; A.data.size = 6; A.rotation_euler = (math.radians(70), 0, 0)


def camera(n_sides, motion, dist_override=None):
    """Feet land on the 2D overlay's floor line (y = 1260 of 1920) and heads below the side labels (y ~600)."""
    bench = motion == "bench"
    barbell = motion in ("squat", "deadlift", "press")
    dist = {1: 4.6, 2: 5.9, 3: 6.6}[n_sides] + (0.6 if bench else 0) + (1.4 if barbell else 0)
    if dist_override: dist = dist_override
    z, lens = 1.05, 40
    bpy.ops.object.camera_add(location=(0, -dist, z), rotation=(math.radians(90), 0, 0))
    cam = bpy.context.object; cam.data.lens = lens; bpy.context.scene.camera = cam
    cam.data.shift_y = (1260 / 1920 - 0.5) - (z / dist) * (lens / 18) * 0.5


YAW = {"calf": 70, "bench": 35}


class Mannequin:
    def __init__(self, x0, kit_rgba, motion, style="mannequin", floor_bar=False):
        self.x0 = x0; self.motion = motion; self.style = style
        before = set(bpy.data.objects)
        self.body = mat("ivory%.2f" % x0, IVORY, rough=0.6) if style == "mannequin" else mat("white%.2f" % x0, (0.92, 0.92, 0.94, 1), rough=0.28)
        self.glow = self.body.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
        self.body.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = kit_rgba
        self.kit = mat("kit%.2f" % x0, kit_rgba, rough=0.35)
        self.metal = mat("steel%.2f" % x0, (0.75, 0.76, 0.8, 1), rough=0.25, metal=1.0)
        self.parts = []
        k = 1.0 if style == "mannequin" else 0.55
        for a, b, r in LIMBS:
            if style == "stick" and a in ("shoulder_l", "hip_l") and b in ("shoulder_r", "hip_r"): continue
            r = r * k
            bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=1, vertices=24); o = bpy.context.object
            o.data.materials.append(self.body); bpy.ops.object.shade_smooth(); self.parts.append(("limb", a, b, r, o))
        for j in BALLS:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=24, ring_count=12); o = bpy.context.object
            o.data.materials.append(self.body); bpy.ops.object.shade_smooth(); self.parts.append(("ball", j, None, 0.055 * k, o))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=32, ring_count=16); self.head = bpy.context.object
        self.head.data.materials.append(self.body); bpy.ops.object.shade_smooth()
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=32, ring_count=16); self.torso = bpy.context.object
        self.torso.data.materials.append(self.body); bpy.ops.object.shade_smooth()
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=32, ring_count=16); self.hips = bpy.context.object
        self.hips.data.materials.append(self.body); bpy.ops.object.shade_smooth()
        self.equip()
        if floor_bar:                                   # a loaded bar resting on the floor in front of the figure
            bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=1.15, vertices=16, location=(0, -0.32, 0.19), rotation=(0, math.pi / 2, 0))
            bpy.context.object.data.materials.append(self.metal)
            for sx in (-0.42, -0.37, 0.37, 0.42):
                bpy.ops.mesh.primitive_cylinder_add(radius=0.19, depth=0.045, vertices=40, location=(sx, -0.32, 0.19), rotation=(0, math.pi / 2, 0))
                bpy.context.object.data.materials.append(self.kit)
        bpy.ops.object.empty_add(location=(x0, 0, 0)); self.root = bpy.context.object
        self.root.rotation_euler = (0, 0, math.radians(YAW.get(motion, 0)))
        for o in set(bpy.data.objects) - before - {self.root}:
            o.parent = self.root; o.matrix_parent_inverse.identity()

    def equip(self):
        m = self.motion; self.dbs = []; self.bar = None
        if m in ("curl", "calf") or (m == "stand" and self.style == "mannequin"):
            for _ in range(2):
                grp = []
                bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.16, vertices=16); h = bpy.context.object; h.data.materials.append(self.metal); grp.append(h)
                for _ in range(2):
                    bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.05, vertices=32); w = bpy.context.object; w.data.materials.append(self.kit); grp.append(w)
                self.dbs.append(grp)
        if m in ("press", "squat", "deadlift", "bench"):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=1.15, vertices=16); self.bar = bpy.context.object
            self.bar.data.materials.append(self.metal)
            self.plates = []
            for _ in range(4):
                bpy.ops.mesh.primitive_cylinder_add(radius={"bench": 0.15, "press": 0.15}.get(m, 0.19), depth=0.045, vertices=40); w = bpy.context.object
                w.data.materials.append(self.kit); self.plates.append(w)
        if m == "calf":
            bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.02, 0.04)); st = bpy.context.object
            st.scale = (0.5, 0.36, 0.08); st.data.materials.append(mat("step", (0.18, 0.18, 0.2, 1), rough=0.7))
        if m == "bench":
            bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.15, 0, 0.44)); b = bpy.context.object
            b.scale = (1.15, 0.28, 0.07); b.data.materials.append(mat("pad", (0.08, 0.08, 0.09, 1), rough=0.5))
            for lx in (-0.6, 0.3):
                bpy.ops.mesh.primitive_cube_add(size=1, location=(lx, 0, 0.2)); l = bpy.context.object
                l.scale = (0.05, 0.22, 0.4); l.data.materials.append(self.metal)

    def pose(self, p, glow=0.0, dx=0.0):
        self.root.location.x = self.x0 + dx
        J = bench_joints(p) if self.motion == "bench" else joints(self.motion, p)
        off = Vector((0, 0, 0))
        V = {k: Vector(v) + off for k, v in J.items()}
        for kind, a, b, r, o in self.parts:
            if kind == "limb":
                A, B = V[a], V[b]; d = B - A; L = max(d.length, 1e-4)
                o.location = (A + B) / 2; o.scale = (r, r, L / 2 if False else L)
                o.rotation_mode = "QUATERNION"; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
                o.scale = (r, r, L)
            else:
                o.location = V[a]; o.scale = (r, r, r)
        self.head.location = V["head"]; self.head.scale = (0.10, 0.11, 0.135) if self.style == "mannequin" else (0.11, 0.11, 0.11)
        if self.motion == "bench": self.head.scale = (0.135, 0.11, 0.10)
        c = (V["neck"] + V["pelvis"]) / 2
        self.torso.location = (V["chest"] + V["neck"]) / 2
        d = V["neck"] - V["pelvis"]
        self.torso.rotation_mode = "QUATERNION"; self.torso.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
        self.torso.scale = (0.19, 0.12, 0.2) if self.style == "mannequin" else (0.05, 0.05, 0.27)
        self.hips.location = V["pelvis"]; self.hips.rotation_mode = "QUATERNION"; self.hips.rotation_quaternion = self.torso.rotation_quaternion
        self.hips.scale = (0.17, 0.11, 0.11) if self.style == "mannequin" else (0.09, 0.06, 0.06)
        for i, grp in enumerate(self.dbs):
            hnd = V["hand_l" if i == 0 else "hand_r"]
            h, w1, w2 = grp
            for o in grp: o.rotation_euler = (0, math.pi / 2, 0)
            h.location = hnd; w1.location = hnd + Vector((-0.08, 0, 0)); w2.location = hnd + Vector((0.08, 0, 0))
        if self.bar is not None:
            if self.motion == "bench":
                mid = (V["hand_l"] + V["hand_r"]) / 2; self.bar.rotation_euler = (math.pi / 2, 0, 0); self.bar.location = mid
                for i, w in enumerate(self.plates):
                    s = -1 if i < 2 else 1; w.rotation_euler = (math.pi / 2, 0, 0); w.location = mid + Vector((0, s * (0.45 + (i % 2) * 0.05), 0))
            else:
                mid = (V["hand_l"] + V["hand_r"]) / 2
                if self.motion == "squat": mid = Vector((0, V["neck"].y + 0.08, V["neck"].z - 0.02))
                self.bar.rotation_euler = (0, math.pi / 2, 0); self.bar.location = mid
                for i, w in enumerate(self.plates):
                    s = -1 if i < 2 else 1; w.rotation_euler = (0, math.pi / 2, 0); w.location = mid + Vector((s * (0.42 + (i % 2) * 0.05), 0, 0))
        self.glow.default_value = glow


def render_frames(sides, motion, n_frames, poses_fn, out_dir, res=(720, 1280), samples=24):
    """poses_fn(i) -> list of (p, glow) per side for frame i. Writes out_dir/f00000.png ..."""
    sc = reset(res); sc.cycles.samples = samples
    xs = {1: [0.0], 2: [-0.75, 0.75], 3: [-1.15, 0.0, 1.15]}[len(sides)]
    if motion in ("squat", "deadlift", "press"): xs = [x * 1.27 for x in xs]
    if motion == "bench": xs = [x * 1.25 for x in xs]
    stage(xs); camera(len(sides), motion)
    men = [Mannequin(x, tuple(c / 255 for c in s["color"]) + (1,), motion) for x, s in zip(xs, sides)]
    os.makedirs(out_dir, exist_ok=True)
    for i in range(n_frames):
        fp = os.path.join(out_dir, f"f{i:05d}.png")
        if os.path.exists(fp): continue
        for m, (p, g) in zip(men, poses_fn(i)): m.pose(p, g)
        sc.render.filepath = fp; bpy.ops.render.render(write_still=True)
    return out_dir


def render_single(motion, poses, out_dir, kit_rgb, style="stick", floor_bar=False, res=(720, 1280), samples=20, glow_rgb=None, x0=-0.55, dist=5.6):
    """One figure, centred. poses: list of (p, glow, dx). Writes out_dir/f00000.png ... (one image per entry)."""
    sc = reset(res); sc.cycles.samples = samples
    stage([x0]); camera(1, motion, dist_override=dist)
    m = Mannequin(x0, tuple(c / 255 for c in kit_rgb) + (1,), motion, style=style, floor_bar=floor_bar)
    if glow_rgb: m.body.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = tuple(c / 255 for c in glow_rgb) + (1,)
    os.makedirs(out_dir, exist_ok=True)
    for i, (p, g, dx) in enumerate(poses):
        fp = os.path.join(out_dir, f"f{i:05d}.png")
        if os.path.exists(fp): continue
        m.pose(p, g, dx); sc.render.filepath = fp; bpy.ops.render.render(write_still=True)
    return out_dir


if __name__ == "__main__":
    import json, sys
    job = json.load(open(sys.argv[1])); out = os.path.dirname(sys.argv[1])
    if job.get("single"):
        render_single(job["motion"], job["poses"], out, job["kit"], style=job.get("style", "stick"), floor_bar=job.get("floor_bar", False),
                      samples=job.get("samples", 20), glow_rgb=job.get("glow"))
        sys.exit(0)
    keys = job["keys"]
    render_frames(job["sides"], job["motion"], len(keys), lambda i: [(p, 0.9 * g) for p, g in keys[i]], out,
                  res=tuple(job.get("res", (720, 1280))), samples=job.get("samples", 20))
