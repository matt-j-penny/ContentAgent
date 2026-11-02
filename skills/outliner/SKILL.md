---
name: outliner
description: Turns a content idea and its research into a strong video outline before any script is written. Long form gets hook, promise, sections with beats, payoff and CTA; short form gets hook, open loop, value beats and payoff. Interviews the user for their own stories, examples and opinions, and can map the outline to Content OS storyboard sections. Use when the user asks to outline, structure or plan a video, or when an idea is researched and ready for scripting.
---

# Outliner

The outline is where a video is won or lost. It decides the promise, the order and the payoff; the script just says it well. Get the user's approval on the outline before anyone writes a script.

Follow [`references/before-you-start.md`](references/before-you-start.md) first. Read `list_idea_tips` (the `premise` and `script` sections).

## Step 1: The idea

Find the idea (`list_content_ideas`; ask which if unclear) and read its premise, research fields, inspiration and packaging. Read any local research in `contentagent-work/research/`.

If the premise is vague or there's no research on a topic that needs facts, say so and offer `researcher` first. A short opinion or story video may not need research.

Move it to `Scripting` (`move_content_idea`, `expected_status` = its current status) if it's in `Idea` or `Researching`.

## Step 2: Lock the core

Agree these three with the user before outlining. If they're not right, nothing else matters.

1. **Promise:** what the viewer gets, in one sentence. Must match the title and thumbnail if packaging exists.
2. **One point:** the single idea the video makes. Everything in the outline serves it.
3. **Payoff:** the most satisfying moment, and where it lands (late, not first).

## Step 3: Interview

Ask for what only the user has. One or two questions at a time:
- Their own story, result or mistake related to this topic.
- Examples, screenshots or demos they can show (these become proof).
- Their opinion: where they disagree with the common advice.
- Anything they must include or must avoid.

Use their answers in the outline. Where something is still missing, put a clear placeholder (`[your result with X]`), never an invented story or number.

## Step 4: Outline

### Long form (`YT Long Form`)

An intro in four beats, then sections:

1. **Intro (20-40s):** payoff line (restates the title's promise), social proof, context, setup (what they'll walk out with, plus one teased detail).
2. **Sections (3-7):** for each, a heading, its job (what the viewer learns or feels), the beats in order, the example or proof, and a re-hook into the next section ("but that only works if…").
3. Order sections so value builds: quick win early, best part late, never a slow stretch after the intro.
4. **Payoff:** where the promise is fully delivered.
5. **CTA:** one, and the one that fits the offer (a link, lead magnet, related video). Place it where it helps, not where it interrupts.

Note estimated length per section. Mark where visuals carry the beat (demo, screen recording, B-roll, graphic).

### Short form (`Short Form`)

1. **Content type:** new tool, news, tutorial, opinion or comparison. It decides the middle.
2. **Hook (0-3s):** 3 options, each with spoken line, on-screen text and the opening visual.
3. **Open loop (3-8s):** continues the hook and names a consequence for the viewer.
4. **Value beats (8-35s):** the beats for that content type, one idea, numbered out loud if more than one item (max three).
5. **Payoff:** definite statement, starts with "So".
6. **CTA or caption keyword**, if any.

Target 30-45 seconds.

## Step 5: Approve and save

Show the outline. Iterate until the user approves it.

Where it lives:
- **Default:** local in `contentagent-work/outlines/<idea>.md`, and in the conversation.
- **If the user wants it in the app:** add the section headings as toggles under the existing premise (read the premise first; add, don't replace).
- **If the user asks for a storyboard:** `create_storyboard_section` for each section in order, and `create_video_segment` for each beat with `title`, `section_id`, `talking_points` (HTML), `screen_direction` (HTML), `visual_type` and `status: "planning"`. Check `list_storyboard_sections` first so you don't duplicate.

Then hand off to `script-writer` with the idea and the approved outline.
