#!/usr/bin/env python3
"""In-app exercise tutorial loops (founder, 2026-11-20: mascot tutorial video per exercise).

  python3 tutorial_loop.py <clip.mp4> <out_dir> <slug> [--pingpong] [--hold 0.4] [--size 1080]

Default: the clip is one full rep (start -> bottom -> start); it is scaled to size x size, silent.
--pingpong: the clip is only the lowering half (start frame -> end frame); the loop is
  forward + hold + reversed + hold, so the rep starts and ends on the exact same frame.
Writes <out_dir>/<slug>.mp4 (H.264, yuv420p, faststart, no audio) and <slug>-poster.jpg (first frame).
"""
import argparse, os, subprocess

ap = argparse.ArgumentParser()
ap.add_argument("clip"); ap.add_argument("out_dir"); ap.add_argument("slug")
ap.add_argument("--pingpong", action="store_true"); ap.add_argument("--hold", type=float, default=0.4)
ap.add_argument("--size", type=int, default=1080)
a = ap.parse_args()
os.makedirs(a.out_dir, exist_ok=True)
out = os.path.join(a.out_dir, a.slug + ".mp4")
S = a.size
base = f"fps=30,scale={S}:{S}:flags=lanczos,setsar=1"
if a.pingpong:
    h = a.hold
    fc = (f"[0:v]{base},split=2[f][r0];[r0]reverse[r];"
          f"[f]tpad=stop_mode=clone:stop_duration={h}[f2];[r]tpad=stop_mode=clone:stop_duration={h}[r2];"
          f"[f2][r2]concat=n=2:v=1:a=0[v]")
else:
    fc = f"[0:v]{base}[v]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.clip, "-filter_complex", fc, "-map", "[v]", "-an",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", out], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-frames:v", "1", "-q:v", "3",
                os.path.join(a.out_dir, a.slug + "-poster.jpg")], check=True)
d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
                   capture_output=True, text=True).stdout.strip()
print("LOOP", out, d, "s")
