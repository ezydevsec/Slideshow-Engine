#!/usr/bin/env python3
"""@earnie.lifts bluebro-style tier-list slideshow (white, gritty anime Earnie, no muscle glow; an amber `works:` tag instead).

  python3 tier_render.py <set_dir>     # reads <set_dir>/tier.json -> final/preview/slide-NN.jpg (1080x1350)

tier.json slides:
  {"type": "cover", "title": ["every lat exercise,", "ranked."], "sub": "argue with me.", "pose": "cover-arms-crossed"}
  {"type": "list", "title": "the whole list", "sub": "...", "rows": [["S", ["lat pulldown", "pull-up"]], ...]}
  {"type": "tier", "tier": "S", "name": "lat pulldown", "works": "lats", "lines": ["...", "..."], "pose": "pulldown", "footer": "optional"}
Poses: 01-app/brand/earnie-v3/<pose>.png
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
W, H = 1080, 1350; AMB = (255, 150, 30); INK = (20, 20, 22)
BL = "/usr/share/fonts/opentype/inter/Inter-Black.otf"; BO = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
TC = {'S': (255, 150, 30), 'A': (255, 196, 120), 'B': (235, 225, 210), 'C': (225, 225, 228), 'D': (215, 215, 218), 'F': (205, 205, 208)}
F = ImageFont.truetype


def pose(n): return Image.open(os.path.join(ROOT, "01-app", "brand", "earnie-v3", f"{n}.png")).convert("RGB")


def bgcol(im):
    a = np.asarray(im); c = np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3), a[:, :8].reshape(-1, 3)])
    return tuple(int(v) for v in np.median(c, axis=0))


def place(s, im, top, bot):
    im = im.copy(); im.thumbnail((W - 100, bot - top)); s.paste(im, ((W - im.width) // 2, bot - im.height))


def foot(s, d, t):
    f = F(BO, 34); d.text(((W - d.textlength(t, font=f)) / 2, H - 80), t, font=f, fill=(110, 110, 115))


def render(set_dir):
    sp = json.load(open(os.path.join(set_dir, "tier.json")))
    out = os.path.join(set_dir, "final", "preview"); os.makedirs(out, exist_ok=True)
    for f_ in os.listdir(out): os.remove(os.path.join(out, f_))
    pages = []
    for n, s in enumerate(sp["slides"], 1):
        t = s["type"]
        if t == "cover":
            im = pose(s["pose"]); img = Image.new("RGB", (W, H), bgcol(im)); d = ImageDraw.Draw(img); y = 80
            for i, ln in enumerate(s["title"]):
                f = F(BL, 88); tw = d.textlength(ln, font=f)
                if i == len(s["title"]) - 1: d.rounded_rectangle([(W - tw) / 2 - 14, y + 10, (W + tw) / 2 + 14, y + 104], 14, fill=AMB)
                d.text(((W - tw) / 2, y), ln, font=f, fill=INK); y += 106
            if s.get("sub"): f = F(BO, 40); d.text(((W - d.textlength(s["sub"], font=f)) / 2, y + 8), s["sub"], font=f, fill=(100, 100, 105)); y += 60
            place(img, im, y + 20, H - 20)
        elif t == "list":
            img = Image.new("RGB", (W, H), (250, 248, 244)); d = ImageDraw.Draw(img)
            d.text((70, 80), s["title"], font=F(BL, 70), fill=INK)
            if s.get("sub"): d.text((70, 170), s["sub"], font=F(BO, 34), fill=(110, 110, 115))
            rows = s["rows"]; rh = min(200, (H - 300) // len(rows) - 25); y = 250
            for tr, items in rows:
                d.rounded_rectangle([70, y, 210, y + rh], 18, fill=TC[tr]); fl = F(BL, int(rh * 0.55)); d.text((140 - d.textlength(tr, font=fl) / 2, y + rh * 0.15), tr, font=fl, fill=INK)
                d.rounded_rectangle([230, y, W - 70, y + rh], 18, fill="white", outline=(225, 222, 215), width=3)
                fi = F(BO, 44); gap = 58; y0 = y + (rh - gap * len(items)) / 2 + 4
                for k, it in enumerate(items): d.text((262, y0 + k * gap), it, font=fi, fill=INK)
                y += rh + 25
            if s.get("footer"): foot(img, d, s["footer"])
        elif t == "tier":
            im = pose(s["pose"]); img = Image.new("RGB", (W, H), bgcol(im)); d = ImageDraw.Draw(img); y = 80
            d.rounded_rectangle([70, y, 190, y + 120], 18, fill=TC[s["tier"]]); f = F(BL, 90); d.text((130 - d.textlength(s["tier"], font=f) / 2, y + 5), s["tier"], font=f, fill=INK)
            fn = F(BL, 62)
            while d.textlength(s["name"], font=fn) > W - 300: fn = F(BL, fn.size - 4)
            d.text((220, y + 24), s["name"], font=fn, fill=INK); y += 145
            if s.get("works"):
                tag = "works: " + s["works"]; ft = F(BL, 32); tw = d.textlength(tag, font=ft)
                d.rounded_rectangle([70, y, 70 + tw + 36, y + 52], 26, fill=AMB); d.text((88, y + 7), tag, font=ft, fill=INK); y += 75
            for ln in s.get("lines", []): d.text((70, y), ln, font=F(BO, 40), fill=(90, 90, 95)); y += 56
            bot = H - (110 if s.get("footer") else 30); place(img, im, y + 20, bot)
            if s.get("footer"): foot(img, d, s["footer"])
        img.save(os.path.join(out, f"slide-{n:02d}.jpg"), quality=93); pages.append(img)
    sh = Image.new("RGB", (len(pages) * 310, 400), (230, 230, 230))
    for i, p in enumerate(pages): sh.paste(p.resize((300, 375)), (5 + i * 310, 12))
    sh.save(os.path.join(set_dir, "final", "contact-sheet.jpg"), quality=90)
    print(f"rendered {len(pages)} slides -> {set_dir}/final")


if __name__ == "__main__":
    render(sys.argv[1])
