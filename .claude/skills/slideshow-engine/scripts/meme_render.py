#!/usr/bin/env python3
"""Render a relatable meme slideshow (@earnie.lifts) from meme.json.

  python3 meme_render.py 04-sets/<set>

meme.json: {"slides": [{"caption": "me walking into the gym", "image": "01-app/brand/memes/x.jpg"}, ...]}
Each slide is 1080x1350: a white caption band on top (black, bold, centred), the image filling the rest.
An optional "footer" on a slide adds a small line under the image (used on the last slide for the CTA).
Writes final/preview/slide-NN.jpg and final/contact-sheet.jpg.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
W, H = 1080, 1350
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


def cover_fit(im, w, h, fy=0.4):
    s = max(w / im.width, h / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x = (im.width - w) // 2; y = min(max(int(fy * im.height - h / 2), 0), im.height - h)
    return im.crop((x, y, x + w, y + h))


def render(s):
    img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
    size = 58 if len(s["caption"]) < 60 else 50
    f = F = ImageFont.truetype(BOLD, size)
    lines = wrap(d, s["caption"], f, W - 120); lh = int(size * 1.22)
    band = max(220, lh * len(lines) + 90)
    y = (band - lh * len(lines)) // 2
    for ln in lines:
        tw = d.textlength(ln, font=f); d.text(((W - tw) / 2, y), ln, font=f, fill="black"); y += lh
    foot = 90 if s.get("footer") else 0
    pic = Image.open(os.path.join(ROOT, s["image"])).convert("RGB")
    img.paste(cover_fit(pic, W, H - band - foot, s.get("focus_y", 0.45)), (0, band))
    if foot:
        ff = ImageFont.truetype(SEMI, 32); t = s["footer"]
        tw = d.textlength(t, font=ff); d.text(((W - tw) / 2, H - foot + 26), t, font=ff, fill="black")
    return img


def main(set_dir):
    spec = json.load(open(os.path.join(set_dir, "meme.json")))
    out = os.path.join(set_dir, "final", "preview"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.startswith("slide-"): os.remove(os.path.join(out, f))
    thumbs = []
    for i, s in enumerate(spec["slides"], 1):
        im = render(s); im.save(os.path.join(out, f"slide-{i:02d}.jpg"), quality=92)
        t = im.copy(); t.thumbnail((320, 400)); thumbs.append(t)
    sheet = Image.new("RGB", (len(thumbs) * 330 + 10, 420), "white")
    for i, t in enumerate(thumbs): sheet.paste(t, (10 + i * 330, 10))
    sheet.save(os.path.join(set_dir, "final", "contact-sheet.jpg"), quality=85)
    print(f"rendered {len(thumbs)} slides -> {set_dir}/final")


if __name__ == "__main__":
    main(sys.argv[1])
