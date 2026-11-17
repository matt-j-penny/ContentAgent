---
name: b-roll
description: Plan and insert full-frame video B-roll cutaways over an existing video while preserving its audio. Use when the user wants to add supplied or appropriately licensed B-roll footage to a video.
---

# B-roll

Follow [references/before-you-start.md](references/before-you-start.md) to choose Content OS or standalone mode. If a local video manifest exists, resolve the matching format profile and follow its B-roll, pacing and layout preferences. Identify the intended audience and source video, then make a timestamped shot list grounded in what is actually said or shown. Do not invent evidence or claim footage was filmed by the creator.

Find suitable footage among user-supplied files, available connected sources or approved generators. Record the source and licence/usage terms; do not assume every search result is reusable. Ask for missing footage or deliver the shot list when no suitable source exists. A connected editor can insert the cutaways if it supports the requested operation; check capabilities rather than claiming an editor integration exists.

## Render video cutaways locally

For a flat file, the included script overlays one or more local video clips full-frame, center-cropped to the source dimensions, while keeping the original audio. It does not add stock footage, insert stills, generate AI video, create editor tracks, or use B-roll audio. It requires Python 3, ffmpeg and ffprobe. Source video dimensions must be even.

Write a JSON file. All timestamps are seconds; paths are absolute or relative to the JSON file. `at` is the destination time and `source_start` is where the B-roll starts. Cutaways must be ordered, non-overlapping and fit inside both files.

```json
{"video":"original.mp4","cutaways":[{"file":"demo.mp4","at":4.0,"source_start":1.0,"duration":2.5}]}
```

`<SKILL_DIR>` is this skill's installed folder. Render to a new path; existing files are never overwritten:

```bash
python3 <SKILL_DIR>/scripts/assemble.py path/to/cutaways.json --out path/to/new-video.mp4
```

Review representative frames before, during and after each cutaway, and check original audio sync and source attribution. If the output is incomplete, report the failure and retain the original and plan. The rendered file is not an editable timeline.
