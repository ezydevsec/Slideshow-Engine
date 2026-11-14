#!/usr/bin/env python3
"""Pixel-art what-if slideshow for @whatif.overload (style: 02-research/formats/account-visual-styles.md).
Drawn by code at 135x240 and scaled x8 to 1080x1920 (0 credits); HUD text drawn at full resolution.

  python3 pixel_render.py <set_dir>     # reads <set_dir>/pixel.json, writes final/preview/slide-NN.jpg

pixel.json slides:
  {"type": "level", "title": ["line", "line"], "hl": 1, "week": "WEEK 1", "kg": "60 KG", "bar": 0.02, "lv": "LV 1",
   "load": "plates"|"vending"|"cow"|"car", "caption": "optional line under the scene", "sweat": false}
  {"type": "stats", "title": [...], "rows": [["WEEK 1", "60 KG", ""], ...], "hl_last": true}
  {"type": "end", "title": [...], "body": ["line", ...], "footer": "disclosure line"}
Dale is our own character: red headband, blue vest. No game's art, fonts or logos.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

LW, LH, S = 135, 240, 8
W, H = LW * S, LH * S
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SKY0, SKY1, FLOOR, FLOORLINE = (30, 24, 60), (42, 34, 78), (58, 44, 70), (66, 50, 80)
WHITE, GOLD, BLUE, GREEN, RED = (245, 245, 250), (255, 200, 64), (80, 170, 255), (90, 220, 120), (230, 70, 70)
SKIN, VEST, SHORTS, BAR, POST = (214, 160, 120), (60, 110, 220), (25, 25, 32), (220, 220, 230), (150, 150, 170)


def F(s): return ImageFont.truetype(MONO, s)


def scene(load, sweat=False):
    im = Image.new("RGB", (LW, LH), SKY0); d = ImageDraw.Draw(im)
    for y in range(LH):
        k = y / LH; d.line([(0, y), (LW, y)], fill=tuple(int(SKY0[i] + (SKY1[i] - SKY0[i]) * k) for i in range(3)))
    d.rectangle([0, 182, LW, LH], fill=FLOOR)
    for x in range(0, LW, 9): d.line([(x, 182), (x, LH)], fill=FLOORLINE)
    cx, by = 67, 130                                    # Dale centre, bar height
    bend = {"plates": 0, "vending": 1, "cow": 2, "car": 3}[load]
    # Dale (front view, bar on shoulders)
    d.rectangle([cx - 6, by - 10, cx + 6, by + 1], fill=SKIN)          # head
    d.rectangle([cx - 6, by - 9, cx + 6, by - 7], fill=RED)            # headband
    d.rectangle([cx - 3, by - 5, cx - 2, by - 4], fill=(20, 20, 20)); d.rectangle([cx + 2, by - 5, cx + 3, by - 4], fill=(20, 20, 20))
    d.rectangle([cx - 10, by + 2, cx + 10, by + 22], fill=VEST)
    d.rectangle([cx - 14, by - 18, cx - 11, by + 6], fill=SKIN); d.rectangle([cx + 11, by - 18, cx + 14, by + 6], fill=SKIN)
    d.rectangle([cx - 14, by + 2, cx - 10, by + 6], fill=VEST); d.rectangle([cx + 10, by + 2, cx + 14, by + 6], fill=VEST)
    d.rectangle([cx - 9, by + 22, cx + 9, by + 30], fill=SHORTS)
    d.rectangle([cx - 8, by + 30, cx - 3, by + 50], fill=SKIN); d.rectangle([cx + 3, by + 30, cx + 8, by + 50], fill=SKIN)
    d.rectangle([cx - 9, by + 50, cx - 2, by + 53], fill=WHITE); d.rectangle([cx + 2, by + 50, cx + 9, by + 53], fill=WHITE)
    by = by - 17                                        # bar overhead from here on
    # rack posts
    for px in (cx - 42, cx + 40): d.rectangle([px, by - 6, px + 2, 185], fill=POST)
    # bar (bends with the load)
    for x in range(cx - 60, cx + 61):
        sag = int(bend * ((abs(x - cx) / 60) ** 2) * 3)
        d.rectangle([x, by - 3 + sag, x, by - 2 + sag], fill=BAR)
    if load == "plates":
        for sx in (-56, 50): d.rectangle([cx + sx, by - 11, cx + sx + 6, by + 7], fill=RED)
    elif load == "vending":
        x0 = cx - 15; d.rectangle([x0, by - 40, x0 + 30, by - 4], fill=(200, 40, 50))
        d.rectangle([x0 + 3, by - 37, x0 + 20, by - 12], fill=(30, 30, 50))
        for r in range(3):
            for c in range(3): d.rectangle([x0 + 5 + c * 5, by - 34 + r * 7, x0 + 8 + c * 5, by - 30 + r * 7], fill=[GOLD, GREEN, BLUE][(r + c) % 3])
        d.rectangle([x0 + 23, by - 32, x0 + 27, by - 24], fill=(90, 90, 110)); d.rectangle([x0 + 5, by - 10, x0 + 18, by - 7], fill=(15, 15, 20))
    elif load == "cow":
        x0 = cx - 26; y0 = by - 33
        d.rectangle([x0, y0, x0 + 40, y0 + 18], fill=WHITE)
        for (a, b, w, h) in ((4, 3, 8, 6), (18, 8, 9, 7), (30, 2, 6, 5)): d.rectangle([x0 + a, y0 + b, x0 + a + w, y0 + b + h], fill=(25, 25, 30))
        d.rectangle([x0 + 40, y0 - 4, x0 + 52, y0 + 8], fill=WHITE); d.rectangle([x0 + 48, y0 + 3, x0 + 53, y0 + 8], fill=(240, 160, 170))
        d.rectangle([x0 + 43, y0 - 1, x0 + 44, y0], fill=(20, 20, 20)); d.rectangle([x0 + 41, y0 - 7, x0 + 42, y0 - 4], fill=(230, 220, 200))
        for lx in (2, 10, 28, 36): d.rectangle([x0 + lx, y0 + 18, x0 + lx + 3, y0 + 30], fill=WHITE)
        d.rectangle([x0 - 4, y0 + 2, x0 - 1, y0 + 3], fill=WHITE)
    elif load == "car":
        x0 = cx - 34; y0 = by - 31
        d.rectangle([x0, y0 + 8, x0 + 68, y0 + 22], fill=(240, 190, 50)); d.rectangle([x0 + 14, y0, x0 + 50, y0 + 9], fill=(240, 190, 50))
        d.rectangle([x0 + 18, y0 + 2, x0 + 30, y0 + 8], fill=(150, 210, 240)); d.rectangle([x0 + 33, y0 + 2, x0 + 46, y0 + 8], fill=(150, 210, 240))
        for wx in (8, 50): d.ellipse([x0 + wx, y0 + 18, x0 + wx + 10, y0 + 28], fill=(20, 20, 25)); d.rectangle([x0 + wx + 4, y0 + 22, x0 + wx + 6, y0 + 24], fill=(150, 150, 160))
        d.rectangle([x0 + 64, y0 + 11, x0 + 67, y0 + 14], fill=WHITE)
    if sweat:
        for (sx, sy) in ((-11, -12), (10, -14), (13, -6)): d.rectangle([cx + sx, by + 17 + sy + 6, cx + sx + 1, by + 17 + sy + 8], fill=(140, 200, 255))
    return im.resize((W, H), Image.NEAREST)


def ctext(d, txt, y, f, fill):
    tw = d.textlength(txt, font=f); d.text(((W - tw) / 2, y), txt, font=f, fill=fill, stroke_width=4, stroke_fill=(10, 8, 20))


def title(d, lines, hl, y=170):
    for i, ln in enumerate(lines):
        f = F(70)
        while d.textlength(ln, font=f) > W - 100: f = F(f.size - 4)
        ctext(d, ln, y + i * 92, f, GOLD if i == hl else WHITE)
    return y + len(lines) * 92


def render(set_dir):
    spec = json.load(open(os.path.join(set_dir, "pixel.json")))
    out = os.path.join(set_dir, "final", "preview"); os.makedirs(out, exist_ok=True)
    pages = []
    for n, s in enumerate(spec["slides"], 1):
        t = s["type"]
        if t == "level":
            img = scene(s["load"], s.get("sweat", False)); d = ImageDraw.Draw(img)
            y = title(d, s["title"], s.get("hl", -1)) + 40
            d.rectangle([90, y, W - 90, y + 60], outline=WHITE, width=6)
            d.rectangle([98, y + 8, 98 + (W - 196) * max(0.01, s.get("bar", 0.1)), y + 52], fill=GREEN)
            d.text((100, y + 80), s["week"], font=F(46), fill=WHITE); kw = d.textlength(s["kg"], font=F(46))
            d.text((W - 100 - kw, y + 80), s["kg"], font=F(46), fill=GOLD)
            if s.get("caption"): ctext(d, s["caption"], 1560, F(52), WHITE)
            ctext(d, s.get("lv", ""), 1720, F(84), BLUE)
        elif t == "stats":
            img = Image.new("RGB", (W, H), SKY0); d = ImageDraw.Draw(img)
            y = title(d, s["title"], s.get("hl", -1), y=200) + 60
            d.rectangle([70, y, W - 70, y + 4 + 120 * len(s["rows"])], outline=WHITE, width=6)
            for i, (a, b, c) in enumerate(s["rows"]):
                ry = y + 30 + i * 120; last = s.get("hl_last") and i == len(s["rows"]) - 1
                d.text((110, ry), a, font=F(48), fill=GOLD if last else WHITE)
                d.text((470, ry), b, font=F(48), fill=GOLD if last else GREEN)
                if c: d.text((470, ry + 56), c, font=F(34), fill=(190, 185, 210))
            if s.get("footer"): ctext(d, s["footer"], y + 4 + 120 * len(s["rows"]) + 70, F(44), BLUE)
        elif t == "end":
            img = scene("plates"); d = ImageDraw.Draw(img)
            d.rectangle([0, 0, W, 760], fill=SKY0)
            y = title(d, s["title"], s.get("hl", -1), y=200) + 50
            for ln in s.get("body", []): ctext(d, ln, y, F(44), WHITE); y += 66
            if s.get("footer"):
                fy = 1620
                for ln in s["footer"]: ctext(d, ln, fy, F(42), (200, 195, 225)); fy += 60
        img.save(os.path.join(out, f"slide-{n:02d}.jpg"), quality=92); pages.append(img)
    sheet = Image.new("RGB", (len(pages) * 280, 490), "white")
    for i, p in enumerate(pages): sheet.paste(p.resize((270, 480)), (i * 280, 5))
    sheet.save(os.path.join(set_dir, "final", "contact-sheet.jpg"), quality=86)
    print(f"rendered {len(pages)} slides -> {out}")


if __name__ == "__main__":
    render(sys.argv[1])
