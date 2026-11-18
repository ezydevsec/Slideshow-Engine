#!/usr/bin/env python3
"""Compose Higgsfield (Kling) clips into a finished vertical video: full-frame or stacked split segments,
our baked 2D text (same items as compose3d.py), EARND end card.

  python3 hf_compose.py <set_dir>      # reads <set_dir>/hf.json

hf.json: {"out": "x.mp4", "accent": [255,196,120], "endcard": [...],
          "segments": [{"dur": 15, "clips": ["hf/a.mp4"]},                       # full frame
                       {"dur": 7.5, "split": true, "clips": ["hf/top.mp4", "hf/bot.mp4"], "crop_y": [550, 550]}],
          "text": [{"t0", "t1", "text", "x", "y", "size", "color", "box", "rate", "max"}]}   # times on the final timeline
Clips are scaled to 1080x1920 at 30 fps; a clip shorter than its segment holds its last frame.
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compose3d import W, H, FPS, F, ease, ctext


class Clip:
    def __init__(self, path):
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={FPS},scale={W}:{H}:flags=lanczos,setsar=1",
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.last = None

    def next(self):
        b = self.p.stdout.read(W * H * 3)
        if len(b) == W * H * 3: self.last = Image.frombytes("RGB", (W, H), b)
        return self.last.copy()


def draw_text(d, it, t, acc):
    COL = {"white": (240, 240, 240), "grey": (175, 175, 182), "acc": acc}
    a = ease((t - it["t0"]) / 0.25); c = tuple(int(v * a) for v in COL[it.get("color", "white")])
    txt, rate = it["text"], it.get("rate", 1)
    if "{n}" in txt: txt = txt.replace("{n}", str(min(it.get("max", 999), int((t - it["t0"]) * rate) + 1)))
    if "{timer}" in txt: s = int((t - it["t0"]) * rate); txt = txt.replace("{timer}", f"{s // 60}:{s % 60:02d}")
    size = it.get("size", 34); f = F(size)
    if it.get("box"):
        tw = d.textlength(txt, font=f); x = it["x"]
        d.rounded_rectangle([x - tw / 2 - 28, it["y"] - 18, x + tw / 2 + 28, it["y"] + size + 22], 22,
                            fill=(8, 8, 10), outline=c, width=3)
    ctext(d, txt, it["x"], it["y"], f, c)


def compose(set_dir):
    sp = json.load(open(os.path.join(set_dir, "hf.json")))
    acc = tuple(sp.get("accent", (255, 196, 120)))
    out = os.path.join(set_dir, sp["out"]); os.makedirs(os.path.join(set_dir, "preview"), exist_ok=True)
    pr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], stdin=subprocess.PIPE)
    T = 0.0; fi = 0
    for seg in sp["segments"]:
        clips = [Clip(os.path.join(set_dir, c)) for c in seg["clips"]]
        for _ in range(int(round(seg["dur"] * FPS))):
            t = fi / FPS
            if seg.get("split"):
                img = Image.new("RGB", (W, H))
                for k, c in enumerate(clips):
                    y0 = seg.get("crop_y", [480, 480])[k]
                    img.paste(c.next().crop((0, y0, W, y0 + H // 2)), (0, k * H // 2))
                ImageDraw.Draw(img).rectangle([0, H // 2 - 3, W, H // 2 + 3], fill=(6, 6, 8))
            else:
                img = clips[0].next()
            d = ImageDraw.Draw(img)
            for it in sp["text"]:
                if it["t0"] <= t < it.get("t1", 1e9): draw_text(d, it, t, acc)
            pr.stdin.write(img.tobytes())
            if fi % int(FPS * 2.5) == 0: img.resize((540, 960)).save(os.path.join(set_dir, "preview", f"f{fi:04d}.jpg"), quality=86)
            fi += 1
        for c in clips: c.p.kill()
        T += seg["dur"]
    for k in range(int(3.0 * FPS)):
        img = Image.new("RGB", (W, H), (6, 6, 8)); d = ImageDraw.Draw(img); a = ease(k / FPS / 0.35)
        for i, ln in enumerate(sp["endcard"]):
            ctext(d, ln.upper(), W / 2, 820 + i * 90, F(50), tuple(int(v * a) for v in (acc if i == 0 else (235, 235, 240))))
        pr.stdin.write(img.tobytes())
        if k == 45: img.resize((540, 960)).save(os.path.join(set_dir, "preview", f"f{fi + k:04d}.jpg"), quality=86)
    pr.stdin.close(); pr.wait(); print("DONE", out, round(T + 3.0, 1), "s")


if __name__ == "__main__":
    compose(sys.argv[1])
