---
name: script-writer
description: Writes a YouTube long-form or short-form (Reels, TikTok, Shorts) script from an approved outline, in the user's own style, then line-edits it and saves it to the content idea in Content OS. Asks the user for stories and details instead of inventing them, and uses the Vault's proven hooks as patterns. Use when the user asks to write, draft, rewrite or punch up a script, hook or intro, or when an outline is approved and ready to script.
---

# Script writer

Writes the script from the approved outline, in the user's voice, and saves it to the idea. The outline decides what's said; this skill decides how it sounds.

Follow [`references/before-you-start.md`](references/before-you-start.md) first. The style profile matters most here: if it's missing, offer `style` first.

## Step 1: Inputs

- **The idea:** `list_content_ideas`, then its `premise`, research fields, `script_idea` (is there already a script?) and packaging (`list_packaging`; the script must deliver the title's promise).
- **The outline:** from the conversation or `contentagent-work/outlines/`. If there's no approved outline, run `outliner` first. For a short script on a simple topic the user can skip it, but then agree the one point and the payoff before writing.
- **Style profile** from `get_agent_profile`.
- `list_idea_tips` (the `script` section).
- Short form: `list_vault_hooks` for hook patterns, plus `list_inspiration` for hooks the user likes.

If a fact or story the outline needs is missing, ask the user. Never invent results, numbers, quotes or personal stories. Leave a visible placeholder `[…]` if they want to fill it later.

## Step 2: Write

### Short form
Follow [`references/short-form.md`](references/short-form.md) step by step: validate the idea, classify the content type ([`references/content-types.md`](references/content-types.md)), 3 hook options ([`references/hook-library.md`](references/hook-library.md) plus the Vault hooks as patterns, never copied word for word), open loop, value delivery, retention locks ([`references/story-locks.md`](references/story-locks.md)), payoff, and the pressure test. Story-driven pieces can use [`references/frameworks.md`](references/frameworks.md).

### Long form
1. **Intro:** follow [`references/long-form-intro.md`](references/long-form-intro.md) (payoff, social proof, context, setup).
2. **Body:** one `<h2>` section per outline section. Each section opens by paying off the previous re-hook, delivers its beats with the example or proof, and ends with a re-hook into the next. Same sentence craft as short form ([`references/story-locks.md`](references/story-locks.md)): spoken, specific, varied rhythm, no filler.
3. **Payoff and CTA** as outlined. No "like and subscribe" padding, no long outro.
4. Write it as the user would say it, not as they'd write it. Target about 150 spoken words per minute for the planned length.

### Both
- Apply the style profile: their phrases, rhythm, openers, words to avoid. Their style wins over the generic advice in the references when they disagree.
- Visual notes go in edit-direction callouts, never inside spoken lines.

## Step 3: Line edit

Run the line edit in [`references/script-check.md`](references/script-check.md) on the draft. If your app can run a subagent, give it that file and the script so it reads with fresh eyes; otherwise do it yourself as a separate pass. Apply the rewrites that make it sound more like the user, and check the result against the style profile.

## Step 4: Show and revise

Show the user:
1. Short form: the 3 hooks with your pick, the script (spoken | on screen), word count, runtime and the sentence-length map. Long form: the script by section with estimated runtime.
2. Any placeholders that still need their input.

Revise until they're happy. When they push back on wording, ask if it's a general rule; if so, offer to add it to the style profile (`style`).

## Step 5: Save

Read the idea again first. Then `update_content_idea {id, fields: {script_idea}}` using the HTML script format in [`references/content-os.md`](references/content-os.md):
- Spoken lines as `<p>`, one thought per paragraph.
- Long form: `<h2>` per section. Short form: one block, hook first in `<strong>`.
- Visual notes as `<div data-edit-direction-callout=""><p>…</p></div>`.
- No Markdown, no stage directions in brackets.

If `script_idea` already holds a script, ask: replace it, or add the new one below `<h2>Draft 2</h2>`.

Once the user approves the saved script, move the idea to `Planning Filming` (`move_content_idea`, `expected_status: "Scripting"`). Add open tasks (record B-roll of X, get screenshot of Y) to `todo` as checklist items, appending to what's there.

Suggest `packager` if the idea has no packaging yet.
