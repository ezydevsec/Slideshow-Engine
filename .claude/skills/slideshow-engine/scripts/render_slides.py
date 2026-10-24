#!/usr/bin/env python3
"""Render a slideshow set into 1080x1920 JPEGs.

Usage:
  python3 render_slides.py 04-sets/<set-folder> [--project .] [--font path.ttf] [--bg "#F4EFE6"]

Reads <set>/slides.json and writes:
  <set>/final/clean/slide-NN.jpg    no text (for Humanpost text layers)
  <set>/final/preview/slide-NN.jpg  text drawn in the safe zone (for review)
  <set>/final/contact-sheet.jpg     every preview side by side

Needs Pillow:  pip install pillow
"""
import argparse
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
SAFE_TOP, SAFE_BOTTOM = int(H * 0.10), int(H * 0.80)
POSITIONS = {"top": 0.19, "upper": 0.30, "middle": 0.50, "lower": 0.70}
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def load_font(path, size):
    for p in ([path] if path else []) + FONT_CANDIDATES:
        if p and os.path.exists(p):
            return ImageFont.truetype(p, size)
    print("warning: no TrueType font found, using Pillow default", file=sys.stderr)
    return ImageFont.load_default(size)


def is_screenshot(path, slide):
    direction = (slide.get("image_direction") or "").upper()
    return "SCREENSHOT" in direction or "01-app/assets" in path.replace("\\", "/")


def cover(img):
    scale = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left, top = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((left, top, left + W, top + H))


def fit_on_blur(img, area=None):
    """Fit a screenshot uncropped on a blurred copy of itself.

    area: optional [top, bottom] as fractions of the canvas height. The
    screenshot is fitted inside that band, leaving room for text above it.
    """
    bg = cover(img).filter(ImageFilter.GaussianBlur(40))
    top, bottom = (int(H * area[0]), int(H * area[1])) if area else (None, None)
    max_h = bottom - top if area else SAFE_BOTTOM * 0.95
    scale = min(W * 0.9 / img.width, max_h / img.height)
    fg = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    y = top if area else (H - fg.height) // 2
    bg.paste(fg, ((W - fg.width) // 2, y))
    return bg


def base_image(set_dir, project, slide, bg):
    rel = slide.get("image") or ""
    for root in (set_dir, project):
        path = os.path.join(root, rel)
        if rel and os.path.exists(path):
            img = Image.open(path).convert("RGB")
            crop = slide.get("shot_crop")
            if crop:  # [left, top, right, bottom] as fractions of the source; crop only, no edits
                img = img.crop((round(crop[0] * img.width), round(crop[1] * img.height),
                                round(crop[2] * img.width), round(crop[3] * img.height)))
            return fit_on_blur(img, slide.get("shot_area")) if is_screenshot(rel, slide) else cover(img)
    if rel:
        print(f"warning: slide {slide.get('n')}: image not found ({rel}), using solid background", file=sys.stderr)
    return Image.new("RGB", (W, H), slide.get("bg") or bg)


def wrap(draw, text, font, max_width):
    lines = []
    for para in text.split("\n"):
        line = ""
        for word in para.split():
            trial = f"{line} {word}".strip()
            if draw.textlength(trial, font=font) <= max_width:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_text(img, slide, font_path):
    text = (slide.get("text") or "").strip()
    if not text:
        return img
    img = img.copy()
    draw = ImageDraw.Draw(img)
    mode = slide.get("text_mode", "stroke")
    size = 72 if slide.get("role") == "hook" else 58
    font = load_font(font_path, size)
    lines = wrap(draw, text, font, W * 0.82)
    line_h = int(size * 1.25)
    block_h = line_h * len(lines)
    center_y = int(H * POSITIONS.get(slide.get("position", "upper"), 0.30))
    top = max(SAFE_TOP, min(center_y - block_h // 2, SAFE_BOTTOM - block_h))
    region = img.crop((0, top, W, top + block_h)).convert("L").resize((1, 1))
    plain_fill = slide.get("text_color") or ("black" if region.getpixel((0, 0)) > 150 else "white")
    box_fill = slide.get("box_color") or "white"
    for i, line in enumerate(lines):
        tw = draw.textlength(line, font=font)
        x, y = (W - tw) / 2, top + i * line_h
        if mode == "background":
            pad = 14
            draw.rounded_rectangle((x - pad, y - pad // 2, x + tw + pad, y + line_h - pad // 2), 12, fill=box_fill)
            draw.text((x, y), line, font=font, fill=slide.get("text_color") or "black")
        elif mode == "plain":
            draw.text((x, y), line, font=font, fill=plain_fill)
        else:
            draw.text((x, y), line, font=font, fill=slide.get("text_color") or "white", stroke_width=max(3, size // 14), stroke_fill="black")
    return img


def contact_sheet(paths, out):
    th = round(270 * H / W)
    thumbs = [Image.open(p).resize((270, th)) for p in paths]
    per_row = 7
    rows = (len(thumbs) + per_row - 1) // per_row
    sheet = Image.new("RGB", (per_row * 280 - 10 if rows > 1 else len(thumbs) * 280 - 10, rows * (th + 10) - 10), "white")
    for i, t in enumerate(thumbs):
        sheet.paste(t, ((i % per_row) * 280, (i // per_row) * (th + 10)))
    sheet.save(out, quality=85)


def set_canvas(canvas):
    global W, H, SAFE_TOP, SAFE_BOTTOM
    W, H = (int(x) for x in canvas.lower().split("x"))
    SAFE_TOP, SAFE_BOTTOM = int(H * 0.10), int(H * 0.80)


def check_account_ready(project, spec):
    """Block rendering when the set's own account isn't ready. Other accounts don't matter."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import account_status
    cfg = account_status.load(project)
    handle = spec.get("account")
    if cfg is None or not handle:
        print("warning: no account set or no 06-queue/accounts.json; skipping account readiness check", file=sys.stderr)
        return
    blockers, warnings, _ = account_status.check(cfg, handle)
    for w in warnings:
        print(f"warning: {handle}: {w}", file=sys.stderr)
    if blockers:
        sys.exit(f"refusing to render: {handle} is not ready: " + "; ".join(blockers))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("set_dir")
    ap.add_argument("--project", default=".", help="project root, for 01-app/assets paths")
    ap.add_argument("--font", default=None)
    ap.add_argument("--bg", default="#F4EFE6")
    a = ap.parse_args()

    spec_path = os.path.join(a.set_dir, "slides.json")
    with open(spec_path) as f:
        spec = json.load(f)
    set_canvas(spec.get("canvas", "1080x1920"))
    check_account_ready(a.project, spec)
    slides = sorted(spec["slides"], key=lambda s: s["n"])
    held = [s["n"] for s in slides if s.get("placeholder")]
    if held:
        sys.exit(f"refusing to render: slides {held} are screenshot placeholders. Add the real asset and remove \"placeholder\" first.")
    if not 2 <= len(slides) <= 20:
        print(f"warning: {len(slides)} slides (Humanpost accepts 2 to 20)", file=sys.stderr)

    clean_dir = os.path.join(a.set_dir, "final", "clean")
    prev_dir = os.path.join(a.set_dir, "final", "preview")
    os.makedirs(clean_dir, exist_ok=True)
    os.makedirs(prev_dir, exist_ok=True)

    previews = []
    for s in slides:
        name = f"slide-{s['n']:02d}.jpg"
        base = base_image(a.set_dir, a.project, s, a.bg)
        base.save(os.path.join(clean_dir, name), quality=92)
        p = os.path.join(prev_dir, name)
        draw_text(base, s, a.font).save(p, quality=90)
        previews.append(p)
        words = len((s.get("text") or "").split())
        if words > 25:
            print(f"warning: slide {s['n']} has {words} words (rule is under 25)", file=sys.stderr)

    contact_sheet(previews, os.path.join(a.set_dir, "final", "contact-sheet.jpg"))
    print(f"rendered {len(slides)} slides -> {os.path.join(a.set_dir, 'final')}")


if __name__ == "__main__":
    main()
