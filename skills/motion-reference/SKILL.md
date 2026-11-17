---
name: motion-reference
description: Analyse and recreate a motion graphic from a reference video using timestamped contact sheets and available motion-design tools. Use when the user wants to study, recreate or adapt a particular video graphic.
---

# Motion reference

Follow [references/before-you-start.md](references/before-you-start.md) for Content OS or standalone mode. Read the creator's local video-manifest profile where available. Identify the source video, relevant time range and whether the user wants analysis, an editable template or a rendered graphic. Use footage the user supplies or can access. Recreate visual techniques using editable placeholders; do not embed a third party's logo, face or footage as the user's own asset.

## Inspect the reference

The included helper needs Python 3, Pillow, ffmpeg and, for URLs, yt-dlp. `<SKILL_DIR>` is this skill's folder. Use a new working directory under the current project. For a URL:

```bash
python3 <SKILL_DIR>/scripts/snatch.py download '<video-url>' contentagent/motion-reference
python3 <SKILL_DIR>/scripts/snatch.py scan contentagent/motion-reference/<video-id> --every 2
python3 <SKILL_DIR>/scripts/snatch.py dense contentagent/motion-reference/<video-id> segment-01 12 16 --fps 6
```

For a local file, put a copy named `source.mp4` in a new work directory and run `scan` and `dense` against that directory. The scan makes timestamped contact sheets; dense capture produces frames and a reference clip for one interval. Output folders must be new; do not delete or overwrite existing frames. Inspect the sheets and verify boundaries, especially fast entrances and exits.

Document each graphic's layout, visual style, timing, entrance, hold, exit, and editable elements. Distinguish observed details from estimates. Use the creator's own brand where requested.

## Build when requested

Discover an available motion-design tool, such as the host's HyperFrames or another supported editor. Use its real installed capabilities to create editable text, colors and media placeholders; do not claim a template was built if the tool is absent. Render or preview representative frames and compare them to the reference for timing and layout. Save the analysis, source attribution and editable result locally in the project. Apply a template to a separate video only when requested, and preserve that video's source. If the necessary tool or footage is unavailable, deliver the visual analysis and explain the missing capability.
