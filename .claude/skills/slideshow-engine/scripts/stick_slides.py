#!/usr/bin/env python3
"""@earnie.lifts stickman story slideshow (stills in the same look as anim_stick.py videos). 1080x1350.

  python3 stick_slides.py <set_dir>     # reads <set_dir>/stickslides.json -> final/preview/slide-NN.jpg

slide: {"text": "line (narration)", "hud": "small mono line", "list": ["..."], "figs": [{"x": 540, "p": 1.0, "slump": 0, "earnie": true, "plates": 2}], "footer": "..."}
Earnie = the figure with "earnie": true (amber glow). Others are plain white.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim_stick as st

W, H = 1080, 1350; FLOOR = 1120; AMB = (255, 196, 120)
INTER = "/usr/share/fonts/opentype/inter/Inter-Black.otf"; MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
F = lambda p, s: ImageFont.truetype(p, s)


def wrap(d, txt, f, maxw):
    out, line = [], ""
    for w in txt.split():
        t = (line + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: line = t
        else: out.append(line); line = w
    return out + [line]


def render(set_dir):
    sp = json.load(open(os.path.join(set_dir, "stickslides.json")))
    out = os.path.join(set_dir, "final", "preview"); os.makedirs(out, exist_ok=True)
    yy, xx = np.mgrid[0:H, 0:W]
    pages = []
    for n, s in enumerate(sp["slides"], 1):
        base = np.zeros((H, W, 3), np.float32)
        for f_ in s.get("figs", []):
            base += 55 * np.exp(-(((xx - f_["x"]) / 230) ** 2 + ((yy - FLOOR) / 60) ** 2))[:, :, None] * np.array([255, 180, 100]) / 255
        img = Image.fromarray(base.clip(0, 255).astype(np.uint8))
        scene = Image.new("RGB", (W, H)); sd = ImageDraw.Draw(scene); glow = Image.new("L", (W, H)); gd = ImageDraw.Draw(glow)
        st.FLOOR = FLOOR
        for f_ in s.get("figs", []):
            sc = f_.get("scale", 1.0)
            hy = st.figure(sd, f_["x"], f_.get("p", 1.0), slump=f_.get("slump", 0), col=(255, 255, 255) if f_.get("earnie") else (205, 205, 212))
            if f_.get("plates"): st.barbell(sd, f_["x"], hy, f_["plates"], AMB)
            if f_.get("earnie"): st.figure(gd, f_["x"], f_.get("p", 1.0), slump=f_.get("slump", 0), col=255, shade=255)
        img.paste(scene, (0, 0), scene.convert("L").point(lambda v: 255 if v > 4 else 0))
        top = scene.crop((0, FLOOR - 230, W, FLOOR)).transpose(Image.FLIP_TOP_BOTTOM)
        refl = Image.blend(Image.new("RGB", top.size), top, 0.2)
        img.paste(refl, (0, FLOOR), refl.convert("L").point(lambda v: 255 if v > 3 else 0))
        arr = np.asarray(img).astype(np.float32) + np.asarray(glow.filter(ImageFilter.GaussianBlur(18)), np.float32)[:, :, None] / 255 * np.array(AMB) * 0.32
        img = Image.fromarray(arr.clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
        f = F(INTER, 60); y = 110
        for ln in wrap(d, s["text"], f, W - 140):
            d.text(((W - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=(245, 245, 245)); y += 74
        if s.get("hud"):
            fh = F(MONO, 34); d.text(((W - d.textlength(s["hud"], font=fh)) / 2, y + 20), s["hud"], font=fh, fill=AMB); y += 70
        for i, ln in enumerate(s.get("list", [])):
            fl = F(MONO, 36); d.text((90, y + 40 + i * 60), ln, font=fl, fill=(230, 230, 235))
        if s.get("footer"):
            ff = F("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 32)
            for i, ln in enumerate(wrap(d, s["footer"], ff, W - 160)):
                d.text(((W - d.textlength(ln, font=ff)) / 2, H - 120 + i * 42), ln, font=ff, fill=AMB)
        img.save(os.path.join(out, f"slide-{n:02d}.jpg"), quality=92); pages.append(img)
    tw = 300; sheet = Image.new("RGB", (tw * len(pages) + 8 * (len(pages) - 1), int(tw * H / W)), "white")
    for i, pg in enumerate(pages): sheet.paste(pg.resize((tw, int(tw * H / W))), (i * (tw + 8), 0))
    sheet.save(os.path.join(set_dir, "final", "contact-sheet.jpg"), quality=88)
    print(f"rendered {len(pages)} slides -> {set_dir}/final")


if __name__ == "__main__":
    render(sys.argv[1])
