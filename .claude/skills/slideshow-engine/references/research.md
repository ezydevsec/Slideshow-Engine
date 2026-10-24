# Research mode

Finds slideshows that are already winning and turns them into reusable formats. Run at setup, then weekly, or any time `02-research/formats/` runs dry. Ends at GATE 2.

## Step 1: Collect

**With the Apify MCP:**

1. Find the Clockworks TikTok Scraper actor. Read its current input schema before running. Do not guess field names.
2. Run two searches:
   - Problem keywords from `app-brief.md` (5 to 10, in the user's words from the pain bank)
   - 3 to 4 unrelated niches with heavy slideshow content (ask the user, or default to: relationships, studying, skincare, fitness)
3. Keep only photo-mode posts (posts with images, not video) from the last 30 days.
4. For every account that appears, pull its last 20 posts to get a median view count.

**Without Apify:** process whatever is in `02-research/swipe/inbox/` (links or screenshots). For links, use WebFetch on `https://www.tiktok.com/embed/v2/<post_id>` to get the caption, sound, and slide images.

## Step 2: Score and shortlist

For each slideshow compute `outlier = views / account_median`.

Shortlist if all of these are true:
- 50,000+ views
- outlier 3x or higher
- posted in the last 30 days

Mark a format as **validated** when the same structure appears on 3+ different accounts.

Save the normalized list to `02-research/swipe/YYYY-MM-DD-raw.json` as an array of:

```json
{"url": "", "account": "", "followers": 0, "views": 0, "likes": 0, "comments": 0,
 "shares": 0, "saves": 0, "account_median": 0, "outlier": 0.0, "posted": "YYYY-MM-DD",
 "caption": "", "sound": "", "slides": ["https://...slide1.jpg", "..."], "niche": "own|other"}
```

Build the gallery:

```
python3 <skill>/scripts/build_gallery.py 02-research/swipe/YYYY-MM-DD-raw.json 02-research/swipe/YYYY-MM-DD-gallery.html
```

## GATE 2

Tell the user to open the gallery, tick the slideshows worth copying, and click "Export selected". That downloads `selected.json`. Ask them to drop it into `02-research/swipe/`.

## Step 3: Break down the picks

For every selected slideshow, look at each slide image and transcribe the text exactly. Then record:

- What slide 1 does and why it stops the scroll
- Slide count and the job of each slide
- Where a product appears, how it's introduced, the exact wording
- Caption, hashtags, sound
- Real photos, generated images, or screenshots
- Which skeleton it fits

The four skeletons:

| Skeleton | Shape |
|---|---|
| Pain funnel | Slide 1 hits a very specific pain. 2-3 make it relatable. 4 brings in the app softly. 5-6 show it working. Last slide CTA. |
| List | 5-7 tips, one per slide. Saved like crazy. Last slide must point at the app. |
| Identity | Who the viewer wants to become. Aesthetic images, short lines. Steady, lower peaks. |
| Quick hit | 2-3 slides. Problem, app, done. For apps that explain themselves. |
| Story (dare / ranking) | Slide 1 forces a swipe (a dare to finish, a ranking where they find themselves). Text-thread drama in the middle. App appears at the turning point as a real screenshot with a casual overlay. Payoff last. |

## Step 4: Write format files

For every structure that shows up 3+ times, write `02-research/formats/<format-name>.md`:

```markdown
# <Format name>
Skeleton: <one of the five, or new>
Status: testing | winner | retired
Examples: <3 links>

## Slide by slide
1. ...

## Where the app goes
Slide N, introduced as ...

## Hook templates (10, written for this app)
1. ...

## Notes
What makes it work. What to avoid.
```
