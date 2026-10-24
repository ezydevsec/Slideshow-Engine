# Review mode (weekly)

Decides what to kill, what to fix, and what to milk. Ends at GATE 4.

## Step 1: Pull the numbers

1. From Humanpost or each platform's analytics: every post in the last 7 days, **per account**. Append to `07-results/performance.csv` (`date,account,platform,post_id,post_url,set_id,messaging_angle,views,profile_visits,likes,comments,shares,saves,app_questions,attributable_purchases`). Leave any metric the source doesn't provide blank, never 0. Fill `attributable_purchases` only where a store or link actually measures it.
2. Count "what app is this" style comments per post if the analytics expose comment text. Otherwise leave `app_questions` blank.
3. Revenue: daily installs, trials, and revenue into `07-results/revenue.csv`, from a RevenueCat export or API, App Store Connect, or the user pasting numbers.

## Step 2: Join

```
python3 <skill>/scripts/results_join.py --project .
```

This writes `07-results/weekly-YYYY-MM-DD.csv` with one row per account and set: views, profile visits, attributable purchases, engagement, best post, and an estimated install share. Unmeasured metrics stay blank. Compare accounts separately: a brand, founder, and theme page have different baselines. Installs are spread across each day's posts by view share, so treat them as directional. They are not true attribution.

## Step 3: Bucket every set

| Views | Converting | Action |
|---|---|---|
| High | Yes | **Milk it.** 10 variations: same structure, fresh hook wording and images. Promote the format to `winner`. |
| High | No | Keep the hook, rework the app slide and CTA. |
| Low | Yes | Keep the app slide, test 5 new hooks. |
| Low | No | **Kill it.** One line in `failure-log.md` with the reason. |

"High" means above the account's own median. A post with 2x its account's median beats a big number on a big account.

## Step 4: Account health

Read each account's median views over the last 7 days:

| Median | Meaning |
|---|---|
| Under 300 | An account problem (warm-up, shadow restriction). Pause it and tell the user. |
| 300 to 1K | The content isn't good enough |
| 1K to 5K | Keep iterating the format |
| 5K to 100K | The hook works |
| 100K+ | Scale it |

If installs are coming in but nobody pays, say so loudly. That's an onboarding or paywall problem, and more posting won't fix it.

## GATE 4

Show the user:
1. The bucket table
2. Proposed updates to `winners.md` (with the winning hooks verbatim)
3. Proposed new lines for `failure-log.md`
4. Proposed new rules for `CLAUDE.md`
5. Next week's plan (how many variations of which winners, how many new formats)

Write nothing until they approve. Then save, and add the winner variations to `03-ideas/backlog.md`.
