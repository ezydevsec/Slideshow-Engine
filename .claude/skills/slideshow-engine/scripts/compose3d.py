"""Compose scenes3d renders into the final video: upscale, 2D text on top (labels, timers, captions), EARND end card.

scene3d.json "text": [{"t0": 0, "t1": 5, "text": "PERFECTIONIST", "x": 200, "y": 560, "size": 34, "color": "grey|white|acc", "box": false}]
Frames: <set_dir>/3d/<scene>/f*.png (+ <scene>-city for rooms), rendered at 15 fps; each is shown twice (30 fps).
"""
import glob, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
F = lambda s: ImageFont.truetype(MONO, s)


def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def ctext(d, txt, x, y, f, fill):
    d.text((x - d.textlength(txt, font=f) / 2, y), txt, font=f, fill=fill)


def compose(set_dir, sp):
    acc = tuple(sp.get("accent", (255, 196, 120)))
    dirs = [os.path.join(set_dir, "3d", sp["scene"])]
    if os.path.isdir(dirs[0] + "-city"): dirs.append(dirs[0] + "-city")
    frames = []
    for d_ in dirs: frames += sorted(glob.glob(os.path.join(d_, "f*.png")))
    T_END = len(frames) / 15.0; DUR = T_END + 3.0
    out = os.path.join(set_dir, sp["out"]); os.makedirs(os.path.join(set_dir, "preview"), exist_ok=True)
    pr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], stdin=subprocess.PIPE)
    COL = {"white": (240, 240, 240), "grey": (175, 175, 182), "acc": acc}
    cache = {}
    for fi in range(int(DUR * FPS)):
        t = fi / FPS
        if t < T_END:
            src = frames[min(len(frames) - 1, int(t * 15))]
            if src not in cache:
                cache.clear(); cache[src] = Image.open(src).convert("RGB").resize((W, H), Image.LANCZOS)
            img = cache[src].copy()
        else:
            img = Image.new("RGB", (W, H), (6, 6, 8))
        d = ImageDraw.Draw(img)
        if t < T_END:
            for it in sp["text"]:
                if not (it["t0"] <= t < it.get("t1", 1e9)): continue
                a = ease((t - it["t0"]) / 0.25); c = tuple(int(v * a) for v in COL[it.get("color", "white")])
                txt = it["text"]
                if "{n}" in txt: txt = txt.replace("{n}", str(min(it.get("max", 999), int((t - it["t0"]) * it.get("rate", 1)) + 1)))
                if "{timer}" in txt: txt = txt.replace("{timer}", f"{int((t - it['t0']) * it.get('rate', 1)) // 60}:{int((t - it['t0']) * it.get('rate', 1)) % 60:02d}")
                f = F(it.get("size", 34))
                if it.get("box"):
                    tw = d.textlength(txt, font=f); x = it["x"]
                    d.rounded_rectangle([x - tw / 2 - 28, it["y"] - 18, x + tw / 2 + 28, it["y"] + it.get("size", 34) + 22], 22, fill=(8, 8, 10), outline=c, width=3)
                ctext(d, txt, it["x"], it["y"], f, c)
        else:
            a = ease((t - T_END) / 0.35)
            for i, ln in enumerate(sp["endcard"]):
                ctext(d, ln.upper(), W / 2, 820 + i * 90, F(50), tuple(int(v * a) for v in (acc if i == 0 else (235, 235, 240))))
        pr.stdin.write(img.tobytes())
        if fi % int(FPS * 2.5) == 0: img.resize((540, 960)).save(os.path.join(set_dir, "preview", f"f{fi:04d}.jpg"), quality=86)
    pr.stdin.close(); pr.wait(); print("DONE", out, round(DUR, 1), "s")
