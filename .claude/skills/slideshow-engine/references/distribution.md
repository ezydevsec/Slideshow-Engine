# Queue mode (Humanpost)

Sends approved sets to Humanpost. Humanpost assigns real people who create the accounts on their own phones, warm them up, and post by hand.

## Before anything

1. Check the Humanpost MCP is connected. If not, give the user this command and stop:
   ```
   claude mcp add --scope user --transport http humanpost https://us-central1-clickbaitcarousel.cloudfunctions.net/mcp --header "Authorization: Bearer YOUR_API_KEY"
   ```
   The key comes from the Humanpost dashboard: Settings → API & MCP.
2. List the Humanpost tools and read their schemas. Tool names can change. Do not guess parameters.
3. Read the company context and usage (plan, account limit, posts left this cycle). If this batch would exceed the plan, say so and ask which sets to drop.

## One-time: accounts

Only when the user asks to create accounts, or none exist.

For each persona in `personas.md`, design accounts:
- Username, display name, bio. **Theme page, never a brand account. No app name anywhere in the profile.**
- Profile photo direction
- 1 to 5 warm-up search terms (from the persona's list)

Show the full list. Create nothing until the user says yes. Then create each account and save the returned IDs to `06-queue/accounts.csv`:

```
account_id,platform,username,persona,created_on,status
```

New accounts need to finish warm-up before they post. Check account status before queueing to them.

## Each batch

For every set marked `approved` in `06-queue/queue.csv`:

1. **Upload** `final/clean/slide-NN.jpg` in order (use the batch upload tool if there is one).
2. **Create a draft** with:
   - `media`: the uploaded images in slide order
   - `slides`: one entry per slide with its `role` and one text element from `slides.json`. Map `text_mode` straight across (`stroke`, `background`, `plain`). Use positionY around 30 for `upper`, 50 for `middle`, 70 for `lower`, and width around 85.
   - `caption` and `hashtags` from `slides.json`
   - `sound`: `{"mode": "trending"}` unless the set names a specific sound URL
   - `notes` for the poster. Always include: "Please add a trending sound that fits the mood." If `ai_images` is true, also include: "Please turn on TikTok's AI-generated content label before posting."
   - content tags for format, trend, and hook ID (create the tags first if they don't exist)
3. **Render the preview** and look at it. If text overlaps badly, fix the positions and re-render.
4. **Queue** the draft to accounts:
   - Each queue call takes at most one TikTok account and one Instagram account.
   - Pick accounts whose persona matches the set's persona.
   - Never send the same set to the same account twice (check `06-queue/` manifests).
   - Never more than 4 posts per account per day (Humanpost's hard limit).
   - **Never set `skipApproval: true`.** Posts wait in the Humanpost dashboard for the user's final approval.
5. Append to `06-queue/YYYY-MM-DD-manifest.csv`:
   ```
   set_id,post_id,account_id,platform,format,trend,hook_id,queued_at,status
   ```

## Never

- Never create comment or Amplify tasks. Coordinated engagement between our own accounts breaks TikTok's authenticity rules.
- Never post a set that wasn't approved at GATE 3.
- Never retry a failed create blindly. Check whether it went through first (use idempotency keys if the tool supports them).

## Report

List what was queued: set, accounts, earliest posting window. Remind the user to approve the posts in the Humanpost dashboard.

## No Humanpost?

Zip `final/clean/`, `slides.json`, and the caption for each approved set into `06-queue/export-YYYY-MM-DD/` so a VA or another scheduler can post them.
