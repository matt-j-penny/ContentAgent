---
name: carousel-generator
description: Create Instagram carousel slides and captions from a topic or video, reuse and save carousel templates, and render optional video slides. Use when the user asks for a designed carousel, a reusable carousel design, or a carousel with clips from a video.
---

# Carousel generator

Follow [references/before-you-start.md](references/before-you-start.md) first. Content OS is the default. In standalone mode follow [references/standalone.md](references/standalone.md). Use the creator's actual brand, voice, audience and offer from the selected source or their input; never invent facts, links or proof. For repurposed content, use [references/formats/carousel.md](references/formats/carousel.md). A user-supplied image or typographic cover works without an image-generation service.

## Prepare the content

Identify the topic or source video, intended audience and desired outcome. If starting from a video, read its transcript or use material supplied by the user, select self-contained moments and verify timestamps against the source. Write concise slide copy and a caption in the creator's voice. Choose a CTA suited to their actual objective; do not force an offer. Where appropriate, route research through `researcher` or source selection through `repurpose`.

## Create or reuse a design

`<SKILL_DIR>` is this skill's installed folder, such as `~/.contentagent/skills/carousel-generator`, not the user's current working directory. Run these commands from the user's project folder. Requires Node.js; final rendering needs Playwright and Chromium. Run `bash <SKILL_DIR>/install.sh` once if needed. It installs dependencies and Chromium. Video slides additionally need `ffmpeg`.

```bash
node <SKILL_DIR>/scripts/library.js list
node <SKILL_DIR>/scripts/library.js new ai-system-breakdown my-carousel
node <SKILL_DIR>/scripts/library.js save path/to/carousel.json my-template
```

`list` combines bundled templates with the user's project-local templates in `contentagent/carousel-templates/`. `new` creates `contentagent/carousels/<slug>/carousel.json`; `save` stores a reusable template without embedded base64 images. Names and slugs use letters, numbers, hyphens and underscores. Existing files are not overwritten. Set `CONTENTAGENT_CAROUSEL_TEMPLATES` to use another template directory. Replace placeholder copy, links and asset paths before rendering; do not reuse the previous creator's claims.

The manifest contains `slug`, `topic`, `theme`, `font`, `handle`, `slides` and optional `caption`. Slide types: `cover`, `cover_image`, `statement`, `list`, `media`, `stat`, `quote`, `cta`. The bundled templates and `scripts/smoketest.json` demonstrate the fields. Use one coherent theme and font. Relative image and video paths resolve from the manifest directory. A `cover_image` needs an `image`; otherwise use a `cover`. Add text separately from the cover image. Use a connected image generator only if wanted; `scripts/cover.py` optionally supports an authenticated Higgsfield CLI and may incur charges. It reads reference photos from the current project's `assets/face-refs`; use them only at the user's request.

## Add video slides

Video slides are optional. Set `source_video` to a local file and add a `video` object to `cover_image` or `media` slides, for example:

```json
{"type":"media","headline":"A useful moment","image":"frames/example.png","video":{"start":15,"duration":6}}
```

`start` and `duration` are seconds. `video.src` overrides `source_video`; `crop` accepts `W:H:X:Y`; `speed` is a duration multiplier (1.4 makes the output 40% slower). A video slide needs a matching still image for preview and its PNG fallback. Clips are silent unless `video.audio` supplies a separate `src` and optional `start`. Check source timestamps and duration, and use footage the user provides or can access.

## Preview and render

```bash
node <SKILL_DIR>/scripts/render.js path/to/carousel.json --preview --no-open
node <SKILL_DIR>/scripts/render.js path/to/carousel.json --scale 1 --no-open
```

Preview shows stills; inspect the HTML and revise before final rendering. The final command produces PNG slides, a caption, a contact sheet, and an MP4 for each video slide beside its PNG. Inspect the contact sheet and sample each video slide for correct content, timing and legibility. Report any missing media or render failure instead of claiming success. If the rendering prerequisites are unavailable, deliver the slide copy and manifest and explain what is needed.

## Save

In Content OS mode, when the user asks to save the result, follow `repurpose`: create or update the appropriate idea only after reading existing content and with the user's agreement; record slide copy and caption in supported fields. Local output files remain local unless explicitly uploaded by a supported integration. In standalone mode keep the manifest, template and exports in the local workspace. Do not publish or post automatically.
