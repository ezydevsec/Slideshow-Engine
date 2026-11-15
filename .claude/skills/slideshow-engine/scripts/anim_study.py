#!/usr/bin/env python3
"""@earndapp "study race" video (format: 02-research/formats/a-vs-b-sim-video.md, 2026-11-15 update).
Graphite mannequins + lime (never Earnie's white/amber sticks), a real study's result, the catch, then a real app screen.

  python3 anim_study.py <set_dir>     # reads <set_dir>/study.json, writes <set_dir>/<out>

study.json: title_a/title_b, question, days_a/days_b (lifting days per week, 0=Mon), weeks, result_a/result_b,
result_note, cite, catch_lines [..], catch_cite, tie_in, shot, endcard [..]
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim_stick as st

W, H, FPS = st.W, st.H, st.FPS
FLOOR = st.FLOOR
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
LIME = (198, 255, 0)
ANTON = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "Anton-Regular.ttf")
INTER = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
ease = st.ease


def fit(d, txt, size, maxw, path=ANTON):
    f = ImageFont.truetype(path, size)
    while d.textlength(txt, font=f) > maxw and size > 20: size -= 2; f = ImageFont.truetype(path, size)
    return f


def ct(d, txt, y, size, fill, x=W / 2, maxw=W - 100, path=ANTON):
    f = fit(d, txt, size, maxw, path); d.text((x - d.textlength(txt, font=f) / 2, y), txt, font=f, fill=fill)


def render(set_dir):
    sp = json.load(open(os.path.join(set_dir, "study.json")))
    weeks = sp.get("weeks", 8); WK = 0.9
    T_RACE0, T_RACE1 = 1.4, 1.4 + weeks * WK
    T_RES, T_CATCH, T_APP = T_RACE1, T_RACE1 + 2.6, T_RACE1 + 6.6
    DUR = T_APP + 3.6
    base = np.zeros((H, W, 3), np.float32); yy, xx = np.mgrid[0:H, 0:W]
    for cx in (310, 770):
        base += 70 * np.exp(-(((xx - cx) / 240) ** 2 + ((yy - FLOOR) / 60) ** 2))[:, :, None] * np.array([210, 220, 200]) / 255
        base += 18 * np.exp(-(((xx - cx) / 200) ** 2 + ((yy - 900) / 600) ** 2))[:, :, None]
    base = Image.fromarray(base.clip(0, 255).astype(np.uint8))
    shot = Image.open(os.path.join(ROOT, sp["shot"])).convert("RGB")
    if sp.get("crop"):
        c = sp["crop"]; shot = shot.crop((int(c[0] * shot.width), int(c[1] * shot.height), int(c[2] * shot.width), int(c[3] * shot.height)))
    shot.thumbnail((760, 1000), Image.LANCZOS)
    m = Image.new("L", shot.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0) + shot.size, 40, fill=255)
    out = os.path.join(set_dir, sp["out"]); os.makedirs(os.path.join(set_dir, "preview"), exist_ok=True)
    pr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], stdin=subprocess.PIPE)
    GA, GB = (150, 156, 166), (88, 92, 100)
    for fi in range(int(DUR * FPS)):
        t = fi / FPS
        img = base.copy(); d = ImageDraw.Draw(img)
        if t < T_APP:
            race = max(0.0, min(1.0, (t - T_RACE0) / (T_RACE1 - T_RACE0)))
            wk_f = race * weeks; day = int((wk_f % 1) * 7) if t < T_RACE1 else -1
            scene = Image.new("RGB", (W, H)); sd = ImageDraw.Draw(scene); glow = Image.new("L", (W, H)); gd = ImageDraw.Draw(glow)
            for x, days, win in ((310, sp["days_a"], False), (770, sp["days_b"], True)):
                lifting = day in days
                ph = (t * 2.2) % 1.0
                p = ease(0.5 - 0.5 * math.cos(ph * 2 * math.pi)) if lifting else 1.0
                lit = win and t >= T_RES
                col = (226, 255, 120) if lit else GA
                hy = st.figure(sd, x, p, col=col, shade=GB)
                st.barbell(sd, x, hy, 2, LIME)
                if lit: st.figure(gd, x, p, col=255, shade=255)
                # week strip: 7 day boxes, lifting days light up on their day
                for k in range(7):
                    bx = x - 3 * 52 + k * 52 - 20
                    on = k in days; now = (k == day)
                    sd.rounded_rectangle([bx, FLOOR + 40, bx + 40, FLOOR + 80], 8,
                                         outline=(90, 94, 100), width=3, fill=(LIME if (on and now) else ((70, 80, 40) if on else None)))
                # growth bar
                target = sp["result_b"] if win else sp["result_a"]
                frac = min(race, 1.0) * target / max(sp["result_a"], sp["result_b"])
                if not win and t >= T_CATCH + 2.0:   # the catch: equal sets close the gap
                    frac += (1.0 - frac) * 0.85 * ease((t - T_CATCH - 2.0) / 0.8)
                sd.rectangle([x - 150, FLOOR + 120, x + 150, FLOOR + 150], outline=(90, 94, 100), width=3)
                sd.rectangle([x - 146, FLOOR + 124, x - 146 + 292 * frac, FLOOR + 146], fill=LIME if win else (170, 176, 186))
            top = scene.crop((0, FLOOR - 650, W, FLOOR)).transpose(Image.FLIP_TOP_BOTTOM)
            refl = Image.blend(Image.new("RGB", top.size), top, 0.18)
            img.paste(Image.composite(scene, img, scene.convert("L").point(lambda v: 255 if v > 4 else 0)), (0, 0))
            sub = img.crop((0, FLOOR, W, FLOOR + 650)); mask = refl.convert("L").point(lambda v: 255 if v > 3 else 0)
            img.paste(Image.composite(refl, sub, mask), (0, FLOOR))
            # redraw strip + bars over the reflection
            img.paste(scene.crop((0, FLOOR + 30, W, FLOOR + 160)), (0, FLOOR + 30), scene.crop((0, FLOOR + 30, W, FLOOR + 160)).convert("L").point(lambda v: 255 if v > 4 else 0))
            if t >= T_RES:
                g = glow.filter(ImageFilter.GaussianBlur(26))
                arr = np.asarray(img).astype(np.float32) + np.asarray(g, np.float32)[:, :, None] / 255 * np.array(LIME) * 0.5
                img = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
            d = ImageDraw.Draw(img)
            # labels
            for x, lab, win in ((310, sp["title_a"], False), (770, sp["title_b"], True)):
                if T_CATCH <= t < T_APP: break
                ct(d, lab, 540, 54, LIME if win else (225, 225, 230), x=x, maxw=440)
            # top text by phase
            if t < T_RACE1:
                a = ease(t / 0.3)
                ct(d, sp["title_a"] + " vs " + sp["title_b"] + ".", 190, 96, (int(245 * a),) * 3)
                ct(d, sp["question"], 320, 50, (int(170 * a), int(175 * a), int(185 * a)), path=INTER)
                if t >= T_RACE0: ct(d, f"WEEK {min(weeks, 1 + int(wk_f))}", 420, 44, LIME)
            elif t < T_CATCH:
                a = ease((t - T_RES) / 0.3)
                ct(d, sp["result_head"], 190, 96, tuple(int(v * a) for v in LIME))
                ct(d, sp["result_note"], 320, 44, (int(220 * a),) * 3, path=INTER)
                for x, val, win in ((310, sp["result_a_label"], False), (770, sp["result_b_label"], True)):
                    ct(d, val, FLOOR + 175, 40, LIME if win else (200, 200, 205), x=x, maxw=400, path=INTER)
                ct(d, sp["cite"], 1830, 30, (150, 150, 158), path=INTER)
            else:
                a = ease((t - T_CATCH) / 0.3)
                ct(d, "HERE'S THE CATCH", 170, 92, tuple(int(v * a) for v in LIME))
                for i, ln in enumerate(sp["catch_lines"]):
                    aa = ease((t - T_CATCH - 0.5 - i * 1.0) / 0.3)
                    ct(d, ln, 290 + i * 66, 46, (int(235 * aa),) * 3, path=INTER)
                ct(d, sp["catch_cite"], 1830, 30, (150, 150, 158), path=INTER)
        else:
            a = ease((t - T_APP) / 0.3)
            ct(d, sp["tie_in"][0], 150, 84, tuple(int(v * a) for v in LIME))
            ct(d, sp["tie_in"][1], 260, 46, (int(230 * a),) * 3, path=INTER)
            img.paste(shot, ((W - shot.width) // 2, 360), m)
            for i, ln in enumerate(sp["endcard"]):
                ct(d, ln, 360 + shot.height + 50 + i * 70, 50, LIME if i == 0 else (235, 235, 240), path=INTER)
        pr.stdin.write(img.convert("RGB").tobytes())
        if fi in [int(s * FPS) for s in (0.8, (T_RACE0 + T_RACE1) / 2, T_RES + 1.4, T_CATCH + 3.2, T_APP + 2)]:
            img.resize((540, 960)).save(os.path.join(set_dir, "preview", f"f{fi:04d}.jpg"), quality=88)
    pr.stdin.close(); pr.wait(); print("DONE", out, round(DUR, 1), "s")


if __name__ == "__main__":
    render(sys.argv[1])
