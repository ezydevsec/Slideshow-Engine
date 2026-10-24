# Writing mode

Writes one slideshow set per idea. Read `winners.md` and `failure-log.md` first, every time.

## Step 1: Hooks

Write 30 slide 1 hooks for the idea.

- Use pain bank language, not marketing language.
- Write like a real person posting from their phone. Lowercase is fine. Use the persona's voice.
- Hooks about another person beat hooks about yourself or the app ("my landlord said..." beats "this app lets you...").
- Banned words: game-changer, unlock, revolutionary, elevate, seamless, transform your, hack (unless the persona would say it), and anything in `CLAUDE.md` under `banned_words`.

Score each 1-10 against the hooks of the last 20 winners in `winners.md` (if fewer than 20 exist, score against the format file's examples). Keep the top 3. Use the best one, and save the other 2 to the backlog as variations.

## Step 2: The set

Follow the chosen format file slide by slide.

- 5 to 10 slides. One idea per slide. Under 25 words per slide.
- Every slide ends with a reason to swipe.
- App enters on the slide the format says (default 3 or 4), in first person, with a real screenshot from `01-app/assets/`.
- Last slide: one clean CTA, or the payoff if the format puts the CTA in the caption.
- Text threads are written by us. Never use a real person's name, handle, or photo.

## Step 3: Caption and sound

- Caption under 150 characters, written like the persona. Mention the app naturally if the format calls for it.
- 3 to 5 hashtags: 1-2 broad, the rest niche.
- Sound: "trending" by default. If a specific rising song from today's trend file fits the mood, name it.

## Step 4: Save

Write `04-sets/YYYY-MM-DD-slug/slides.json`:

```json
{
  "set_id": "2026-10-15-jealous-ranking",
  "idea": "backlog line or winner variation",
  "format": "ranking-thread",
  "trend": "celebrity reunion",
  "hook_id": "H07",
  "persona": "Persona 1",
  "caption": "astra really said what my friends wouldn't",
  "hashtags": ["#astrology", "#zodiac", "#relationships"],
  "sound": {"mode": "trending", "note": ""},
  "ai_images": true,
  "app_slide": 4,
  "slides": [
    {"n": 1, "role": "hook", "image": "images/slide-01.jpg",
     "image_direction": "soft pastel gradient, no photo",
     "text": "most to least likely to act jealous in a relationship:",
     "text_mode": "stroke", "position": "upper"},
    {"n": 4, "role": "middle", "image": "01-app/assets/ask-anything-answer.png",
     "image_direction": "REAL SCREENSHOT",
     "text": "had to check w astra", "text_mode": "background", "position": "upper"}
  ]
}
```

Field rules:
- `role`: `hook` for slide 1, `cta` for the last slide, `middle` for everything else.
- `text_mode`: `stroke` (white text, black outline, the classic TikTok look), `background` (black text on a white box), or `plain`.
- `position`: `upper` (about 30% down, the default for hooks), `middle`, or `lower` (stays above the bottom 20%).
- `image`: a path relative to the set folder, or a path starting with `01-app/assets/` for screenshots.

Also write `slides.md`: a plain list of each slide's text and image direction, plus the caption, for the user to read at the gate.
