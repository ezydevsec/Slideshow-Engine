#!/usr/bin/env python3
"""Render a 3D anatomy exercise-demo slideshow (format A, @workitapp-style) from demo.json.

  python3 demo_render.py 04-sets/<set>

demo.json slides (1080x1920, light studio grey):
  {"type": "cover",    "image": "01-app/brand/demos/x.jpg", "hook": "...", "sub": "..."}
  {"type": "exercise", "image": "...", "kicker": "#1", "title": "CALF PRESS", "muscle": "calves", "sets": "2 × 4–8", "cue": "..."}
  {"type": "app",      "title": "...", "body": "...", "shot": "01-app/assets/x.png", "crop": [l,t,r,b], "example": true}
  {"type": "cta",      "image": "...", "title": "...", "body": "..."}
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
W, H = 1080, 1920
BG = (232, 232, 232); INK = (17, 17, 17); RED = (226, 54, 54); LIME = (198, 255, 0)
BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
if not os.path.exists(SEMI): SEMI = BOLD
F = lambda p, s: ImageFont.truetype(p, s)


def wrap(d, text, f, maxw):
    out, line = [], ""
    for wd in text.split():
        t = (line + " " + wd).strip()
        if d.textlength(t, font=f) <= maxw: line = t
        else: out.append(line); line = wd
    out.append(line); return out


def text(d, s, f, y, fill=INK, maxw=W - 140, lh=1.2, x=None):
    for ln in wrap(d, s, f, maxw):
        tw = d.textlength(ln, font=f); d.text(((W - tw) / 2 if x is None else x, y), ln, font=f, fill=fill)
        y += int(f.size * lh)
    return y


def pill(d, s, size, y, bg=RED, fg="white"):
    f = F(BOLD, size); tw = d.textlength(s, font=f); a, b = f.getmetrics()
    x = (W - tw) / 2 - 26; d.rounded_rectangle((x, y, x + tw + 52, y + a + b + 20), radius=30, fill=bg)
    d.text((x + 26, y + 10), s, font=f, fill=fg); return y + a + b + 20


def place(img, path, top, bottom, fy=0.5):
    pic = Image.open(os.path.join(ROOT, path)).convert("RGB")
    h = bottom - top; s = max(W / pic.width, h / pic.height)
    pic = pic.resize((int(pic.width * s) + 1, int(pic.height * s) + 1), Image.LANCZOS)
    x = (pic.width - W) // 2; y = min(max(int(fy * pic.height - h / 2), 0), pic.height - h)
    img.paste(pic.crop((x, y, x + W, y + h)), (0, top))


def render(s):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img); t = s["type"]
    if t == "cover":
        place(img, s["image"], 560, H, s.get("focus_y", 0.5)); d = ImageDraw.Draw(img)
        y = text(d, s["hook"], F(BOLD, 84), 150, lh=1.12)
        if s.get("sub"): text(d, s["sub"], F(SEMI, 44), y + 24, fill=(70, 70, 70))
        return img
    if t == "exercise":
        place(img, s["image"], 440, H - 300, s.get("focus_y", 0.5)); d = ImageDraw.Draw(img)
        d.text((70, 110), s["kicker"], font=F(BOLD, 44), fill=RED)
        y = text(d, s["title"], F(BOLD, 76), 170, x=70, lh=1.08)
        pill(d, s["muscle"], 38, max(y + 16, 340))
        d.rectangle((0, H - 300, W, H), fill=BG)
        y = text(d, s["sets"], F(BOLD, 52), H - 270)
        text(d, s["cue"], F(SEMI, 40), y + 18, fill=(60, 60, 60), maxw=W - 180)
        return img
    if t == "app":
        y = text(d, s["title"], F(BOLD, 70), 170, lh=1.1)
        y = text(d, s["body"], F(SEMI, 42), y + 30, fill=(60, 60, 60))
        if s.get("example"): y = pill(d, "example", 34, y + 40, bg=LIME, fg="black")
        shot = Image.open(os.path.join(ROOT, s["shot"])).convert("RGB")
        if s.get("crop"):
            l, tp, r, b = s["crop"]; w, h = shot.size
            shot = shot.crop((int(l * w), int(tp * h), int(r * w), int(b * h)))
        shot.thumbnail((860, H - y - 220), Image.LANCZOS)
        m = Image.new("L", shot.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0) + shot.size, radius=44, fill=255)
        img.paste(shot, ((W - shot.width) // 2, y + 50), m)
        return img
    if t == "cta":
        place(img, s["image"], 600, H, s.get("focus_y", 0.5)); d = ImageDraw.Draw(img)
        y = text(d, s["title"], F(BOLD, 80), 200, lh=1.1)
        text(d, s["body"], F(SEMI, 42), y + 30, fill=(60, 60, 60))
        return img
    raise ValueError(t)


def main(set_dir):
    spec = json.load(open(os.path.join(set_dir, "demo.json")))
    out = os.path.join(set_dir, "final", "preview"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.startswith("slide-"): os.remove(os.path.join(out, f))
    thumbs = []
    for i, s in enumerate(spec["slides"], 1):
        im = render(s); im.save(os.path.join(out, f"slide-{i:02d}.jpg"), quality=92)
        t = im.copy(); t.thumbnail((270, 480)); thumbs.append(t)
    sheet = Image.new("RGB", (len(thumbs) * 280 + 10, 500), "white")
    for i, t in enumerate(thumbs): sheet.paste(t, (10 + i * 280, 10))
    sheet.save(os.path.join(set_dir, "final", "contact-sheet.jpg"), quality=85)
    print(f"rendered {len(thumbs)} slides -> {set_dir}/final")


if __name__ == "__main__":
    main(sys.argv[1])
