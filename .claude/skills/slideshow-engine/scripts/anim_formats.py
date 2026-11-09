#!/usr/bin/env python3
"""Code-drawn animated video formats (0 generation credits). 1080x1920, 30 fps.

  python3 anim_formats.py hang    <set_dir>   # "who lets go last?" contest (12 s, thud sfx)
  python3 anim_formats.py avb     <set_dir>   # A vs B week-counter comparison (15 s)
  python3 anim_formats.py essay   <set_dir>   # paradox essay, glowing pictograms, needs <set_dir>/voice.mp3
  python3 anim_formats.py parable <set_dir>   # "imagine a man" ladder parable, needs <set_dir>/voice.mp3

Each writes <set_dir>/<name>.mp4 plus preview/ frames. Formats: 02-research/formats/
(who-lets-go-last-video.md, a-vs-b-sim-video.md, paradox-essay-animation.md, imagine-a-man-parable.md).
Scene timings for essay/parable are tied to the current voiceover scripts (word timings from video_finish.py --words).
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
ANTON = os.path.join(HERE, "..", "assets", "fonts", "Anton-Regular.ttf")
IB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
IBOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
IMED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
LIME = (198, 255, 0); GRAPH = (62, 68, 76); WHITE = (240, 242, 245); GREY = (120, 126, 134)
_fc = {}
def F(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]

def ctext(d, txt, font, y, fill, x=W / 2, spacing=0):
    tw = d.textlength(txt, font=font) + spacing * (len(txt) - 1)
    if spacing:
        cx = x - tw / 2
        for ch in txt:
            d.text((cx, y), ch, font=font, fill=fill); cx += d.textlength(ch, font=font) + spacing
    else:
        d.text((x - tw / 2, y), txt, font=font, fill=fill)

def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)

def rline(d, a, b, w, fill):
    d.line([a, b], fill=fill, width=w)
    for p in (a, b): d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=fill)

class Writer:
    def __init__(self, path, audio=None, sfx=None):
        self.path, self.audio, self.sfx = path, audio, sfx
        self.tmp = path + ".noaudio.mp4"
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                   "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", self.tmp],
                                  stdin=subprocess.PIPE)
    def add(self, img): self.p.stdin.write(img.convert("RGB").tobytes())
    def close(self, dur):
        self.p.stdin.close(); self.p.wait()
        aud = self.audio
        if self.sfx is not None:
            aud = self.path + ".sfx.wav"; write_wav(aud, self.sfx)
        if aud:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", self.tmp, "-i", aud, "-filter_complex",
                            f"[1:a]apad,atrim=0:{dur}[a]", "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac",
                            "-b:a", "192k", self.path], check=True)
            os.remove(self.tmp)
            if self.sfx is not None: os.remove(aud)
        else:
            os.replace(self.tmp, self.path)

SR = 44100
def write_wav(path, x):
    import wave
    x = np.clip(x, -1, 1); w = wave.open(path, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()

def thud(n, t0, vol=0.6):
    i = int(t0 * SR); L = int(0.35 * SR); tt = np.arange(L) / SR
    s = np.sin(2 * np.pi * (70 - 40 * tt) * tt) * np.exp(-tt * 12) + 0.25 * np.random.randn(L) * np.exp(-tt * 40)
    n[i:i + L] += vol * s[: len(n) - i]

def tick(n, t0, vol=0.12):
    i = int(t0 * SR); L = int(0.03 * SR); tt = np.arange(L) / SR
    n[i:i + L] += vol * np.sin(2 * np.pi * 2200 * tt) * np.exp(-tt * 200)

def save_preview(set_dir, name, img):
    os.makedirs(os.path.join(set_dir, "preview"), exist_ok=True)
    img.convert("RGB").resize((540, 960)).save(os.path.join(set_dir, "preview", name + ".jpg"), quality=88)

def wordmark(d, y=1800, fill=(90, 96, 104)):
    ctext(d, "EARND", F(IBOLD, 26), y, fill, spacing=14)

# ---------------------------------------------------------------- HANG
def hang(set_dir):
    DUR = 12.0
    labels = ["MOTIVATION", "DISCIPLINE", "EGO", "LAST WEEK'S\nNUMBER"]
    xs = [165, 415, 665, 915]
    drop = {0: 2.2, 2: 4.6, 1: 7.4}            # index -> time the grip goes
    BAR = 820
    bg = Image.new("RGB", (W, H), (10, 11, 13))
    g = np.linspace(0, 1, H)[:, None]
    arr = np.array(bg).astype(np.float32); arr += (18 * (1 - abs(g - 0.45) * 2)).clip(0)[:, :, None]
    bg = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
    def cone(i, a):
        m = Image.new("L", (W, H), 0); dm = ImageDraw.Draw(m)
        x = xs[i]; dm.polygon([(x - 40, 520), (x + 40, 520), (x + 135, 1560), (x - 135, 1560)], fill=int(60 * a))
        return m.filter(ImageFilter.GaussianBlur(28))
    cones = [cone(i, 1) for i in range(4)]
    n = np.zeros(int(DUR * SR) + SR)
    for t in drop.values(): thud(n, t + 0.45)
    for s in range(1, 40): tick(n, s * 0.25, 0.05)
    wr = Writer(os.path.join(set_dir, "who-lets-go-last.mp4"), sfx=n)
    for fi in range(int(DUR * FPS)):
        t = fi / FPS
        img = bg.copy()
        for i in range(4):
            a = 1.0
            if i in drop and t > drop[i]: a = max(0.15, 1 - (t - drop[i]) * 1.5)
            if i == 3 and t > 8.6: a = 1 + 0.8 * ease((t - 8.6) / 0.6)
            img.paste((255, 255, 255), (0, 0), cones[i].point(lambda v, a=a: min(255, int(v * a))))
        d = ImageDraw.Draw(img)
        ctext(d, "WHO LETS GO LAST?", F(ANTON, 104), 250, WHITE)
        secs = int(min(t, 9.0) * 11); ctext(d, f"{secs // 60}:{secs % 60:02d}", F(MONO, 92), 470,
                                            LIME if t > 8.6 else (150, 156, 164))
        rline(d, (60, BAR), (W - 60, BAR), 10, (88, 94, 102))
        for px in (60, W - 60): rline(d, (px, BAR), (px, 1500), 10, (70, 76, 84))
        d.line([(40, 1500), (W - 40, 1500)], fill=(48, 52, 58), width=4)
        for i, x in enumerate(xs):
            gone = i in drop and t > drop[i]
            lab = labels[i]; lc = WHITE
            if gone: lc = (80, 84, 90)
            if i == 3 and t > 8.6: lc = LIME
            for k, ln in enumerate(lab.split("\n")):
                ctext(d, ln, F(MONO, 30 if len(ln) > 8 else 34), 680 + k * 40 - (20 if "\n" in lab else 0), lc, x=x)
            dy, sx = 0.0, 0.0
            if i in drop:
                if drop[i] - 0.7 < t <= drop[i]: sx = 4 * math.sin(t * 70)
                if gone: tt = t - drop[i]; dy = 0.5 * 5200 * tt * tt
            if dy > 900: continue
            body = LIME if (i == 3 and t > 8.6) else (205, 210, 216)
            hand_y = BAR + dy - (0 if not gone else min(60, dy * 0.3))
            y0 = BAR + dy; x0 = x + sx
            # arms (released arms flail up slightly)
            rline(d, (x0 - 48, hand_y), (x0 - 30, y0 + 120), 20, body); rline(d, (x0 + 48, hand_y), (x0 + 30, y0 + 120), 20, body)
            d.ellipse([x0 - 40, y0 + 62, x0 + 40, y0 + 142], fill=body)
            rline(d, (x0, y0 + 150), (x0, y0 + 360), 22, body)
            rline(d, (x0 - 13, y0 + 360), (x0 - 13, y0 + 610), 20, body); rline(d, (x0 + 13, y0 + 360), (x0 + 13, y0 + 610), 20, body)
        if t > 9.2:
            a = ease((t - 9.2) / 0.6); c = tuple(int(v * a) for v in WHITE)
            ctext(d, "the number to beat", F(IBOLD, 52), 1600, c)
            ctext(d, "never lets go.", F(IBOLD, 52), 1665, tuple(int(v * a) for v in LIME))
        wordmark(d)
        wr.add(img)
        if fi in (int(1.0 * FPS), int(5.0 * FPS), int(11.5 * FPS)): save_preview(set_dir, f"f{fi:03d}", img)
    wr.close(DUR)

# ---------------------------------------------------------------- A vs B
def avb(set_dir):
    DUR = 16.0; WEEKS = 12; W0, WSTEP = 1.6, 0.85
    hop = ["BENCH PRESS", "CABLE FLY", "DIPS", "INCLINE DB", "PUSH-UPS", "PEC DECK", "LANDMINE PRESS", "SVEND PRESS",
           "BENCH PRESS", "CHEST PRESS", "DECLINE BENCH", "FLOOR PRESS"]
    trk = [(60, 6), (60, 7), (60, 8), (62.5, 6), (62.5, 7), (62.5, 7), (62.5, 8), (65, 6), (65, 7), (65, 8), (67.5, 7), (67.5, 8)]
    bg = Image.new("RGB", (W, H), (12, 13, 16)); db = ImageDraw.Draw(bg)
    for x in (270, 810):
        m = Image.new("L", (W, H), 0); dm = ImageDraw.Draw(m)
        dm.polygon([(x - 50, 600), (x + 50, 600), (x + 230, 1300), (x - 230, 1300)], fill=55)
        bg.paste((255, 255, 255), (0, 0), m.filter(ImageFilter.GaussianBlur(30)))
        db.ellipse([x - 230, 1250, x + 230, 1330], fill=(26, 28, 33))
    n = np.zeros(int(DUR * SR) + SR)
    for k in range(WEEKS): tick(n, W0 + k * WSTEP, 0.18)
    thud(n, W0 + WEEKS * WSTEP + 0.1, 0.4)
    wr = Writer(os.path.join(set_dir, "tracked-vs-new-every-week.mp4"), sfx=n)
    def bench(d, x, t, r, col, plate):
        by = 1170
        d.rounded_rectangle([x - 170, by, x + 150, by + 26], 8, fill=(70, 76, 84))
        rline(d, (x - 120, by + 26), (x - 120, 1290), 12, (70, 76, 84)); rline(d, (x + 110, by + 26), (x + 110, 1290), 12, (70, 76, 84))
        rline(d, (x - 140, by - 22), (x + 100, by - 22), 30, col)              # torso
        d.ellipse([x - 215, by - 58, x - 145, by + 12], fill=col)               # head
        rline(d, (x + 100, by - 22), (x + 175, by + 40), 24, col); rline(d, (x + 175, by + 40), (x + 175, 1290), 22, col)
        ph = 0.5 - 0.5 * math.cos(2 * math.pi * t / 1.1); bar_y = by - 70 - 130 * ph
        el = (x - 35, (by - 22 + bar_y) / 2 + 20)
        rline(d, (x - 85, by - 22), el, 20, col); rline(d, el, (x - 70, bar_y), 20, col)
        d.ellipse([x - 70 - r, bar_y - r, x - 70 + r, bar_y + r], fill=plate)
        d.ellipse([x - 70 - 10, bar_y - 10, x - 70 + 10, bar_y + 10], fill=(20, 20, 24))
    for fi in range(int(DUR * FPS)):
        t = fi / FPS; img = bg.copy(); d = ImageDraw.Draw(img)
        ctext(d, "New workout every week", F(IB, 64), 200, WHITE)
        ctext(d, "vs", F(IMED, 44), 285, GREY)
        ctext(d, "same program, tracked.", F(IB, 64), 345, LIME)
        wk = 0 if t < W0 else min(WEEKS - 1, int((t - W0) / WSTEP))
        ctext(d, f"WEEK {wk + 1:>2} / {WEEKS}", F(MONO, 50), 480, (170, 176, 184))
        ctext(d, "NEW EVERY WEEK", F(MONO, 30), 600, WHITE, x=270); ctext(d, "TRACKED", F(MONO, 30), 600, LIME, x=810)
        kg, reps = trk[wk]
        bench(d, 270, t, 52, (205, 210, 216), (95, 100, 108))
        bench(d, 810, t + 0.3, 40 + (kg - 60) * 5, LIME, (70, 150, 220))
        ctext(d, hop[wk], F(MONO, 34), 1370, WHITE, x=270)
        ctext(d, "last time: ?", F(MONO, 30), 1420, GREY, x=270)
        ctext(d, f"{kg:g} kg × {reps}", F(MONO, 38), 1366, LIME, x=810)
        if wk: pk, pr = trk[wk - 1]; ctext(d, f"last time: {pk:g} × {pr}", F(MONO, 30), 1420, (150, 200, 60), x=810)
        else: ctext(d, "last time: -", F(MONO, 30), 1420, GREY, x=810)
        ctext(d, "(weights: example)", F(IMED, 26), 1470, GREY, x=810)
        tend = W0 + WEEKS * WSTEP
        if t > tend:
            a = ease((t - tend) / 0.5)
            d.rectangle([0, 1530, W, 1760], fill=(int(12 + 6 * a), int(13 + 6 * a), int(16 + 6 * a)))
            ctext(d, "12 weeks later:", F(IBOLD, 40), 1545, tuple(int(v * a) for v in GREY))
            ctext(d, "nothing to compare", F(IB, 46), 1610, tuple(int(v * a) for v in WHITE), x=270)
            ctext(d, "60 → 67.5 kg × 8", F(IB, 46), 1610, tuple(int(v * a) for v in LIME), x=810)
            if t > tend + 1.2: ctext(d, "which one are you?", F(IBOLD, 44), 1690, tuple(int(v * ease((t - tend - 1.2) / 0.5)) for v in WHITE))
        wordmark(d, 1820)
        wr.add(img)
        if fi in (int(0.8 * FPS), int(7 * FPS), int(15.5 * FPS)): save_preview(set_dir, f"f{fi:03d}", img)
    wr.close(DUR)

# ---------------------------------------------------------------- glow line-art helpers
BASE = None
def glow_compose(white, lime, base):
    out = np.asarray(base).astype(np.float32)
    for lay, col, k in ((white, (235, 238, 242), 1.0), (lime, LIME, 1.0)):
        a = np.asarray(lay).astype(np.float32) / 255
        if a.max() == 0: continue
        b = np.asarray(lay.resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(5)).resize((W, H))).astype(np.float32) / 255
        aa = np.clip(a + 0.9 * b, 0, 1)[:, :, None]
        out = out * (1 - aa) + np.array(col, np.float32) * aa * k + out * 0  # light over
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))

def dark_base():
    base = np.full((H, W, 3), 6, np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    base += 22 * np.exp(-(((xx - W / 2) / 700) ** 2 + ((yy - H * 0.45) / 900) ** 2))[:, :, None]
    dots = Image.new("L", (W, H), 0); dd = ImageDraw.Draw(dots)
    for y in range(60, H, 60):
        for x in range(30, W, 60): dd.point((x, y), fill=40)
    base += np.asarray(dots)[:, :, None] * 0.6
    return Image.fromarray(base.clip(0, 255).astype(np.uint8))

def stick(d, x, yf, s=1.0, w=9, pose="stand", ph=0.0, fill=255):
    """Line-art person, feet at yf. pose: stand | climb | walk | slump."""
    hd = 34 * s; hy = yf - 330 * s
    d.ellipse([x - hd, hy - hd, x + hd, hy + hd], outline=fill, width=w)
    neck = (x, hy + hd); hip = (x, yf - 150 * s)
    if pose == "slump": hip = (x + 10 * s, yf - 140 * s)
    d.line([neck, hip], fill=fill, width=w)
    sh = (x, hy + hd + 30 * s)
    if pose == "climb":
        a = math.sin(ph); lh = (x - 34 * s, hy - 40 * s + 50 * s * a); rh = (x + 34 * s, hy - 40 * s - 50 * s * a)
        lf = (x - 30 * s, yf - 40 * s - 60 * s * a); rf = (x + 30 * s, yf - 40 * s + 60 * s * a)
        for hnd in (lh, rh): d.line([sh, hnd], fill=fill, width=w)
        for ft in (lf, rf): d.line([hip, ((hip[0] + ft[0]) / 2 + (ft[0] - x) * 0.6, (hip[1] + ft[1]) / 2), ft], fill=fill, width=w, joint="curve")
    else:
        sw = math.sin(ph) * (30 * s if pose == "walk" else 0)
        d.line([sh, (x - 50 * s - sw * 0.5, yf - 175 * s)], fill=fill, width=w)
        d.line([sh, (x + 50 * s + sw * 0.5, yf - 175 * s)], fill=fill, width=w)
        d.line([hip, (x - 40 * s - sw, yf)], fill=fill, width=w); d.line([hip, (x + 40 * s + sw, yf)], fill=fill, width=w)

def pill(d, x, y, txt, fill=255, size=30):
    f = F(IBOLD, size); tw = d.textlength(txt, font=f)
    d.rounded_rectangle([x - tw / 2 - 26, y, x + tw / 2 + 26, y + size + 28], radius=(size + 28) // 2, outline=fill, width=4)
    d.text((x - tw / 2, y + 12), txt, font=f, fill=fill)

def keyword(d, kicker, big, t, t0, y=300, col=255, bigsize=110):
    a = int(255 * ease((t - t0) / 0.25))
    if kicker: ctext(d, kicker.upper(), F(IBOLD, 30), y - 50, int(a * 0.55) if col == 255 else int(a * 0.55), spacing=6)
    if big:
        f = F(IB, bigsize)
        while d.textlength(big, font=f) > W - 120: f = F(IB, f.size - 6)
        ctext(d, big, f, y, int(a) if col == 255 else int(a))

def seq(t, items):
    cur = None
    for it in items:
        if t >= it[0]: cur = it
    return cur

# ---------------------------------------------------------------- ESSAY
def essay(set_dir):
    voice = os.path.join(set_dir, "voice.mp3")
    DUR = 45.4; base = dark_base()
    kw = [(0.0, "the guy who knows", "THE MOST"), (4.0, "is probably", "THE WEAKEST"), (5.9, "and the reason explains", "EVERYTHING"),
          (10.0, "he's read", "EVERY STUDY"), (11.7, "he knows", "EVERY SPLIT"), (13.6, "every month", "A BETTER PROGRAM"),
          (16.0, "so he starts again", "WEEK 1"), (18.2, "", "MEANWHILE"), (21.3, "", "SAME 4 DAYS"), (25.0, "", "WRITES IT DOWN"),
          (27.8, "tries to beat it by", "+1 REP"), (29.9, "", "A YEAR LATER"), (31.0, "", "STILL STARTING OVER"),
          (34.4, "", "LIFTING MORE THAN EVER"), (37.3, "people say", "\"GENETICS\""), (39.9, None, None)]
    wr = Writer(os.path.join(set_dir, "knows-the-most.mp4"), audio=voice)
    for fi in range(int(DUR * FPS)):
        t = fi / FPS
        wl = Image.new("L", (W, H), 0); ll = Image.new("L", (W, H), 0)
        dw, dl = ImageDraw.Draw(wl), ImageDraw.Draw(ll)
        k = seq(t, kw)
        if k and k[2]: keyword(dw if k[2] not in ("+1 REP", "LIFTING MORE THAN EVER") else dl, k[1], k[2], t, k[0], y=330)
        floor = 1460
        if t < 39.9: dw.line([(80, floor), (W - 80, floor)], fill=90, width=3)
        if t < 18.2:                                            # guy A alone, centre
            x = 540; stick(dw, x, floor, 1.15)
            pill(dw, x, floor - 600, "KNOWS EVERYTHING")
            if t > 4.0:                                          # strength meter, low
                dw.text((x + 120, floor - 330), "STRENGTH", font=F(IBOLD, 26), fill=150)
                dw.rectangle([x + 120, floor - 290, x + 360, floor - 268], outline=150, width=3)
                dw.rectangle([x + 124, floor - 286, x + 124 + 40, floor - 272], fill=255)
            if 10.0 < t < 16.0:                                  # papers / icons orbit
                for j, lab in enumerate(["STUDY", "SPLIT", "PPL", "5x5", "PHUL", "BRO"]):
                    if t < 10.0 + j * 0.9: continue
                    ang = j * 1.05 + t * 0.4; px = x + 300 * math.cos(ang); py = floor - 470 + 150 * math.sin(ang)
                    dw.rounded_rectangle([px - 60, py - 30, px + 60, py + 30], 8, outline=200, width=3)
                    ctext(dw, lab, F(IBOLD, 24), py - 14, 200, x=px)
            if t >= 13.6:                                        # calendar card, resets to week 1
                wkn = 1 + int(max(0, t - 13.6) * 3) % 4 if t < 16.0 else 1
                cx, cy = x - 300, floor - 520
                dw.rounded_rectangle([cx - 90, cy - 70, cx + 90, cy + 70], 12, outline=255, width=4)
                ctext(dw, "WEEK", F(IBOLD, 24), cy - 50, 170, x=cx); ctext(dw, str(wkn), F(IB, 64), cy - 20, 255, x=cx)
        elif t < 29.9:                                          # A left (still resetting), B right with log
            a = ease((t - 18.2) / 0.8)
            xa = 540 - 260 * a; stick(dw, xa, floor, 1.0)
            pill(dw, xa, floor - 540, "WEEK 1 AGAIN", 140, 26)
            xb = 1240 - 440 * ease((t - 18.4) / 1.2); stick(dl, xb, floor, 1.0, pose="walk" if t < 19.6 else "stand", ph=t * 9)
            if t > 21.3: pill(dl, xb, floor - 540, "SAME 4 DAYS", 255, 26)
            if t > 25.0:                                         # logbook
                lx, ly = 540, 560
                dl.rounded_rectangle([lx - 250, ly, lx + 260, ly + 300], 14, outline=255, width=4)
                ctext(dl, "UPPER A · BENCH", F(MONO, 28), ly + 22, 200, x=lx)
                rows = [("last time", "60 × 7"), ("today", "60 × 8" if t > 28.3 else "60 × _")]
                for r, (lab, val) in enumerate(rows):
                    dl.text((lx - 200, ly + 90 + r * 70), lab, font=F(MONO, 30), fill=170)
                    dl.text((lx + 40, ly + 90 + r * 70), val, font=F(MONO, 34), fill=255)
                if t > 28.3: dl.text((lx + 185, ly + 160), "+1", font=F(MONO, 34), fill=255)
                ctext(dw, "(example)", F(IMED, 24), ly + 255, 120, x=lx)
        elif t < 39.9:                                          # one-year graph
            gx0, gx1, gy0, gy1 = 140, 960, 1360, 760
            dw.line([(gx0, gy1 - 40), (gx0, gy0), (gx1, gy0)], fill=150, width=4)
            ctext(dw, "1 YEAR", F(MONO, 28), gy0 + 20, 150, x=(gx0 + gx1) / 2)
            ctext(dw, "STRENGTH", F(MONO, 24), gy1 - 90, 150, x=gx0 + 40)
            p = ease((t - 30.2) / 3.5)
            pa, pb = [], []
            for i in range(int(200 * p) + 1):
                u = i / 200; x = gx0 + (gx1 - gx0) * u
                pa.append((x, gy0 - 120 - 60 * ((u * 12) % 1)))     # resets every month
                pb.append((x, gy0 - 120 - 430 * (u ** 0.8)))
            if len(pa) > 1: dw.line(pa, fill=230, width=6); dl.line(pb, fill=255, width=7)
            if p > 0.98:
                ctext(dw, "starting over", F(IBOLD, 28), gy0 - 110, 200, x=gx1 - 120)
                if t > 37.3: pill(dl, gx1 - 130, gy1 - 30, "GENETICS?", 255, 30)
        else:                                                   # moral
            ctext(dw, "THE GYM DOESN'T PAY YOU", F(IB, 66), 760, int(255 * ease((t - 39.9) / 0.3)))
            ctext(dw, "FOR KNOWING.", F(IB, 66), 850, int(255 * ease((t - 39.9) / 0.3)))
            if t > 42.3:
                ctext(dl, "IT PAYS YOU", F(IB, 76), 1010, int(255 * ease((t - 42.3) / 0.3)))
                ctext(dl, "FOR REPEATING.", F(IB, 76), 1110, int(255 * ease((t - 42.3) / 0.3)))
        img = glow_compose(wl, ll, base); wordmark(ImageDraw.Draw(img))
        wr.add(img)
        if fi in [int(s * FPS) for s in (2, 12, 22, 29, 36, 44)]: save_preview(set_dir, f"f{fi:04d}", img)
    wr.close(DUR)

# ---------------------------------------------------------------- PARABLE
def parable(set_dir):
    voice = os.path.join(set_dir, "voice.mp3")
    DUR = 39.0; base = dark_base(); RUNG = 70
    yy, xx = np.mgrid[0:H, 0:W]
    kw = [(0.0, "imagine", "A MAN"), (2.2, "climbing a ladder", "IN THE DARK"), (6.3, "", "EVERY NIGHT"), (8.9, "after", "A MONTH"),
          (12.3, "so he climbs", "BACK DOWN"), (14.2, "looking for", "A BETTER LADDER"), (16.2, "", "ANOTHER MAN"),
          (20.2, "", "COUNTS EVERY RUNG"), (23.6, "some nights", "10"), (25.7, "some nights", "1"),
          (27.6, "he always knows", "THE NUMBER TO BEAT"), (30.7, "", "A YEAR LATER"), (34.4, None, None)]
    def a_height(t):   # rungs climbed by man A
        if t < 6.3: return 2 * ease(t / 6.3)
        if t < 12.3: return 2 + 4 * ease((t - 6.3) / 4.0)
        if t < 15.5: return 6 * (1 - ease((t - 12.3) / 2.2))
        return 0
    def b_count(t):
        if t < 18.5: return 0
        if t < 23.6: return int(1 + 47 * ease((t - 18.5) / 5.0))
        if t < 25.7: return 48 + int(10 * ease((t - 23.6) / 1.2))
        if t < 27.6: return 58 + (1 if t > 26.4 else 0)
        if t < 30.7: return 59
        return int(59 + 1181 * ease((t - 30.7) / 3.0))
    wr = Writer(os.path.join(set_dir, "ladder-in-the-dark.mp4"), audio=voice)
    for fi in range(int(DUR * FPS)):
        t = fi / FPS
        wl = Image.new("L", (W, H), 0); ll = Image.new("L", (W, H), 0)
        dw, dl = ImageDraw.Draw(wl), ImageDraw.Draw(ll)
        if t < 16.2: who, h = "A", a_height(t)
        else: who, h = "B", min(b_count(t), 59) / 6.0
        zoom = 1.0 - 0.82 * ease((t - 31.0) / 2.8) if t > 31.0 else 1.0
        ground = 1500; cam = max(0, h * RUNG - 300) * zoom
        if t > 31.0: cam = 0; h_vis = 1240
        lx = 540
        top = -40000
        for side in (-70, 70):
            dw.line([(lx + side * zoom, ground + cam), (lx + side * zoom, max(top, -200))], fill=210, width=max(3, int(7 * zoom)))
        r0 = int(max(0, (ground + cam - H - 50) / (RUNG * zoom)))
        for r in range(r0, r0 + int(H / (RUNG * zoom)) + 3):
            y = ground + cam - r * RUNG * zoom
            if y < -10: break
            dw.line([(lx - 70 * zoom, y), (lx + 70 * zoom, y)], fill=210, width=max(2, int(6 * zoom)))
        dw.line([(0, ground + cam), (W, ground + cam)], fill=120, width=3)
        if t > 31.0:   # far up the ladder, tiny man + glowing top marker
            yb = 680; stick(dl, lx, yb + 40, 0.18, w=3, pose="climb", ph=t * 6)
        else:
            yfeet = ground + cam - h * RUNG * zoom
            d = dl if who == "B" else dw
            if who == "A" and 15.5 < t < 16.2: stick(dw, lx + 160, ground + cam, 1.0, pose="slump")
            elif who == "A" and t > 12.3 and h < 0.05: stick(dw, lx + 160, ground + cam, 1.0, pose="slump")
            else: stick(d, lx, yfeet, 1.0, pose="climb" if (h > 0.02 or (who == "B" and t > 18.5)) else "stand", ph=t * (5 if who == "B" else 3))
        # darkness: vignette around the climber (lifts at the end)
        if t < 31.0:
            fy = ground + cam - h * RUNG - 180
            rad = 330 + (0 if who == "A" else 60)
            m = np.exp(-(((xx - lx) / rad) ** 2 + ((yy - fy) / (rad * 1.3)) ** 2))
            m = np.clip(m * 1.6, 0.05, 1.0).astype(np.float32)
            wl = Image.fromarray((np.asarray(wl) * m).astype(np.uint8)); ll = Image.fromarray((np.asarray(ll) * m).astype(np.uint8))
            dw, dl = ImageDraw.Draw(wl), ImageDraw.Draw(ll)
        if t > 34.4: wl = Image.new("L", (W, H), 0); ll = Image.new("L", (W, H), 0); dw, dl = ImageDraw.Draw(wl), ImageDraw.Draw(ll)
        else: dw.rectangle([0, 0, W, 600], fill=0); dl.rectangle([0, 0, W, 600], fill=0)
        k = seq(t, kw)
        if k and k[2]:
            tgt = dl if k[2] in ("10", "1", "THE NUMBER TO BEAT") else dw
            keyword(tgt, k[1], k[2], t, k[0], y=300, bigsize=120)
        if 8.9 < t < 12.3: ctext(dw, "HEIGHT: ?", F(MONO, 44), 470, 200)
        if t > 18.5 and t < 34.4:
            c = b_count(t); ctext(dl, f"RUNG {c:,}", F(MONO, 52), 470, 255)
            if 27.6 < t < 30.7: ctext(dw, "TO BEAT: 58", F(MONO, 36), 540, 180)
        if t > 34.4:
            a = int(255 * ease((t - 34.4) / 0.3)); ctext(dw, "YOU CAN'T FEEL PROGRESS.", F(IB, 70), 760, a)
            if t > 36.8: ctext(dl, "YOU HAVE TO SEE IT.", F(IB, 84), 880, int(255 * ease((t - 36.8) / 0.3)))
        img = glow_compose(wl, ll, base); wordmark(ImageDraw.Draw(img))
        wr.add(img)
        if fi in [int(s * FPS) for s in (1.5, 10, 14, 21, 29, 33, 38)]: save_preview(set_dir, f"f{fi:04d}", img)
    wr.close(DUR)

if __name__ == "__main__":
    {"hang": hang, "avb": avb, "essay": essay, "parable": parable}[sys.argv[1]](sys.argv[2])
