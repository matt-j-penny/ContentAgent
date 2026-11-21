---
name: video-manifest
description: "Create or update a Video Manifest: an HTML page plus manifest.json that tells an AI exactly how a creator edits videos, covering pacing and cut tightness, J/L cuts, audio, music, SFX, transitions, camera, B-roll, layouts and PIP positions, layout switching, video structure, captions, motion graphics style and placement, a template bank, colour, effects, and the AI edit workflow, with per-platform profiles. Builds it from any mix of: NLE projects (CapCut, Palmier Pro, Premiere XML, DaVinci Resolve, FCPXML), the creator's own videos, other people's videos they like, or from scratch using their website/assets and an interview. Use when the user says '/video-manifest', asks for a video manifest, editing style guide, editing rules for AI, or wants to capture/document how they edit."
metadata:
  version: 1.0.0
  last_updated: 2026-11-13
---

# Video Manifest

A Video Manifest is the editing rulebook an AI follows when it edits for this creator. It has two forms:
- `manifest.json`: the source of truth. Other skills read this.
- `manifest.html`: the readable page, generated from the JSON. It has a profile switcher, layout diagrams, a live template bank, and evidence.

Structure is **base + profiles**. `base` holds everything shared. `profiles.<id>` (youtube, shorts, ...) holds only what differs for that format. To apply it, an AI deep-merges the profile over the base.

Follow [references/before-you-start.md](references/before-you-start.md) to select Content OS or standalone mode. Content OS remains the default for creator context; read its profile when connected, or local context in standalone mode. The manifest itself is a local file in either mode: do not claim Content OS stores it or alter remote records without a supported operation and the user's request.

## Files

`V = <folder containing this SKILL.md>`

- `$V/scripts/manifest.py`: `init`, `render`, `gaps`, `lock`
- `$V/scripts/measure.py`: measures a finished video or a dialogue-only audio file (ffmpeg + Deepgram)
- `$V/scripts/nle.py`: reads CapCut drafts, Palmier Pro projects, FCP7 XML (Premiere) and FCPXML (Resolve, FCP)
- `$V/assets/manifest.example.json`: **the schema**. A fully filled example. Match its keys and shapes.
- `$V/references/sources.md`: how to analyse each source type and map results into the manifest
- `$V/references/interview.md`: question bank with defaults and visual previews

Requirements: python3, ffmpeg/ffprobe, yt-dlp (URLs), `DEEPGRAM_API_KEY` (transcription), `OPENROUTER_API_KEY` (only for the `youtube-editing-style` visual read).

## Step 0: Where it lives

Output dir `D`: `contentagent/video-manifest/` in the working directory, unless the user names another location. Do not overwrite an existing manifest or template bank.

- `D/manifest.json` exists → this is an **update**. Read it, bump `meta.version`, set `meta.updated`, and never change anything listed in `_locked`.
- Otherwise: `python3 $V/scripts/manifest.py init D --name "<name>"`. This creates an empty manifest, a `sources/` folder, and the 10 starter templates in `D/templates/`.

## Step 1: Intake

Ask the following in plain language, combining questions when helpful:
1. **What can I build it from?** (multi-select) NLE projects · My own videos · Videos by someone else whose style I like · My website / brand assets (from scratch)
2. **Which formats do you edit for?** (multi-select) YouTube long-form · Shorts/Reels/TikTok · LinkedIn/feed · Podcast clips · Ads

Then collect the actual inputs: draft names/paths, video files or URLs, reference URLs, website URL. For CapCut, list the drafts folder and let them pick. Register each source in `meta.sources` with an id (`nle-1`, `vid-1`, `ref-1`, `web-1`, `int-1`). Create each profile in `profiles` with `label`, `platform`, `aspect`, `description`.

## Step 2: Analyse each source

Follow `references/sources.md` for the source type. Save all raw output under `D/sources/<id>/`. Analyse each source and map its findings to manifest paths with measured or observed provenance.

Tell the user what each source showed as you go: one or two lines per source with the headline numbers.

## Step 3: Write the manifest

Edit `D/manifest.json` directly:
- Use the keys and shapes from `assets/manifest.example.json`. Adding a key is fine when something real doesn't fit. Don't invent values to fill the shape.
- Put shared values in `base`. Put values that differ by format in `profiles.<id>`, and only the differing keys. Arrays replace the base array wholesale, so a profile's `layouts.library` is that profile's full layout list.
- Every value written gets a `_sources` entry (`measured:nle-1`, `observed:vid-2`, `asked:int-1`, `default`).
- Layout regions are `% of frame` from the top-left: `x, y, w, h`, plus `shape`, `radius` (px at 1080p), `border`, `shadow`, `cutout`. Get these right, because the diagrams are drawn from them.
- `structure.beatMap` uses `% of runtime`.
- `repos` lists the GitHub repos and skills the creator builds with: `core` (default for every graphic) and `selective` (only when a beat needs it), each `{repo, url, what, use}`. Ask for them in the interview if the creator has any.
- Conflicts and priority: see the end of `references/sources.md`.

## Step 4: Fill the gaps

```bash
python3 $V/scripts/manifest.py gaps D
python3 $V/scripts/manifest.py gaps D --profile shorts
```

Ask about what's empty using `references/interview.md`, one section per round, recommended default first. From scratch this is the whole interview. With rich sources it may be a handful of questions. If the user wants it done fast, fill the rest with interview defaults tagged `default`. Lock everything the user answered:

```bash
python3 $V/scripts/manifest.py lock D captions.enabled pacing.cutsPerMin
```

## Step 5: Template bank

The bank is a growing library, not a fixed set. Each template is a folder `D/templates/<id>/index.html` registered in `templates[]` (`id, name, category, path, variables, durationSec, use, layouts, profiles, build, origin`).

- **Starter templates** (from `init`) use `../_brand.css` tokens, so they restyle to the brand automatically on render. Remove any that don't fit the creator's style.
- **Extracted templates** come from `mograph-snatcher` or from frames of the creator's videos. Recreate them as HTML that renders on its own in an iframe. HyperFrames output is fine. Prefer brand tokens over hard-coded colours.
- **New templates** that a style calls for but nothing supplies: build them in the motion style from `motionGraphics.motion`. Match the starter pattern: `[data-var]` text slots filled from the URL query, and `body[data-loop]` to loop the preview.
- Categories: titles, lower-thirds, callouts, data, lists, quotes, social-proof, frames, dividers, captions, ctas, transitions, backgrounds.

## Step 6: Render and review

```bash
python3 $V/scripts/manifest.py render D
```

Open `D/manifest.html` for the user. Serve `D` with `python3 -m http.server` and open it in the built-in browser, or `open` it locally. Check that the brand, layouts and templates sections render correctly in base and each profile. Then tell the user in a few lines:
- what was **measured** vs **observed** vs **defaulted**
- the 3–5 defining rules of their edit
- anything uncertain worth checking

Apply their corrections to the JSON, lock those paths, and re-render. Repeat until they're happy.

## Step 7: Updating later

Re-running the skill with a new source is an update: analyse only the new source, merge by the priority rules, skip `_locked` paths, add new templates to the bank, bump the version, and re-render. Tell the user which values changed.

## How other skills should use it

Read `manifest.json` and select the profile matching the output format. Run `python3 $V/scripts/manifest.py resolve D --profile <id>` to deep-merge it over `base` (arrays replace base arrays). Follow the relevant rules and QA for the current task; do not imply that the manifest performs editing itself. `rough-cut` can use its pacing settings. Use available templates where appropriate.
