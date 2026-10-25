# Tool setup plan (2026-10-25)

Goal: get research → production → approval → publishing running. Production continues with current tools throughout. Nothing is subscribed or upgraded without the founder's go-ahead.

Prices checked 2026-10-25. Apify's are from its own pricing page. Higgsfield's official page didn't load, so its figures come from secondary sources and must be confirmed at sign-up. Humanpost's are from humanpost.com and its MCP docs.

## Key finding: Humanpost doesn't fit our two accounts
Humanpost's MCP docs say posts can only target **company-owned accounts that its posters create**, not accounts the customer already has. So it can't publish to @earndapp or @ezyxbt. It's built for theme pages run by its posters, which are on hold until a format shows repeatable results. For our own two accounts we need a scheduler that posts to accounts we connect ourselves.

## Recommendation

| Tool | Job | When | Plan | Est. cost | Access needed from you |
|---|---|---|---|---|---|
| **Upload-Post** (replaces Humanpost for our own accounts) | Send approved slideshows to @earndapp and @ezyxbt as **TikTok drafts** (photo mode). You add a trending sound and tap publish, so approval stays with you | **Now**: 7 approved-and-ready sets are waiting to post | Free tier to test, then the lowest paid plan (advertised "from $24/month"; confirm limits at sign-up) | ~$24/mo | Create an account, connect both TikTok accounts in its dashboard, and share an API key (or approve OAuth for the connector) |
| **Apify** | Competitor research + weekly performance tracking of our posts | **When the first batch is live** (measurement starts) | Starter, $19/mo ($17/mo billed annually). Includes $19 of usage, then pay as you go | $19/mo | Upgrade the existing account. **Regenerate the API token** (it was pasted in chat) and add it as an environment secret, not in chat |
| **Higgsfield** | Exercise illustrations for the held formats (tier lists, plan sheets) | **Not yet.** Only if you move a held format out of the backlog | One month of the entry plan (≈$15–19/mo for ≈200–270 credits per secondary sources) for a 10–20 image test | ≈$15–19 once | Account + connector, after you approve the test |
| **Humanpost** | Real people post from accounts they create | **Not yet.** Only if you approve theme pages after a format repeats | Trial: $200/mo minimum spend ($2 per post + $1 per 1,000 views, capped at $250 per post). Scaling: $1,125/mo | $0 now | API key from Settings → API & MCP, plus approved theme-account entries in `accounts.json` |

## Why each one, in detail

### Upload-Post: the current bottleneck
- Seven sets are approved or awaiting gate 3, and posting is manual.
- Its MCP `upload_photos` posts up to 35 images as a TikTok photo post to accounts you connect. Draft mode (`tiktokPostMode: MEDIA_UPLOAD`) sends to your TikTok inbox, so nothing publishes without you.
- In draft mode TikTok ignores the caption sent via the API, so you paste the caption from `posting.md`.

### Apify: what the $5 Free plan blocks
- Used so far this cycle (24 Oct – 23 Nov): **$3.15 of $5**. That leaves room for roughly one measurement pull of our two accounts, nothing else.
- Blocked:
  - **Weekly competitor monitoring:** ~12 accounts × 20 posts is ~$0.90/week.
  - **Weekly tracking of our own posts.**
  - **One keyword search per month:** ~$1–3.
  - **App Store reviews beyond 10:** the review Actor caps Free accounts at 10 results; Apple's own feed worked as a free workaround.
- Estimated real workload: **~$8–12/month**. Starter's $19 covers it with headroom.

### Higgsfield: what it would unlock
- **Not needed for the two selected formats.**
  - The countdown uses your real photos.
  - The text-on-colour format uses solid black and lime with real screenshots.
- **The held formats need exercise illustrations** (a figure doing each lift). Our photos can't supply these:
  - They show you posing, not performing lifts.
  - We have no shots of 15–20 different exercises.
- **Proposed test:** 10–20 illustrations for one plan sheet. Every set that uses them is marked `ai_images: true` and gets TikTok's AI-generated content label.
- **Alternative:** licensed exercise illustrations (one-off purchase, no AI label).

### Humanpost: when it becomes relevant
- Only after a format shows repeatable results **and** you approve theme pages.
- Each theme page needs disclosure ("run by the EARND team").
- We never use its comment or Amplify tasks.

## Proposed monthly budget (replaces the $5 cap)

| Line | Now | After a format repeats |
|---|---|---|
| Upload-Post | ~$24 | ~$24 |
| Apify Starter | $19 (from first live batch) | $19 (Scale only if monitoring passes ~$19/mo) |
| Higgsfield | $0 | ≈$15–19 for a test month, if a held format is selected |
| Humanpost | $0 | from $200/mo, only with approved theme pages |
| **Total** | **~$43/month** | ~$62/month before any theme pages |

## Order
1. **Now:** connect Upload-Post and post the four approved sets plus any of today's four you approve.
2. **When the first posts are live:** upgrade Apify to Starter and start weekly tracking. Report views and profile visits per post. Purchases stay blank until launch.
3. **After 1–2 weeks of data:** weekly review (gate 4). Decide whether a held format earns a Higgsfield test.
4. **Only after repeatable results:** consider theme pages and Humanpost.
