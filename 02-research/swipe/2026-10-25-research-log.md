# Research run 2026-10-25

**Result: no outlier gallery. Gate 2 not reached.** No TikTok photo-mode slideshow met the shortlist rules (50,000+ views, 3x account median, posted in the last 30 days).

## What ran (Apify, Clockworks TikTok Scraper)

| Run | Input | Result | Cost |
|---|---|---|---|
| Keyword search, past-month filter, GB proxy | 8 pain keywords + study tips, skincare routine tips, relationship advice | Failed: "Could not get a working device id in 3 attempts" on every query. Aborted. | $0.001 |
| Hashtag feeds, `oldestPostDateUnified: 30 days` | #progressiveoverload #gymtips #upperlowersplit #workoutplan #gymbeginner #gymmotivationtips #studytips #skincaretips #relationshipadvice, 25 each | 225 posts, **0 slideshows**. Date filter not applied (posts back to 2022). Hashtag feeds appear to return video only. | $0.83 |
| Plain keyword search (test) | "progressive overload slideshow", "gym tips slideshow", 10 each | 20 posts, 6 slideshows, none qualifying (newest under 3K views; the 100K+ ones are from 2023 and May 2026) | $0.08 |
| Keyword search, past-month filter, no proxy (test) | "gym tips slideshow", 10 | Same device-id failure | $0.001 |

**Conclusion:** in this Actor, the date filter and sort options (the mobile-API path) are currently failing. Plain web search works, but about 30% of its results are slideshows and most are months old. Finding ~20 qualifying outliers that way would take roughly 1,000+ results plus account-median pulls, about $4–5, which is over this month's remaining Free-plan credit.

## Slideshows seen (not outliers, kept for reference only)

- https://www.tiktok.com/@kai.desai/video/7687374161198501151 (2026-09-19, 2.3K views, 7 slides, gym tips)
- https://www.tiktok.com/@layla.lifts7/video/7692392197882252557 (2026-10-03, 1.2K views, 6 slides)
- https://www.tiktok.com/@tevabolic/video/7640014893277564168 (2026-05-15, 118.7K views, 2 slides, transformation)
- https://www.tiktok.com/@gymmyworm/video/7212019847092325674 (2023-03-18, 295.8K views, 6 slides, squat tips)
- https://www.tiktok.com/@gymmyworm/video/7295066975389207851 (2023-10-28, 43.5K views, 8 slides)
- https://www.tiktok.com/@adz_560/video/7558094269181889814 (2025-10-06, 728 views, 7 slides)

## Options for the next research run

1. **Swipe inbox (free):** paste TikTok slideshow links or screenshots you come across into `02-research/swipe/inbox/`. The engine scores and breaks them down.
2. **Retry the date-filtered search later:** the device-id error may be temporary on the Actor's side. A 10-result test costs about $0.05.
3. **Larger plain search:** about $4–5 for ~1,000 results plus medians. Needs a paid Apify plan or next month's credit, and your approval.

## Update: founder-supplied accounts (same day)

The founder supplied three accounts. Pulled the last 30 posts of each with Apify's TikTok profile scraper ($0.22) and scored each post against its account's median views.

| Account | Slideshows / 30 | Median views | Result |
|---|---|---|---|
| @gymbratzzzz (gym tips, 71K followers) | 30 | 6,779 | **5 qualify** (50K+, 3x+, last 30 days): 1.5M (221x), 252K (37x), 82.7K, 78.9K, 52.9K |
| @getastraapp (astrology app, 19.7K followers) | 30 | 61,250 | 6 posts of 2.9M–3.9M, but all Feb–Mar 2024 (the account hasn't posted since). Outside the 30-day rule: kept as a reference |
| @plug_ai | 20 | 15,000 | Outliers are videos, not slideshows. Nothing kept |

Gallery: `2026-10-25-gallery.html` (11 slideshows), data in `2026-10-25-raw.json`. Slide image links come from TikTok's CDN and expire after a few days.

Neither structure has appeared on 3+ different accounts yet, so neither counts as **validated**.

## Update 2: nine more founder-supplied accounts

Last 20 posts of each, $0.67. 17 new slideshows qualify (50K+, 3x+, last 30 days); 4 more kept as older references. Gallery now holds 32.

| Format | Seen on (qualifying or reference) | Best result | Notes |
|---|---|---|---|
| **Top-5 ranked countdown** ("top 5 PEAK exercises for X", each rated x/10, a "bonus/pro tip: track your progressive overload, I use [app]" slide near the end) | @creed.lifter (3.4M, 3.1M, 1.9M; Feb–May), @aaliyahwellness (171.6K 46x, 112.7K 30x), @gymbratzzzz (same tip-slide app plug) | 3.4M | **Validated (3 accounts).** Real photo backgrounds, no illustrations needed. The tip slide pitches tracking + progressive overload, which is EARND's job |
| **Exercise tier list** (F → S tiers, one exercise per slide, illustration + 1-line verdict) | @arrowfitnessapp (812K, 519K, 394K, 304K), @liftx.app (chest tier list) | 812K (72x) | Two app accounts. 18–22 slides, over our 10-slide cap. Needs exercise illustrations |
| **Plan sheets** ("build your upper day: pick one per slide", "push / pull / legs" day sheets) | @bluebro.fit (73.4K), @liftx.app (83.5K, 55.5K, 55K), @gymbratzzzz (zone-by-zone) | 83.5K | Validated (3). Matches EARND's "just give me a plan" pain. Needs illustrations |
| **Text on colour + app on last slide** ("5 questions I'm too scared to ask", "most to least likely to…") | @sandrawritesthis (6 outliers, 507K top), @getastraapp (2024) | 507K (37x) | Text only, cheap to make. Last slide: search the app by name |
| Self-improvement steps (4–6 slides) | @thcowboyproject (1.4M, June) | 1.4M | Reference only |

@adamxbukhari posts videos only. @mayaviefit's slideshow outlier is a lifestyle photo dump with no app.

Caution: several accounts present an app as a personal recommendation ("I use X app and I love it"). Ours must say EARND is ours.
