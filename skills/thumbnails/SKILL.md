---
name: thumbnails
description: Designs YouTube thumbnail concepts (and Shorts or Reels covers) for a content idea as clear briefs, scores them, and generates the images when an image-generation tool is connected, then saves them to the idea's packaging in Content OS. Use when the user asks for thumbnail ideas, a thumbnail concept or brief, to generate or critique a thumbnail, or for a Reel or Short cover.
---

# Thumbnails

Turns an idea into thumbnail concepts that win at stamp size, and into images when a generator is available. Usually called by `packager` for a concept paired with a title; can be used on its own.

Follow [`references/before-you-start.md`](references/before-you-start.md) first. Read [`references/thumbnails.md`](references/thumbnails.md) every time.

## Inputs

- The idea: `name`, `premise`, script if written, existing packaging (`list_packaging`) and `thumbnail_ideas`.
- If called by `packager`: the title this thumbnail must pair with.
- `list_idea_tips` (the `packaging` section, Thumbnail subsection).
- `list_inspiration {kind: "youtube_thumbnail"}`: thumbnails the user likes (the URL is the video; look at its thumbnail).
- The user's recent thumbnails (`list_youtube_videos`, then `https://i.ytimg.com/vi/<id>/maxresdefault.jpg`): their current style, and what to stand out from.
- Niche outliers' thumbnails, if research was done this conversation.

## Concepts

1. Name the feeling or question the thumbnail should create, in one line.
2. Draft 4-6 concepts across at least 3 concept types from `thumbnails.md`.
3. Write each as a full brief (concept type, focal point, composition, face and expression, text, colours, why it pairs with the title).
4. Score each with the table in `thumbnails.md`. Drop anything that fails at small size or repeats the title's words.
5. Show the top 3 ranked, with your pick.

To critique an existing thumbnail: view it, score it, and give the 2-3 changes that would most improve it.

## Images

If an image generator is connected and the user wants images:
- Follow the generation rules in `thumbnails.md` (16:9; no real people other than the user, and only from their own photo; text added afterwards unless the generator spells well).
- 2-4 variants for the chosen concept. View each at small size and drop weak ones before showing.
- If the user wants their face in it, ask for a photo, or generate the scene with a clear space for them.

No generator: the brief is the deliverable. Mention that connecting one lets you produce images.

## Save

- Called by `packager`: return the briefs and image URLs; `packager` saves them.
- On its own: ask where. A finished option is a Packaging entry: read `list_packaging`, then `update_packaging {id, description, image_url}` on the option with the paired title, or `add_packaging {content_idea_id, description, image_url}`. `description` is the one- or two-sentence version of the brief.
- `image_url` must be a public URL. If the generator only gives a local file, tell the user where it is and leave `image_url` empty; they can upload it in the app.
- Rough concepts go in `thumbnail_ideas` (read it, add to it, don't replace).
