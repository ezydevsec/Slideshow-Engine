# Reel: "missing one of these three things"

- **Account:** @earndapp (brand). Phase: prelaunch.
- **Format:** vertical talking-head / voiceover reel, about 49 s. Not a slideshow.
- **Reference:** https://www.tiktok.com/@h.a.m.e.e.d.k.h.a.n1/video/7688714096295906591 ("How To Force Your Skinny Arms To Grow", 4.8M plays, 423K likes, 217K saves, 101 s; stats read 2026-11-04)
- **Status:** draft script. Not approved, not filmed, not queued.
- **Checker:** `score.py` 100/100, 0 hard fails, 196 words.

## Why the reference worked (breakdown)

| Time | Line (reference) | Part |
|---|---|---|
| 0:00–0:09 | "If you're like me and you've struggled with skinny arms your entire life… then this is what you need to do." | Hook + stakes (a named pain, insult as the villain) |
| 0:09–0:19 | "Three parts, width, height and depth. Train all three properly and…" | Promise (a 3-part map, an open loop) |
| 0:19–0:25 | (no speech: demo footage) | Visual re-hook |
| 0:25–0:50 | "If your arms look okay from the side but small the moment you turn around… It's the brachialis." | Beat 1 + reveal (named muscle) |
| 0:50–1:15 | Hammer curls: grip, curl, squeeze, lower slowly | Beat 1: the how-to |
| 1:15–1:37 | "When I say slowly, I mean it… three sets of 12… if they're not burning, you're not pushing hard enough." | Specific numbers + a self-check |

**Hook template:** "If you [specific pain, in their words], then this is what you need to do. [N] parts: [A], [B], [C]."
**Re-hooks:** the 3-part list (0:09), a silent demo (0:19), a named muscle (0:39), the grip change (0:57), "when I say slowly, I mean it" (1:15), the 3×12 numbers (1:22). Gaps are about 6–10 s.

**What we take:** the "if you… [N] parts" hook, the numbered map that opens a loop, concrete cues and numbers, and the self-check at the end of each part.
**What we drop:** the physique promise ("no choice but to grow"), first-person "like me" (brand voice has no first-person user claims), the topic, and the wording.

## Script (spoken, ~4 words/s)

| Time | Line | On screen |
|---|---|---|
| 0:00 | If you've lifted the same weights for months, you're probably missing one of these three things. | Text: "same weights for months?" Hands loading the same plates (real footage) |
| 0:04 | What you lifted last time, one target for today, and a log of every set. | 1 / 2 / 3 list builds |
| 0:08 | A lot of people remember the exercises but walk in and guess the weight. | Gym floor, someone hesitating at the rack |
| 0:11 | First, last session. Before your first set, check exactly what you did. | "1. last session". Real screenshot `exercise-target.png`, zoom on "Previous: 100 kg × 7, 100 kg × 6" |
| 0:14 | The weight and the reps for every set, so you're not guessing. | Same crop, slow push-in |
| 0:17 | Second, pick one target and only one. | "2. one target" |
| 0:19 | For example, if last time was a hundred kilos for seven, today's target is a hundred for eight. | Text: "example: 100 kg × 7 → 100 kg × 8". Crop on "Beat 100 kg × 7, Target 8 reps" |
| 0:23 | Same weight, one more rep, and lower it at the same speed as last time so it's a fair comparison. | Real lifting footage, slow lowering |
| 0:28 | Third, log the set before you rest, because if you leave it till later you'll forget it. | "3. log every set" |
| 0:33 | But scrolling a notes app between sets gets old fast. | A crowded notes-app page (filmed prop, not the EARND UI) |
| 0:35 | So EARND puts your last session and today's target on one screen, for all four sessions in your week. | Full `exercise-target.png`, then `train-week-overview.png` ("3 of 4 sessions this week") |
| 0:40 | Enter your reps, tick the set, and the rest timer starts by itself. | `exercise-target.png` crop: Set 1 ticked, "Resting · 1:47" |
| 0:43 | The progress screen shows your best set over time, so you can see when you've improved. | `progress-chest-press.png`, best-set chart |
| 0:47 | EARND launches soon. Follow for the launch. | Lime text on black (account template), end on the last word |

## Alternate hooks
1. If you can't remember what you lifted last session, this is the fix, and it takes three steps.
2. You know your exercises. But do you know what weight to use today?

## Caption
If you've lifted the same weights for months, you're probably missing one of these three things.
EARND launches soon. Follow for the launch.
#gym #progressiveoverload #workouttracker #gymtok #upperlower

## Facts sheet
| Fact in script | Source |
|---|---|
| Last session and today's target on one screen | `01-app/app-brief.md` → Magic moment; `01-app/assets/exercise-target.png` |
| Example 100 kg × 7 → 100 kg × 8 (labelled "example") | `exercise-target.png` ("Beat 100 kg × 7, Target 8 reps"); CLAUDE.md example rule |
| Tick the set and the rest timer starts by itself | app-brief.md ("Completing a set automatically starts the rest timer"); screenshot shows "Resting · 1:47" |
| Four sessions in your week | app-brief.md (four-day Upper/Lower); `train-week-overview.png` ("3 of 4 sessions this week") |
| Progress screen shows best set over time | `progress-chest-press.png` |
| "lower it at the same speed… fair comparison" | General training advice, not an EARND claim |
| CTA | `06-queue/accounts.json` → @earndapp `cta.prelaunch` |

Not claimed: pre-filled weights (not verified), how EARND decides when to add weight, physique change, a free trial, or a download link.

## Rule checks
- No physique promise. The payoff is "see when you've improved".
- No invented UI. Every app shot is a real screenshot from `01-app/assets/`, cropped only.
- No first-person user claims, testimonials or invented results.
- Numerical example labelled on screen.
- Prelaunch CTA verbatim, no download CTA.
- Note: the spoken product mention comes at 0:35. The app screenshot is on screen from 0:11, to stay close to the "app by slide 3–4" default.

## Rewrite log
1. Wrote 3 drafts (A "missing three things", B "what did you bench last Tuesday", C "can't remember, three steps"). All scored 95: each had a 33–48 word stretch with no re-hook.
2. Picked A. Its hook is closest to the reference shape and it avoids B's unsourced "most lifters can't tell you" and B's "you don't need X, you need Y" line.
3. Fixed the app-section sag by adding "all four sessions in your week" (a real number). Replaced "lower it slowly so the rep counts" with a concrete, true cue. Softened "most people" to "a lot of people". Tightened lines 12–13. Final score 100/100.

## Open before filming
- Who's on camera or doing the voiceover for @earndapp?
- Real gym and notes-app footage needs filming. Don't use generated B-roll that looks like real people or the EARND UI.
- Chat approval of this script before anything is queued.
