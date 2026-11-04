# TikTok distribution plan (draft, 2026-11-04)

Status: **proposal, awaiting user approval.** Research: `02-research/swipe/2026-11-04-animated-fitness-accounts.md` and `2026-11-04-3d-character-accounts.md`.
The user lifted the account-count limit on 2026-11-04. Every other standing rule still applies: disclosure, no interaction between our accounts, real screenshots only, no physique promises, numbers labelled "example", prelaunch CTA, and approval before anything is queued or posted.

Assumption: 2 posts a day per account (the user's limit is 2 to 3).

## Phase 1: test (weeks 1 to 2), one account per format

| # | Account | Format | EARND angle | Posts/day | Production |
|---|---|---|---|---|---|
| 1 | @earndapp (existing) | C. Flat-vector tip animation (Jabmax-style) | Strength-history stories, one-fix tips about progression and tracking | 2 | Coded motion graphics (no generation credits) |
| 2 | @ezyxbt (existing) | Founder photo slideshows | Unchanged | 2 | Current engine |
| 3 | new | A. 3D anatomy demo | "Same lift, different setup", how to load and progress a lift | 2 | 3D generation (Higgsfield) |
| 4 | new | B. Sketch animated how-to | "How to force your bench/squat to go up" (progression, not physique) | 2 | Generated line art and pans, voice-over |
| 5 | new | D. Minimal relatable loops (12 to 16 s) | "ME / MY NOTES APP", gym-friend dynamics, "send this to" | 2 | Coded motion graphics |
| 6 | new | E. 3D comedic character skits, with hook-pivot | Gym situations (forgot last week's weight, no plan). The final beat may pivot to EARND. | 2 | 3D generation (Higgsfield) |
| 7 | new | F. What-if escalation | "+2.5 kg every week" escalations | 2 | 3D stills (slideshow) first, video if it hits |

**Phase 1 totals: 5 new accounts, 7 accounts in all, about 14 posts a day.**
New accounts: about 3 days of normal use before the first post, then 1 post a day in week 1 and 2 a day from week 2.

## Kill and scale rule (end of week 2, about 20 posts per account)
- **Winner:** median views of 20k or more, or one post at 250k or more, *and* measurable profile visits to @earndapp or the waitlist.
- **Keep testing:** median 5 to 20k. Change the hook style for one more week.
- **Kill:** median under 5k. Retire the format, and move that account to a winning format with a new identity.

## Phase 2: scale (weeks 3 to 6)
- Each winning format gets **+2 accounts**, each with its own angle (sub-niche, character, audience), never a clone. Planned splits:
  - A: men's strength lifts / women's lower body / home and dumbbell-only
  - C: lifting-history stories / one-fix form tips
  - E: a second original character, or a couple's gym skits
- Target: **12 to 15 accounts, 25 to 35 posts a day**, weighted toward the 2 to 3 best formats.
- Losing formats are not revived without new outlier evidence.

## Before scaling
1. **Waitlist link.** Jabmax (prelaunch, 93k followers in about 6 weeks) sends everyone to a waitlist. EARND's only conversion is "follow @earndapp", which can't be measured per account. A waitlist page with UTM per account would make the kill and scale rule measurable.
2. **Video pipeline.** The engine renders slideshows. Formats A, B, E and F need video. C and D can be coded animations (cheap and consistent). A and E use Higgsfield generation credits for every video. Check the per-video cost before phase 2.
3. **Humanpost.** Confirm it can post video and how many accounts it handles.
4. **Account config.** Each new account goes into `06-queue/accounts.json` with handle, voice, template, CTA and disclosure, and is checked with `account_status.py`.

## Rules that still apply to every account
- Theme accounts say EARND is ours (bio and final beat). No posing as an independent recommendation.
- Our accounts never like, comment on or reply to each other.
- App UI only from real screenshots in `01-app/assets/`.
- No physique promises. Formats A and B are reframed around progression and tracking.
- Prelaunch CTA only. No download links, no trial references.
