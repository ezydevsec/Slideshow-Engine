#!/usr/bin/env python3
"""Render a native-text tip slideshow (the @gymbratzzzz / @mayaviefit style) from native.json.

Usage: python3 native_render.py 04-sets/<set>
Writes final/preview/slide-NN.jpg (1080x1920) and final/contact-sheet.jpg.

native.json:
  {"slides": [
    {"type": "cover",    "photo": {"file": "b16-01.jpg", "focus": [0.5, 0.35], "crop": [x0,y0,x1,y1]},
                         "hook": "the 4 chest exercises i actually do", "sub": "(every week)", "anatomy": "chest"},
    {"type": "exercise", "anatomy": "chest", "name": "Machine Chest Press", "sets": "2 × 4–8",
                         "text": "handles at mid-chest. press straight out."},
    {"type": "list",     "photo": {...}, "title": "my chest day", "lines": ["...", "..."], "note": "..."},
    {"type": "tip",      "photo": {...}, "label": "bonus tip (don't skip this)", "text": "...",
                         "shot": "01-app/assets/exercise-target.png", "crop": [0,0,1,0.56], "example": true, "footer": "..."},
    {"type": "cta",      "photo": {...}, "text": "...", "sub": "..."}
  ]}
Photos come from 01-app/founder-photos/. Anatomy diagrams from 01-app/brand/anatomy/<name>.png.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
W, H = 1080, 1920
BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
if not os.path.exists(SEMI): SEMI = BOLD
F = lambda p, s: ImageFont.truetype(p, s)


def photo_bg(spec, dim=0.0, blur=0):
    im = Image.open(os.path.join(ROOT, "01-app", "founder-photos", spec["file"])).convert("RGB")
    if spec.get("crop"):
        x0, y0, x1, y1 = spec["crop"]; w, h = im.size
        im = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
    fx, fy = spec.get("focus", [0.5, 0.4])
    w, h = im.size; s = max(W / w, H / h); im = im.resize((int(w * s) + 1, int(h * s) + 1), Image.LANCZOS)
    w, h = im.size
    x = min(max(int(fx * w - W / 2), 0), w - W); y = min(max(int(fy * h - H / 2), 0), h - H)
    im = im.crop((x, y, x + W, y + H))
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    if dim: im = ImageEnhance.Brightness(im).enhance(1 - dim)
    return im


def wrap(d, text, f, maxw):
    out = []
    for para in text.split("\n"):
        line = ""
        for wd in para.split(" "):
            t = (line + " " + wd).strip()
            if d.textlength(t, font=f) <= maxw: line = t
            else:
                if line: out.append(line)
                line = wd
        out.append(line)
    return out


def native_text(img, text, size, cy, maxw=880, shadow=True, font=BOLD):
    """TikTok 'classic' style: white, centred, soft dark shadow."""
    d = ImageDraw.Draw(img); f = F(font, size)
    lines = wrap(d, text, f, maxw); lh = int(size * 1.22); y = cy - lh * len(lines) // 2
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        for i, ln in enumerate(lines):
            tw = sd.textlength(ln, font=f)
            sd.text(((W - tw) / 2, y + i * lh), ln, font=f, fill=(0, 0, 0, 200), stroke_width=4, stroke_fill=(0, 0, 0, 200))
        sh = sh.filter(ImageFilter.GaussianBlur(6)); img.paste(sh, (0, 0), sh)
        d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=f)
        d.text(((W - tw) / 2, y + i * lh), ln, font=f, fill="white")
    return y + lh * len(lines)


def pill(img, text, size, cy, fg="black", bg="white", pad=(30, 16), font=BOLD):
    d = ImageDraw.Draw(img); f = F(font, size)
    tw = d.textlength(text, font=f); asc, desc = f.getmetrics(); th = asc + desc
    x0 = (W - tw) / 2 - pad[0]; y0 = cy - th / 2 - pad[1]
    d.rounded_rectangle((x0, y0, x0 + tw + 2 * pad[0], y0 + th + 2 * pad[1]), radius=18, fill=bg)
    d.text((x0 + pad[0], y0 + pad[1]), text, font=f, fill=fg)
    return int(y0 + th + 2 * pad[1])


def example_tag(img, cx, y):
    d = ImageDraw.Draw(img); f = F(BOLD, 30); t = "example"
    tw = d.textlength(t, font=f); x = cx - tw / 2 - 16
    d.rounded_rectangle((x, y, x + tw + 32, y + 50), radius=25, fill=(198, 255, 0))
    d.text((x + 16, y + 7), t, font=f, fill="black")
    return y + 50


def anatomy(name, box_w, box_h):
    im = Image.open(os.path.join(ROOT, "01-app", "brand", "anatomy", name + ".png")).convert("RGB")
    im.thumbnail((box_w, box_h), Image.LANCZOS); return im


def render(s):
    t = s["type"]
    if t == "cover":
        img = photo_bg(s["photo"], dim=0.12)
        y = native_text(img, s["hook"], 76, int(H * 0.60))
        if s.get("sub"): native_text(img, s["sub"], 46, y + 50, font=SEMI)
        if s.get("anatomy"):
            a = anatomy(s["anatomy"], 300, 300); m = Image.new("L", a.size, 0)
            ImageDraw.Draw(m).rounded_rectangle((0, 0) + a.size, radius=28, fill=255)
            img.paste(a, ((W - a.width) // 2, int(H * 0.60) + 260), m)
        return img
    if t == "exercise":
        img = Image.new("RGB", (W, H), "black")
        band_y, band_h = 420, 760
        ImageDraw.Draw(img).rectangle((0, band_y, W, band_y + band_h), fill="white")
        a = anatomy(s["anatomy"], W - 120, band_h - 40)
        img.paste(a, ((W - a.width) // 2, band_y + (band_h - a.height) // 2))
        y = pill(img, s["name"], 50, band_y + band_h + 110)
        if s.get("sets"): y = native_text(img, s["sets"], 44, y + 60, shadow=False)
        if s.get("text"): native_text(img, s["text"], 40, y + 90, maxw=820, shadow=False, font=SEMI)
        return img
    if t == "list":
        img = photo_bg(s["photo"], dim=0.55)
        y = pill(img, s["title"], 50, 520)
        yy = y + 70
        if s.get("text"): yy = native_text(img, s["text"], 42, yy + 30, maxw=860, font=SEMI) + 50
        if s.get("example"): yy = example_tag(img, W // 2, yy) + 40  # the lines below are a numeric example
        d = ImageDraw.Draw(img); f = F(SEMI, 42)
        for ln in s.get("lines", []):
            if ln.startswith("#"):
                ln = ln[1:].strip(); ff = F(BOLD, 46); yy += 26
            else: ff = f
            tw = d.textlength(ln, font=ff); d.text(((W - tw) / 2, yy), ln, font=ff, fill="white"); yy += 62
        if s.get("note"): pill(img, s["note"], 36, yy + 80, pad=(24, 12))
        return img
    if t == "tip":
        img = photo_bg(s["photo"], dim=0.55)
        y = pill(img, s["label"], 46, 250)
        y = native_text(img, s["text"], 42, y + 110, maxw=860, font=SEMI)
        shot = Image.open(os.path.join(ROOT, s["shot"])).convert("RGB")
        if s.get("crop"):
            x0, y0, x1, y1 = s["crop"]; w, h = shot.size
            shot = shot.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
        top = int(y + (110 if s.get("example") else 50))
        maxh = H - top - (300 if s.get("footer") else 140)
        shot.thumbnail((760, maxh), Image.LANCZOS)
        m = Image.new("L", shot.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0) + shot.size, radius=40, fill=255)
        sx = (W - shot.width) // 2
        if s.get("example"): example_tag(img, W // 2, top - 80)
        img.paste(shot, (sx, top), m)
        if s.get("footer"): native_text(img, s["footer"], 40, top + shot.height + 120, maxw=880, font=SEMI)
        return img
    if t == "cta":
        img = photo_bg(s["photo"], dim=0.35)
        y = native_text(img, s["text"], 70, int(H * 0.45))
        if s.get("sub"): native_text(img, s["sub"], 44, y + 70, font=SEMI)
        return img
    raise ValueError(t)


def main(set_dir):
    spec = json.load(open(os.path.join(set_dir, "native.json")))
    out = os.path.join(set_dir, "final", "preview"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.startswith("slide-"): os.remove(os.path.join(out, f))
    thumbs = []
    for i, s in enumerate(spec["slides"], 1):
        im = render(s); p = os.path.join(out, f"slide-{i:02d}.jpg"); im.save(p, quality=92)
        t = im.copy(); t.thumbnail((270, 480)); thumbs.append(t)
    sheet = Image.new("RGB", (len(thumbs) * 280 + 10, 500), "white")
    for i, t in enumerate(thumbs): sheet.paste(t, (10 + i * 280, 10))
    sheet.save(os.path.join(set_dir, "final", "contact-sheet.jpg"), quality=85)
    print(f"rendered {len(thumbs)} slides -> {set_dir}/final")


if __name__ == "__main__":
    main(sys.argv[1])
