"""Assemble explainer ep 1 from frames/ + voiceover. Run from the repo root:
python3 04-sets/2026-10-28-explainer-ep1-arms-width/build_video.py"""
import math, subprocess, os
from PIL import Image, ImageDraw, ImageFont
D = "04-sets/2026-10-28-explainer-ep1-arms-width"; F = f"{D}/frames"
W, H, FPS = 1080, 1920, 30
LIME, WHITE, BLACK = (198, 255, 0), (255, 255, 255), (8, 8, 8)
ANTON = ".claude/skills/slideshow-engine/assets/fonts/Anton-Regular.ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
fA = lambda s: ImageFont.truetype(ANTON, s); fI = lambda s: ImageFont.truetype(INTER, s)
img = {k: Image.open(f"{F}/{k}.jpg").convert("RGB") for k in ["f00-character-reference", "f01", "f02", "f03", "f04"]}
shot = Image.open("01-app/assets/exercise-target.png").convert("RGB")

def cover(im):  # scale to cover 1080x1920
    s = max(W / im.width, H / im.height); return im.resize((math.ceil(im.width * s), math.ceil(im.height * s)), Image.LANCZOS)
covers = {k: cover(v) for k, v in img.items()}
def view(k, cx, cy, z):  # crop around (cx,cy) in 0-1 coords with zoom z
    c = covers[k]; w, h = W / z, H / z
    x0 = min(max(cx * c.width - w / 2, 0), c.width - w); y0 = min(max(cy * c.height - h / 2, 0), c.height - h)
    return c.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))
ease = lambda t: 0.5 - 0.5 * math.cos(math.pi * min(max(t, 0), 1))

def shot_frame(t):
    bg = Image.new("RGB", (W, H), BLACK); sh = shot.crop((0, int(0.14 * shot.height), shot.width, int(0.56 * shot.height)))
    z = 1 + 0.15 * ease(t); sw = int((W - 80) * z); sh = sh.resize((sw, int(sh.height * sw / sh.width)), Image.LANCZOS)
    bg.paste(sh, ((W - sw) // 2, (H - sh.height) // 2 - 60)); return bg

def card(lines, tag=False):
    bg = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(bg); y = 760 - len(lines) * 70
    if tag:
        f = fI(40); tw = d.textlength("example", font=f); d.rounded_rectangle(((W - tw) / 2 - 24, y - 110, (W + tw) / 2 + 24, y - 40), 16, fill=LIME)
        d.text(((W - tw) / 2, y - 100), "example", font=f, fill=BLACK)
    for txt, size, col in lines:
        f = fA(size); d.text(((W - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=col); y += int(size * 1.2)
    return bg

# (start, end, renderer(t in 0..1) -> Image, overlays [(time, text, x, y)])
beats = [
 (0.0, 3.7, lambda t: view("f01", 0.5, 0.45, 1.05 + 0.08 * ease(t))),
 (3.7, 8.7, lambda t: view("f02", 0.55, 0.42, 1.0 + 0.12 * ease(t))),
 (8.7, 15.8, lambda t: view("f03", 0.5, 0.48, 1.25)),
 (15.8, 21.9, lambda t: view("f04", 0.5, 0.42, 1.0 + 0.15 * ease(t))),
 (21.9, 29.9, lambda t: view("f01", 0.42, 0.42, 1.6 + 0.2 * ease(t))),
 (29.9, 36.9, lambda t: view("f04", 0.5, 0.62, 1.4 + 0.15 * ease(t))),
 (36.9, 45.6, lambda t: view("f04", 0.5, 0.35 + 0.15 * ease(t), 1.25)),
 (45.6, 52.2, lambda t: card([("3 × 10–12", 190, WHITE), ("CLOSE TO FAILURE", 90, LIME)], tag=True)),
 (52.2, 61.5, lambda t: view("f02", 0.62, 0.25, 1.9 + 0.2 * ease(t))),
 (61.5, 68.2, shot_frame),
 (68.2, 73.1, lambda t: view("f00-character-reference", 0.5, 0.45, 1.0 + 0.1 * ease(t))),
 (73.1, 75.3, lambda t: card([("PART 2", 120, WHITE), ("DEPTH", 200, LIME)])),
 (75.3, 80.0, lambda t: view("f00-character-reference", 0.5, 0.4, 1.12)),
]
labels = [  # big on-screen labels: (start, end, text, x, y)
 (12.0, 15.8, "HEIGHT", 700, 560), (12.7, 15.8, "WIDTH", 150, 900), (14.0, 15.8, "DEPTH", 720, 1090),
 (23.1, 29.9, "BRACHIALIS", None, 1250), (30.4, 36.9, "HAMMER CURLS", None, 1250),
 (38.9, 40.8, "SQUEEZE", None, 1250), (40.8, 45.6, "LOWER SLOWLY", None, 1250), (55.4, 61.5, "CAN'T REMEMBER?", None, 1250),
]
# captions: phrase chunks from word timings
words = []
for l in open(f"{F}/voiceover-words.tsv"):
    s, e, w = l.rstrip("\n").split("\t"); w = w.replace("Earned", "EARND").replace("ERND", "EARND"); words.append((float(s), float(e), w))
chunks, cur = [], []
for wd in words:
    cur.append(wd)
    if len(cur) == 3 or wd[2][-1] in ",.?":
        chunks.append((cur[0][0], cur[-1][1], " ".join(x[2] for x in cur).strip(",.").lower().replace("earnd", "EARND"))); cur = []
if cur: chunks.append((cur[0][0], cur[-1][1], " ".join(x[2] for x in cur).lower()))
KEY = ("height", "width", "depth", "brachialis", "hammer", "beat", "EARND", "track")

def draw_stroked(d, xy, txt, f, fill, sw=7):
    d.text(xy, txt, font=f, fill=fill, stroke_width=sw, stroke_fill=BLACK)

TITLE = "WHY YOUR ARMS LOOK SMALL FROM THE FRONT"
out = f"{D}/final/ep1-arms-width.mp4"; os.makedirs(f"{D}/final", exist_ok=True)
DUR = 79.6
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-i", f"{F}/voiceover.mp3", "-c:v", "libx264", "-crf", "21", "-preset", "slow", "-pix_fmt", "yuv420p",
                       "-c:a", "aac", "-b:a", "192k", "-af", "apad", "-t", str(DUR), "-movflags", "+faststart", out], stdin=subprocess.PIPE)
for n in range(int(DUR * FPS)):
    t = n / FPS
    b = next((x for x in beats if x[0] <= t < x[1]), beats[-1])
    fr = b[2]((t - b[0]) / (b[1] - b[0])); d = ImageDraw.Draw(fr)
    if t - b[0] < 0.12 and b[0] > 0: fr = Image.blend(Image.new("RGB", (W, H), WHITE), fr, 0.6); d = ImageDraw.Draw(fr)
    # title bar
    f = fA(54); tw = d.textlength(TITLE, font=f)
    d.rounded_rectangle(((W - tw) / 2 - 30, 150, (W + tw) / 2 + 30, 240), 18, fill=LIME); d.text(((W - tw) / 2, 158), TITLE, font=f, fill=BLACK)
    for s, e, txt, x, y in labels:
        if s <= t < e:
            f = fA(110 if x is None else 90); tx = (W - d.textlength(txt, font=f)) / 2 if x is None else x
            draw_stroked(d, (tx, y), txt, f, LIME, 9)
    if 61.5 <= t < 68.2:  # example tag on the app screen
        f = fI(40); d.rounded_rectangle((W - 260, 300, W - 60, 370), 16, fill=LIME); d.text((W - 240, 310), "example", font=f, fill=BLACK)
    if t >= 75.3:
        f = fA(96)
        for i, ln in enumerate(["EARND LAUNCHES SOON.", "FOLLOW FOR THE LAUNCH."]):
            draw_stroked(d, ((W - d.textlength(ln, font=f)) / 2, 1250 + i * 120), ln, f, LIME, 9)
    else:
        c = next((c for c in chunks if c[0] <= t < c[1] + 0.25), None)
        if c:
            f = fI(64); txt = c[2]; col = LIME if any(k in txt for k in KEY) else WHITE
            draw_stroked(d, ((W - d.textlength(txt, font=f)) / 2, 1560), txt, f, col, 8)
    a = min(1, t / 0.3, (DUR - t) / 0.4)
    if a < 1: fr = Image.blend(Image.new("RGB", (W, H)), fr, max(a, 0))
    ff.stdin.write(fr.tobytes())
ff.stdin.close(); ff.wait(); print("wrote", out)
