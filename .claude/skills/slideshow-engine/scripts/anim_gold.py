#!/usr/bin/env python3
"""Line-art account videos: warm gold glow sketches on black (style: 02-research/formats/account-visual-styles.md).
Gold, never @earndapp's lime, so the account reads as its own page. 0 generation credits + one AI voiceover.

  python3 anim_gold.py escalator <set_dir>   # parable: "the down escalator"
  python3 anim_gold.py feeling   <set_dir>   # manifesto: "the feeling comes after"
  python3 anim_gold.py oneline   <set_dir>   # faceless one-line clip, no voice: reads <set_dir>/oneline.json {"out","line1","line2","end"}

Voiced scenes need <set_dir>/voice.mp3 (oneline has none); scene timings match the current voiceovers (video_finish.py --words).
Every video ends on a disclosure card: the account is ours and EARND is our app.
"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anim_formats import W, H, FPS, F, IB, IBOLD, MONO, ctext, ease, Writer, save_preview, dark_base, stick, seq

CREAM = (255, 236, 205); GOLD = (255, 186, 72)


def compose(cream, gold, base):
    out = np.asarray(base).astype(np.float32)
    for lay, col in ((cream, CREAM), (gold, GOLD)):
        a = np.asarray(lay).astype(np.float32) / 255
        if a.max() == 0: continue
        b = np.asarray(lay.resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(6)).resize((W, H))).astype(np.float32) / 255
        aa = np.clip(a + 1.1 * b, 0, 1)[:, :, None]
        out = out * (1 - aa) + np.array(col, np.float32) * aa
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def warm_base():
    b = np.asarray(dark_base()).astype(np.float32)
    b[:, :, 0] *= 1.12; b[:, :, 2] *= 0.8   # warm spotlight
    return Image.fromarray(b.clip(0, 255).astype(np.uint8))


def big(d, txt, y, a, size=120):
    f = F(IB, size)
    while d.textlength(txt, font=f) > W - 120: f = F(IB, f.size - 6)
    ctext(d, txt, f, y, int(255 * a))


def kw_draw(dc, dg, t, kws, gold_words, y=300):
    k = seq(t, kws)
    if not k or not k[2]: return
    a = ease((t - k[0]) / 0.25); d = dg if k[2] in gold_words else dc
    if k[1]: ctext(dc, k[1].upper(), F(IBOLD, 30), y - 50, int(140 * a), spacing=6)
    big(d, k[2], y, a)


def endcard(dc, dg, t, t0, line1, line2):
    a = ease((t - t0) / 0.3)
    ctext(dg, line1, F(IB, 64), 760, int(255 * a))
    for i, ln in enumerate(line2): ctext(dc, ln, F(IBOLD, 46), 900 + i * 66, int(220 * a))


def render(set_dir, out, dur, draw, previews):
    base = warm_base(); va = os.path.join(set_dir, "voice.mp3"); wr = Writer(os.path.join(set_dir, out), audio=va if os.path.exists(va) else None)
    for fi in range(int(dur * FPS)):
        t = fi / FPS
        c = Image.new("L", (W, H), 0); g = Image.new("L", (W, H), 0)
        draw(t, ImageDraw.Draw(c), ImageDraw.Draw(g))
        img = compose(c, g, base); wr.add(img)
        if fi in [int(s * FPS) for s in previews]: save_preview(set_dir, f"f{fi:04d}", img)
    wr.close(dur)


DISCLOSE = ["this page is made by EARND, our gym app.", "follow @earndapp for the launch."]


# ------------------------------------------------------------------ the down escalator (parable)
def escalator(set_dir):
    END = 27.4
    kws = [(0.0, "imagine a man on a", "DOWN ESCALATOR"), (3.0, "every week he", "TRAINS"), (6.4, "every week he", "SKIPS"),
           (10.5, "one month on", "ONE MONTH OFF"), (14.2, "ends up", "WHERE HE STARTED"), (16.8, "", "ANOTHER MAN"),
           (18.9, "he", "NEVER STOPS"), (20.1, "missed a day?", "MOVE IT"), (22.9, "don't", "SKIP IT"), (24.2, None, None)]
    x0, y0, x1, y1 = 140, 1550, 940, 650          # escalator: bottom-left to top-right
    N = 14
    def pos(u):                                  # u: 0 bottom .. 1 top
        return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
    def man_a(t):                                # height along the escalator, 0..1
        if t < 3.0: return 0.08
        if t < 6.4: return 0.08 + 0.42 * ease((t - 3.0) / 2.8)
        if t < 10.4: return 0.5 - 0.42 * ease((t - 6.4) / 3.6)
        if t < 13.0: return 0.08 + 0.4 * ease((t - 10.5) / 2.0)
        if t < 16.4: return 0.48 - 0.4 * ease((t - 13.0) / 2.6)
        return 0.08
    def man_b(t): return 0.08 + 0.75 * ease((t - 17.0) / 7.0)
    def draw(t, dc, dg):
        if t >= END:
            return endcard(dc, dg, t, END, "slow beats stopped.", DISCLOSE)
        if t > 24.2:
            a = ease((t - 24.2) / 0.3); big(dg, "SLOW BEATS", 760, a, 130); big(dg, "STOPPED.", 900, ease((t - 24.6) / 0.3), 130)
            if t > 26.0: ctext(dc, "EVERY TIME.", F(IBOLD, 48), 1080, int(230 * ease((t - 26.0) / 0.3)), spacing=8)
            return
        kw_draw(dc, dg, t, kws, ("NEVER STOPS", "MOVE IT", "ANOTHER MAN"))
        # rails + moving steps (always running downwards)
        for off in (-60, 60):
            dc.line([(x0 - 40, y0 + off), (x1 - 40, y1 + off)], fill=150, width=5)
        sh = (t * 0.35) % 1.0
        for i in range(N + 1):
            u = (i - sh) / N
            if 0 <= u <= 1:
                x, y = pos(u); dc.line([(x - 70, y + 40), (x + 10, y + 40)], fill=210, width=6); dc.line([(x + 10, y + 40), (x + 10, y - 10)], fill=210, width=5)
        dc.line([(40, y0 + 40), (x0 - 70, y0 + 40)], fill=150, width=4); dc.line([(x1 + 10, y1 - 10), (W - 40, y1 - 10)], fill=150, width=4)
        # down arrows on the rail
        for i in range(3):
            u = 1 - ((t * 0.25 + i / 3) % 1.0); x, y = pos(u); dc.polygon([(x + 60, y - 120), (x + 90, y - 120), (x + 75, y - 95)], fill=120)
        if t < 16.8:
            u = man_a(t); x, y = pos(u); walking = (3.0 < t < 6.4) or (10.5 < t < 13.0)
            stick(dc, x - 30, y + 40, 0.55, w=6, pose="walk" if walking else ("slump" if t > 14.2 else "stand"), ph=t * 7)
            lab = "TRAINING" if walking else ("SKIPPING" if t > 6.4 else "")
            if lab: ctext(dc, lab, F(MONO, 30), int(y - 230), 180, x=x)
            if t > 14.2: ctext(dg, "STEP 0", F(MONO, 44), 1680, int(255 * ease((t - 14.2) / 0.3)))
        else:
            u = man_b(t); x, y = pos(u); stick(dg, x - 30, y + 40, 0.55, w=6, pose="walk", ph=t * 4)
            ctext(dg, f"STEP {int(u * 40)}", F(MONO, 44), 1680, 255)
            if t > 20.1:   # the week strip: a missed day moved, not skipped
                days = ["M", "T", "W", "T", "F", "S", "S"]; xs = [180 + i * 120 for i in range(7)]
                for i, dd in enumerate(days): ctext(dc, dd, F(MONO, 30), 470, 170, x=xs[i])
                src, dst = 1, 2; a = ease((t - 21.9) / 0.8)
                for i in (0, 3):
                    dg.rounded_rectangle([xs[i] - 40, 520, xs[i] + 40, 580], 10, outline=255, width=4)
                bx = xs[src] + (xs[dst] - xs[src]) * a
                dg.rounded_rectangle([bx - 40, 520 + 0 * a, bx + 40, 580], 10, outline=255, width=4)
                if a > 0.05: dc.line([(xs[src] - 30, 600), (xs[src] + 30, 600)], fill=140, width=3)
    render(set_dir, "down-escalator.mp4", END + 3.2, draw, (1.2, 5, 8.5, 12, 15.5, 19, 22.5, 25.5, 29.5))


# ------------------------------------------------------------------ the feeling comes after (manifesto)
def feeling(set_dir):
    END = 24.0
    kws = [(0.0, "", "NOBODY"), (0.9, "", "FEELS LIKE TRAINING"), (2.3, "not the guy", "10 YEARS IN"), (5.2, "not the guy who's", "\"DISCIPLINED\""),
           (7.5, "motivation isn't", "THE START"), (10.1, "it's what you feel", "ONCE YOU'RE THERE"), (12.2, "", "10 MINUTES IN"),
           (14.8, "", "EVERY TIME"), (16.1, "stop waiting to", "FEEL READY"), (18.4, None, None)]
    def draw(t, dc, dg):
        if t >= END:
            return endcard(dc, dg, t, END, "save this for tomorrow.", DISCLOSE)
        kw_draw(dc, dg, t, kws, ("ONCE YOU'RE THERE", "EVERY TIME"))
        if t < 7.5:                                    # three people, all slumped
            n = 1 if t < 2.3 else (2 if t < 5.2 else 3)
            for i in range(n):
                x = [540, 300, 780][i]; stick(dc, x, 1400, 0.85, w=7, pose="slump")
            if t > 2.3: ctext(dc, "YEAR 10", F(MONO, 28), 1450, 160, x=300)
            if t > 5.2: ctext(dc, "\"DISCIPLINED\"", F(MONO, 28), 1450, 160, x=780)
            ctext(dc, "MOTIVATION: LOW", F(MONO, 30), 1560, 150)
        elif t < 12.2:                                 # door diagram: motivation shows up after the door
            dx = 540; dc.rectangle([dx - 90, 900, dx + 90, 1400], outline=220, width=6); dc.ellipse([dx + 50, 1140, dx + 64, 1154], fill=220)
            p = ease((t - 7.6) / 2.4); x = 200 + (760 - 200) * p
            stick(dg if x > dx else dc, x, 1400, 0.6, w=6, pose="walk", ph=t * 7)
            lvl = 0.15 if x < dx else 0.15 + 0.85 * ease((t - 10.1) / 1.4)
            bx, by = 920, 1400; dc.rectangle([bx - 30, by - 420, bx + 30, by], outline=170, width=4)
            dg.rectangle([bx - 22, by - 412 * lvl, bx + 22, by - 8], fill=255)
            ctext(dc, "WANT TO", F(MONO, 24), by + 20, 160, x=bx); ctext(dc, "BE HERE", F(MONO, 24), by + 50, 160, x=bx)
        elif t < 16.1:                                 # timer 0:00 -> 10:00 and the meter fills
            p = ease((t - 12.2) / 2.0); m = int(10 * p)
            ctext(dg, f"{m:02d}:00", F(MONO, 150), 760, 255)
            bx0, bx1, by = 190, 890, 1150; dc.rounded_rectangle([bx0, by, bx1, by + 70], 35, outline=190, width=5)
            dg.rounded_rectangle([bx0 + 10, by + 10, bx0 + 10 + (bx1 - bx0 - 20) * max(0.06, p), by + 60], 25, fill=255)
            ctext(dc, "GLAD YOU CAME", F(MONO, 30), by + 110, 170)
            stick(dc, 540, 1650, 0.45, w=6)
        elif t < 22.0:                                 # the three steps
            steps = [(18.44, "PACK THE BAG"), (19.58, "WALK IN"), (20.6, "START THE FIRST SET")]
            for i, (t0, lab) in enumerate(steps):
                if t < t0 - 0.1: continue
                a = ease((t - t0 + 0.1) / 0.3); y = 760 + i * 300; d = dg if i == len([s for s in steps if t >= s[0] - 0.1]) - 1 else dc
                cx = 260
                if i == 0:
                    d.rounded_rectangle([cx - 70, y - 40, cx + 70, y + 50], 14, outline=int(255 * a), width=6); d.arc([cx - 35, y - 80, cx + 35, y - 10], 180, 360, fill=int(255 * a), width=6)
                elif i == 1:
                    d.rectangle([cx - 45, y - 80, cx + 45, y + 60], outline=int(255 * a), width=6); d.ellipse([cx + 22, y - 5, cx + 32, y + 5], fill=int(255 * a))
                else:
                    d.line([(cx - 90, y), (cx + 90, y)], fill=int(255 * a), width=8)
                    for sx in (-70, 70): d.rectangle([cx + sx - 12, y - 45, cx + sx + 12, y + 45], outline=int(255 * a), width=6)
                d.text((400, y - 30), lab, font=F(IBOLD, 54), fill=int(255 * a))
            if t < 18.4: stick(dc, 540, 1400, 0.85, w=7, pose="slump")
        else:
            big(dc, "THE FEELING", 780, ease((t - 22.0) / 0.3), 130); big(dg, "COMES AFTER.", 930, ease((t - 22.6) / 0.3), 130)
    render(set_dir, "feeling-comes-after.mp4", END + 3.2, draw, (0.5, 3.5, 6, 9, 11.5, 14, 17, 21, 23.5, 26))


# ------------------------------------------------------------------ two walls (stickman-style metaphor)
def walls(set_dir):
    END = 17.6
    kws = [(0.0, "two men start", "THE SAME WALL"), (2.6, "one gets bored and", "STARTS A BETTER ONE"), (6.0, "", "THEN ANOTHER"),
           (8.7, "the other", "LAYS THE NEXT BRICK"), (11.3, "a year later", "ONE HAS A WALL"), (14.4, None, None)]
    BW, BH = 84, 48
    def wall(d, x0, y0, n, cols=5, fill=230, w=4):
        for i in range(n):
            r, c = divmod(i, cols); off = (BW // 2) if r % 2 else 0
            x = x0 + c * BW + off; y = y0 - (r + 1) * BH
            d.rectangle([x, y, x + BW - 6, y + BH - 6], outline=fill, width=w)
        return y0 - ((n + cols - 1) // cols) * BH
    def draw(t, dc, dg):
        if t >= END:
            return endcard(dc, dg, t, END, "lay the next brick.", DISCLOSE)
        if t > 14.4:
            big(dc, "PICK ONE PLAN.", 760, ease((t - 14.4) / 0.3), 120); big(dg, "LAY THE NEXT BRICK.", 900, ease((t - 16.1) / 0.3), 110)
            return
        kw_draw(dc, dg, t, kws, ("LAYS THE NEXT BRICK", "ONE HAS A WALL"))
        ground = 1520
        dc.line([(60, ground), (W - 60, ground)], fill=120, width=3)
        # left: restarts at 2.6, 6.0, 7.1 -> abandoned stubs to the left, current short wall
        starts = [0.0, 2.6, 6.0, 7.1]
        cur = max(i for i, s0 in enumerate(starts) if t >= s0)
        for i in range(cur):                                   # abandoned stubs shrink into the distance
            sx = 30 + i * 52; wall(dc, sx, ground, 2, cols=1, fill=110, w=3)
        since = t - starts[cur]; n_left = min(9, int(since * 3.2))
        lx = 200; ltop = wall(dc, lx, ground, n_left, cols=3)
        stick(dc, lx + 300, ground, 0.8, w=6, pose="walk" if 0.2 < since < 2.5 else "stand", ph=t * 5)
        # right: steady, never stops
        n_right = int(min(t, 14.4) * 3.6)
        rtop = wall(dg if t > 8.7 else dc, 560, ground, n_right, cols=5)
        sy = min(ground, rtop + 2) if t > 8.7 else ground
        stick(dg if t > 8.7 else dc, 1000, ground, 0.8, w=6, pose="walk", ph=t * 6)
        if t > 11.3:
            ctext(dg, f"BRICK {n_right}", F(MONO, 44), 1580, 255, x=780)
            ctext(dc, f"BRICK {n_left}", F(MONO, 44), 1580, 160, x=330)
    render(set_dir, "two-walls.mp4", END + 3.2, draw, (1, 4, 7.5, 10, 13, 16.5, 19.5))


# ------------------------------------------------------------------ one line (faceless clip, no voice)
def oneline(set_dir):
    import json
    sp = json.load(open(os.path.join(set_dir, "oneline.json")))
    END = 6.4
    def bar(d, x, y, fill):
        d.line([(x - 150, y), (x + 150, y)], fill=fill, width=8)
        for sx in (-1, 1):
            for k in range(2): px = x + sx * (110 + k * 22); d.rounded_rectangle([px - 8, y - 55, px + 8, y + 55], 6, outline=fill, width=5)
    def draw(t, dc, dg):
        if t >= END:
            return endcard(dc, dg, t, END, sp.get("end", "save this."), DISCLOSE)
        big(dc, sp["line1"], 300, ease((t - 0.2) / 0.35), 110)
        if t > 2.6: big(dg, sp["line2"], 450, ease((t - 2.6) / 0.35), 110)
        fy = 1560
        x = 160 + 380 * ease(t / 2.4)
        if t < 2.4:
            stick(dc, x, fy, 1.4, w=9, pose="walk", ph=t * 7); bar(dc, 540, fy - 40, 200)
        else:
            p = ease((t - 3.2) / 1.2)                      # bar from the floor to the hips
            hy = fy - 40 - (175 * 1.4 - 40) * p
            stick(dg, 540, fy, 1.4, w=9); bar(dg, 540, hy, 255)
        dc.line([(80, fy + 4), (W - 80, fy + 4)], fill=90, width=3)
    render(set_dir, sp["out"], END + 3.0, draw, (1.0, 3.0, 5.0, 8.0))


if __name__ == "__main__":
    {"escalator": escalator, "feeling": feeling, "walls": walls, "oneline": oneline}[sys.argv[1]](sys.argv[2])
