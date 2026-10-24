# Setup mode

Run once per app. Ends at GATE 1.

## Step 1: Scaffold

Create this tree in the current folder (skip anything that already exists, never overwrite):

```
CLAUDE.md
01-app/app-brief.md
01-app/personas.md
01-app/assets/
02-research/swipe/inbox/
02-research/formats/
02-research/trends/
03-ideas/backlog.md
04-sets/
06-queue/queue.csv
07-results/performance.csv
07-results/revenue.csv
07-results/winners.md
07-results/failure-log.md
```

Copy `<skill>/assets/CLAUDE.template.md` to `CLAUDE.md` and fill in the app name.

Seed the CSVs with headers:

- `06-queue/queue.csv`: `set_id,account,status,approved_on,notes`
- `06-queue/accounts.json`: one entry per posting account (see `references/distribution.md`)
- `07-results/performance.csv`: `date,account,platform,post_id,post_url,set_id,messaging_angle,views,profile_visits,likes,comments,shares,saves,app_questions,attributable_purchases`
- `07-results/revenue.csv`: `date,installs,trials,revenue`

## Step 2: App brief interview

Interview the user one question at a time. Keep each question short. Cover:

1. What the app does in one sentence.
2. Who it's for (age, situation, what they're doing when they need it).
3. The magic moment: the one thing someone SEES the app do that makes them think "wait, I need that." What does it look like on the phone screen?
4. The top 10 pains the user feels before they find the app.
5. The top 5 objections.
6. Competitors, and which of them run slideshows.
7. What life looks like after.
8. Pricing and paywall type (so the review can sanity check conversion).

Then ask for raw customer language: App Store reviews, support tickets, surveys, Reddit threads. Read whatever they give and build a **pain bank**: 50 real phrases, quoted exactly, grouped by theme. If the user has none, pull public App Store reviews of the app and its top 2 competitors with WebFetch.

Write `01-app/app-brief.md` with these sections: One-liner, Who it's for, Magic moment, Pains, Objections, Competitors, After, Pricing, Pain bank.

## Step 3: Personas

Write 3 personas to `01-app/personas.md`. A persona is the person whose feed one cluster of accounts lives in. For each:

- Name and one-line description
- What they search, watch, and save on TikTok
- The 5 pains from the brief that hit them hardest
- Voice: how they type (lowercase? slang? emojis?)
- 5 warm-up search terms they'd actually type into TikTok
- Account theme (the theme page this persona would follow)

## Step 4: Assets

Ask the user to drop real app screenshots and screen recordings into `01-app/assets/`, named by what they show (`ask-anything-answer.png`, `compatibility-score.png`). Ask for at least one screenshot of the magic moment. List what's there and flag gaps.

## GATE 1

Show the user the brief, the pain bank, and the personas. Ask them to correct anything. Do not start research until they confirm.
