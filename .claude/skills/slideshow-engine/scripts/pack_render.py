#!/usr/bin/env python3
"""'Slideshow photos you may be looking for' pack (format: 02-research/formats/photos-you-may-be-looking-for.md).

  python3 pack_render.py <set_dir>      # reads <set_dir>/pack.json -> final/preview/slide-NN.jpg (1080x1920)

pack.json: {"cover": "gym slideshow photos you may be looking for\n( part 1 )",
            "mark": "@earnie.lifts",
            "slides": [{"image": "art/01.png", "quote": "optional short quote"},
                       {"placeholder": "Picture 1"}, ...],
            "end": ["part 2 tomorrow.", "ryo trains on EARND, our app. follow @earndapp"]}
Cover: plain small white text on black (the reference's look). Images are centred on black, never stretched.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
SERIF_CANDIDATES = ["/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"]
SERIF = next(p for p in SERIF_CANDIDATES if os.path.exists(p))


def wrap(d, text, font, maxw):
    out = []
    for para in text.split("\n"):
        line = ""
        for w in para.split():
            t = (line + " " + w).strip()
            if d.textlength(t, font=font) <= maxw: line = t
            else: out.append(line); line = w
        out.append(line)
    return out


def centred_lines(d, lines, font, y, fill, gap=1.25):
    lh = font.size * gap
    for i, ln in enumerate(lines):
        d.text(((W - d.textlength(ln, font=font)) / 2, y + i * lh), ln, font=font, fill=fill)
    return y + len(lines) * lh


def render(set_dir):
    sp = json.load(open(os.path.join(set_dir, "pack.json")))
    out = os.path.join(set_dir, "final", "preview"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.startswith("slide-"): os.remove(os.path.join(out, f))
    slides = []
    # cover
    im = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(im); f = ImageFont.truetype(BOLD, 40)
    lines = wrap(d, sp["cover"], f, 760); centred_lines(d, lines, f, (H - len(lines) * 50) / 2, (245, 245, 245))
    slides.append(im)
    for s in sp["slides"]:
        im = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
        if s.get("placeholder"):
            f = ImageFont.truetype(BOLD, 84); t = s["placeholder"]
            d.text(((W - d.textlength(t, font=f)) / 2, H / 2 - 50), t, font=f, fill=(245, 245, 245))
            if s.get("sub"):
                f2 = ImageFont.truetype(BOLD, 34); d.text(((W - d.textlength(s["sub"], font=f2)) / 2, H / 2 + 60), s["sub"], font=f2, fill=(150, 150, 150))
        else:
            art = Image.open(os.path.join(set_dir, s["image"])).convert("RGB")
            tw = s.get("width", 1000); th = int(art.height * tw / art.width)
            if th > 1500: th = 1500; tw = int(art.width * th / art.height)
            art = art.resize((tw, th), Image.LANCZOS); y0 = (H - th) // 2
            im.paste(art, ((W - tw) // 2, y0))
            if s.get("quote"):                         # serif quote on the black above the panel
                fq = ImageFont.truetype(SERIF, 54); ql = wrap(d, s["quote"], fq, 980)
                qh = len(ql) * 54 * 1.25
                centred_lines(d, ql, fq, max(60, y0 - qh - 50), (240, 240, 240))
            if sp.get("mark"):
                fm = ImageFont.truetype(BOLD, 24); m = sp["mark"]
                d.text(((W + tw) // 2 - d.textlength(m, font=fm) - 18, y0 + th - 42), m, font=fm, fill=(200, 200, 200), stroke_width=2, stroke_fill=(0, 0, 0))
        slides.append(im)
    if sp.get("end"):
        im = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(im); y = H / 2 - 60
        for i, ln in enumerate(sp["end"]):
            f = ImageFont.truetype(BOLD, 40 if i == 0 else 30)
            y = centred_lines(d, wrap(d, ln, f, 900), f, y, (245, 245, 245) if i == 0 else (170, 170, 170)) + 20
        slides.append(im)
    for i, im in enumerate(slides, 1): im.save(os.path.join(out, f"slide-{i:02d}.jpg"), quality=92)
    print("rendered", len(slides), "slides ->", out)


if __name__ == "__main__":
    render(sys.argv[1])
