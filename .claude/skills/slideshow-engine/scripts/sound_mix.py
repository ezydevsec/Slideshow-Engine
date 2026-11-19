#!/usr/bin/env python3
"""Bake sound into a finished video: generated music bed (Higgsfield / ElevenLabs Music, instrumental, ours) +
our own synthesized SFX on the story beats + optional narration, mixed to a fixed-length track, then muxed.
Founder 2026-11-19: "there should be some sort of sound for the videos" (reference reels: beat + a hit on every step + swell at the payoff).

  python3 sound_mix.py <set_dir>        # reads <set_dir>/sound.json

sound.json: {"video": "x.mp4", "music": "audio/music.mp3", "music_db": -9, "music_fade": [17.5, 19.0],
             "voice": "voice/narration.wav", "voice_db": 0, "duck_db": -9,     # music drops by duck_db while the voice speaks
             "music_curve": [[0, -6], [11, 0], [12.5, 0]],      # optional volume automation (dB) for the build
             "sfx": [{"t": 1.6, "type": "hit", "db": -4}, ...]}
Sound profiles per format (from the founder's reference links): 02-research/formats/video-sound-profiles.md
SFX types: boom (deep 808-style drop), clank (plate), hit (boom + clank), whoosh, riser (dur), ding, tick, thud.
"""
import json, os, subprocess, sys
import numpy as np

SR = 44100


def env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay)


def boom(d=0.9):
    n = int(SR * d); t = np.arange(n) / SR
    f = 35 + 60 * np.exp(-t / 0.08); ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * env(n, 0.003, 0.35) + 0.25 * np.tanh(3 * np.sin(ph)) * env(n, 0.003, 0.12)
    s[:400] += np.random.randn(400) * np.linspace(0.4, 0, 400)
    return s


def clank(d=0.45):
    n = int(SR * d); t = np.arange(n) / SR; s = np.zeros(n)
    for f, a, dc in ((523, 0.5, 0.18), (1307, 0.35, 0.12), (2213, 0.3, 0.09), (3301, 0.2, 0.06), (4703, 0.12, 0.04)):
        s += a * np.sin(2 * np.pi * f * t + np.random.rand() * 6) * np.exp(-t / dc)
    s[:200] += np.random.randn(200) * 0.6
    return s * env(n, 0.001, 0.5)


def whoosh(d=0.55):
    n = int(SR * d); x = np.random.randn(n); y = np.zeros(n); a = 0.0
    for i in range(n):                                   # sweeping one-pole lowpass
        k = 0.02 + 0.25 * np.sin(np.pi * i / n) ** 2; a += k * (x[i] - a); y[i] = a
    return y * np.sin(np.pi * np.arange(n) / n) ** 2 * 2.2


def riser(d=1.5):
    n = int(SR * d); t = np.arange(n) / SR
    f = 200 * (6 ** (t / d)); s = 0.3 * np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.25 * np.random.randn(n)
    return s * (t / d) ** 2


def ding(d=0.7):
    n = int(SR * d); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1318 * t) + 0.4 * np.sin(2 * np.pi * 2637 * t)) * env(n, 0.002, 0.18) * 0.6


def tick(d=0.08):
    n = int(SR * d); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2400 * t) * env(n, 0.0005, 0.012)


def thud(d=0.3):
    n = int(SR * d); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (60 + 40 * np.exp(-t / 0.03)) * t) * env(n, 0.002, 0.08) + np.random.randn(n) * env(n, 0.001, 0.01) * 0.3


GEN = {"boom": boom, "clank": clank, "whoosh": whoosh, "riser": riser, "ding": ding, "tick": tick, "thud": thud,
       "hit": lambda **k: np.pad(boom(), (0, 0)) + np.pad(clank() * 0.7, (0, len(boom()) - len(clank())))}


def load(path, n):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
    out = np.zeros((n, 2)); out[:min(n, len(a))] = a[:n]; return out


def db(x): return 10 ** (x / 20)


def main(set_dir):
    sp = json.load(open(os.path.join(set_dir, "sound.json")))
    vid = os.path.join(set_dir, sp["video"])
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", vid], capture_output=True, text=True).stdout)
    n = int(dur * SR); mix = np.zeros((n, 2))
    music = load(os.path.join(set_dir, sp["music"]), n) if sp.get("music") else np.zeros((n, 2))
    if sp.get("music"):                                  # level-match every bed: RMS of the non-silent part -> 0.12, then music_db
        lv = np.abs(music).mean(1); act = lv > 0.002
        r = np.sqrt((music[act] ** 2).mean()) if act.any() else 1.0
        music *= 0.12 / max(r, 1e-6) * db(sp.get("music_db", -9) + 9)
    if sp.get("music_curve"):                            # volume automation [[t, dB], ...] (the build every reference has)
        pts = sorted(sp["music_curve"]); ts = np.arange(n) / SR
        g = db(np.interp(ts, [p_[0] for p_ in pts], [p_[1] for p_ in pts])); music *= g[:, None]
    if sp.get("music_fade"):
        a, b = (int(x * SR) for x in sp["music_fade"]); g = np.ones(n); g[a:b] = np.linspace(1, 0, b - a); g[b:] = 0; music *= g[:, None]
    voice = None
    if sp.get("voice"):
        voice = load(os.path.join(set_dir, sp["voice"]), n) * db(sp.get("voice_db", 0))
        lvl = np.abs(voice).mean(1); win = int(0.25 * SR)
        act = np.convolve(lvl > 0.01, np.ones(win) / win, mode="same") > 0.05
        g = np.where(act, db(sp.get("duck_db", -9)), 1.0); k = int(0.15 * SR)
        g = np.convolve(g, np.ones(k) / k, mode="same"); music *= g[:, None]
    mix += music
    np.random.seed(7)
    for e in sp.get("sfx", []):
        s = GEN[e["type"]]() if e["type"] != "riser" else riser(e.get("dur", 1.5))
        s = s / (np.abs(s).max() + 1e-9) * db(e.get("db", -6)); i = int(e["t"] * SR); j = min(n, i + len(s))
        if i < n: mix[i:j] += s[: j - i, None] * np.array([1.0, 1.0])
    if voice is not None: mix += voice
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)               # soft limiter: hits can't push the bed down
    mix *= db(-1) / (np.abs(mix).max() + 1e-9)
    wav = os.path.join(set_dir, "audio", "final-mix.wav"); os.makedirs(os.path.dirname(wav), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", wav], input=mix.astype(np.float32).tobytes(), check=True)
    tmp = vid + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.3f}", tmp], check=True)
    os.replace(tmp, vid); print("SOUND", vid, round(dur, 1), "s")


if __name__ == "__main__":
    main(sys.argv[1])
