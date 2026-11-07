#!/usr/bin/env python3
"""Render 'tweet card' images (Cal AI / drbeckycampbell ad style) from tweets.json.

  python3 tweetcard_render.py 04-sets/<set>

tweets.json: {"cards": [ {"name": "EARND", "handle": "@earndapp", "avatar": "01-app/brand/profile/pfp-lime.png",
   "avatar_crop": [x0,y0,x1,y1] (pixels, optional), "text": "...",
   "shot": "01-app/assets/demo-x.png" (real screenshot, inner phone screen is cropped) | "image": "01-app/brand/memes/x.jpg", "focus_y": 0.0-1.0 (image crop anchor),
   "shot_crop": [l,t,r,b] fractions (optional), "example": true} ]}
Output 1080x1350 (4:5) final/preview/card-NN.jpg. No verified badge (we're not verified), no platform logos.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
W, H = 1080, 1350
B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"; M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
if not os.path.exists(M): M = B
F = lambda p, s: ImageFont.truetype(p, s)

def wrap(d, text, f, maxw):
    out = []
    for para in text.split("\n"):
        line = ""
        for w in para.split():
            t = (line + " " + w).strip()
            if d.textlength(t, font=f) <= maxw: line = t
            else: out.append(line); line = w
        out.append(line)
    return out

def render(c):
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    av = Image.open(os.path.join(ROOT, c["avatar"])).convert("RGB")
    if c.get("avatar_crop"): av = av.crop(tuple(c["avatar_crop"]))
    av = av.resize((150, 150), Image.LANCZOS); m = Image.new("L", (150, 150), 0); ImageDraw.Draw(m).ellipse((0, 0, 149, 149), fill=255)
    im.paste(av, (60, 60), m)
    d.text((240, 82), c["name"], font=F(B, 48), fill=(15, 15, 15)); d.text((240, 145), c["handle"], font=F(M, 40), fill=(110, 110, 115))
    f = F(M, 46); y = 270
    for ln in wrap(d, c["text"], f, W - 120): d.text((60, y), ln, font=f, fill=(20, 20, 20)); y += 60
    top = y + 40; bot = H - 50
    d.rounded_rectangle((50, top, W - 50, bot), radius=36, fill=(28, 28, 34))
    if c.get("shot"):
        s = Image.open(os.path.join(ROOT, c["shot"])).convert("RGB"); w, h = s.size
        l, t, r, b = c.get("shot_crop", [0.175, 0.148, 0.825, 0.6]); s = s.crop((int(l * w), int(t * h), int(r * w), int(b * h)))
        bw = W - 260; s = s.resize((bw, int(s.height * bw / s.width)), Image.LANCZOS)
        s = s.crop((0, 0, bw, min(s.height, bot - top - 40)))
        mk = Image.new("L", s.size, 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0) + s.size, radius=40, fill=255)
        im.paste(s, ((W - bw) // 2, top + 40), mk)
    elif c.get("image"):
        s = Image.open(os.path.join(ROOT, c["image"])).convert("RGB"); bw, bh = W - 100, bot - top
        sc = max(bw / s.width, bh / s.height); s = s.resize((int(s.width * sc) + 1, int(s.height * sc) + 1), Image.LANCZOS)
        oy = int((s.height - bh) * c.get("focus_y", 0.5)); s = s.crop(((s.width - bw) // 2, oy, (s.width - bw) // 2 + bw, oy + bh))
        mk = Image.new("L", s.size, 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0) + s.size, radius=36, fill=255); im.paste(s, (50, top), mk)
    if c.get("example"):
        ft = F(B, 30); tw = d.textlength("example", font=ft)
        d.rounded_rectangle((W - 90 - tw - 32, top + 20, W - 90, top + 70), radius=25, fill=(198, 255, 0)); d.text((W - 90 - tw - 16, top + 27), "example", font=ft, fill="black")
    return im

def main(set_dir):
    spec = json.load(open(os.path.join(set_dir, "tweets.json"))); out = os.path.join(set_dir, "final", "preview"); os.makedirs(out, exist_ok=True)
    for i, c in enumerate(spec["cards"], 1): render(c).save(os.path.join(out, f"card-{i:02d}.jpg"), quality=92)
    print(f"rendered {len(spec['cards'])} cards -> {out}")

if __name__ == "__main__": main(sys.argv[1])
