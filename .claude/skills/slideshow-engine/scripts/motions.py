"""Exercise motions for the study-race mannequins (founder 2026-11-18: the motion must match the topic).

draw(d, motion, x, floor, p, col, shade, kit)
  motion: deadlift | squat | curl | calf | press | bench
  p: 0..1 position in the rep (0 = start/stretch, 1 = top/lockout)
  col/shade: body colours (ints on a glow layer); kit: plate/dumbbell colour (None on a glow layer: body only)
IDLE[motion] is the pose to hold on rest days. Front view except bench (side view).
"""
import math


def cap(d, a, b, w, fill):
    d.line([a, b], fill=fill, width=int(w))
    for p in (a, b): d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=fill)


def limb(d, a, b, w, col, shade):
    cap(d, a, b, w + 8, shade); cap(d, (a[0] + 3, a[1]), (b[0] + 3, b[1]), w, col)


def head(d, x, y, col, shade, r=50):
    d.ellipse([x - r, y - r, x + r, y + r], fill=shade)
    d.ellipse([x - r + 6, y - r + 3, x + r - 2, y + r - 5], fill=col)
    d.ellipse([x - 22, y - 34, x + 2, y - 14], fill=col if isinstance(col, int) else (255, 255, 255))


def plates(d, x, y, kit, half=150, n=2, h=74):
    if kit is None: return
    d.line([(x - half - 40, y), (x + half + 40, y)], fill=(205, 205, 210), width=12)
    for s in (-1, 1):
        for k in range(n):
            px = x + s * (half - 32 + k * 26); d.ellipse([px - 14, y - h, px + 14, y + h], fill=kit)


def dumbbell(d, x, y, kit):
    if kit is None: return
    d.line([(x - 34, y), (x + 34, y)], fill=(205, 205, 210), width=10)
    for s in (-1, 1): d.ellipse([x + s * 34 - 12, y - 32, x + s * 34 + 12, y + 32], fill=kit)


def standing(d, x, floor, col, shade, lift=0, knee=0, hip_drop=0, legs=True):
    """Upright body; returns (shoulder_y, hip_y). lift raises the whole body (calf raise); knee pushes knees out (squat)."""
    hip_y = floor - 300 - lift + hip_drop
    sh_y = hip_y - 250
    if legs:
        for s in (-1, 1):
            hip = (x + s * 32, hip_y); kn = (x + s * (44 + knee), (hip_y + floor - lift) / 2 + hip_drop * 0.2)
            ankle = (x + s * 46, floor - 30 - lift); toe = (x + s * 50, floor - 8)
            limb(d, hip, kn, 26, col, shade); limb(d, kn, ankle, 26, col, shade); limb(d, ankle, toe, 18, col, shade)
    limb(d, (x, sh_y), (x, hip_y), 52, col, shade)
    head(d, x, sh_y - 70, col, shade)
    return sh_y, hip_y


def draw(d, motion, x, floor, p, col, shade, kit):
    if motion == "deadlift":
        import anim_stick as st
        old = st.FLOOR; st.FLOOR = floor
        hy = st.figure(d, x, p, col=col, shade=shade); st.FLOOR = old
        plates(d, x, hy, kit); return
    if motion == "squat":                         # bar on the back, hips drop
        drop = 150 * (1 - p)
        sh_y, hip_y = standing(d, x, floor, col, shade, knee=60 * (1 - p), hip_drop=drop)
        for s in (-1, 1):
            limb(d, (x + s * 52, sh_y + 14), (x + s * 120, sh_y + 60), 21, col, shade)
            limb(d, (x + s * 120, sh_y + 60), (x + s * 125, sh_y - 4), 21, col, shade)
        plates(d, x, sh_y - 4, kit, half=180); return
    if motion == "curl":                          # elbows pinned, forearms come up
        sh_y, _ = standing(d, x, floor, col, shade)
        a = math.pi * 0.85 * p; pts = {}
        for s in (-1, 1):
            elbow = (x + s * 66, sh_y + 175)
            hand = (x + s * 70, elbow[1] + 150 * math.cos(a))
            limb(d, (x + s * 52, sh_y + 14), elbow, 21, col, shade); limb(d, elbow, hand, 19, col, shade)
            dumbbell(d, hand[0] + s * 8, hand[1], kit)
            if s == 1: pts = {"hand": (hand[0] + 8, hand[1]), "biceps": ((x + 52 + elbow[0]) / 2 + 4, (sh_y + 14 + elbow[1]) / 2)}
        return pts
    if motion == "calf":                          # on a step: heels drop (p=0) to high on toes (p=1)
        if kit is not None: d.rectangle([x - 110, floor - 8, x + 110, floor + 40], fill=(120, 120, 128))
        lift = -45 + 115 * p
        sh_y, _ = standing(d, x, floor, col, shade, lift=lift)
        for s in (-1, 1):
            hand = (x + s * 82, sh_y + 235)
            limb(d, (x + s * 52, sh_y + 14), hand, 21, col, shade); dumbbell(d, hand[0], hand[1] + 10, kit)
        return
    if motion == "press":                         # overhead press: shoulders to lockout
        sh_y, _ = standing(d, x, floor, col, shade)
        bar_y = (sh_y - 10) - (sh_y - 10 - (sh_y - 260)) * p
        for s in (-1, 1):
            hand = (x + s * 105, bar_y)
            elbow = (x + s * (150 - 50 * p), (sh_y + 14 + bar_y) / 2 + 40 * (1 - p))
            limb(d, (x + s * 52, sh_y + 14), elbow, 21, col, shade); limb(d, elbow, hand, 19, col, shade)
        plates(d, x, bar_y, kit, half=170); return
    if motion == "bench":                         # side view: lying on a bench, bar from chest to lockout
        by = floor - 230                           # bench top
        if kit is not None:
            d.rounded_rectangle([x - 190, by, x + 120, by + 34], 10, fill=(110, 110, 118))
            for lx in (x - 160, x + 90): d.line([(lx, by + 34), (lx, floor)], fill=(110, 110, 118), width=14)
        hip = (x + 80, by - 28); sh = (x - 120, by - 34)
        limb(d, sh, hip, 52, col, shade)
        head(d, x - 185, by - 50, col, shade, r=44)
        for kx in (0,):
            knee = (x + 160, by - 70); foot = (x + 200, floor - 10)
            limb(d, hip, knee, 26, col, shade); limb(d, knee, foot, 26, col, shade)
        bar_y = (by - 90) - 190 * p
        elbow = (x - 160 + 40 * p, (by - 40 + bar_y) / 2 + 30 * (1 - p))
        hand = (x - 110, bar_y)
        limb(d, (sh[0], sh[1]), elbow, 21, col, shade); limb(d, elbow, hand, 19, col, shade)
        if kit is not None:
            d.ellipse([hand[0] - 52, bar_y - 52, hand[0] + 52, bar_y + 52], fill=kit)
            d.ellipse([hand[0] - 14, bar_y - 14, hand[0] + 14, bar_y + 14], fill=(205, 205, 210))
        return
    raise ValueError(motion)


IDLE = {"deadlift": 1.0, "squat": 1.0, "curl": 0.0, "calf": 0.3, "press": 0.0, "bench": 1.0}
