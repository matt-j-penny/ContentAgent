---
name: repurpose
description: Turns one piece of content into others. Long-form YouTube videos become short-form clips or rewritten shorts; shorts and long-form sections become Instagram carousels. Finds the best moments, writes each piece to a format template in the user's style, can produce carousel slides and images when tools are connected, and adds the new pieces to the short-form board in Content OS. Use when the user asks to repurpose, cut shorts or clips from a video, turn a video into a carousel, or get more content out of something they've published.
---

# Repurpose

Gets more out of content the user already made. Each new piece must stand on its own; nobody should need the original to understand it.

Follow [`references/before-you-start.md`](references/before-you-start.md) first. Format templates:
- Long form → shorts: [`references/formats/short-from-long.md`](references/formats/short-from-long.md)
- Video or short → carousel: [`references/formats/carousel.md`](references/formats/carousel.md)
- Hooks for both: [`references/hooks.md`](references/hooks.md)

## Step 1: The source

Find it: a content idea (`list_content_ideas`), a YouTube video (`list_youtube_videos`), an Instagram post, or something the user pastes. Get the words:
- The idea's `script_idea`, if the video followed it closely.
- Otherwise the real transcript, with timestamps when cutting clips: a transcript tool, `yt-dlp --write-auto-subs --skip-download`, or `video-breakdown` for a short.
- For long form, the retention graph helps find the best moments; ask the user for a YouTube Studio screenshot if they want it used.

Ask which output they want if it isn't clear: shorts, carousels, or both.

## Step 2: Find the pieces

Go through the source and list every candidate moment that could stand alone (the rules in each format file say what qualifies). For each: what the one point is, where it is (timestamps or section), the hook it could open with, and the format it suits.

Rank by hook strength and payoff, and show the top candidates (3-8 for a 10-20 minute video). Let the user pick.

## Step 3: Write each piece

Fill in the template from the format file for every chosen piece, in the user's style (`get_agent_profile`):
- **Shorts:** decide clip or rewrite. Clips get a cut plan with in/out timestamps and the hook; rewrites get a full short-form script (hook, open loop, value, payoff), using `list_vault_hooks` as patterns. If `script-writer` is installed, use it for rewrites.
- **Carousels:** every slide's exact text and visual, plus the caption.

Show them all and revise with the user.

## Step 4: Produce assets (when asked and possible)

- **Carousel slides:** follow the producing routes in `carousel.md`: HTML rendered to images if there's a terminal and a browser tool, an image generator for backgrounds or illustrations, or the brief alone. Keep files in `contentagent-work/repurpose/<source>/`. Use the user's brand colours and fonts, and ask if they're unknown.
- **Clips:** cutting video needs the source file and `ffmpeg`. With both, you can cut rough clips from the timestamps (`ffmpeg -ss <start> -to <end> -i source.mp4 -c copy clip.mp4`) for the user to finish in their editor. Otherwise the cut plan is the deliverable.

Tell the user where every file is.

## Step 5: Save to Content OS

Ask first, then for each piece:
- `create_content_idea` on the short-form board: `name`, `content_type: "Short Form"`, a `premise` (one-line premise, plus the source: "From <long-form title>, 4:12-5:01"), and the original's `tags`. It lands in `Idea`.
- A rewrite that's finished and approved: save its script to `script_idea` in the script HTML format from `content-os.md`, then move it to `Planning Filming` with the user's OK (from `Idea`: through `Scripting` first, one move at a time).
- A clip that only needs cutting: add the cut plan to `todo` as checklist items.
- A carousel: create it as a `Short Form` idea too, with the slide text in `script_idea` (one `<h2>` per slide) and the caption at the end.

Don't change the source idea, except adding a `todo` item like "Cut 3 shorts (see Short-form board)" if the user wants a reminder.
