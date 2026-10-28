import sys, math, subprocess, random
from PIL import Image, ImageDraw, ImageFont
S, OUT, SHOT = sys.argv[1], sys.argv[2], sys.argv[3]
W, H, FPS = 1080, 1920, 30
LIME, WHITE = (198, 255, 0), (255, 255, 255)
coach = Image.open(f"{S}/test/coach1.png").convert("RGB")
font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 66)
cta_font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 74)
tag_font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 44)

# screenshot on a black canvas, sized to 90% height
shot = Image.open(SHOT).convert("RGB")
sh = int(H * 0.9); sw = int(shot.width * sh / shot.height)
shot_canvas = Image.new("RGB", (W, H), (11, 11, 11))
sx0, sy0 = (W - sw) // 2, (H - sh) // 2
shot_canvas.paste(shot.resize((sw, sh), Image.LANCZOS), (sx0, sy0))
# target: "Previous / Beat" box, fractions of the screenshot
bx = sx0 + 0.5 * sw; by = sy0 + (330 / 1216) * sh

def box(cx, cy, w, img):
    h = w * 16 / 9
    x0 = min(max(cx - w / 2, 0), img.width - w); y0 = min(max(cy - h / 2, 0), img.height - h)
    return (x0, y0, x0 + w, y0 + h)

def lerp(a, b, t): return tuple(x + (y - x) * t for x, y in zip(a, b))
def ease(t): return 0.5 - 0.5 * math.cos(math.pi * min(max(t, 0), 1))

CW, CH = coach.size
beats = [  # start, end, image, from-box, to-box
    (0.0, 4.6, coach, box(576, 1024, 1152, coach), box(576, 900, 860, coach)),
    (4.6, 9.6, coach, box(576, 470, 560, coach), box(576, 400, 360, coach)),
    (9.6, 13.4, None, None, None),
    (13.4, 17.3, coach, box(560, 1120, 620, coach), box(560, 1110, 520, coach)),
    (17.3, 22.8, coach, box(576, 760, 980, coach), box(576, 700, 780, coach)),
    (22.8, 30.2, shot_canvas, (0, 0, W, H), box(bx, by + 250, 840, shot_canvas)),
    (30.2, 36.2, coach, box(576, 760, 800, coach), box(576, 1024, 1152, coach)),
]
DUR = 36.2

words = [l.split("\t") for l in open(f"{S}/test/words.tsv").read().strip().splitlines()]
fixed = []
i = 0
while i < len(words):
    s, e, w = float(words[i][0]), float(words[i][1]), words[i][2]
    if w == "ER":  # "EARND" split by the recogniser
        e = float(words[i + 1][1]); w = "earnd"; i += 1
    if w.lower().strip(",.") != "uh":
        fixed.append((s, e, w.lower().strip(",.")))
    i += 1
fixed = [f for f in fixed if f[0] < 30.2]  # CTA card takes over
KEY = {"lift", "beat", "down", "earnd", "know", "guess"}
fixed = [(s, e, w + ("?" if w in ("lift",) else "")) for s, e, w in fixed]
KEY |= {"lift?"}

def caption(t):
    for k, (s, e, w) in enumerate(fixed):
        nxt = fixed[k + 1][0] if k + 1 < len(fixed) else e + 0.6
        if s <= t < min(nxt, e + 0.6):
            return w
    return None

def draw_center(d, text, y, f, fill):
    tw = d.textlength(text, font=f)
    d.text(((W - tw) / 2, y), text, font=f, fill=fill, stroke_width=6, stroke_fill=(0, 0, 0))

ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-i", f"{S}/test/vo.wav", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
                       "-af", "apad", "-t", str(DUR), OUT], stdin=subprocess.PIPE)
random.seed(7)
for n in range(int(DUR * FPS)):
    t = n / FPS
    b = next(x for x in beats if x[0] <= t < x[1]) if t < beats[-1][1] else beats[-1]
    s, e, img, b0, b1 = b
    if img is None:
        frame = Image.new("RGB", (W, H), (0, 0, 0))
    else:
        bb = lerp(b0, b1, ease((t - s) / (e - s)))
        if s == 13.4 and t - s < 0.6:  # slam shake
            amp = 40 * (1 - (t - s) / 0.6)
            dx, dy = random.uniform(-amp, amp), random.uniform(-amp, amp)
            bb = (bb[0] + dx, bb[1] + dy, bb[2] + dx, bb[3] + dy)
        frame = img.resize((W, H), Image.BICUBIC, box=bb)
    if s == 13.4 and t - s < 0.1:
        frame = Image.blend(frame, Image.new("RGB", (W, H), WHITE), 0.85)
    d = ImageDraw.Draw(frame)
    if s == 22.8:
        tx, ty = 60, 140
        d.rounded_rectangle((tx, ty, tx + 230, ty + 80), 16, fill=LIME)
        d.text((tx + 30, ty + 12), "example", font=tag_font, fill=(0, 0, 0))
    if t >= 30.4:
        draw_center(d, "EARND launches soon.", 1390, cta_font, LIME)
        draw_center(d, "Follow for the launch.", 1480, cta_font, LIME)
    else:
        w = caption(t)
        if w:
            y = 1300 if img is not None else 900
            if s == 22.8:
                y = 1660; tw = d.textlength(w, font=font)
                d.rounded_rectangle(((W - tw) / 2 - 30, y - 10, (W + tw) / 2 + 30, y + 90), 20, fill=(0, 0, 0))
            draw_center(d, w, y, font, LIME if w in KEY else WHITE)
    # fade in/out
    a = min(1, t / 0.4, (DUR - t) / 0.5)
    if a < 1: frame = Image.blend(Image.new("RGB", (W, H)), frame, max(a, 0))
    ff.stdin.write(frame.tobytes())
ff.stdin.close(); ff.wait()
