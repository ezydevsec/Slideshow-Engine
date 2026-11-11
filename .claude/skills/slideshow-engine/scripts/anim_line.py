#!/usr/bin/env python3
"""Narrated line-art videos (glow pictograms on black), 0 generation credits + one voiceover.

  python3 anim_line.py nobody   <set_dir>   # manifesto: "Nobody at the gym is watching you"
  python3 anim_line.py january  <set_dir>   # manifesto: "Don't wait for January"
  python3 anim_line.py cliff    <set_dir>   # named concept: "The novice cliff"

Needs <set_dir>/voice.mp3; scene timings match the current scripts (video_finish.py --words).
Formats: 02-research/formats/line-art-manifesto.md, named-concept-diagram.md. Our own scripts and drawings;
the reference accounts only informed the structure.
"""
import math, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anim_formats import (W, H, FPS, F, IB, IBOLD, IMED, MONO, ctext, ease, Writer, save_preview, wordmark,
                          glow_compose, dark_base, stick, pill, keyword, seq)


def run(set_dir, out, dur, kw, draw, previews, lime_words=()):
    base = dark_base()
    wr = Writer(os.path.join(set_dir, out), audio=os.path.join(set_dir, "voice.mp3"))
    for fi in range(int(dur * FPS)):
        t = fi / FPS
        wl = Image.new("L", (W, H), 0); ll = Image.new("L", (W, H), 0)
        dw, dl = ImageDraw.Draw(wl), ImageDraw.Draw(ll)
        k = seq(t, kw)
        if k and k[2]:
            keyword(dl if k[2] in lime_words else dw, k[1], k[2], t, k[0], y=330)
        draw(t, dw, dl)
        img = glow_compose(wl, ll, base); wordmark(ImageDraw.Draw(img))
        wr.add(img)
        if fi in [int(s * FPS) for s in previews]: save_preview(set_dir, f"f{fi:04d}", img)
    wr.close(dur)


def eye(d, x, y, r, fill=255, w=4, look=0.0):
    d.chord([x - r, y - r * 0.55, x + r, y + r * 0.55], 0, 360, outline=fill, width=w)
    px = x + look * r * 0.45
    d.ellipse([px - r * 0.22, y - r * 0.22, px + r * 0.22, y + r * 0.22], fill=fill)


def card(d, cx, cy, txt, fill=255, w=4, crossed=0.0, size=30):
    f = F(IBOLD, size); tw = d.textlength(txt, font=f); bw = max(170, tw + 50)
    d.rounded_rectangle([cx - bw / 2, cy - 55, cx + bw / 2, cy + 55], 12, outline=fill, width=w)
    d.text((cx - tw / 2, cy - size / 2 - 4), txt, font=f, fill=fill)
    if crossed > 0:
        a = ease(crossed); x0, y0, x1, y1 = cx - bw / 2 + 15, cy - 45, cx + bw / 2 - 15, cy + 45
        d.line([(x0, y0), (x0 + (x1 - x0) * a, y0 + (y1 - y0) * a)], fill=fill, width=6)
        d.line([(x1, y0), (x1 - (x1 - x0) * a, y0 + (y1 - y0) * a)], fill=fill, width=6)


def xmark(d, x, y, r, fill=255, w=6):
    d.line([(x - r, y - r), (x + r, y + r)], fill=fill, width=w); d.line([(x + r, y - r), (x - r, y + r)], fill=fill, width=w)


def tick_mark(d, x, y, r, fill=255, w=6):
    d.line([(x - r, y), (x - r * 0.3, y + r * 0.7), (x + r, y - r * 0.8)], fill=fill, width=w, joint="curve")


def stairs(d, x0, y0, n, sw, sh, fill=200, labels=None, xs=(), w=4):
    pts = [(x0, y0)]
    for i in range(n):
        x, y = pts[-1]; pts += [(x, y - sh), (x + sw, y - sh)]
    d.line(pts, fill=fill, width=w)
    for i in range(n):
        cx = x0 + i * sw + sw / 2; cy = y0 - (i + 1) * sh - 30
        if labels: ctext(d, labels[i], F(MONO, 20), y0 - (i + 1) * sh + 8, 130, x=cx)
        if i in xs: xmark(d, cx, cy, 13, fill=fill, w=5)
    return lambda i: (x0 + i * sw + sw / 2, y0 - (i + 1) * sh)


# ------------------------------------------------------------- "Nobody at the gym is watching you"
def nobody(set_dir):
    kw = [(0.0, "", "NOBODY IS WATCHING"), (2.5, "they're all busy with", "THEIR OWN SET"), (5.4, "stop waiting until you feel", "READY"),
          (8.3, "stop changing your", "PROGRAM"), (11.7, "stop guessing", "LAST WEEK"), (14.4, "", "PICK A PLAN"), (15.7, "", "4 DAYS"),
          (16.8, "", "SAME EXERCISES"), (18.4, "", "WRITE IT DOWN"), (20.4, "beat it by", "+1 REP"), (22.1, "some weeks", "YOU WON'T"),
          (23.4, "that's", "FINE"), (24.5, "", "SHOW UP ANYWAY"), (25.7, "a year from now", None)]
    floor = 1420

    def draw(t, dw, dl):
        cx, cy = 540, 1000
        if t < 5.4:                                              # ring of eyes -> everyone on their own set
            stick(dl if t > 2.5 else dw, cx, cy + 170, 0.8)
            for i in range(8):
                a = i / 8 * 2 * math.pi + 0.2; ex, ey = cx + 330 * math.cos(a), cy + 20 + 300 * math.sin(a)
                if t < 2.5: eye(dw, ex, ey, 46, look=-math.cos(a))
                else:
                    p = ease((t - 2.5) / 0.6); stick(dw, ex, ey + 70, 0.32, w=5)
                    if p > 0.3:                                  # each holds their own dumbbell
                        dw.line([(ex + 18, ey - 20), (ex + 46, ey - 20)], fill=200, width=5)
                        dw.rectangle([ex + 40, ey - 32, ex + 52, ey - 8], outline=200, width=3)
        elif t < 8.3:                                            # loading bar stuck
            stick(dw, cx, floor, 1.0); pill(dw, cx, floor - 560, "READY?")
            dw.rounded_rectangle([cx - 300, 760, cx + 300, 810], 25, outline=220, width=4)
            p = 0.12 + 0.02 * math.sin(t * 3); dw.rounded_rectangle([cx - 292, 768, cx - 292 + 584 * p, 802], 18, fill=255)
            ctext(dw, f"{int(p * 100)}%", F(MONO, 30), 830, 150)
        elif t < 11.7:                                           # programmes flipping
            names = ["PROGRAM A", "PROGRAM B", "PROGRAM C", "PROGRAM D", "PROGRAM E"]
            k = int((t - 8.3) * 2.2) % len(names)
            for j in range(3):
                card(dw, cx - 20 + j * 20, 820 + j * 20, names[(k + j) % len(names)], fill=90 + 70 * j)
            stick(dw, cx, floor, 1.0)
        elif t < 14.4:                                           # logbook of question marks
            dw.rounded_rectangle([cx - 260, 700, cx + 260, 1060], 16, outline=230, width=4)
            ctext(dw, "LAST WEEK", F(MONO, 30), 725, 170)
            for r in range(3):
                dw.text((cx - 210, 800 + r * 80), f"SET {r + 1}", font=F(MONO, 34), fill=170)
                dw.text((cx + 40, 800 + r * 80), "? × ?", font=F(MONO, 40), fill=255)
            stick(dw, cx, floor, 1.0)
        elif t < 15.7:                                           # fork, one branch ticked
            dw.line([(cx, 1300), (cx, 1050)], fill=230, width=5)
            dw.line([(cx, 1050), (cx - 260, 760)], fill=110, width=5); dw.line([(cx, 1050), (cx + 260, 760)], fill=255, width=6)
            tick_mark(dl, cx + 280, 720, 30)
            stick(dw, cx, 1340, 0.6, w=6)
        elif t < 18.4:                                           # week strip(s)
            days = "MTWTFSS"; on = (0, 1, 3, 4)
            rows = 1 if t < 16.8 else 3
            for r in range(rows):
                for i, ch in enumerate(days):
                    x = 165 + i * 125; y = 760 + r * 150
                    tgt = dl if i in on else dw
                    tgt.rounded_rectangle([x - 50, y - 50, x + 50, y + 50], 12, outline=255 if i in on else 110, width=4)
                    ctext(tgt, ch, F(IB, 40), y - 24, 255 if i in on else 110, x=x)
                if r == 0 or t > 16.8:
                    ctext(dw, "UPPER A · LOWER A · UPPER B · LOWER B", F(MONO, 22), 840 + r * 150, 140)
        elif t < 22.1:                                           # checklist ticking, then +1 rep
            dw.rounded_rectangle([cx - 280, 680, cx + 280, 1120], 16, outline=230, width=4)
            rows = [("SET 1", "60 × 7"), ("SET 2", "60 × 6")]
            for r, (a, b) in enumerate(rows):
                y = 760 + r * 110; dw.text((cx - 230, y), a, font=F(MONO, 34), fill=170); dw.text((cx - 20, y), b, font=F(MONO, 38), fill=255)
                if t > 18.8 + r * 0.6: tick_mark(dl, cx + 210, y + 22, 22)
            if t > 20.4:
                y = 990; dl.text((cx - 230, y), "TODAY", font=F(MONO, 34), fill=255); dl.text((cx - 20, y), "60 × 8", font=F(MONO, 38), fill=255)
                dl.text((cx + 170, y), "+1", font=F(MONO, 38), fill=255)
            ctext(dw, "(example)", F(IMED, 24), 1130, 120)
        elif t < 24.5:                                           # stairs with misses
            stairs(dw, 170, 1300, 6, 125, 80, xs=(1, 4))
            if t > 23.4: tick_mark(dl, 540, 1360, 30)
        elif t < 25.7:                                           # walking
            dw.line([(80, floor), (W - 80, floor)], fill=110, width=3)
            stick(dw, 200 + (t - 24.5) * 520, floor, 0.9, pose="walk", ph=t * 10)
        else:                                                    # doorway -> new person
            p = ease((t - 26.6) / 1.4)
            dw.rectangle([cx - 130, 820, cx + 130, 1420], outline=200, width=5)
            if t < 26.9:
                stick(dw, cx - 260, floor, 0.6, w=6); ctext(dw, "SCARED TO WALK IN", F(MONO, 26), 1460, 150)
            else:
                stick(dl, cx, floor, 0.6 + 0.6 * p, w=int(6 + 6 * p))
                if t > 27.2:
                    a = int(255 * ease((t - 27.2) / 0.3)); ctext(dl, "YOU WON'T", F(IB, 90), 300, a); ctext(dl, "RECOGNISE THEM", F(IB, 90), 410, a)
    run(set_dir, "nobody-is-watching.mp4", 31.4, kw, draw, (1, 4, 6, 9, 13, 16, 19, 21, 23, 29), lime_words=("+1 REP", "FINE"))


# ------------------------------------------------------------- "Don't wait for January"
def january(set_dir):
    kw = [(0.0, "you could start", "NOW"), (1.4, "or wait for", "JANUARY"), (4.8, "it's not", None), (11.9, "it's", "TONIGHT"),
          (13.1, "there will always be", "SOMETHING"), (18.3, "", "FAILING A REP: OK"), (20.4, "", "MISSING A SET: OK"),
          (22.3, "", "NOT SHOWING UP"), (24.2, "by january", "7 WEEKS IN")]

    def draw(t, dw, dl):
        cx = 540
        if t < 4.8:                                              # start step vs far-off flag
            dw.line([(100, 1350), (420, 1350), (420, 1250), (980, 1250)], fill=200, width=5)
            stick(dl if t < 1.4 else dw, 250, 1350, 0.6, w=6); ctext(dw, "START HERE", F(MONO, 24), 1380, 160, x=250)
            if t > 1.4:
                fx = 900; dw.line([(fx, 1250), (fx, 1050)], fill=230, width=5); dw.polygon([(fx, 1050), (fx + 80, 1080), (fx, 1110)], outline=230)
                ctext(dw, "JANUARY", F(MONO, 26), 1000, 200, x=fx)
        elif t < 11.9:
            items = [("MONDAY", 5.7, 7.0), ("AFTER THE HOLIDAYS", 7.2, 9.6), ("JANUARY", 9.8, 11.2)]
            for i, (txt, t0, tx) in enumerate(items):
                if t > t0 - 0.2: card(dw, cx, 760 + i * 170, txt, crossed=(t - tx) / 0.4 if t > tx else 0, size=36)
        elif t < 13.1:
            a = int(255 * ease((t - 11.9) / 0.25)); ctext(dl, "START", F(IB, 150), 760, a); ctext(dl, "TONIGHT", F(IB, 150), 920, a)
            stick(dw, cx, 1450, 0.7)
        elif t < 18.3:                                           # bars: always something
            bars = [("BUSY WEEK", 13.1, 260), ("LATE SHIFT", 15.5, 330), ("BAD SLEEP", 16.7, 400)]
            dw.line([(120, 1300), (960, 1300)], fill=150, width=3)
            for i, (lab, t0, hgt) in enumerate(bars):
                if t < t0: continue
                x = 260 + i * 280; hh = hgt * ease((t - t0) / 0.4)
                dw.rectangle([x - 70, 1300 - hh, x + 70, 1300], fill=235)
                ctext(dw, lab, F(MONO, 24), 1320, 170, x=x)
            ctext(dw, "ALWAYS", F(MONO, 30), 1400, 200)
        elif t < 22.3:
            step = stairs(dw, 160, 1350, 7, 110, 75, labels=[f"WK {i+1}" for i in range(7)], xs=(1,) + ((4,) if t > 20.4 else ()))
            tick_mark(dl, 900, 760, 34)
        elif t < 24.2:
            a = ease((t - 22.3) / 0.3); xmark(dw, cx, 1000, 130 * a + 1, w=14)
            ctext(dw, "IS NOT OK", F(IBOLD, 40), 1200, int(200 * a))
        else:                                                    # climb to week 7
            step = stairs(dw, 160, 1350, 7, 110, 75, labels=[f"WK {i+1}" for i in range(7)], xs=(1, 4))
            p = ease((t - 24.2) / 3.4); i = min(6, int(p * 7)); x, y = step(i)
            stick(dl, x, y, 0.42, w=6, pose="walk", ph=t * 8)
            if t > 27.2: ctext(dl, "JANUARY", F(MONO, 30), y - 210, 255, x=min(x, 900))
    run(set_dir, "dont-wait-for-january.mp4", 29.3, kw, draw, (1, 3, 8, 10.5, 12.3, 17, 21, 23, 28.5), lime_words=("TONIGHT", "7 WEEKS IN"))


# ------------------------------------------------------------- "The novice cliff"
def cliff(set_dir):
    kw = [(0.0, "your first year in the gym is", "EASY"), (2.5, "that's the", "PROBLEM"), (3.8, "at the start", "IT GOES UP"),
          (7.3, "then one day", "IT DOESN'T"), (9.7, "", "STUCK?"), (12.4, "so they", "SWITCH PROGRAMS"), (16.2, "", "AND AGAIN"),
          (17.2, "that drop-off has a name", None), (20.7, "you didn't stop", "IMPROVING"), (22.8, "the wins just got", "SMALLER"),
          (28.3, "only if you", "WRITE THEM DOWN"), (30.8, "they stopped", "STARTING OVER")]
    gx0, gx1, gy0, gy1 = 130, 950, 1360, 640

    def curve(u):  # steep then flat
        return 1 - math.exp(-u * 5)

    def draw(t, dw, dl):
        if t < 20.7 or t >= 30.8:
            dw.line([(gx0, gy1 - 20), (gx0, gy0), (gx1, gy0)], fill=150, width=4)
            ctext(dw, "TIME", F(MONO, 24), gy0 + 18, 150, x=(gx0 + gx1) / 2)
            dw.text((gx0 + 14, gy1 - 30), "STRENGTH", font=F(MONO, 24), fill=150)
        if t < 12.4:
            end = 0.0 if t < 3.8 else (0.35 * ease((t - 3.8) / 3.0) if t < 7.3 else 0.35 + 0.65 * ease((t - 7.3) / 2.2))
            pts = [(gx0 + (gx1 - gx0) * u / 100, gy0 - (gy0 - gy1 - 60) * curve(u / 100) * 0.85) for u in range(int(end * 100) + 1)]
            if len(pts) > 1: dw.line(pts, fill=255, width=7)
            if t > 9.7: pill(dw, 760, gy1 + 40, "STUCK?")
        elif t < 20.7:                                           # restarts -> sawtooth
            nre = 1 + (1 if t > 14.3 else 0) + (1 if t > 16.2 else 0)
            seg = 1 / (nre + 1); pts = []
            for k in range(nre + 1):
                for u in range(31):
                    uu = u / 30; x = gx0 + (gx1 - gx0) * (k * seg + seg * uu)
                    pts.append((x, gy0 - (gy0 - gy1 - 60) * curve(uu * 0.6) * 0.5))
            dw.line(pts, fill=255, width=7)
            if t > 17.2:                                         # the stamp
                a = ease((t - 17.2) / 0.3)
                if a > 0:
                    stamp = Image.new("L", (620, 170), 0); sd = ImageDraw.Draw(stamp)
                    sd.rounded_rectangle([6, 6, 614, 164], 14, outline=255, width=8)
                    tw = sd.textlength("THE NOVICE CLIFF", font=F(IB, 64)); sd.text(((620 - tw) / 2, 42), "THE NOVICE CLIFF", font=F(IB, 64), fill=255)
                    stamp = stamp.rotate(-6, expand=True, resample=Image.BICUBIC)
                    dl.bitmap((540 - stamp.width / 2, 260), stamp, fill=int(255 * a))
        elif t < 28.3:                                           # zoom: tiny steps
            step = stairs(dl, 170, 1300, 6, 120, 45, w=5)
            if t > 24.8: ctext(dl, "+1 REP", F(MONO, 40), 1000, 255, x=300)
            if t > 26.2:
                ctext(dl, "+2.5 KG", F(MONO, 40), 880, 255, x=700); ctext(dw, "(example)", F(IMED, 24), 935, 120, x=700)
            ctext(dw, "ZOOMED IN", F(MONO, 24), 1340, 140)
        elif t < 30.8:                                           # logbook
            cx = 540; dw.rounded_rectangle([cx - 260, 700, cx + 260, 1080], 16, outline=230, width=4)
            for r, (a, b) in enumerate([("WK 10", "60 × 7"), ("WK 11", "60 × 8"), ("WK 12", "62.5 × 5")]):
                y = 760 + r * 95; dw.text((cx - 220, y), a, font=F(MONO, 34), fill=170); dl.text((cx + 10, y), b, font=F(MONO, 38), fill=255)
            ctext(dw, "(example)", F(IMED, 24), 1040, 120)
        else:                                                    # sawtooth vs steady climb
            pts_a, pts_b = [], []
            for u in range(101):
                uu = u / 100; x = gx0 + (gx1 - gx0) * uu
                pts_a.append((x, gy0 - 220 * curve((uu * 4) % 1 * 0.6) * 0.8))
                pts_b.append((x, gy0 - (gy0 - gy1 - 80) * (0.7 * curve(uu * 0.9) + 0.3 * uu)))
            dw.line(pts_a, fill=200, width=6); dl.line(pts_b, fill=255, width=7)
            ctext(dw, "starting over", F(IBOLD, 28), gy0 - 270, 170, x=gx1 - 130)
    run(set_dir, "the-novice-cliff.mp4", 36.6, kw, draw, (1, 5.5, 8.5, 11, 15, 18.5, 22, 27, 29.5, 35), lime_words=("IMPROVING", "WRITE THEM DOWN", "STARTING OVER"))


if __name__ == "__main__":
    {"nobody": nobody, "january": january, "cliff": cliff}[sys.argv[1]](sys.argv[2])
