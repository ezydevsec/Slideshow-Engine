# In-app exercise tutorials (founder, 2026-11-20; v2 style 2026-11-22)

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

## v2 — realistic 3D (founder 2026-11-22: "pilot was bad, fully realistic 3D exactly like our mascot")

- **Look:** photorealistic CGI of the posts' mascot (`01-app/brand/mascot-final-matte-reference.jpg`): faceless smooth head, dark graphite #3E444C matte skin, detailed real muscle anatomy, black shorts, barefoot, target muscle lime #C6FF00 with fibre striations. Real modern commercial gym at night behind him, softly out of focus. 1:1, 1080×1080, silent loop + poster.
- **Pipeline:** Nano Banana Pro start frame (refs: matte mascot + the exercise's 2D pose from `01-app/brand/poses/`) → end frame from the start frame ("exactly the same image, only the pose changes") → Kling 3.0 pro start→end (3 s) → **vidstab tripod stabilisation** (Kling drifts the camera mid-move) → `tutorial_loop.py --pingpong`.
- **Lessons:** render hard lifts (RDL) from the 2D pose first, then derive the other end frame from it; rear/three-quarter views lose depth and bar position. Check that lime sits on the right muscle (first RDL coloured the quads).

| Exercise | File | Status |
|---|---|---|
| Machine chest press | `v2/out/machine-chest-press.mp4` | for review (lime also covers the front delts) |
| Lat pulldown (three-quarter rear view) | `v2/out/lat-pulldown.mp4` | for review |
| Romanian deadlift | `v2/out/romanian-deadlift.mp4` | for review |

### v2 batch 1 (2026-11-22)

Style ref for frames: the machine-free RDL frame (a chest press ref made the model paste the machine into other exercises). Pose-change edits often fail in Nano Banana, so most of these use a free 5 s one-rep Kling clip from the start frame (full loop), stabilised.

| Exercise | File | Method | Status |
|---|---|---|---|
| Lateral raise | `v2/out/lateral-raise.mp4` | start→end, ping-pong | for review |
| Seated leg curl | `v2/out/seated-leg-curl.mp4` | free rep 5 s | for review |
| Chest-supported row | `v2/out/chest-supported-row.mp4` | free rep 5 s | for review |
| Leg extension | `v2/out/leg-extension.mp4` | free rep 5 s | for review |
| Preacher curl | `v2/out/preacher-curl.mp4` | free rep 5 s | for review (3rd frame: first two put lime on the triceps) |
| Poliquin (seated) pushdown | `v2/out/poliquin-pushdown.mp4` | free rep 5 s, 2nd try | for review (1st clip pushed the bar forward and moved the lime to the biceps) |

### v2 batch 2 (2026-11-22)

Free 5 s one-rep Kling clips from each start frame, vidstab, full loop, unless noted.

| Exercise | File | Status |
|---|---|---|
| Hip adductor | `v2/out/hip-adductor.mp4` | for review (2nd frame: 1st coloured the quads) |
| Bayesian cable curl | `v2/out/bayesian-curl.mp4` | for review (2nd frame: 1st started mid-curl; lime reaches the forearm) |
| Hack squat | `v2/out/hack-squat.mp4` | for review |
| Hammer curl | `v2/out/hammer-curl.mp4` | for review |
| Hip thrust | `v2/out/hip-thrust.mp4` | for review |
| Seated overhead triceps extension | `v2/out/overhead-triceps-extension.mp4` | for review |
| Pec deck | `v2/out/pec-deck.mp4` | for review |
| Cable pullover | `v2/out/cable-pullover.mp4` | for review |
| Machine shoulder press | `v2/out/machine-shoulder-press.mp4` | for review |
| Dumbbell shrug | `v2/out/dumbbell-shrug.mp4` | start→end, ping-pong (two free clips turned it into a lateral raise) |
| Y-raise | `v2/out/y-raise.mp4` | for review |
| Single-leg extension | `v2/out/single-leg-extension.mp4` | for review (only the near leg moves) |
| Single-leg curl | `v2/out/single-leg-curl.mp4` | for review: hard to see that only one leg works; may need a redo |
| Calf press | — | **open**: the model keeps putting the heels on the plate (the clip bent the knees instead of the ankles). A seated calf raise frame works (`frames/calf-a4.png`); founder to choose |
