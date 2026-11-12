#!/usr/bin/env python3
"""Comic story slideshow for @earnie.lifts (style: 02-research/formats/account-visual-styles.md).

  python3 comic_render.py <set_dir>     # reads <set_dir>/comic.json, writes final/preview/slide-NN.jpg

comic.json: {"slides": [{"image": "p1.png", "caption": "earnie's first day...", "footer": "optional"}]}
Each slide: 1080x1350 off-white page, the panel inset with a thick black border, a yellow comic caption box
(top-left) with the narration in bold caps. Images are paths relative to the set folder.
"""
import json, os, sys, textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
INK = (15, 15, 18); PAGE = (250, 247, 238); YELLOW = (255, 221, 64)
BOLD = "/usr/share/fonts/opentype/inter/Inter-Black.otf"; MED = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"


def fit(im, w, h):
    s = max(w / im.width, h / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def render(set_dir):
    spec = json.load(open(os.path.join(set_dir, "comic.json")))
    out = os.path.join(set_dir, "final", "preview"); os.makedirs(out, exist_ok=True)
    for i, s in enumerate(spec["slides"], 1):
        img = Image.new("RGB", (W, H), PAGE); d = ImageDraw.Draw(img)
        m = 34; foot = 70 if s.get("footer") else 0
        x0, y0, x1, y1 = m, m, W - m, H - m - foot
        panel = fit(Image.open(os.path.join(set_dir, s["image"])).convert("RGB"), x1 - x0, y1 - y0)
        img.paste(panel, (x0, y0)); d.rectangle([x0, y0, x1, y1], outline=INK, width=10)
        f = ImageFont.truetype(BOLD, 44); lines = textwrap.wrap(s["caption"].upper(), 26)
        lh = 54; bw = max(d.textlength(l, font=f) for l in lines) + 56; bh = lh * len(lines) + 36
        bx, by = x0 + 24, y0 + 24
        d.rectangle([bx + 8, by + 8, bx + bw + 8, by + bh + 8], fill=INK)           # drop shadow
        d.rectangle([bx, by, bx + bw, by + bh], fill=YELLOW, outline=INK, width=6)
        for k, l in enumerate(lines): d.text((bx + 28, by + 18 + k * lh), l, font=f, fill=INK)
        if s.get("footer"):
            ff = ImageFont.truetype(MED, 28); tw = d.textlength(s["footer"], font=ff)
            d.text(((W - tw) / 2, H - m - foot + 22), s["footer"], font=ff, fill=INK)
        img.save(os.path.join(out, f"slide-{i:02d}.jpg"), quality=92)
    print(f"rendered {len(spec['slides'])} slides -> {out}")


if __name__ == "__main__":
    render(sys.argv[1])
