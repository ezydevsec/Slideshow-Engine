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
