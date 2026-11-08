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

daily_batch_size: 9-15  # 3–5 posts per account per day on @earndapp, @ezyxbt, @earnie.lifts (founder, 2026-11-06); rises as the new accounts go live
winner_variation_share: 0.6
trend_communities: [r/naturalbodybuilding, r/StrongerByScience, r/GYM]
trend_scan: daily, 07:47 London, trend file + sound bank refreshed every day (founder, 2026-11-06; replaces the weekly scan).
stats_pull: weekly, Sunday morning (founder, 2026-11-01).
banned_words: []
default_app_slide: 4

## Standing rules

- Optimize each post for views. Judge formats weekly on total downloads.
- Target market (founder, 2026-11-08): **UK and US first**, then Canada and Australia, then Ireland and New Zealand. Write for them (English, UK/US gym references, trends and sounds from UK/US creators), suggest posting times for UK/US evenings, and track the viewer location split weekly (TikTok Studio → Analytics → Viewers → Locations). On 1–7 Nov @earndapp's viewers were 55.5% Greece, 7% UK.
- Volume and testing (founder, 2026-11-06): each active account posts 3–5 times a day. Every day, each account gets at least one new-format test alongside its proven formats; log each test's format in `posting.md` so the Sunday review can compare.
- Slide length (founder, 2026-11-08, ends the 2026-11-06 length test early): TikTok Studio shows viewers see only 2.3–2.9 slides whatever the length, so slideshows default to **5 slides** on @earndapp and @ezyxbt (@earndapp: cover, payoff, value, app, CTA; @ezyxbt: cover, payoff, tip, real tip with app, CTA). @earnie.lifts memes stay 5–6.
- Accounts are configured in `06-queue/accounts.json` (handle, type, voice, visual template, CTA and destination, disclosure). Every set is written for exactly one account and names it in `slides.json` → `account`. Never use a field marked TO CONFIRM without asking.
- Readiness is per account: `python3 .claude/skills/slideshow-engine/scripts/account_status.py`. An account with unconfirmed required settings blocks only its own sets.
- Founder (@ezyxbt) photos: always pick the strongest, most relevant of the founder's supplied photos for each slide (`01-app/founder-photo-catalog.md`). Minor edits allowed (crop, resize, straighten, exposure/colour, cropping out background clutter and other people; blur only lightly, never heavy background blur) (founder, 2026-11-01; light blur only, founder 2026-11-03). Never edit the face; physique unchanged; nothing generated. Crop out other gym members. If none fit, ask the founder for more photos.
- Adapting a set for another account means a new set with its own hooks and visuals in that account's voice and template, never a copy.
- Never present our own promotional pages as independent recommendations. Founder and theme-page posts say EARND is ours.
- The app enters on slide 3 or 4 by default, in the account's voice (brand: direct EARND product language). Exception: @ezyxbt native-tip format puts it on the second-to-last "real tip" slide (founder, 2026-11-01).
- Report every post per account: account, post ID, messaging angle, views, profile visits, attributable purchases where measurable. Leave unavailable metrics blank, never 0.
- Accounts (founder lifted the account limit 2026-11-04; plan in `03-ideas/distribution-plan-2026-11-04.md`). TikTok: @earndapp, @ezyxbt, @earnie.lifts, @gymbro.skits, @whatif.overload. Instagram: @earndapp, @earnie.lifts, @gymbro.skits, @whatif.overload (same brand and content as its TikTok; @ezyxbt is TikTok only). Every account runs its own format: never post one account's set on another brand. Content mix (founder, 2026-11-04): @ezyxbt stays photo slideshows only; @earndapp and @earnie.lifts post a mix of slideshows and mascot videos (3–5 posts a day: 2–4 slideshows + exactly 1 video, at least one post a new-format test; videos carry TikTok's AI label; founder 2026-11-06, 1 video a day). Judge each format on the kill/scale rule in the plan.
- 5 to 10 slides (5 is the default on @earndapp and @ezyxbt, see slide length). One idea per slide. Under 25 words per slide. Exception: @ezyxbt one-liner photos are a single image with one line, no app slide, no CTA and no caption; one per day on top of his 2–4 slideshows (founder, 2026-11-05; format: `02-research/formats/oneliner-photo.md`).
- Every post gets a specific trending sound suggestion in its `posting.md`: a primary and a backup (name + artist), picked from the latest sound bank `02-research/trends/sounds-YYYY-MM-DD.md` (refreshed daily with the trend scan, via Apify on niche accounts). Videos with our own voice keep their audio; any trending sound goes underneath at low volume (founder, 2026-11-04). Audio on every post, always: never "optional", never "pick something", always a named primary + backup, including videos with our own voice (trending sound underneath at ~5–10%) (founder, 2026-11-05).
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

- 2026-11-08 (TikTok Studio, founder-approved): every post gets its views on day 1 from For You, then flatlines; "most viewers left after 2 photos" on every slideshow; a 10 s video averaged 3.0 s watched (4.85% full). Retention, not suppression, is the bottleneck. So:
  1. **Slide 2 is the payoff.** It carries the complete answer (the whole split, all the fixes, the full exercise list) so people who leave at slide 2 still get the value and save it; later slides add detail.
  2. **5 slides by default** on @earndapp and @ezyxbt.
  3. **Covers:** a big, specific hook in the top third with the number or outcome in it (e.g. "4 days. 6 exercises. this exact split"), never small text at the bottom over the photo.
  4. **Videos:** punchline or movement in the first second, big text at the top, 5–8 s long unless it's a voiced explainer.
