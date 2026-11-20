# In-app exercise tutorials (founder, 2026-11-20)

One silent looping video per programme exercise, starring the EARND mascot (graphite mannequin, target muscle in lime), 3D via Higgsfield.

- Format (pilot defaults, founder "go pilot"): 1:1, 1080×1080, side view, dark charcoal studio, H.264 MP4, no audio, plus a poster JPG (first frame).
- One slow rep per loop. Form cues live in the app as text, never in the video.
- Pipeline: Nano Banana start frame (mascot + pose refs from `01-app/brand/poses/`) → Nano Banana end frame (same scene, bottom of the rep) → Kling 3.0 pro start→end clip → `tutorial_loop.py --pingpong` (forward + hold + reverse + hold), so every loop starts and ends on the same frame. Free one-rep generations go wrong on hinges (the first RDL came out as a squat); start+end frames fix the form.
- Every clip is signed off by the founder before it ships in the app.

## Pilot (2026-11-20)

| Exercise | File | Method | Status |
|---|---|---|---|
| Machine chest press | `pilot/out/machine-chest-press.mp4` | free rep, 5 s | for review |
| Lat pulldown | `pilot/out/lat-pulldown.mp4` | start→end, ping-pong, 6.9 s | for review: camera drifts slightly (end frame's angle differed) |
| Romanian deadlift | `pilot/out/romanian-deadlift.mp4` | start→end, ping-pong, 6.9 s | for review |
