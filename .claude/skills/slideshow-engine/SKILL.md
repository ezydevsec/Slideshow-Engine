---
name: slideshow-engine
description: Runs a full TikTok and Instagram slideshow marketing engine for a consumer app from Claude Code. Sets up the project, finds outlier slideshows, scans daily trends and bridges them to the app, writes slideshow sets, generates and renders slide images, queues drafts to Humanpost through its MCP, and runs a weekly performance review. Use when the user says "set up the slideshow engine", "run today's slideshows", "daily run", "trend scan", "find outlier slideshows", "write slideshows", "render the sets", "queue to Humanpost", "weekly slideshow review", or asks for TikTok photo-mode slideshows or carousels for an app at volume.
---

# Slideshow Engine

Turns one Claude Code project folder into a slideshow factory for one app.

The engine does the research, writing, image work, rendering, queueing, and reporting.
The human makes four decisions: what the app is, which formats to copy, which sets ship, and what to kill or scale.

## Modes

Figure out the mode from the request. If the project has no `CLAUDE.md` containing the line `slideshow-engine: v1`, run **setup** first no matter what was asked.

| Mode | Trigger phrases | Reference file | Ends with |
|---|---|---|---|
| setup | "set up", first run | `references/setup.md` | GATE 1: app brief approved |
| research | "find outliers", "research formats", weekly or when formats run dry | `references/research.md` | GATE 2: user picks formats in the gallery |
| daily | "daily run", "run today's slideshows" | trends → bridge → write → visuals | GATE 3: user approves sets |
| trends | "trend scan" only | `references/trends.md` | trend file + scored ideas |
| write | "write slideshows for X" | `references/writing.md` | slides.json per set |
| visuals | "make the images", "render" | `references/visuals.md` | final/ folder + contact sheet |
| queue | "queue to Humanpost", "send approved sets" | `references/distribution.md` | Humanpost drafts queued, awaiting dashboard approval |
| review | "weekly review", "what's working" | `references/review.md` | GATE 4: user approves kill/scale + rule changes |

Read only the reference file for the current mode. Each one is self-contained.

## The daily run (the mode used most)

1. Read `CLAUDE.md`, `01-app/app-brief.md`, `01-app/personas.md`, `07-results/winners.md`, `07-results/failure-log.md`.
2. Run the trend scan in `references/trends.md`. Save `02-research/trends/YYYY-MM-DD.md`.
3. Bridge trends to the app and score them. Add 7+ ideas to `03-ideas/backlog.md`.
4. Also pull from the backlog: variations of current winners from `winners.md` (these come first, milking a winner beats a new idea).
5. Pick today's batch. Default batch size is in `CLAUDE.md` (start at 10 sets: ~6 winner variations, ~4 new trend ideas).
6. Write each set (`references/writing.md`).
7. Make the images and render (`references/visuals.md`).
8. **GATE 3.** Stop. Show the user a table of today's sets (set ID, format, trend, hook, app slide number) and the path to each `final/contact-sheet.jpg`. Ask which to approve, edit, or kill. Write approvals to `06-queue/queue.csv`.
9. Only after approval, offer to run **queue** mode.

Never chain from step 8 into queueing without an explicit yes in chat.

## Ground rules (apply in every mode)

- **Optimize each post for views.** Judge formats on total downloads, weekly. Never judge a single post on conversion rate.
- **App placement:** default slide 3 or 4, inside the story, in first person ("i've been using this app that..."). If moving it earlier raises conversion but costs views, move it back.
- **Length:** 5 to 10 slides. One idea per slide. Under 25 words per slide. Every slide gives a reason to swipe.
- **Real UI only.** App slides use screenshots from `01-app/assets/`. Never generate an app interface.
- **No coordinated engagement.** Never plan comments, likes, or replies between our own accounts. Never create Humanpost comment or Amplify tasks.
- **AI disclosure.** Any set with a generated image gets `ai_images: true`, and the Humanpost post notes tell the poster to turn on TikTok's AI-generated content label.
- **Trend safety.** Skip tragedies, deaths, disasters, crime victims, politics, and minors. Skip any trend where the bridge to the app feels forced.
- **No real private people.** No screenshots of real people's profiles, DMs, or faces unless they are our own creators with permission. Text threads are written by us.
- **Log everything.** Every flop gets a line in `failure-log.md` with the reason. Every rule learned goes into `CLAUDE.md` after the user approves it.

## Tools this skill expects (and the fallback for each)

| Job | Preferred | Fallback |
|---|---|---|
| Outlier research | Apify MCP (Clockworks TikTok Scraper) | User pastes TikTok links or screenshots into `02-research/swipe/inbox/` |
| Trend scan | WebSearch + WebFetch (TikTok Creative Center, Google Trends, Reddit, news) | Same, with fewer sources |
| Images | Higgsfield MCP (or any image MCP the user has) | User drops photos into the set's `images/` folder |
| Render | `scripts/render_slides.py` (Pillow, no browser needed) | none needed |
| Distribution | Humanpost MCP | `final/clean/` + `slides.json` exported for manual upload |
| Revenue data | RevenueCat export or API, App Store Connect CSV | User pastes daily installs into `07-results/revenue.csv` |

At the start of any mode that needs an MCP, check that its tools are available. If one is missing, say which, give the fallback, and keep going. Never stall the whole run on one missing tool.

## File contracts

Every set lives in `04-sets/YYYY-MM-DD-slug/`:

```
04-sets/2026-10-15-jealous-ranking/
├── slides.json      ← source of truth (schema in references/writing.md)
├── slides.md        ← human-readable version for review
├── images/          ← slide-01.jpg ... (raw images, no text)
└── final/
    ├── clean/       ← 1080x1920 JPEGs, no text (what Humanpost gets)
    ├── preview/     ← 1080x1920 JPEGs with text (what the user reviews)
    └── contact-sheet.jpg
```

Scripts live in this skill's `scripts/` folder. Run them by full path:

- `python3 <skill>/scripts/render_slides.py 04-sets/<set>` renders one set
- `python3 <skill>/scripts/build_gallery.py <raw.json> <out.html>` builds the research gallery
- `python3 <skill>/scripts/results_join.py` builds the weekly results table

## Gates (the human's job)

| Gate | When | What the user decides |
|---|---|---|
| 1 | End of setup | The app brief, pain bank, and personas are right |
| 2 | End of research | Which outlier slideshows become formats |
| 3 | End of every daily run | Which sets ship |
| 4 | End of weekly review | What to kill, what to scale, which new rules to adopt |

Plus Humanpost's own dashboard approval on every queued post (never set `skipApproval: true`).
