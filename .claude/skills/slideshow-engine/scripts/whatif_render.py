#!/usr/bin/env python3
"""Render a what-if escalation slideshow (@whatif.overload) from whatif.json.

  python3 whatif_render.py 04-sets/<set>

Each slide is 1080x1920: a full-bleed 3D still, bold white text with a black stroke near the top,
an optional counter pill ("week 52"), and an optional lime "example" tag for numbers.
  {"image": "01-app/brand/whatif/x.jpg", "text": "...", "counter": "week 52", "example": true, "sub": "...", "focus_y": 0.5}
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
W, H = 1080, 1920
BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
if not os.path.exists(SEMI): SEMI = BOLD


def wrap(d, text, f, maxw):
    out, line = [], ""
    for wd in text.split():
        t = (line + " " + wd).strip()
        if d.textlength(t, font=f) <= maxw: line = t
        else: out.append(line); line = wd
    out.append(line); return out


def stroke_text(d, s, f, y, maxw=W - 120, sw=7):
    for ln in wrap(d, s, f, maxw):
        tw = d.textlength(ln, font=f)
        d.text(((W - tw) / 2, y), ln, font=f, fill="white", stroke_width=sw, stroke_fill="black")
        y += int(f.size * 1.18)
    return y


def pill(d, s, size, y, bg, fg):
    f = ImageFont.truetype(BOLD, size); tw = d.textlength(s, font=f); a, b = f.getmetrics()
    x = (W - tw) / 2 - 24; d.rounded_rectangle((x, y, x + tw + 48, y + a + b + 18), radius=28, fill=bg)
    d.text((x + 24, y + 9), s, font=f, fill=fg); return y + a + b + 18


def render(s):
    pic = Image.open(os.path.join(ROOT, s["image"])).convert("RGB")
    sc = max(W / pic.width, H / pic.height); pic = pic.resize((int(pic.width * sc) + 1, int(pic.height * sc) + 1), Image.LANCZOS)
    fy = s.get("focus_y", 0.5); x = (pic.width - W) // 2; y = min(max(int(fy * pic.height - H / 2), 0), pic.height - H)
    img = pic.crop((x, y, x + W, y + H)); d = ImageDraw.Draw(img)
    y = 190
    if s.get("counter"): y = pill(d, s["counter"], 44, y, (0, 0, 0), "white") + 30
    y = stroke_text(d, s["text"], ImageFont.truetype(BOLD, 74 if len(s["text"]) < 70 else 62), y)
    if s.get("example"): y = pill(d, "example", 32, y + 20, (198, 255, 0), "black")
    if s.get("sub"): stroke_text(d, s["sub"], ImageFont.truetype(SEMI, 44), H - 330, sw=5)
    return img


def main(set_dir):
    spec = json.load(open(os.path.join(set_dir, "whatif.json")))
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
