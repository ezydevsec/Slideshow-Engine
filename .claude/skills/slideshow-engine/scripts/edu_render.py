#!/usr/bin/env python3
"""Render an educational template slideshow (bluebro/Arrow style) from edu.json.

  python3 edu_render.py 04-sets/<set> [--project .]

edu.json: {"theme": "light"|"dark", "slides": [ {"type": ...}, ... ]}
Slide types:
  cover   {"lines": [["RANKING EVERY", false], ["GYM SPLIT", true]], "mascot": true}
  rank    {"rank": 1, "title": "...", "stars": 4.5, "body": "...", "days": [["MON","UPPER"], ...]}
  steps   {"kicker": "STEP 1", "title": "...", "body": "...", "example": "100 kg × 5 → 6 → 7"}
  app     {"title": "...", "body": "...", "shot": "01-app/assets/x.png", "crop": [l,t,r,b]}
  cta     {"title": "...", "body": "...", "mascot": true}
Outputs final/preview/slide-NN.jpg (1080x1350) and final/contact-sheet.jpg.
"""
import json, sys, os, argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ANTON = os.path.join(HERE, "..", "assets", "fonts", "Anton-Regular.ttf")
INTER_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
INTER_M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
W, H, M = 1080, 1350, 90
LIME = (198, 255, 0)
THEMES = {
    "light": dict(bg=(242, 240, 234), ink=(26, 26, 26), soft=(90, 90, 90), card=(255, 255, 255), head=(26, 26, 26)),
    "dark": dict(bg=(11, 11, 11), ink=(245, 245, 245), soft=(170, 170, 170), card=(28, 28, 28), head=(40, 40, 40)),
}

def font(p, s): return ImageFont.truetype(p, s)

def wrap(d, text, f, width):
    out = []
    for para in text.split("\n"):
        line = ""
        for w in para.split():
            t = (line + " " + w).strip()
            if d.textlength(t, font=f) <= width: line = t
            else: out.append(line); line = w
        out.append(line)
    return out

def para(d, text, f, x, y, width, fill, gap=1.3):
    for ln in wrap(d, text, f, width):
        d.text((x, y), ln, font=f, fill=fill); y += int(f.size * gap)
    return y

def accent_text(d, xy, text, f, th, accent):
    """Accent words: lime text on dark, black text on a lime box on light."""
    x, y = xy
    if not accent: d.text((x, y), text, font=f, fill=th["ink"]); return
    if th is THEMES["dark"]: d.text((x, y), text, font=f, fill=LIME); return
    b = d.textbbox((x, y), text, font=f)
    d.rectangle((b[0] - 14, b[1] - 10, b[2] + 14, b[3] + 10), fill=LIME)
    d.text((x, y), text, font=f, fill=th["ink"])

def star(d, cx, cy, r, fill, outline):
    import math
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(a), cy - rr * math.sin(a)))
    d.polygon(pts, fill=fill, outline=outline)
    return pts

def stars(img, x, y, val, th):
    d = ImageDraw.Draw(img); r = 34
    empty = (205, 205, 205) if th is THEMES["light"] else (70, 70, 70)
    for i in range(5):
        cx = x + r + i * (2 * r + 18)
        star(d, cx, y + r, r, empty, None)
        frac = max(0, min(1, val - i))
        if frac > 0:
            lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            star(ld, cx, y + r, r, LIME + (255,), None)
            mask = Image.new("L", img.size, 0); ImageDraw.Draw(mask).rectangle((cx - r, y, cx - r + 2 * r * frac, y + 2 * r), fill=255)
            img.paste(lay, (0, 0), Image.composite(lay, Image.new("RGBA", img.size), mask).split()[3])
            if th is THEMES["light"]: star(d, cx, y + r, r, None, (26, 26, 26))

def brand(d, th, mark="EARND"):
    if mark: d.text((M, 54), mark, font=font(ANTON, 40) if mark == "EARND" else font(INTER_B, 34), fill=th["ink"])

def mascot(img, box, path):
    m = Image.open(path).convert("RGBA"); x0, y0, x1, y1 = box
    s = min((x1 - x0) / m.width, (y1 - y0) / m.height); m = m.resize((int(m.width * s), int(m.height * s)), Image.LANCZOS)
    px, py = x0 + (x1 - x0 - m.width) // 2, y1 - m.height
    if sum(img.getpixel((5, 5))) < 100:  # dark theme: soft spotlight so the graphite mascot reads
        glow = Image.new("L", img.size, 0); gd = ImageDraw.Draw(glow)
        gd.ellipse((px - m.width * 0.15, py + m.height * 0.05, px + m.width * 1.15, py + m.height * 1.05), fill=150)
        glow = glow.filter(ImageFilter.GaussianBlur(70)); img.paste(Image.new("RGB", img.size, (95, 102, 112)), (0, 0), glow)
    img.paste(m, (px, py), m)

def photo(img, box, project, spec):
    """Real photo panel: crop + resize only (founder-photo rule), rounded corners. spec: {"file", "focus": [fx, fy], "crop": [l,t,r,b]}."""
    x0, y0, x1, y1 = [int(v) for v in box]; bw, bh = x1 - x0, y1 - y0
    if bw < 200 or bh < 200: return
    ph = Image.open(os.path.join(project, "01-app/founder-photos", spec["file"])).convert("RGB")
    c = spec.get("crop", [0, 0, 1, 1]); ph = ph.crop((int(c[0] * ph.width), int(c[1] * ph.height), int(c[2] * ph.width), int(c[3] * ph.height)))
    s = max(bw / ph.width, bh / ph.height); ph = ph.resize((int(ph.width * s) + 1, int(ph.height * s) + 1), Image.LANCZOS)
    fx, fy = spec.get("focus", [0.5, 0.4]); cx = min(max(fx * ph.width - bw / 2, 0), ph.width - bw); cy = min(max(fy * ph.height - bh / 2, 0), ph.height - bh)
    ph = ph.crop((int(cx), int(cy), int(cx) + bw, int(cy) + bh))
    mask = Image.new("L", (bw, bh), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, bw, bh), 36, fill=255); img.paste(ph, (x0, y0), mask)

def example_tag(d, x, y, th):
    f = font(INTER_B, 30); t = "example"
    w = d.textlength(t, font=f)
    d.rounded_rectangle((x, y, x + w + 36, y + 52), 12, fill=LIME); d.text((x + 18, y + 8), t, font=f, fill=(11, 11, 11))
    return y + 52

def render(setdir, project):
    spec = json.load(open(os.path.join(setdir, "edu.json"))); th = THEMES[spec["theme"]]
    default_mas = mas = os.path.join(project, spec.get("mascot", "01-app/brand/poses/cover-arms-open-cutout.png"))
    out = os.path.join(setdir, "final", "preview"); os.makedirs(out, exist_ok=True)
    for f_ in os.listdir(out): os.remove(os.path.join(out, f_))
    pages = []
    for n, s in enumerate(spec["slides"], 1):
        mas = os.path.join(project, f"01-app/brand/poses/{s['pose']}-cutout.png") if s.get("pose") else default_mas
        img = Image.new("RGB", (W, H), th["bg"]); d = ImageDraw.Draw(img); brand(d, th, spec.get("mark")); t = s["type"]
        if t == "cover":
            f = font(ANTON, 128); y = 170
            for text, acc in s["lines"]:
                tw = d.textlength(text, font=f); accent_text(d, ((W - tw) / 2, y), text, f, th, acc); y += 150
            if s.get("photo"): photo(img, (M, y + 20, W - M, H - 60), project, s["photo"])
            elif s.get("mascot"): mascot(img, (M, y + 10, W - M, H), mas)
        elif t in ("rank", "grid"):
            f = font(ANTON, 96); x = M
            if s.get("rank"):
                d.text((M, 150), f"#{s['rank']}", font=f, fill=th["ink"] if th is THEMES["light"] else LIME); x = M + d.textlength(f"#{s['rank']}", font=f) + 40
            d.text((x, 150), s["title"], font=f, fill=th["ink"])
            if th is THEMES["light"]: d.rectangle((M, 285, M + 130, 293), fill=LIME)
            by = 330
            if s.get("stars") is not None: stars(img, M, 330, s["stars"], th); by = 440
            para(d, s["body"], font(INTER_M, 44), M, by, W - 2 * M, th["soft"])
            days = s["days"]; n_ = len(days); gx, gy, gw, gh = 40, 760, W - 80, 440; cw = gw / n_
            d.rectangle((gx, gy, gx + gw, gy + 70), fill=th["head"] if th is THEMES["light"] else (60, 60, 60))
            for i, (dn, wk) in enumerate(days):
                x = gx + i * cw; fd = font(ANTON, 40 if n_ <= 5 else 34)
                d.text((x + (cw - d.textlength(dn, font=fd)) / 2, gy + 10), dn, font=fd, fill=(245, 245, 245))
                rest = wk.upper() == "REST"
                d.rectangle((x, gy + 70, x + cw, gy + gh), fill=th["card"] if not rest else th["bg"], outline=th["ink"], width=3)
                fw = font(ANTON, 44 if n_ <= 5 else 34)
                lines = wrap(d, wk.upper(), fw, cw - 16); ty = gy + 70 + (gh - 70 - len(lines) * fw.size * 1.15) / 2
                for ln in lines:
                    col = th["soft"] if rest else th["ink"]
                    if not rest and th is THEMES["dark"]: col = LIME
                    d.text((x + (cw - d.textlength(ln, font=fw)) / 2, ty), ln, font=fw, fill=col); ty += fw.size * 1.15
        elif t == "list":
            y = 150
            if s.get("kicker"): accent_text(d, (M, y), s["kicker"], font(ANTON, 60), th, True); y += 105
            y = para(d, s["title"], font(ANTON, 96), M, y, W - 2 * M, th["ink"], 1.1) + 10
            if s.get("note"):
                fn = font(INTER_B, 44); d.text((M, y), s["note"], font=fn, fill=th["soft"])
                if s.get("example"): example_tag(d, M + d.textlength(s["note"], font=fn) + 24, y - 4, th)
                y += 90
            fi = font(INTER_B, 50); gap = min(130, (H - 80 - y) // max(1, len(s["items"])))
            for i, it in enumerate(s["items"], 1):
                cy = y + (i - 1) * gap
                d.ellipse((M, cy, M + 72, cy + 72), fill=LIME); n_ = str(i); fn2 = font(ANTON, 46)
                d.text((M + 36 - d.textlength(n_, font=fn2) / 2, cy + 6), n_, font=fn2, fill=(11, 11, 11))
                d.text((M + 100, cy + 8), it, font=fi, fill=th["ink"])
        elif t == "exercise":
            y = 150
            accent_text(d, (M, y), s["kicker"], font(ANTON, 56), th, True); y += 100
            y = para(d, s["title"], font(ANTON, 100), M, y, W - 2 * M, th["ink"], 1.08) + 26
            fm = font(INTER_B, 40); d.text((M, y), s["muscle"], font=fm, fill=th["soft"]); y += 64
            if s.get("example"):
                ex = example_tag(d, M, y, th); d.text((M + 200, y), s["example"], font=font(INTER_B, 44), fill=th["ink"]); y = ex + 20
            if s.get("sets"): d.text((M, y), s["sets"], font=font(INTER_B, 44), fill=th["ink"]); y += 70
            if s.get("cue"): y = para(d, s["cue"], font(INTER_M, 40), M, y, W - 2 * M, th["soft"]) + 10
            mascot(img, (M, y + 10, W - M, H - 30), os.path.join(project, f"01-app/brand/poses/{s['pose']}-cutout.png"))
        elif t == "cards":
            y = 140; y = para(d, s["title"], font(ANTON, 90), M, y, W - 2 * M, th["ink"], 1.08) + 10
            if s.get("note"):
                fn = font(INTER_B, 38); d.text((M, y), s["note"], font=fn, fill=th["soft"])
                if s.get("example"): example_tag(d, M + d.textlength(s["note"], font=fn) + 20, y - 6, th)
                y += 70
            items = s["items"]; cols = 3; rows_ = (len(items) + cols - 1) // cols; gap = 20
            cw = (W - 2 * 40 - (cols - 1) * gap) / cols; ch = (H - y - 40 - (rows_ - 1) * gap) / rows_
            for i, (name, pose) in enumerate(items):
                cx = 40 + (i % cols) * (cw + gap); cy = y + (i // cols) * (ch + gap)
                d.rounded_rectangle((cx, cy, cx + cw, cy + ch), 24, fill=th["card"] if th is THEMES["light"] else (24, 24, 24))
                fl = font(ANTON, 34); d.ellipse((cx + 14, cy + 14, cx + 58, cy + 58), fill=LIME)
                d.text((cx + 36 - d.textlength(str(i + 1), font=fl) / 2, cy + 14), str(i + 1), font=fl, fill=(11, 11, 11))
                lines = wrap(d, name, font(INTER_B, 30), cw - 80); ly = cy + 18
                for ln in lines[:2]: d.text((cx + 70, ly), ln, font=font(INTER_B, 30), fill=th["ink"]); ly += 36
                mascot(img, (int(cx + 10), int(cy + 100), int(cx + cw - 10), int(cy + ch - 12)), os.path.join(project, f"01-app/brand/poses/{pose}-cutout.png"))
                d = ImageDraw.Draw(img)
        elif t == "tier":
            y = 150; y = para(d, s["title"], font(ANTON, 96), M, y, W - 2 * M, th["ink"], 1.1) + 30
            rows = s["rows"]; rh = min(190, (H - 70 - y) // len(rows)); shades = [LIME, (222, 255, 120), (235, 235, 235), (200, 200, 200), (170, 170, 170)]
            for i, (lab, items) in enumerate(rows):
                ry = y + i * rh
                d.rectangle((M - 30, ry, M + 110, ry + rh - 12), fill=shades[min(i, 4)]); fl = font(ANTON, 90)
                d.text((M + 40 - d.textlength(lab, font=fl) / 2, ry + (rh - 12 - 110) / 2), lab, font=fl, fill=(11, 11, 11))
                d.rectangle((M + 110, ry, W - M + 30, ry + rh - 12), fill=th["card"])
                lines = wrap(d, " · ".join(items), font(INTER_B, 40), W - 2 * M - 120)
                ty = ry + (rh - 12 - len(lines) * 50) / 2
                for ln in lines: d.text((M + 140, ty), ln, font=font(INTER_B, 40), fill=th["ink"]); ty += 50
        elif t == "steps":
            y = 170
            if s.get("kicker"):
                fk = font(ANTON, 60); accent_text(d, (M, y), s["kicker"], fk, th, True); y += 110
            y = para(d, s["title"], font(ANTON, 104), M, y, W - 2 * M, th["ink"], 1.12) + 30
            if s.get("body"): y = para(d, s["body"], font(INTER_M, 44), M, y, W - 2 * M, th["soft"]) + 40
            if s.get("sets"): y = para(d, s["sets"], font(INTER_B, 56), M, y, W - 2 * M, th["ink"], 1.35) + 10
            if s.get("example"):
                y = example_tag(d, M, y, th) + 24
                y = para(d, s["example"], font(INTER_B, 56), M, y, W - 2 * M, th["ink"], 1.35)
            if s.get("photo"): photo(img, (M, y + 20, W - M, H - 60), project, s["photo"])
            elif s.get("mascot"): mascot(img, (W // 2 + 40, max(y + 20, H - 620), W - 20, H), mas)
        elif t == "app":
            y = para(d, s["title"], font(ANTON, 80), M, 150, W - 2 * M, th["ink"], 1.12) + 24
            if s.get("body"): y = para(d, s["body"], font(INTER_M, 40), M, y, W - 2 * M, th["soft"]) + 90
            sh = Image.open(os.path.join(project, s["shot"])).convert("RGB"); c = s.get("crop", [0, 0, 1, 1])
            sh = sh.crop((int(c[0] * sh.width), int(c[1] * sh.height), int(c[2] * sh.width), int(c[3] * sh.height)))
            bw, bh = W - 2 * 60, H - y - 50; sc = min(bw / sh.width, bh / sh.height); sh = sh.resize((int(sh.width * sc), int(sh.height * sc)), Image.LANCZOS)
            px, py = (W - sh.width) // 2, y + (bh - sh.height) // 2
            mask = Image.new("L", sh.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, *sh.size), 36, fill=255)
            img.paste(sh, (px, py), mask)
            if s.get("example"): example_tag(d, px + sh.width - 190, py - 66, th)
        elif t == "cta":
            y = para(d, s["title"], font(ANTON, 100), M, 190, W - 2 * M, th["ink"], 1.12) + 20
            if s.get("body"):
                fb = font(INTER_B, 48)
                for ln in wrap(d, s["body"], fb, W - 2 * M):
                    accent_text(d, (M, y), ln, fb, th, True); y += 80
            if s.get("photo"): photo(img, (M, y + 30, W - M, H - 60), project, s["photo"])
            elif s.get("mascot"): mascot(img, (M, y + 30, W - M, H), mas)
        p = os.path.join(out, f"slide-{n:02d}.jpg"); img.save(p, quality=93); pages.append(img)
    th_w = 360; sheet = Image.new("RGB", (th_w * len(pages) + 10 * (len(pages) - 1), int(th_w * H / W)), (255, 255, 255))
    for i, pg in enumerate(pages): sheet.paste(pg.resize((th_w, int(th_w * H / W))), (i * (th_w + 10), 0))
    sheet.save(os.path.join(setdir, "final", "contact-sheet.jpg"), quality=88)
    print(f"rendered {len(pages)} slides -> {setdir}/final")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("set"); ap.add_argument("--project", default=".")
    a = ap.parse_args(); render(a.set, a.project)
