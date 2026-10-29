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

daily_batch_size: 10
winner_variation_share: 0.6
trend_communities: [r/..., r/...]
banned_words: []
default_app_slide: 4

## Standing rules

- Optimize each post for views. Judge formats weekly on total downloads.
- Accounts are configured in `06-queue/accounts.json` (handle, type, voice, visual template, CTA and destination, disclosure). Every set is written for exactly one account and names it in `slides.json` → `account`. Never use a field marked TO CONFIRM without asking.
- Readiness is per account: `python3 .claude/skills/slideshow-engine/scripts/account_status.py`. An account with unconfirmed required settings blocks only its own sets.
- Founder (@ezyxbt) photos: always pick the strongest, most relevant of the founder's supplied photos for each slide (`01-app/founder-photo-catalog.md`). Crop and resize only: face and physique unchanged, never generated. Crop out other gym members. If none fit, ask the founder for more photos.
- Adapting a set for another account means a new set with its own hooks and visuals in that account's voice and template, never a copy.
- Never present our own promotional pages as independent recommendations. Founder and theme-page posts say EARND is ours.
- The app enters on slide 3 or 4 by default, in the account's voice (brand: direct EARND product language).
- Report every post per account: account, post ID, messaging angle, views, profile visits, attributable purchases where measurable. Leave unavailable metrics blank, never 0.
- @earndapp and @ezyxbt run in parallel (approved 2026-10-24). Don't add theme pages or more posting workload until a format shows repeatable results. More accounts alone don't show which message sells EARND.
- 5 to 10 slides. One idea per slide. Under 25 words per slide.
- Never invent app UI. Only real screenshots from `01-app/assets/`.
- Read `07-results/winners.md` and `07-results/failure-log.md` before writing any set.
- Nothing is queued without my approval in chat. Posting is manual for now (2026-10-28): no Humanpost. Approved sets get a `posting.md` pack, and I post them myself.
- Our accounts never comment on or engage with each other.
- EARND has no free trial. Weekly reviews track paid subscriptions, not trials (the `trials` column in `07-results/revenue.csv` stays blank). Locate drop-offs with the funnel in `01-app/app-brief.md` → Pricing.
- Prelaunch: every set ends with its account's prelaunch CTA from `accounts.json` (@earndapp: "EARND launches soon. Follow for the launch."). No download CTA or links until `phase` is "launched" and `launch.download_url` is set. No trial references.
- Numerical examples (e.g. 100 kg × 7 → 100 kg × 8) are always labelled "example" on the slide. This includes sets × reps prescriptions and any weights (founder, 2026-10-29).
- Scheduling: users move the four prescribed sessions to available days. Never say the programme adapts to fewer sessions.
- Never invent user experiences, testimonials, or independent endorsements.
- No physique promises. Hooks and payoffs talk about tracking, targets, and having a plan. Users "can see when they've improved," never "numbers go up every week" or "know it's working."

## Learned rules

(Added after each weekly review. Newest at the top.)
