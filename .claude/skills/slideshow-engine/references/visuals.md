# Visuals mode

Makes the images for a set and renders the final slides.

## Step 1: Decide each slide's source

Read `slides.json`. For every slide, use its `image_direction`:

| Direction | Source |
|---|---|
| REAL SCREENSHOT | Copy from `01-app/assets/`. Never generate. |
| A real-world photo (people, places, objects) | The user's photo library or licensed stock first. Generate only if nothing fits. |
| Background, gradient, texture, scene with no people | Generate, or render a flat color (the renderer handles solid backgrounds). |
| Text thread / chat bubbles | Build as a plain image: render the bubbles in the slide's image, or use a solid background and put the thread in `text`. |

Mixing real and generated images matters. All-AI sets read as fake.

## Step 2: Generate

With the Higgsfield MCP (or another image MCP):

1. Write ONE locked scene description for the whole set: setting, lighting, camera ("shot on iPhone, natural light"), color palette. Reuse it word for word in every prompt. Change only what each slide needs.
2. Generate one image at a time, in 9:16 portrait.
3. No text in generated images. The renderer adds text.
4. Never generate app UI, logos, or real people.
5. Save to `images/slide-NN.jpg` (convert PNG to JPEG).
6. If any slide uses a generated image, set `"ai_images": true` in `slides.json`.

Look at every generated image before rendering. Regenerate anything with warped hands, garbled text, or an obvious AI look. After 2 failed tries, flag it for the user to swap in a real photo.

## Step 3: Render

```
python3 <skill>/scripts/render_slides.py 04-sets/<set-folder> --project .
```

The renderer:
- Crops every image to 1080x1920 (cover crop, centered). Screenshots are fitted, not cropped, on a blurred background.
- Writes `final/clean/slide-NN.jpg` (no text, for Humanpost text layers)
- Writes `final/preview/slide-NN.jpg` (text drawn in the safe zone, for review)
- Writes `final/contact-sheet.jpg` (all previews side by side)
- Fills a missing image with a solid color and prints a warning

Optional flags: `--font <path.ttf>`, `--bg "#F4EFE6"` (color for slides with no image).

The renderer also checks the set's account in `06-queue/accounts.json` (`scripts/account_status.py`). If that account has unconfirmed required settings, it refuses that set only. Run `python3 <skill>/scripts/account_status.py --project .` to see every account's readiness.

## Step 4: Check

Open the contact sheet. Check:
- Is every slide readable at phone size?
- Does any text sit under the top status bar or the bottom caption area?
- Is the app slide a real screenshot?
- Does the set look like one person made it?

Fix and re-render before the gate.
