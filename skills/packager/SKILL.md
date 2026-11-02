---
name: packager
description: Plans a video's packaging, the title and thumbnail together as a pair. Reads the idea or script, generates and ranks several packaging concepts, uses the titles and thumbnails skills to develop each, and saves the chosen options to the idea's Packaging in Content OS. Use when the user asks to package a video, wants title and thumbnail ideas together, asks how to make a video more clickable, or when a script is done and the idea has no packaging.
---

# Packager

Packaging decides whether anyone clicks. The title and thumbnail are planned as one unit: each carries half of one idea and neither repeats the other.

Follow [`references/before-you-start.md`](references/before-you-start.md) first. Read [`references/titles.md`](references/titles.md) and [`references/thumbnails.md`](references/thumbnails.md).

## Step 1: Understand the video

Find the idea (`list_content_ideas`) and read `premise`, `script_idea`, `thumbnail_ideas`, and existing options (`list_packaging`). Read `list_idea_tips` (the `packaging` section).

Write down:
- **The promise:** what the viewer gets, in one sentence.
- **The audience:** who should click (and who shouldn't).
- **The hook in the video:** the intro's payoff line, which the packaging must match.

If the premise is too fuzzy to package, say so and suggest `outliner`. Packaging before the script is fine (and often helps shape it), as long as the promise is clear.

## Step 2: Concepts

A concept is one angle: the reason someone would click. Draft 4-6 different angles (the result, the mistake, the test, the secret, the comparison, the story), each as:
- **Angle:** one line
- **Title direction:** a draft title
- **Thumbnail direction:** what it shows, in one line
- **The question it opens** in the viewer's head

Rank them on how much the target audience would want it and how honestly the video delivers it. Show the top 3-4 and let the user pick 1-3 to develop.

## Step 3: Develop

For each chosen concept:
- Use the `titles` approach (in `titles.md`) to write and score titles for that angle, with the thumbnail direction as the pairing.
- Use the `thumbnails` approach (in `thumbnails.md`) to write the thumbnail brief for the best title, and generate images if a generator is connected and the user wants them.
- Check the pair: one question between them, no shared words, thumbnail readable small.

If the `titles` and `thumbnails` skills are installed, you can follow them directly; the knowledge files above are enough if they're not.

## Step 4: Save

Read `list_packaging` first. Then for each finished pair, best first:
- `add_packaging {content_idea_id, title, description, image_url}`: `description` is the thumbnail concept in a sentence or two; `image_url` only if a public image URL exists.
- Set `order_index` with `update_packaging` so the recommended option is first (lower is better). Don't reorder or overwrite the user's own options without asking.

Put the rejected concepts and rough notes in `thumbnail_ideas` (read it and add to it). Tick the matching checklist step (`get_idea_checklist`, `set_idea_checklist_item`) if the template has one for packaging.

If the script was written before packaging, check the intro's payoff line still matches the chosen title. If it doesn't, suggest the one-line fix and offer `script-writer`.
