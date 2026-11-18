#!/usr/bin/env python3
"""Overthinker vs doer: two stacked spotlight panels, white 3D-look stick figures (anim_stick look), gold glow on the doer.
Structure from founder links 11-18 (@sticktoit16 4.6M / 3.5M, @neuronvisuals 16M); our own drawing and gym story.

  python3 anim_doer.py <set_dir>     # reads <set_dir>/doer.json, writes <set_dir>/<out>

doer.json: {"out": "heavy-set.mp4", "title": "THE HEAVY SET", "top": "OVERTHINKER", "bottom": "DOER",
            "thoughts": ["what if i fail?", ...], "doer_label": "ALREADY HOME", "end_line": ["same weight.", "one just started."],
            "endcard": ["this page is made by EARND,", "our gym app. follow @earndapp"], "accent": [255, 196, 120],
            "render": "3d"}   # optional: real 3D stick figures via mannequin3d.py
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim_stick as st

W, H, FPS = st.W, st.H, st.FPS
ease, F, ctext = st.ease, st.F, st.ctext
FL = (900, 1830)            # floor line of each panel


def base_img():
    yy, xx = np.mgrid[0:H, 0:W]; b = np.full((H, W, 3), 8, np.float32)
    for fl, cx in ((FL[0], 380), (FL[1], 380)):
        top = fl - 820
        inside = (yy > top) & (yy < fl)
        spread = 120 + (yy - top) * 0.32
        cone = np.exp(-((xx - cx) / np.maximum(spread, 1)) ** 2) * inside * 34
        b += cone[:, :, None]
        b += 50 * np.exp(-(((xx - cx) / 260) ** 2 + ((yy - fl) / 40) ** 2))[:, :, None] * np.array([255, 200, 140]) / 255
    b[H // 2 - 2:H // 2 + 2, 60:W - 60] = 70
    return Image.fromarray(b.clip(0, 255).astype(np.uint8))


def render(set_dir):
    sp = json.load(open(os.path.join(set_dir, "doer.json")))
    acc = tuple(sp.get("accent", (255, 196, 120)))
    END, DUR = 12.0, 14.8
    base = base_img()
    out = os.path.join(set_dir, sp["out"]); os.makedirs(os.path.join(set_dir, "preview"), exist_ok=True)
    THREE_D = sp.get("render") == "3d"
    if THREE_D:                                   # real 3D stick figures (mannequin3d.py), each pose rendered once
        q = lambda v, n: round(v * n) / n
        def top_state(t):
            step = 0.5 - 0.5 * math.cos(t * 2 * math.pi / 2.6); return (0.0, 0.0, q(-0.12 + 0.12 * step, 8))
        def bot_state(t):
            if t < 4.2:
                p = ease(0.5 - 0.5 * math.cos(max(0.0, t - 0.6) * 2 * math.pi / 1.2)) if t > 0.6 else 0.0
                return ("lift", (q(p, 12), 2.0, 0.0))
            dx = 3.2 * ease((t - 4.4) / 2.0)
            return ("walk", (q((t * 1.6) % 1.0, 6), 2.0, q(dx, 16)))
        tk, bk = {}, {"lift": {}, "walk": {}}
        for fi in range(int(END * FPS)):
            t = fi / FPS; tk.setdefault(top_state(t), len(tk))
            ph, k = bot_state(t); bk[ph].setdefault(k, len(bk[ph]))
        cache = os.path.join(set_dir, "3d"); acc_rgb = list(acc)
        jobs = [("top", dict(motion="stand", poses=[list(k) for k in tk], floor_bar=True, kit=acc_rgb)),
                ("lift", dict(motion="deadlift", poses=[list(k) for k in bk["lift"]], kit=acc_rgb, glow=acc_rgb)),
                ("walk", dict(motion="walk", poses=[list(k) for k in bk["walk"]], floor_bar=True, kit=acc_rgb, glow=acc_rgb))]
        for name, job in jobs:
            d_ = os.path.join(cache, name); os.makedirs(d_, exist_ok=True)
            jf = os.path.join(d_, "job.json"); json.dump(dict(job, single=True, style="stick"), open(jf, "w"))
            subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "mannequin3d.py"), jf], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        def panel(name, idx):
            im = Image.open(os.path.join(cache, name, f"f{idx:05d}.png")).convert("RGB").resize((W, H), Image.LANCZOS)
            return im.crop((0, 330, W, 330 + H // 2))
        def base3d(t):
            b = Image.new("RGB", (W, H)); b.paste(panel("top", tk[top_state(t)]), (0, 0))
            ph, k = bot_state(t); b.paste(panel(ph, bk[ph][k]), (0, H // 2))
            ImageDraw.Draw(b).rectangle([60, H // 2 - 2, W - 60, H // 2 + 2], fill=(70, 70, 70))
            return b
    pr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], stdin=subprocess.PIPE)
    for fi in range(int(DUR * FPS)):
        t = fi / FPS
        img = base3d(t) if (THREE_D and t < END) else base.copy()
        if t < END and not THREE_D:
            scene = Image.new("RGB", (W, H)); sd = ImageDraw.Draw(scene); glow = Image.new("L", (W, H)); gd = ImageDraw.Draw(glow)
            # top: overthinker steps up to the bar and back, never lifts
            st.FLOOR = FL[0]
            step = 0.5 - 0.5 * math.cos(t * 2 * math.pi / 2.6)
            x = 250 + 60 * step
            st.figure(sd, x, 1.0, slump=0.15 + 0.2 * step, col=(215, 215, 222))
            st.barbell(sd, 560, FL[0] - 60, 3, acc)
            # bottom: doer lifts 3 reps, racks, walks out of frame
            st.FLOOR = FL[1]
            if t < 4.2:
                p = ease(0.5 - 0.5 * math.cos(max(0.0, t - 0.6) * 2 * math.pi / 1.2)) if t > 0.6 else 0.0
                hy = st.figure(sd, 380, p, col=(255, 255, 255)); st.barbell(sd, 380, hy, 3, acc)
                st.figure(gd, 380, p, col=255, shade=255)
            else:
                st.barbell(sd, 380, FL[1] - 60, 3, acc)
                xw = 380 + 950 * ease((t - 4.4) / 2.0)
                if xw < W + 120:
                    st.figure(sd, xw, 1.0, col=(255, 255, 255)); st.figure(gd, xw, 1.0, col=255, shade=255)
            img.paste(Image.composite(scene, img, scene.convert("L").point(lambda v: 255 if v > 4 else 0)), (0, 0))
            g = glow.filter(ImageFilter.GaussianBlur(26))
            arr = np.asarray(img).astype(np.float32) + np.asarray(g, np.float32)[:, :, None] / 255 * np.array(acc) * 0.5
            img = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
        d = ImageDraw.Draw(img)
        if t < END:
            ctext(d, sp["title"], 40, F(56), (245, 245, 245))
            ctext(d, sp["top"], 130, F(34), (190, 190, 196), x=780)
            ctext(d, sp["bottom"], FL[0] + 60, F(34), acc, x=780)
            # overthinker: timer + thoughts
            ctext(d, f"0:{min(int(t * 1.25), 59):02d}", 200, F(64), (235, 235, 240), x=780)
            th = sp["thoughts"][int(t / 2.4) % len(sp["thoughts"])]
            a = int(255 * ease((t % 2.4) / 0.25))
            f = F(30); tw = d.textlength(th, font=f)
            d.rounded_rectangle([780 - tw / 2 - 24, 330, 780 + tw / 2 + 24, 390], 26, outline=(a, a, a), width=3)
            ctext(d, th, 342, f, (a, a, a), x=780)
            ctext(d, "SETS DONE: 0", 440, F(30), (150, 150, 158), x=780)
            # doer: reps then label
            reps = min(3, int(max(0.0, t - 0.6) / 1.2) + (1 if t > 1.2 else 0)) if t < 4.2 else 3
            ctext(d, f"SETS DONE: {1 if t > 4.2 else 0}  REPS: {reps}", FL[0] + 120, F(30), (220, 220, 226), x=780)
            if t > 6.6:
                a = ease((t - 6.6) / 0.3); ctext(d, sp["doer_label"], FL[0] + 330, F(56), tuple(int(v * a) for v in acc), x=700)
            if t > 9.0:
                a = ease((t - 9.0) / 0.3)
                d.rounded_rectangle([90, H // 2 - 150, W - 90, H // 2 + 70], 30, fill=(10, 10, 12), outline=tuple(int(v * a) for v in acc), width=3)
                for i, ln in enumerate(sp["end_line"]):
                    ctext(d, ln.upper(), H // 2 - 110 + i * 80, F(54), tuple(int(v * a) for v in ((245, 245, 245) if i == 0 else acc)))
        else:
            a = ease((t - END) / 0.35)
            for i, ln in enumerate(sp["endcard"]):
                ctext(d, ln.upper(), 820 + i * 90, F(52), tuple(int(v * a) for v in (acc if i == 0 else (235, 235, 240))))
        pr.stdin.write(img.tobytes())
        if fi in [int(s * FPS) for s in (0.8, 3.0, 7.5, 10.5, 13.5)]:
            img.resize((540, 960)).save(os.path.join(set_dir, "preview", f"f{fi:04d}.jpg"), quality=88)
    pr.stdin.close(); pr.wait(); print("DONE", out, DUR, "s")


if __name__ == "__main__":
    render(sys.argv[1])
