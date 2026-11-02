---
name: titles
description: Writes and scores YouTube titles, plus Instagram and Shorts on-screen hook text and caption first lines, for a content idea. Uses the Vault's proven titles and hooks as patterns, the user's saved title inspiration and niche outliers, and scores each option for clarity, desire, specificity, believability, fit and pairing with the thumbnail. Use when the user asks for titles, title ideas, to improve or score a title, or for on-screen hook text or a caption opener.
---

# Titles

Writes titles that are clear, wanted and honest, and scores them so the best one is obvious. Usually called by `packager` for a concept; can be used on its own.

Follow [`references/before-you-start.md`](references/before-you-start.md) first. Read [`references/titles.md`](references/titles.md) every time; for short form also [`references/hooks.md`](references/hooks.md).

## Inputs

- The idea: `name`, `premise`, `script_idea` if written, and existing packaging (`list_packaging`).
- If called by `packager`: the thumbnail concept this title must pair with.
- Style profile and About You (audience words, channel tone).
- `list_idea_tips` (the `packaging` section, Title subsection).
- `list_vault_titles` (long form) or `list_vault_hooks` (short form): proven patterns. `X`/`Y` and `[brackets]` are placeholders.
- `list_inspiration {kind: "youtube_title"}`: titles the user likes. Their taste beats the Vault when they differ.
- Niche conventions: 10-20 recent outlier titles in the niche (vidIQ, competitors' channels or `researcher`), if not already gathered this conversation.

## Write

1. Name what the video truly delivers, in one sentence. Every title must be true to it.
2. Write 10-15 candidates across at least 4 different patterns from `titles.md` and the Vault. Adapt patterns to the topic; never copy a Vault or competitor title word for word.
3. Cut anything the video can't deliver, anything over ~70 characters, and near-duplicates.
4. Score the rest with the table in `titles.md` (1-5 each). Check character count and that the hook is in the first five words.

For short form, write instead: 5-8 on-screen hook texts (3-8 words) matched to the spoken hook, 3 caption first lines, and for YouTube Shorts 3 titles under 40 characters.

## Show

The top 5, ranked, as a table: title, characters, pattern, total score, one-line reason. Then your pick and why. If pairing with a thumbnail, show how each pairs.

Let the user mix and edit. If they reject a style ("no questions in titles"), suggest adding it to the style profile.

## Save

- Called by `packager`: return the chosen titles; `packager` saves them.
- On its own: ask where. A finished title goes on a Packaging option (`add_packaging {content_idea_id, title}`, or `update_packaging` on an existing one after reading `list_packaging`). Rough lists go in `thumbnail_ideas` (read it first and add to it, don't replace).
- A title the user loves from elsewhere: `save_inspiration {kind: "youtube_title", title, url}` when they ask.

Never change the idea's `name` to the packaged title unless the user asks; `name` is the working title.
