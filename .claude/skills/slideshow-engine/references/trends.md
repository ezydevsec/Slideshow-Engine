# Trends mode

Finds what people are talking about today and the bridge from that conversation to the app.

## Step 1: Scan

Use WebSearch and WebFetch. Sources, in order:

1. **TikTok Creative Center** (`ads.tiktok.com/business/creativecenter`): trending hashtags and songs, US, last 7 days. Note the "Rising" songs, they haven't peaked yet. If the page won't load, search for "trending TikTok sounds this week".
2. **Google Trends** daily trending searches, US.
3. **Reddit and X**: top posts from the last 48 hours in the communities listed in `CLAUDE.md` under `trend_communities`.
4. **Pop culture news**: celebrity moments, shows, sports, music releases.
5. **The calendar**: holidays, award shows, school calendar, astrology events, seasonal moments in the next 7 days.

If the `last30days` skill is installed and the user wants a deeper read on one topic, offer to run it.

Write `02-research/trends/YYYY-MM-DD.md` with the 15 biggest items:

```markdown
## <Trend>
What happened:
Why people care:
Shelf life: hours | days | weeks
Emotion it triggers:
Sounds attached (if any):
Source:
```

## Step 2: Bridge

For each trend, find the bridge: the angle where the conversation naturally leads to a pain in the pain bank.

Rules:
- The trend is the hook. The app answers a question the trend raised.
- If the bridge is forced, write "no bridge" and move on. A weak bridge kills views.
- Apply the trend safety rule in SKILL.md.

Score each surviving idea 1-10 on:

| Factor | What 10 looks like |
|---|---|
| Size | Everyone is talking about it |
| Freshness | Started in the last 24 hours |
| Bridge | The app feels like the obvious answer |
| Repeatability | 10 versions are easy to make |

Total out of 40. Add anything 28+ to `03-ideas/backlog.md`:

```markdown
- [ ] YYYY-MM-DD | <trend> | bridge: <one sentence> | format: <format file> | hook: "<slide 1>" | app on slide N | score NN | expires: <date>
```

Mark expired ideas `[x] expired` when their shelf life passes.

## Step 3: Report

Show the top 5 ideas with their scores and the trending sounds worth using today.
