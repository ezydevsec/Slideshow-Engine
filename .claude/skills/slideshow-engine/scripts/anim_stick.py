#!/usr/bin/env python3
"""3D-look stickman comparison videos (format: 02-research/formats/stick-comparison-3d.md). 0 credits, no voice.

  python3 anim_stick.py <set_dir>        # reads <set_dir>/stick.json, writes <set_dir>/<out>

stick.json:
{
  "out": "same-gym.mp4", "accent": [198,255,0],           # winner glow colour (lime @earndapp, gold @quiet.reps4)
  "premise": "same gym. same days.",
  "left":  {"label": "SAME WEIGHT", "lift": "DEADLIFT", "start": 60, "per_week": 0},
  "right": {"label": "+2.5 KG A WEEK", "lift": "DEADLIFT", "start": 60, "per_week": 2.5},
  "weeks": 12, "example": true,                            # adds an "example" tag to the numbers
  "end_line": ["same effort.", "only one knew what to beat."],
  "endcard": ["EARND launches soon.", "follow for the launch."]
}
Steps mode (no weekly counter): "steps": [{"hud": "24 HOURS", "left": "still weaker", "right": "back to normal"}, ...],
"step_t": 2.0, and fixed "plates" per side. The left figure looks more tired each step.
Look: black void, glossy floor with reflections, spotlight pools, round-headed white figures; the right figure glows.
Our own drawing; the reference accounts only informed the structure.
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
FLOOR = 1260
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
F = lambda s: ImageFont.truetype(MONO, s)


def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def ctext(d, txt, y, f, fill, x=W / 2, maxw=None):
    maxw = maxw or (W - 80 if x == W / 2 else 420)
    while d.textlength(txt, font=f) > maxw and f.size > 18: f = F(f.size - 2)
    d.text((x - d.textlength(txt, font=f) / 2, y), txt, font=f, fill=fill)


def capsule(d, a, b, w, fill):
    d.line([a, b], fill=fill, width=w)
    for p in (a, b): d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=fill)


def figure(d, x, p, slump=0.0, col=(235, 235, 240), shade=(150, 150, 160)):
    """Front view, deadlift. p: 0 = bar on the floor, 1 = lockout. Returns hand y (bar height)."""
    s = 1.0
    hip_y = FLOOR - 300 + (1 - p) * 120
    torso = 250 * (0.55 + 0.45 * p) * (1 - 0.15 * slump)        # foreshortened when hinged
    sh_y = hip_y - torso
    head_y = sh_y - 70 + slump * 40
    knee_out = 40 * (1 - p)
    hand_y = sh_y + 230 * (0.75 + 0.25 * p) if p > 0.05 else FLOOR - 60
    hand_y = min(hand_y, FLOOR - 60)
    for side in (-1, 1):
        hip = (x + side * 32, hip_y); knee = (x + side * (44 + knee_out), (hip_y + FLOOR) / 2); foot = (x + side * 46, FLOOR - 14)
        capsule(d, hip, knee, 34, shade); capsule(d, knee, foot, 34, shade)
        capsule(d, (hip[0] + 3, hip[1]), (knee[0] + 3, knee[1]), 26, col); capsule(d, (knee[0] + 3, knee[1]), (foot[0] + 3, foot[1]), 26, col)
    capsule(d, (x, sh_y), (x, hip_y), 64, shade); capsule(d, (x + 4, sh_y), (x + 4, hip_y), 52, col)
    for side in (-1, 1):
        shp = (x + side * 52, sh_y + 14); hand = (x + side * 78, hand_y)
        capsule(d, shp, hand, 28, shade); capsule(d, (shp[0] + 3, shp[1]), (hand[0] + 3, hand[1]), 21, col)
    r = 50
    d.ellipse([x - r, head_y - r, x + r, head_y + r], fill=shade)
    d.ellipse([x - r + 6, head_y - r + 3, x + r - 2, head_y + r - 5], fill=col)
    d.ellipse([x - 22, head_y - 34, x + 2, head_y - 14], fill=col if isinstance(col, int) else (255, 255, 255))     # highlight
    return hand_y


def barbell(d, x, y, plates, accent):
    d.line([(x - 195, y), (x + 195, y)], fill=(200, 200, 210), width=12)
    cols = [(60, 110, 230), (230, 70, 70), (250, 200, 50), (80, 200, 120), accent]
    for side in (-1, 1):
        for i in range(plates):
            px = x + side * (112 + i * 22); c = cols[i % len(cols)]
            d.rounded_rectangle([px - 9, y - 66, px + 9, min(y + 66, FLOOR - 4)], 7, fill=c)


def render(set_dir):
    sp = json.load(open(os.path.join(set_dir, "stick.json")))
    acc = tuple(sp.get("accent", (198, 255, 0))); steps = sp.get("steps")
    weeks = len(steps) if steps else sp.get("weeks", 12)
    WEEK_T = sp.get("step_t", 2.0) if steps else 0.9
    END_T, CARD_T = weeks * WEEK_T + 0.6, weeks * WEEK_T + 3.4
    DUR = CARD_T + 2.6
    base = np.zeros((H, W, 3), np.float32); yy, xx = np.mgrid[0:H, 0:W]
    for cx, c in ((310, (255, 170, 80)), (770, (255, 190, 110))):
        base += 60 * np.exp(-(((xx - cx) / 260) ** 2 + ((yy - FLOOR) / 70) ** 2))[:, :, None] * np.array(c) / 255
    base += 10 * np.exp(-(((xx - W / 2) / 600) ** 2 + ((yy - 900) / 700) ** 2))[:, :, None]
    base = Image.fromarray(base.clip(0, 255).astype(np.uint8))
    out = os.path.join(set_dir, sp["out"]); os.makedirs(os.path.join(set_dir, "preview"), exist_ok=True)
    pr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], stdin=subprocess.PIPE)
    L, R = sp["left"], sp["right"]
    for fi in range(int(DUR * FPS)):
        t = fi / FPS
        wk = min(weeks, 1 + int(t / WEEK_T)); prog = min(1.0, t / (weeks * WEEK_T))
        img = base.copy(); d = ImageDraw.Draw(img)
        if t < CARD_T:
            scene = Image.new("RGB", (W, H), (0, 0, 0)); sd = ImageDraw.Draw(scene)
            glow = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(glow)
            # left: same weight, slows down and slumps at the end
            pl = ease(0.5 - 0.5 * math.cos(t * 2 * math.pi / (1.5 + prog * 0.9))) * (1 - 0.6 * ease((t - END_T + 0.4) / 0.6))
            sl = ease((t - END_T + 0.4) / 0.6)
            if steps: sl = max(sl, 0.25 + 0.5 * prog); pl *= (1 - 0.4 * prog)
            hl = figure(sd, 310, pl, slump=sl, col=(205, 205, 212) if (t > END_T or steps) else (235, 235, 240))
            barbell(sd, 310, hl, L.get("plates", 2), acc)
            pr_ = ease(0.5 - 0.5 * math.cos(t * 2 * math.pi / 1.5))
            hr = figure(sd, 770, pr_, col=(255, 255, 255))
            nplates = R["plates"] if "plates" in R else 2 + int(4 * prog)
            barbell(sd, 770, hr, nplates, acc)
            figure(gd, 770, pr_, col=255, shade=255)
            # reflection
            top = scene.crop((0, FLOOR - 700, W, FLOOR)).transpose(Image.FLIP_TOP_BOTTOM)
            refl = Image.blend(Image.new("RGB", top.size), top, 0.22)
            img.paste(Image.composite(scene, img, scene.convert("L").point(lambda v: 255 if v > 4 else 0)), (0, 0))
            img.paste(Image.composite(refl, img.crop((0, FLOOR, W, FLOOR + 700)), refl.convert("L").point(lambda v: 255 if v > 3 else 0)), (0, FLOOR))
            g = glow.filter(ImageFilter.GaussianBlur(28))
            arr = np.asarray(img).astype(np.float32) + np.asarray(g, np.float32)[:, :, None] / 255 * np.array(acc) * 0.55
            img = Image.fromarray(arr.clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
            # HUD
            if t < END_T:
                ctext(d, steps[wk - 1]["hud"] if steps else f"WEEK {wk}" + ("  >>" if wk > 1 else ""), 250, F(84), (245, 245, 245))
                ctext(d, sp["premise"].upper(), 360, F(34), (190, 190, 195))
            else:
                a = int(255 * ease((t - END_T) / 0.3))
                for i, ln in enumerate(sp["end_line"]):
                    ctext(d, ln.upper(), 240 + i * 90, F(64), (a, a, a) if i == 0 else tuple(int(v * a / 255) for v in acc))
            kl = L["start"] + L["per_week"] * (wk - 1); kr = R["start"] + R["per_week"] * (wk - 1)
            for x, lab, col, kg in ((310, L["label"], (225, 225, 230), kl), (770, R["label"], acc, kr)):
                ctext(d, lab, 455, F(36), col, x=x)
                line2 = steps[wk - 1]["left" if x < 540 else "right"] if steps else f"{L['lift'] if x < 540 else R['lift']}: {kg:g} KG"
                ctext(d, line2.upper() if steps else line2, 500, F(34), (235, 235, 240), x=x)
            if sp.get("example"):
                f = F(28); tw = d.textlength("example", font=f)
                d.rounded_rectangle([W / 2 - tw / 2 - 16, 556, W / 2 + tw / 2 + 16, 600], 10, fill=acc); ctext(d, "example", 562, f, (10, 10, 10))
        else:
            a = ease((t - CARD_T) / 0.35)
            for i, ln in enumerate(sp["endcard"]):
                ctext(d, ln.upper(), 820 + i * 90, F(56), tuple(int(v * a) for v in (acc if i == 0 else (235, 235, 240))))
        pr.stdin.write(img.tobytes())
        if fi in [int(s * FPS) for s in (0.5, weeks * WEEK_T * 0.5, weeks * WEEK_T - 0.2, END_T + 1.5, CARD_T + 1.5)]:
            img.resize((540, 960)).save(os.path.join(set_dir, "preview", f"f{fi:04d}.jpg"), quality=88)
    pr.stdin.close(); pr.wait()
    print("DONE", out, round(DUR, 1), "s")


if __name__ == "__main__":
    render(sys.argv[1])
