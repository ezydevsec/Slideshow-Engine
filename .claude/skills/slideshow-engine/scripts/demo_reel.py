#!/usr/bin/env python3
"""Hero reels from the REAL EARND demo pack (content brief + 2-week plan, founder 2026-11-24).

  python3 demo_reel.py <set_dir>        # reads <set_dir>/reel.json -> <set_dir>/<out> (1080x1920, 30 fps, silent)

reel.json:
{"out": "x.mp4",
 "segments": [
   {"clip": "01-app/assets/demos/lock-screen-tap.mp4", "ss": 0, "dur": 4.0, "hold": 0.7, "frame": {"scale": 0.74, "y": 330}},
   {"image": "01-app/assets/demos/home-screen-island.jpg", "dur": 2.0, "frame": {"scale": 0.74, "y": 330}, "zoom": 0.04},
   {"photo": "01-app/founder-photos/b9-02.jpg", "dur": 1.6, "focus": [0.5, 0.45], "dim": 0.45},   # full-bleed founder photo
   {"blank": true, "dur": 1.0}],                                     # brand background (text from "text")
 "text": [{"t0": 0, "t1": 1.6, "y": 150, "size": 72, "lines": [[["Log sets without ", 0], ["unlocking", 1]], [["your phone.", 0]]]}],
 "taps": [{"t": 1.6, "x": 800, "y": 1350}],                          # lime tap ring at the ✓ (final-timeline time, px)
 "endcard": {"dur": 1.2, "lines": [[["EARND", 1]], [["coming to iPhone", 0]]]}}
Paths are relative to the repo root. Clips play from "ss" for "dur" s; "hold" freezes the first frame that long first.
"frame" = real screen in a stroked phone frame (brief: #2A2D30 stroke); omit it for full-bleed. Text: Inter Bold,
off-white #F5F4F0, lime #C6FF3D only on runs flagged 1. Keep text out of the bottom 20% and away from the right edge.
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
W, H, FPS = 1080, 1920, 30
BG, INK, LIME, STROKE = (11, 12, 13), (245, 244, 240), (198, 255, 61), (42, 45, 48)
BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"


def frames_of(path, ss, dur):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(ss), "-i", path, "-t", str(dur), "-vf", f"fps={FPS},scale={W}:{H}",
                         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield Image.frombytes("RGB", (W, H), b)


def framed(img, fr):
    s = fr.get("scale", 0.74); sw, sh = int(W * s), int(H * s)
    sc = img.resize((sw, sh), Image.LANCZOS)
    m = Image.new("L", (sw, sh), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, sw, sh), int(70 * s / 0.74), fill=255)
    out = Image.new("RGB", (W, H), BG); x = (W - sw) // 2; y = fr.get("y", 330)
    out.paste(sc, (x, y), m)
    ImageDraw.Draw(out).rounded_rectangle((x - 9, y - 9, x + sw + 9, y + sh + 9), int(78 * s / 0.74), outline=STROKE, width=9)
    return out


def draw_lines(d, it):
    f = ImageFont.truetype(BOLD, it.get("size", 72)); y = it["y"]; lh = it.get("size", 72) * 1.18
    for line in it["lines"]:
        tw = sum(d.textlength(t, font=f) for t, _ in line); x = (W - tw) / 2
        for t, hl in line:
            d.text((x, y), t, font=f, fill=LIME if hl else INK); x += d.textlength(t, font=f)
        y += lh


def render(set_dir):
    sp = json.load(open(os.path.join(set_dir, "reel.json")))
    out = os.path.join(set_dir, sp["out"]); os.makedirs(os.path.join(set_dir, "preview"), exist_ok=True)
    pr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    fi = 0

    def emit(img):
        nonlocal fi
        t = fi / FPS; d = ImageDraw.Draw(img)
        for it in sp.get("text", []):
            if it["t0"] <= t < it["t1"]: draw_lines(d, it)
        for tp in sp.get("taps", []):
            k = (t - tp["t"]) / 0.45
            if 0 <= k <= 1:
                r = 40 + 70 * k; a = int(255 * (1 - k))
                ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ov).ellipse((tp["x"] - r, tp["y"] - r, tp["x"] + r, tp["y"] + r), outline=LIME + (a,), width=8)
                img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        pr.stdin.write(img.tobytes())
        if fi % 15 == 0: img.resize((360, 640)).save(os.path.join(set_dir, "preview", f"f{fi:04d}.jpg"), quality=85)
        fi += 1

    for seg in sp["segments"]:
        n = int(round(seg["dur"] * FPS))
        if seg.get("clip"):
            fr = seg.get("frame"); src = list(frames_of(os.path.join(ROOT, seg["clip"]), seg.get("ss", 0), seg["dur"]))
            src = [src[0]] * int(round(seg.get("hold", 0) * FPS)) + src
            for k in range(n): emit(framed(src[min(k, len(src) - 1)], fr) if fr else src[min(k, len(src) - 1)].copy())
        elif seg.get("image"):
            im = Image.open(os.path.join(ROOT, seg["image"])).convert("RGB"); fr = seg.get("frame"); z = seg.get("zoom", 0)
            for k in range(n):
                s = 1 + z * k / max(1, n - 1); iw, ih = im.size; cw, ch = int(iw / s), int(ih / s)
                c = im.crop(((iw - cw) // 2, (ih - ch) // 2, (iw + cw) // 2, (ih + ch) // 2))
                if seg.get("inset"):                 # wide image (e.g. the Dynamic Island close-up) centred on the brand background
                    iw2 = seg["inset"].get("w", 1000); c2 = c.resize((iw2, int(c.height * iw2 / c.width)), Image.LANCZOS)
                    base = Image.new("RGB", (W, H), BG); base.paste(c2, ((W - iw2) // 2, seg["inset"].get("y", 800))); emit(base)
                else:
                    emit(framed(c, fr) if fr else ImageOps.fit(c, (W, H), Image.LANCZOS))
        elif seg.get("photo"):
            im = ImageOps.fit(Image.open(os.path.join(ROOT, seg["photo"])).convert("RGB"), (W, H), Image.LANCZOS, centering=tuple(seg.get("focus", (0.5, 0.5))))
            dim = seg.get("dim", 0.0)
            if dim: im = Image.blend(im, Image.new("RGB", (W, H), BG), dim)
            for k in range(n): emit(im.copy())
        else:
            for k in range(n): emit(Image.new("RGB", (W, H), BG))
    ec = sp.get("endcard")
    if ec:
        for k in range(int(round(ec["dur"] * FPS))):
            img = Image.new("RGB", (W, H), BG); draw_lines(ImageDraw.Draw(img), {"y": 780, "size": 84, "lines": ec["lines"]}); emit(img)
    pr.stdin.close(); pr.wait(); print("DONE", out, round(fi / FPS, 2), "s")


if __name__ == "__main__":
    render(sys.argv[1])
