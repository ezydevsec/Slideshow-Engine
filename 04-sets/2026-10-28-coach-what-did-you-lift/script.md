# Test video: "what did you lift?" (the Coach)

- **Status:** DRAFT. Awaiting founder approval of the script. Nothing generated yet.
- **Account:** @earndapp (brand)
- **Format:** narrated video, anime coach explainer (`02-research/formats/anime-coach-explainer.md`). This is a short test of the look and voice before any full explainer.
- **Character:** the Coach, "Baki energy" version (spec below)
- **Voice:** Higgsfield preset **Vlad** (`e5666b9c-99a2-4fac-8b4e-abee078b186d`), slow, with long pauses
- **Angle / pain:** #1 "i can't remember what i lifted last time" → previous performance next to today's target
- **Persona:** Persona 1: The inconsistent tracker
- **Length:** about 30 s, 7 beats, about 55 spoken words
- **App moment:** beat 6 (of 7), real screenshot `01-app/assets/exercise-target.png`, crop and zoom only

## Character spec: the Coach (Baki energy)

Original character. Not Baki: no red hair, no Baki face, no Baki clothing, no scar pattern copied from the anime.

- Late 40s, enormous and grotesquely defined: veins, cords of muscle, neck as wide as his head. Exaggerated proportions are fine (it's a style).
- Shaved head, short grey beard, heavy brow, eyes in shadow, a menacing stillness.
- An old black tracksuit jacket, sleeves pushed up, worn open. Taped knuckles.
- Prop: a battered training notebook with **lime #C6FF00 page tabs**. It's the only colour in the frame.
- Setting: a concrete underground gym, one hard overhead light, chalk dust in the air.
- Style: high-contrast black-and-white manga, hard ink shadows, screentone grain, black background.

## Script

Captions: one word at a time, centred, small white text. Key words in lime. Lowercase.

| # | Time | Visual | Voiceover (Vlad) | On-screen text |
|---|---|---|---|---|
| 1 | 0–4 s | The Coach seated in the dark, the light hitting only his shoulders. Slow push-in. | "Last week... you trained hard." | word-by-word captions |
| 2 | 4–8 s | Extreme close-up: his eyes open. | "So tell me." *(pause)* "What did you lift?" | "what did you **lift?**" |
| 3 | 8–11 s | Cut to black. Silence, then one line. | "...You don't know." | "you don't know." |
| 4 | 11–16 s | He slams the notebook on a bench and chalk dust explodes. | "Then what are you trying to beat today?" | word-by-word captions |
| 5 | 16–21 s | He opens the notebook; lime tabs catch the light. | "The strong don't guess." *(pause)* "They write it down." | word-by-word captions |
| 6 | 21–26 s | **Real screenshot**, slow zoom onto "Previous: 100 kg × 7, 100 kg × 6 / Beat 100 kg × 7 — Target 8 reps". Lime "example" tag in the corner. | "EARND shows your last session..." *(pause)* "...and the number to beat." | "**example**" label (required) |
| 7 | 26–30 s | Back to the Coach, notebook shut, staring at the camera. EARND wordmark fades in. | "EARND launches soon." *(pause)* "Follow for the launch." | "EARND launches soon. Follow for the launch." (lime) |

Spoken words: 54.

**Caption:** "what did you lift last week? exactly."
**Hashtags:** #gymtok #progressiveoverload #gymtips #workouttracker
**TikTok settings:** mark as AI-generated content.

## Rule check

- [x] Original character and voice; no Baki likeness, name, footage, or cloned actor voice
- [x] No physique promise: the payoff is "last session + number to beat"
- [x] No first-person user claims; the Coach speaks to "you" and never claims his own results
- [x] Numbers on screen labelled "example"
- [x] Real screenshot only, crop and zoom, UI untouched; copy matches what it shows (no "pre-filled" claim)
- [x] App enters late (beat 6 of 7). Default is slide 3–4; for a 30 s video, the founder may prefer it earlier (see open questions)
- [x] Prelaunch CTA from accounts.json; no download link, no trial
- [ ] Founder approval of the script
- [ ] Founder approval of the generated Coach look before any video clips

## Production plan (quote before each paid step)

1. Coach reference image (one character still), founder approves the look.
2. Voiceover: the full 54-word script in Vlad's voice (one audio file).
3. Video clips for beats 1, 2, 4, 5, 7 (image-to-video from the approved still, about 4–5 s each).
4. Beats 3 and 6 built locally: black card, plus a zoom on the real screenshot. Captions, timing and assembly in ffmpeg (no credits).

## Open questions

1. App moment: keep it at beat 6 (more Baki tension) or move it to beat 4, closer to the default "slide 3–4" rule?
2. "The strong don't guess." OK as the line before the app moment?
