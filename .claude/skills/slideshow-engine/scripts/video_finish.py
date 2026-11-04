#!/usr/bin/env python3
"""Finish a short-form video: visuals timed to a voiceover, word-by-word captions,
labels, music bed and simple synthesized sound effects.

  python3 video_finish.py <video.json>            # build
  python3 video_finish.py <video.json> --words    # print the voice's word timings, then exit

video.json (paths relative to the json's folder unless absolute):
{
  "out": "final.mp4",
  "voice": "voice.mp3", "music": "music.mp3", "music_vol": 0.14, "voice_delay": 0.0,
  "layout": "full" | "meme",            # meme = white caption band on top + 3:4 clip below
  "band_text": ["line 1", "line 2"],    # meme layout only
  "segments": [ {"src": "clip.mp4" | "card.png", "start": 0.0, "end": 4.2, "focus_y": 0.5} ],
  "labels":   [ {"text": "WRONG", "start": 1.0, "end": 4.2, "color": "#FF4444", "size": 110, "y": 1560, "font": "anton"} ],
  "captions": {"on": true, "y": 1180, "size": 84, "words_per": 1, "color": "#FFFFFF", "hl": "#C6FF00", "hl_words": ["earnd"]},
  "sfx": [ {"type": "whoosh"|"pop"|"thud", "t": 4.2, "vol": 0.35} ]
}
Times are in seconds on the final timeline. The voice starts at voice_delay.
"""
import json, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = {"anton": os.path.join(HERE, "..", "assets", "fonts", "Anton-Regular.ttf"),
         "inter": "/usr/share/fonts/opentype/inter/Inter-Black.otf"}
if not os.path.exists(FONTS["inter"]): FONTS["inter"] = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def dur(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout.strip())


def words(voice):
    from faster_whisper import WhisperModel
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", voice, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    segs, _ = WhisperModel("base", compute_type="int8").transcribe(a, language="en", word_timestamps=True)
    return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]


def png_text(path, text, font, size, color, stroke=0, shadow=True):
    f = ImageFont.truetype(FONTS[font], size)
    im = Image.new("RGBA", (W, int(size * 1.6)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    tw = d.textlength(text, font=f); x = (W - tw) / 2
    if shadow:
        for dx, dy in ((0, 6), (3, 6), (-3, 6)):
            d.text((x + dx, 10 + dy), text, font=f, fill=(0, 0, 0, 170))
    d.text((x, 10), text, font=f, fill=color, stroke_width=stroke, stroke_fill="black")
    im.save(path)


def segment_clip(seg, base, tmp, i, layout):
    src = seg["src"] if os.path.isabs(seg["src"]) else os.path.join(base, seg["src"])
    d = seg["end"] - seg["start"]; out = os.path.join(tmp, f"seg{i:02d}.mp4"); layout = seg.get("layout", layout)
    if layout == "meme":
        vf = f"scale=1080:1446,pad=1080:1920:0:440:white"
    else:
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    if src.lower().endswith((".png", ".jpg", ".jpeg")):
        run(["ffmpeg", "-y", "-loop", "1", "-t", f"{d:.3f}", "-i", src, "-vf", vf + ",format=yuv420p", "-r", str(FPS),
             "-c:v", "libx264", "-an", out])
    else:
        sp = seg.get("speed", 1.0)  # <1 = slow motion (e.g. 0.7 stretches a 5 s clip to ~7.1 s)
        pre = f"setpts=PTS/{sp}," if sp != 1.0 else ""
        loop = [] if seg.get("hold") else ["-stream_loop", "-1"]
        post = f",tpad=stop_mode=clone:stop_duration={d:.3f}" if seg.get("hold") else ""
        run(["ffmpeg", "-y"] + loop + ["-ss", str(seg.get("ss", 0)), "-i", src, "-vf",
             pre + vf + post + ",format=yuv420p", "-t", f"{d:.3f}", "-r", str(FPS), "-c:v", "libx264", "-an", out])
    return out


def sfx(kind, path):
    if kind == "whoosh":
        f = "anoisesrc=d=0.45:c=pink:a=0.6,bandpass=f=1800:w=1400,afade=t=in:d=0.18,afade=t=out:st=0.2:d=0.25"
    elif kind == "pop":
        f = "sine=f=880:d=0.12,afade=t=out:st=0.01:d=0.11"
    else:  # thud
        f = "sine=f=70:d=0.35,afade=t=out:st=0.02:d=0.33"
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", f, "-ar", "44100", "-ac", "2", path])


def main(spec_path, show_words=False):
    base = os.path.dirname(os.path.abspath(spec_path)); s = json.load(open(spec_path))
    P = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    voice = P(s["voice"]); wd = words(voice); vdel = s.get("voice_delay", 0.0)
    if show_words:
        for i, (t, a, b) in enumerate(wd): print(f"{i:3d} {a+vdel:6.2f}-{b+vdel:6.2f} {t}")
        print("voice duration", dur(voice)); return
    tmp = tempfile.mkdtemp(prefix="vf_")
    layout = s.get("layout", "full")
    segs = [segment_clip(g, base, tmp, i, layout) for i, g in enumerate(s["segments"])]
    total = s["segments"][-1]["end"]
    with open(os.path.join(tmp, "list.txt"), "w") as f:
        for p in segs: f.write(f"file '{p}'\n")
    vid = os.path.join(tmp, "visual.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "list.txt"), "-c", "copy", vid])

    # overlay pngs: meme band, labels, captions
    ovs = []  # (png, start, end, y)
    if layout == "meme" and s.get("band_text"):
        band = Image.new("RGBA", (W, 440), "white"); d = ImageDraw.Draw(band)
        f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 62)
        for i, t in enumerate(s["band_text"]):
            tw = d.textlength(t, font=f); d.text(((W - tw) / 2, 70 + i * 86), t, font=f, fill="black")
        bp = os.path.join(tmp, "band.png"); band.save(bp); ovs.append((bp, 0, s.get("band_end", total), 0))
    for i, l in enumerate(s.get("labels", [])):
        p = os.path.join(tmp, f"lab{i}.png")
        png_text(p, l["text"], l.get("font", "anton"), l.get("size", 110), l.get("color", "#FFFFFF"), l.get("stroke", 0))
        ovs.append((p, l["start"], l["end"], l.get("y", 1560)))
    c = s.get("captions", {"on": True})
    if c.get("on", True):
        n = c.get("words_per", 1); hl = [h.lower() for h in c.get("hl_words", ["earnd"])]
        chunks = [wd[i:i + n] for i in range(0, len(wd), n)]
        for i, ch in enumerate(chunks):
            text = " ".join(t for t, _, _ in ch).strip(" .,!?…").upper()
            for a_, b_ in c.get("fix", {"EARNED": "EARND", "EARN": "EARND"}).items():
                text = " ".join(b_ if w_ == a_ else w_ for w_ in text.split())
            if not text: continue
            st = ch[0][1] + vdel
            if st >= c.get("until", 1e9): continue
            en = (chunks[i + 1][0][1] + vdel) if i + 1 < len(chunks) else ch[-1][2] + vdel + 0.3
            en = min(en, st + 1.2)
            col = c.get("hl", "#C6FF00") if any(h in text.lower() for h in hl) else c.get("color", "#FFFFFF")
            p = os.path.join(tmp, f"cap{i:03d}.png"); png_text(p, text, "inter", c.get("size", 84), col, c.get("stroke", 0))
            ovs.append((p, st, en, c.get("y", 1180)))
    cmd = ["ffmpeg", "-y", "-i", vid]
    for p, _, _, _ in ovs: cmd += ["-i", p]
    fc, last = [], "[0:v]"
    for k, (p, a, b, y) in enumerate(ovs):
        fc.append(f"{last}[{k+1}:v]overlay=0:{y}:enable='between(t,{a:.3f},{b:.3f})'[v{k}]"); last = f"[v{k}]"
    vout = os.path.join(tmp, "video_ov.mp4")
    cmd += ["-filter_complex", ";".join(fc) if fc else "null", "-map", last if fc else "0:v", "-c:v", "libx264",
            "-pix_fmt", "yuv420p", "-r", str(FPS), vout]
    run(cmd)

    # audio: voice (delayed) + music bed + sfx
    ain = ["-i", voice]; parts = [f"[0:a]adelay={int(vdel*1000)}|{int(vdel*1000)},loudnorm=I=-15:TP=-1.5,apad[vo]"]; mixn = ["[vo]"]
    k = 1
    if s.get("music"):
        ain += ["-i", P(s["music"])]
        parts.append(f"[{k}:a]volume={s.get('music_vol', 0.14)},afade=t=in:d=0.4,afade=t=out:st={max(0,total-1.2):.2f}:d=1.2[mu]")
        mixn.append("[mu]"); k += 1
    for j, e in enumerate(s.get("sfx", [])):
        sp = os.path.join(tmp, f"sfx{j}.wav"); sfx(e["type"], sp); ain += ["-i", sp]
        ms = int(e["t"] * 1000); parts.append(f"[{k}:a]volume={e.get('vol', 0.35)},adelay={ms}|{ms}[s{j}]")
        mixn.append(f"[s{j}]"); k += 1
    parts.append("".join(mixn) + f"amix=inputs={len(mixn)}:normalize=0:duration=longest,atrim=0:{total:.3f},alimiter=limit=0.89:level=false[a]")
    out = P(s["out"])
    # audio input indexes shift by one because the video is input 0
    import re
    parts2 = [re.sub(r"\[(\d+):a\]", lambda m: f"[{int(m.group(1))+1}:a]", p) for p in parts]
    run(["ffmpeg", "-y", "-i", vout] + ain + ["-filter_complex", ";".join(parts2), "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", "-movflags", "+faststart", out])
    print("DONE", out, f"{dur(out):.2f}s")


if __name__ == "__main__":
    main(sys.argv[1], "--words" in sys.argv)
