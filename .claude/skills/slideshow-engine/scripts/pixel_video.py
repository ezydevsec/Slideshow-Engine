#!/usr/bin/env python3
"""@whatif.overload animated what-if (pixel art, no voice). Reuses pixel_render.scene().

  python3 pixel_video.py <set_dir>     # reads <set_dir>/pixelvid.json, writes <set_dir>/<out>

pixelvid.json: {"out": "...mp4", "title": ["WHAT IF DALE ADDED", "+2.5 KG EVERY WEEK"], "start": 60, "per_week": 2.5,
 "stages": [{"until_week": 52, "load": "plates", "caption": ""}, {"until_week": 104, "load": "vending", "caption": "about a vending machine"}, ...],
 "end_title": [...], "end_body": [...], "disclose": [...]}
Weeks speed up as the counter climbs (the joke accelerates). No "example" tags on joke escalations (founder 2026-11-04).
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pixel_render as pr

W, H, FPS = pr.W, pr.H, 30


def render(set_dir):
    sp = json.load(open(os.path.join(set_dir, "pixelvid.json")))
    last = sp["stages"][-1]["until_week"]
    RUN = 11.0                                     # seconds for the counter; quadratic so it accelerates
    week_at = lambda t: max(1, int(1 + (last - 1) * (t / RUN) ** 2.2))
    END = RUN + 0.8; DUR = END + 5.0
    scenes = {}
    out = os.path.join(set_dir, sp["out"]); os.makedirs(os.path.join(set_dir, "preview"), exist_ok=True)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], stdin=subprocess.PIPE)
    for fi in range(int(DUR * FPS)):
        t = fi / FPS
        if t < END:
            wk = week_at(min(t, RUN)); st = next(s for s in sp["stages"] if wk <= s["until_week"])
            sweat = st["load"] in ("cow", "car")
            key = (st["load"], sweat)
            if key not in scenes: scenes[key] = pr.scene(st["load"], sweat)
            img = scenes[key].copy(); d = ImageDraw.Draw(img)
            if (fi // 4) % 2 and st["load"] == "car": img = img.transform(img.size, Image.AFFINE, (1, 0, 4, 0, 1, 0))   # strain shake
            d = ImageDraw.Draw(img)
            y = pr.title(d, sp["title"], 1, y=170) + 40
            frac = wk / last
            d.rectangle([90, y, W - 90, y + 60], outline=pr.WHITE, width=6)
            d.rectangle([98, y + 8, 98 + (W - 196) * frac, y + 52], fill=pr.GREEN)
            d.text((100, y + 80), f"WEEK {wk}", font=pr.F(46), fill=pr.WHITE)
            kg = f"{sp['start'] + sp['per_week'] * (wk - 1):,.1f}".rstrip("0").rstrip(".") + " KG"
            d.text((W - 100 - d.textlength(kg, font=pr.F(46)), y + 80), kg, font=pr.F(46), fill=pr.GOLD)
            if st.get("caption"): pr.ctext(d, st["caption"], 1560, pr.F(52), pr.WHITE)
            pr.ctext(d, f"LV {wk}", 1720, pr.F(84), pr.BLUE)
        else:
            img = Image.new("RGB", (W, H), pr.SKY0); d = ImageDraw.Draw(img)
            a = min(1.0, (t - END) / 0.3)
            y = pr.title(d, sp["end_title"], 0, y=520) + 60
            if t > END + 1.2:
                for ln in sp["end_body"]: pr.ctext(d, ln, y, pr.F(46), pr.WHITE); y += 70
            if t > END + 2.6:
                fy = 1500
                for ln in sp["disclose"]: pr.ctext(d, ln, fy, pr.F(40), (200, 195, 225)); fy += 60
        p.stdin.write(img.convert("RGB").tobytes())
        if fi in [int(s * FPS) for s in (1, 6, 9.5, 10.8, END + 3.5)]:
            img.resize((540, 960)).save(os.path.join(set_dir, "preview", f"f{fi:04d}.jpg"), quality=88)
    p.stdin.close(); p.wait(); print("DONE", out, round(DUR, 1), "s")


if __name__ == "__main__":
    render(sys.argv[1])
