# EARND Slideshow Engine

slideshow-engine: v1

This folder runs TikTok and Instagram slideshows for EARND using the `slideshow-engine` skill.

## Where things live

- `01-app/` the brief, pain bank, personas, and REAL app screenshots
- `02-research/` outlier slideshows (`swipe/`), proven formats (`formats/`), daily trends (`trends/`)
- `03-ideas/backlog.md` every scored idea and winner variation
- `04-sets/YYYY-MM-DD-slug/` one folder per slideshow set
- `06-queue/` account settings (`accounts.json`), approvals, and posting manifests
- `07-results/` performance, revenue, winners, failure log

## Settings

daily_batch_size: 6  # @earndapp + @ezyxbt today; rises as the new accounts go live (see distribution plan)
winner_variation_share: 0.6
trend_communities: [r/naturalbodybuilding, r/StrongerByScience, r/GYM]
trend_scan: weekly, Monday morning (founder, 2026-11-01). Daily runs reuse that week's file; no daily rescans.
stats_pull: weekly, Sunday morning (founder, 2026-11-01).
banned_words: []
default_app_slide: 4

## Standing rules

- Optimize each post for views. Judge formats weekly on total downloads.
- Accounts are configured in `06-queue/accounts.json` (handle, type, voice, visual template, CTA and destination, disclosure). Every set is written for exactly one account and names it in `slides.json` → `account`. Never use a field marked TO CONFIRM without asking.
- Readiness is per account: `python3 .claude/skills/slideshow-engine/scripts/account_status.py`. An account with unconfirmed required settings blocks only its own sets.
- Founder (@ezyxbt) photos: always pick the strongest, most relevant of the founder's supplied photos for each slide (`01-app/founder-photo-catalog.md`). Minor edits allowed (crop, resize, straighten, exposure/colour, cropping out background clutter and other people; blur only lightly, never heavy background blur) (founder, 2026-11-01; light blur only, founder 2026-11-03). Never edit the face; physique unchanged; nothing generated. Crop out other gym members. If none fit, ask the founder for more photos.
- Adapting a set for another account means a new set with its own hooks and visuals in that account's voice and template, never a copy.
- Never present our own promotional pages as independent recommendations. Founder and theme-page posts say EARND is ours.
- The app enters on slide 3 or 4 by default, in the account's voice (brand: direct EARND product language). Exception: @ezyxbt native-tip format puts it on the second-to-last "real tip" slide (founder, 2026-11-01).
- Report every post per account: account, post ID, messaging angle, views, profile visits, attributable purchases where measurable. Leave unavailable metrics blank, never 0.
- Accounts (founder lifted the account limit 2026-11-04; plan in `03-ideas/distribution-plan-2026-11-04.md`). TikTok: @earndapp, @ezyxbt, @earnie.lifts, @gymbro.skits, @whatif.overload. Instagram: @earndapp, @earnie.lifts, @gymbro.skits, @whatif.overload (same brand and content as its TikTok; @ezyxbt is TikTok only). Every account runs its own format: never post one account's set on another brand. Content mix (founder, 2026-11-04): @ezyxbt stays photo slideshows only; @earndapp and @earnie.lifts post a mix of slideshows and mascot videos (default 2 slideshows + 1 video per day; videos carry TikTok's AI label). Judge each format on the kill/scale rule in the plan.
- 5 to 10 slides. One idea per slide. Under 25 words per slide. Exception: @ezyxbt one-liner photos are a single image with one line, no app slide, no CTA and no caption; one per day on top of his 3 slideshows (founder, 2026-11-05; format: `02-research/formats/oneliner-photo.md`).
- Every post gets a specific trending sound suggestion in its `posting.md`: a primary and a backup (name + artist), picked from that week's sound bank `02-research/trends/sounds-YYYY-MM-DD.md` (refreshed every Monday with the trend scan, via Apify on niche accounts). Videos with our own voice keep their audio; any trending sound goes underneath at low volume (founder, 2026-11-04). Audio on every post, always: never "optional", never "pick something", always a named primary + backup, including videos with our own voice (trending sound underneath at ~5–10%) (founder, 2026-11-05).
- Never invent app UI. Only real screenshots from `01-app/assets/`.
- Read `07-results/winners.md` and `07-results/failure-log.md` before writing any set.
- Nothing is queued without my approval in chat. Posting is manual for now (2026-10-28): no Humanpost. Approved sets get a `posting.md` pack, and I post them myself.
- Our accounts never comment on or engage with each other.
- EARND has no free trial. Weekly reviews track paid subscriptions, not trials (the `trials` column in `07-results/revenue.csv` stays blank). Locate drop-offs with the funnel in `01-app/app-brief.md` → Pricing.
- Prelaunch: every set ends with its account's prelaunch CTA from `accounts.json` (@earndapp: "EARND launches soon. Follow for the launch."). No download CTA or links until `phase` is "launched" and `launch.download_url` is set. No trial references.
- Numerical examples (e.g. 100 kg × 7 → 100 kg × 8) are always labelled "example" on the slide. Sets × reps prescriptions (e.g. 2 × 4–8) are shown plain, without the "example" tag (founder, 2026-10-30); weights in progression examples stay labelled "example". Exception: @whatif.overload's joke escalations (e.g. Dale's +2.5 kg/week) carry no "example" tag (founder, 2026-11-04).
- Scheduling: users move the four prescribed sessions to available days. Never say the programme adapts to fewer sessions.
- Never invent user experiences, testimonials, or independent endorsements.
- No physique promises. Hooks and payoffs talk about tracking, targets, and having a plan. Users "can see when they've improved," never "numbers go up every week" or "know it's working."

## Learned rules

(Added after each weekly review. Newest at the top.)
