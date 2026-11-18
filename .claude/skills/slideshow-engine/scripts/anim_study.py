#!/usr/bin/env python3
"""@earndapp "study race" video (format: 02-research/formats/a-vs-b-sim-video.md, 2026-11-15 update).
Graphite mannequins + lime (never Earnie's white/amber sticks), a real study's result, the catch, then a real app screen.

  python3 anim_study.py <set_dir>     # reads <set_dir>/study.json, writes <set_dir>/<out>

study.json: title_a/title_b, question, days_a/days_b (lifting days per week, 0=Mon), weeks, result_a/result_b,
result_note, cite, catch_lines [..], catch_cite, tie_in, shot, endcard [..]
Optional: render ("3d": real Blender mannequins via mannequin3d.py, each pose rendered once and reused), sides (2–3 sides: [{title, head, sub, days, result, label, color, range, off_weeks, win}]), always_move (rep continuously during the race, like the reference videos), title_parts ([[text, colour], ...] headline override), focus per side ("hand" | "biceps" on curls), res_t / catch_t / app_t (phase lengths, defaults 2.6 / 4.0 / 3.6), motion (deadlift | squat | curl | calf | press | bench; must match the study's exercise), range_a / range_b ([lo, hi] part of the rep each side moves through, e.g. bottom-half partials), off_weeks_a / off_weeks_b (weeks with no training; the bar dips, then regains), tie (light both sides at the result), days_shown + day_labels (e.g. 4 days: "the session", "24 h later", ...) replace the WEEK counter; week_t (seconds per week, default 0.9), catch_closes (default true: the losing bar catches up during the catch).
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim_stick as st
import motions

W, H, FPS = st.W, st.H, st.FPS
FLOOR = st.FLOOR
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
LIME = (198, 255, 0)
ANTON = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "Anton-Regular.ttf")
INTER = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
ease = st.ease


def fit(d, txt, size, maxw, path=ANTON):
    f = ImageFont.truetype(path, size)
    while d.textlength(txt, font=f) > maxw and size > 20: size -= 2; f = ImageFont.truetype(path, size)
    return f


def ct(d, txt, y, size, fill, x=W / 2, maxw=W - 100, path=ANTON):
    f = fit(d, txt, size, maxw, path); d.text((x - d.textlength(txt, font=f) / 2, y), txt, font=f, fill=fill)


def growth(off, weeks, w):
    """Cumulative growth 0..1 at week w for a side with weeks off: +1 per training week, -0.35 per week off,
    +1.6 for the first 2 weeks back (regain). Normalised so week `weeks` ends at 1.0."""
    def cum(upto):
        g, back = 0.0, 0
        for k in range(1, weeks + 1):
            f = min(1.0, max(0.0, upto - (k - 1)))
            if f <= 0: break
            if k in off: g -= 0.35 * f; back = 2
            elif back: g += 1.6 * f; back -= 1 if f >= 1 else 0
            else: g += 1.0 * f
        return max(g, 0.0)
    return cum(w) / cum(weeks)


def sides_of(sp):
    """Normalise to a list of sides. Either sp["sides"] = [{title, head, sub, days, result, label, color, range, off_weeks, win}]
    (2 or 3 sides) or the classic _a/_b keys (b is the winner)."""
    if sp.get("sides"): return sp["sides"]
    out = []
    for k, win in (("a", False), ("b", True)):
        out.append(dict(title=sp["title_" + k], head=sp.get("head_" + k, sp["title_" + k]), sub=sp.get("sub_" + k), days=sp["days_" + k],
                        result=sp["result_" + k], label=sp["result_" + k + "_label"], win=win,
                        color=sp.get("color_" + k, (198, 255, 0) if win else (110, 190, 255)),
                        range=sp.get("range_" + k, [0.0, 1.0]), off_weeks=sp.get("off_weeks_" + k, [])))
    return out


def render(set_dir):
    sp = json.load(open(os.path.join(set_dir, "study.json")))
    SIDES = sides_of(sp); N = len(SIDES)
    XS = [310, 770] if N == 2 else [190, 540, 890]
    HALF = 150 if N == 2 else 125
    weeks = sp.get("weeks", 8); WK = sp.get("week_t", 0.9)
    T_RACE0, T_RACE1 = 1.4, 1.4 + weeks * WK
    T_RES = T_RACE1; T_CATCH = T_RES + sp.get("res_t", 2.6); T_APP = T_CATCH + sp.get("catch_t", 4.0)
    DUR = T_APP + sp.get("app_t", 3.6)
    STAGE = sp.get("style") == "stage"          # @appforthegym look: charcoal stage, spotlight cones, ivory mannequins, side colours
    WINC = tuple(next((sd_["color"] for sd_ in SIDES if sd_.get("win")), LIME))
    MAXR = max(sd_["result"] for sd_ in SIDES)
    MOT = sp.get("motion", "deadlift")
    base = np.zeros((H, W, 3), np.float32); yy, xx = np.mgrid[0:H, 0:W]
    if STAGE:
        base += np.array([15, 17, 23], np.float32)
        for cx in XS:
            cone = Image.new("L", (W, H), 0); ImageDraw.Draw(cone).polygon([(cx - 40, 380), (cx + 40, 380), (cx + 230 * HALF / 150, FLOOR + 20), (cx - 230 * HALF / 150, FLOOR + 20)], fill=70)
            cone = np.asarray(cone.filter(ImageFilter.GaussianBlur(40)), np.float32) / 255
            base += cone[:, :, None] * np.array([120, 124, 135]) * (0.4 + 0.6 * (yy / H))[:, :, None]
            base += 90 * np.exp(-(((xx - cx) / (220 * HALF / 150)) ** 2 + ((yy - FLOOR) / 34) ** 2))[:, :, None] * np.array([0.75, 0.77, 0.82])
    else:
        for cx in XS:
            base += 70 * np.exp(-(((xx - cx) / 240) ** 2 + ((yy - FLOOR) / 60) ** 2))[:, :, None] * np.array([210, 220, 200]) / 255
            base += 18 * np.exp(-(((xx - cx) / 200) ** 2 + ((yy - 900) / 600) ** 2))[:, :, None]
    base = Image.fromarray(base.clip(0, 255).astype(np.uint8))
    shot = Image.open(os.path.join(ROOT, sp["shot"])).convert("RGB")
    if sp.get("crop"):
        c = sp["crop"]; shot = shot.crop((int(c[0] * shot.width), int(c[1] * shot.height), int(c[2] * shot.width), int(c[3] * shot.height)))
    shot.thumbnail((760, 1000), Image.LANCZOS)
    m = Image.new("L", shot.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0) + shot.size, 40, fill=255)
    out = os.path.join(set_dir, sp["out"]); os.makedirs(os.path.join(set_dir, "preview"), exist_ok=True)
    pr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], stdin=subprocess.PIPE)
    GA, GB = (150, 156, 166), (88, 92, 100)
    THREE_D = sp.get("render") == "3d" and STAGE
    def side_state(t, S_):
        race = max(0.0, min(1.0, (t - T_RACE0) / (T_RACE1 - T_RACE0)))
        wk_f = race * weeks; day = int((wk_f % 1) * sp.get("days_shown", 7)) if t < T_RACE1 else -1
        is_off = t < T_RACE1 and (int(wk_f) + 1) in S_.get("off_weeks", [])
        lifting = ((sp.get("always_move") and t < T_RES) or day in S_["days"]) and not is_off
        lo, hi = S_.get("range", [0.0, 1.0])
        p = lo + (hi - lo) * ease(0.5 - 0.5 * math.cos(((t * 2.2) % 1.0) * 2 * math.pi)) if lifting else motions.IDLE[MOT]
        lit = (S_.get("win") or sp.get("tie")) and t >= T_RES
        return round(p * 16) / 16, (1 if lit else 0)
    if THREE_D:
        import subprocess as _sp, json as _js
        keys = {}
        for fi in range(int(T_APP * FPS)):
            k = tuple(side_state(fi / FPS, S_) for S_ in SIDES); keys.setdefault(k, len(keys))
        cache = os.path.join(set_dir, "3d", MOT); os.makedirs(cache, exist_ok=True)
        job = os.path.join(cache, "job.json"); _js.dump({"sides": SIDES, "motion": MOT, "keys": [list(map(list, k)) for k in keys]}, open(job, "w"))
        _sp.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "mannequin3d.py"), job], check=True,
                stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)
        cone = np.zeros((H, W, 3), np.float32)
        for cx in XS:
            c_ = Image.new("L", (W, H), 0); ImageDraw.Draw(c_).polygon([(cx - 30, 330), (cx + 30, 330), (cx + 200 * HALF / 150, FLOOR), (cx - 200 * HALF / 150, FLOOR)], fill=38)
            cone += np.asarray(c_.filter(ImageFilter.GaussianBlur(45)), np.float32)[:, :, None] * np.array([0.8, 0.82, 0.9])
        def base3d(t):
            k = tuple(side_state(t, S_) for S_ in SIDES)
            im = Image.open(os.path.join(cache, f"f{keys[k]:05d}.png")).convert("RGB").resize((W, H), Image.LANCZOS)
            return Image.fromarray((np.asarray(im, np.float32) + cone).clip(0, 255).astype(np.uint8))
    for fi in range(int(DUR * FPS)):
        t = fi / FPS
        img = base3d(t) if (THREE_D and t < T_APP) else base.copy(); d = ImageDraw.Draw(img)
        if t < T_APP:
            race = max(0.0, min(1.0, (t - T_RACE0) / (T_RACE1 - T_RACE0)))
            wk_f = race * weeks; day = int((wk_f % 1) * sp.get("days_shown", 7)) if t < T_RACE1 else -1
            scene = Image.new("RGB", (W, H)); sd = ImageDraw.Draw(scene); glow = Image.new("L", (W, H)); gd = ImageDraw.Draw(glow)
            for x, S_ in zip(XS, SIDES):
                win = bool(S_.get("win")); offw = S_.get("off_weeks", []); sc = tuple(S_["color"])
                is_off = t < T_RACE1 and (int(wk_f) + 1) in offw
                lifting = (sp.get("always_move") and t < T_RES) or (day in S_["days"]) and not is_off
                lifting = lifting and not is_off
                ph = (t * 2.2) % 1.0
                lo, hi = S_.get("range", [0.0, 1.0])
                p = lo + (hi - lo) * ease(0.5 - 0.5 * math.cos(ph * 2 * math.pi)) if lifting else motions.IDLE[MOT]
                lit = (win or sp.get("tie")) and t >= T_RES
                if THREE_D:
                    pts = {}
                elif STAGE:
                    pts = motions.draw(sd, MOT, x, FLOOR, p, (238, 232, 220), (150, 144, 134), sc) or {}
                    fo = S_.get("focus")
                    if fo and fo in pts and t < T_CATCH:          # "FOCUS" corner brackets on the hand or the muscle
                        fx, fy = pts[fo]; r = 58
                        for cx_, cy_ in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                            px_, py_ = fx + cx_ * r, fy + cy_ * r
                            sd.line([(px_, py_), (px_ - cx_ * 22, py_)], fill=sc, width=5); sd.line([(px_, py_), (px_, py_ - cy_ * 22)], fill=sc, width=5)
                        sd.text((fx - 34, fy + r + 8), "FOCUS", font=ImageFont.truetype(INTER, 24), fill=sc)
                else:
                    hy = st.figure(sd, x, p, col=(226, 255, 120) if lit else GA, shade=GB); st.barbell(sd, x, hy, 2, LIME)
                if lit and not THREE_D:
                    if STAGE: motions.draw(gd, MOT, x, FLOOR, p, 255, 255, None)
                    else: st.figure(gd, x, p, col=255, shade=255)
                bw = 52 if N == 2 else 40
                for k in range(7):
                    bx = x - 3 * bw + k * bw - (20 if N == 2 else 15)
                    on = k in S_["days"]; now = (k == day)
                    sd.rounded_rectangle([bx, FLOOR + 40, bx + bw - 12, FLOOR + 80], 8, outline=(90, 94, 100), width=3,
                                         fill=((sc if STAGE else LIME) if (on and now) else ((70, 80, 40) if on else None)))
                frac = min(race, 1.0) * S_["result"] / MAXR
                if offw: frac = growth(offw, weeks, min(race, 1.0) * weeks) * S_["result"] / MAXR
                if N == 2 and not win and sp.get("catch_closes", True) and t >= T_CATCH + 2.0:
                    frac += (1.0 - frac) * 0.85 * ease((t - T_CATCH - 2.0) / 0.8)
                sd.rectangle([x - HALF, FLOOR + 120, x + HALF, FLOOR + 150], outline=(90, 94, 100), width=3)
                sd.rectangle([x - HALF + 4, FLOOR + 124, x - HALF + 4 + (2 * HALF - 8) * frac, FLOOR + 146], fill=sc if STAGE else (LIME if win else (170, 176, 186)))
            top = scene.crop((0, FLOOR - 650, W, FLOOR)).transpose(Image.FLIP_TOP_BOTTOM)
            refl = Image.blend(Image.new("RGB", top.size), top, 0.0 if STAGE else 0.18)
            img.paste(Image.composite(scene, img, scene.convert("L").point(lambda v: 255 if v > 4 else 0)), (0, 0))
            sub = img.crop((0, FLOOR, W, FLOOR + 650)); mask = refl.convert("L").point(lambda v: 255 if v > 3 else 0)
            img.paste(Image.composite(refl, sub, mask), (0, FLOOR))
            img.paste(scene.crop((0, FLOOR + 30, W, FLOOR + 160)), (0, FLOOR + 30), scene.crop((0, FLOOR + 30, W, FLOOR + 160)).convert("L").point(lambda v: 255 if v > 4 else 0))
            if t >= T_RES:
                g = glow.filter(ImageFilter.GaussianBlur(26))
                arr = np.asarray(img).astype(np.float32) + np.asarray(g, np.float32)[:, :, None] / 255 * np.array(WINC if STAGE else LIME) * 0.5
                img = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
            d = ImageDraw.Draw(img)
            mw = 440 if N == 2 else 320
            if not (T_CATCH <= t < T_APP):
                for x, S_ in zip(XS, SIDES):
                    lab = S_["title"]
                    if STAGE:
                        ct(d, lab.capitalize() if lab.isupper() else lab, 455, 58 if N == 2 else 46, tuple(S_["color"]), x=x, maxw=mw, path=INTER)
                        if S_.get("sub"): ct(d, S_["sub"], 522, 32 if N == 2 else 26, (190, 192, 200), x=x, maxw=mw, path=INTER)
                    else:
                        ct(d, lab, 540, 54, LIME if S_.get("win") else (225, 225, 230), x=x, maxw=mw)
            if t < T_RACE1:
                for x, S_ in zip(XS, SIDES):
                    if (int(race * weeks) + 1) in S_.get("off_weeks", []): ct(d, "WEEKS OFF", FLOOR + 175, 40, (255, 170, 90), x=x, maxw=400, path=INTER)
            if t < T_RACE1:
                a = ease(t / 0.3)
                if STAGE:
                    parts = []
                    for i, S_ in enumerate([] if sp.get("title_parts") else SIDES):
                        if i: parts.append((" vs ", (245, 245, 245)))
                        parts.append((S_["head"], tuple(S_["color"])))
                    if sp.get("title_parts"): parts = [(t_, tuple(c_)) for t_, c_ in sp["title_parts"]]
                    else: parts.append((".", (245, 245, 245)))
                    full = "".join(t_ for t_, _ in parts)
                    f = fit(d, full, 96, W - 100, INTER); tx = (W - d.textlength(full, font=f)) / 2
                    for t_, c_ in parts:
                        d.text((tx, 190), t_, font=f, fill=tuple(int(v * a) for v in c_)); tx += d.textlength(t_, font=f)
                else:
                    ct(d, " vs ".join(S_["title"] for S_ in SIDES) + ".", 190, 96, (int(245 * a),) * 3)
                ct(d, sp["question"], 320, 50, (int(170 * a), int(175 * a), int(185 * a)), path=INTER)
                if t >= T_RACE0: ct(d, sp["day_labels"][max(day, 0)] if sp.get("day_labels") else f"WEEK {min(weeks, 1 + int(wk_f))}", 390, 44, LIME, path=INTER if sp.get("day_labels") else ANTON)
            elif t < T_CATCH:
                a = ease((t - T_RES) / 0.3)
                ct(d, sp["result_head"], 190, 96, tuple(int(v * a) for v in (WINC if STAGE else LIME)), path=INTER if STAGE else ANTON)
                ct(d, sp["result_note"], 320, 44, (int(220 * a),) * 3, path=INTER)
                for x, S_ in zip(XS, SIDES):
                    ct(d, S_["label"], FLOOR + 175, 40 if N == 2 else 34, tuple(S_["color"]) if S_.get("win") else (200, 200, 205), x=x, maxw=mw - 40, path=INTER)
                ct(d, sp["cite"], 1830, 30, (150, 150, 158), path=INTER)
            else:
                a = ease((t - T_CATCH) / 0.3)
                ct(d, "Here's the catch." if STAGE else "HERE'S THE CATCH", 170, 92, tuple(int(v * a) for v in (WINC if STAGE else LIME)), path=INTER if STAGE else ANTON)
                step = max(0.6, (sp.get("catch_t", 4.0) - 1.0) / max(1, len(sp["catch_lines"])))
                for i, ln in enumerate(sp["catch_lines"]):
                    aa = ease((t - T_CATCH - 0.4 - i * step) / 0.3)
                    ct(d, ln, 290 + i * 66, 46, (int(235 * aa),) * 3, path=INTER)
                ct(d, sp["catch_cite"], 1830, 30, (150, 150, 158), path=INTER)
        else:
            a = ease((t - T_APP) / 0.3)
            ct(d, sp["tie_in"][0], 150, 84, tuple(int(v * a) for v in LIME), path=INTER if STAGE else ANTON)
            ct(d, sp["tie_in"][1], 260, 46, (int(230 * a),) * 3, path=INTER)
            img.paste(shot, ((W - shot.width) // 2, 360), m)
            for i, ln in enumerate(sp["endcard"]):
                ct(d, ln, 360 + shot.height + 50 + i * 70, 50, LIME if i == 0 else (235, 235, 240), path=INTER)
        pr.stdin.write(img.convert("RGB").tobytes())
        if fi in [int(s * FPS) for s in (0.8, (T_RACE0 + T_RACE1) / 2, T_RES + 1.0, T_CATCH + 2.0, T_APP + 1.5)]:
            img.resize((540, 960)).save(os.path.join(set_dir, "preview", f"f{fi:04d}.jpg"), quality=88)
    pr.stdin.close(); pr.wait(); print("DONE", out, round(DUR, 1), "s")


if __name__ == "__main__":
    render(sys.argv[1])
