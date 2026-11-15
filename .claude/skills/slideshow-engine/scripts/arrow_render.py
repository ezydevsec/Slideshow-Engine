#!/usr/bin/env python3
"""@earndapp "pick 1 per slide" slideshow, the current @arrowfitnessapp / @bluebro.fit structure (checked 2026-11-15),
on @earndapp's black + lime brand. Real EARND exercises, our graphite mascot, real app screen. No invented reviews.

  python3 arrow_render.py <set_dir>     # reads <set_dir>/arrow.json, writes final/preview/slide-NN.jpg (1080x1350)

arrow.json slides:
  {"type": "cover", "title": [["the science of the", false], ["perfect upper day", true]], "sub": "(pick 1 exercise per slide → your full workout)", "pose": "cover-arms-open"}
  {"type": "structure", "title": "the structure", "sub": "...", "items": ["chest (pressing)", ...]}
  {"type": "pick", "n": 1, "muscle": "chest (pressing)", "sets": "2 × 4–8", "anatomy": "chest", "options": [["machine chest press", "chest-press"], ["pec deck", "pec-deck"]], "note": "optional cue"}
  {"type": "app", "title": [["EARND shows you", false], ["what to beat", true], ["on every set", false]], "shot": "01-app/assets/x.png", "crop": [l,t,r,b], "example": true, "footer": "launches soon. follow for the launch."}
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
W, H, M = 1080, 1350, 80
BG, INK, SOFT, LIME, DARK = (11, 11, 11), (245, 245, 245), (160, 160, 165), (198, 255, 0), (11, 11, 11)
BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"; BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
ITAL = "/usr/share/fonts/opentype/inter/Inter-MediumItalic.otf"
if not os.path.exists(ITAL): ITAL = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
F = lambda p, s: ImageFont.truetype(p, s)


def hl_line(d, x, y, text, size, hl, center=False):
    f = F(BLACK, size); tw = d.textlength(text, font=f)
    if center: x = (W - tw) / 2
    if hl:
        d.rounded_rectangle([x - 10, y + size * 0.12, x + tw + 10, y + size * 1.08], 10, fill=LIME)
        d.text((x, y), text, font=f, fill=DARK)
    else:
        d.text((x, y), text, font=f, fill=INK)
    return y + size * 1.12


def pose(name):
    return Image.open(os.path.join(ROOT, "01-app", "brand", "poses", f"{name}-cutout.png")).convert("RGBA")


def anatomy(name, size):
    """Red-muscle anatomy art recoloured to lime on a light card (Arrow's green-muscle look)."""
    im = Image.open(os.path.join(ROOT, "01-app", "brand", "anatomy", f"{name}.png")).convert("RGB")
    a = np.asarray(im).astype(np.float32); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = np.clip((r - (g + b) / 2) / 120, 0, 1)[..., None]
    a = a * (1 - red) + np.array(LIME, np.float32) * red * (0.55 + 0.45 * (a.mean(axis=2, keepdims=True) / 255))
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8)); im.thumbnail((size, size))
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0) + im.size, 26, fill=255)
    return im, m


def fit_in(img, im, box):
    x0, y0, x1, y1 = box; im = im.copy(); im.thumbnail((x1 - x0, y1 - y0), Image.LANCZOS)
    img.paste(im, (int(x0 + (x1 - x0 - im.width) / 2), int(y1 - im.height)), im)


def render(set_dir):
    sp = json.load(open(os.path.join(set_dir, "arrow.json")))
    out = os.path.join(set_dir, "final", "preview"); os.makedirs(out, exist_ok=True)
    for f_ in os.listdir(out): os.remove(os.path.join(out, f_))
    pages = []
    for n, s in enumerate(sp["slides"], 1):
        img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img); t = s["type"]
        if t == "cover":
            y = 150
            for text, hl in s["title"]: y = hl_line(d, 0, y, text, 92, hl, center=True)
            if s.get("sub"):
                f = F(ITAL, 34); tw = d.textlength(s["sub"], font=f); d.text(((W - tw) / 2, y + 20), s["sub"], font=f, fill=SOFT); y += 80
            fit_in(img, pose(s.get("pose", "cover-arms-open")), (M, y + 20, W - M, H - 40))
        elif t == "structure":
            y = 150; y = hl_line(d, M, y, s["title"], 80, False)
            if s.get("sub"):
                f = F(ITAL, 34); d.text((M, y + 10), s["sub"], font=f, fill=SOFT); y += 70
            y += 50
            for it in s["items"]:
                d.ellipse([M, y, M + 52, y + 52], fill=LIME)
                d.line([(M + 13, y + 27), (M + 23, y + 37), (M + 40, y + 16)], fill=DARK, width=6, joint="curve")
                d.text((M + 80, y + 4), it, font=F(BOLD, 44), fill=INK); y += 92
            if s.get("note"): d.text((M, y + 30), s["note"], font=F(BOLD, 38), fill=LIME)
        elif t == "pick":
            y = 130
            f = F(BLACK, 30); pw = d.textlength("pick 1", font=f)
            d.rounded_rectangle([M, y, M + pw + 32, y + 50], 25, fill=LIME); d.text((M + 16, y + 7), "pick 1", font=f, fill=DARK)
            ana, am = anatomy(s["anatomy"], 230); img.paste(ana, (W - M - ana.width, y - 10), am)
            y += 80
            d.text((M, y), f"{s['n']} · {s['muscle']}", font=F(BLACK, 66), fill=INK); y += 90
            d.text((M, y), s["sets"], font=F(BOLD, 40), fill=SOFT); y += 70
            if s.get("note"): d.text((M, y), s["note"], font=F(ITAL, 32), fill=SOFT); y += 50
            top = max(y + 30, 450); bot = H - 150; mid = W // 2
            for i, (name, p) in enumerate(s["options"]):
                x0 = M if i == 0 else mid + 20; x1 = mid - 20 if i == 0 else W - M
                fit_in(img, pose(p), (x0, top, x1, bot))
                f2 = F(BOLD, 38); tw = d.textlength(name, font=f2)
                d.text(((x0 + x1 - tw) / 2, bot + 30), name, font=f2, fill=INK)
            d = ImageDraw.Draw(img); d.line([(mid, top + 40), (mid, bot)], fill=LIME, width=5)
        elif t == "app":
            y = 120
            for text, hl in s["title"]: y = hl_line(d, 0, y, text, 76, hl, center=True)
            sh = Image.open(os.path.join(ROOT, s["shot"])).convert("RGB"); c = s.get("crop", [0, 0, 1, 1])
            sh = sh.crop((int(c[0] * sh.width), int(c[1] * sh.height), int(c[2] * sh.width), int(c[3] * sh.height)))
            sh.thumbnail((W - 2 * M, H - y - 240), Image.LANCZOS)
            m = Image.new("L", sh.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0) + sh.size, 36, fill=255)
            px = (W - sh.width) // 2; py = int(y + 60); img.paste(sh, (px, py), m)
            if s.get("example"):
                f = F(BLACK, 28); tw = d.textlength("example", font=f)
                d.rounded_rectangle([px + sh.width - tw - 40, py - 54, px + sh.width, py - 10], 10, fill=LIME); d.text((px + sh.width - tw - 20, py - 50), "example", font=f, fill=DARK)
            if s.get("footer"):
                f = F(BOLD, 40); tw = d.textlength(s["footer"], font=f); d.text(((W - tw) / 2, H - 110), s["footer"], font=f, fill=LIME)
        p = os.path.join(out, f"slide-{n:02d}.jpg"); img.save(p, quality=93); pages.append(img)
    tw_ = 300; sheet = Image.new("RGB", (tw_ * len(pages) + 8 * (len(pages) - 1), int(tw_ * H / W)), "white")
    for i, pg in enumerate(pages): sheet.paste(pg.resize((tw_, int(tw_ * H / W))), (i * (tw_ + 8), 0))
    sheet.save(os.path.join(set_dir, "final", "contact-sheet.jpg"), quality=88)
    print(f"rendered {len(pages)} slides -> {set_dir}/final")


if __name__ == "__main__":
    render(sys.argv[1])
