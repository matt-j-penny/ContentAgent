---
name: audio-design
description: Select and mix supplied music and timed sound effects into a video, with music ducked under dialogue. Use when the user asks for background music, sound effects, or a dialogue-friendly audio mix.
---

# Audio design

Follow [references/before-you-start.md](references/before-you-start.md) to choose Content OS or standalone mode. If a local video manifest exists, resolve the relevant profile and use its music, SFX, pacing and audio preferences. Ask for the actual video and music or sound-effect files when they aren't available. Only use assets the user has supplied or can legitimately use; retain source and licence/attribution details. Use a connected provider only when available and appropriate. Do not claim a bundled music library or generate assets silently.

## Plan

Identify the source video, desired mood, and specific moments for sound effects. Respect explicit creative choices and leave dialogue intelligible. Generate a short list of music and SFX placements using real timestamps; don't add arbitrary effects throughout. A connected editor can place the tracks if the user wants an editable project and that editor actually supports it. Otherwise, use the local mixer below, which renders a new file and leaves the original untouched.

## Mix local files

Requires Python 3, `ffmpeg` and `ffprobe`. Input video must have video and audio streams. The music track loops if needed, is ducked under the original audio using sidechain compression, and ends with the video. Sound effects are delayed to the given timestamps. Gains are linear (1 is unchanged, 0.15 is quiet); start low, listen, then adjust. The limiter caps peaks but does not replace listening and proper loudness review.

Write a JSON file in a working directory, resolving relative paths from that file:

```json
{"video":"input.mp4","music":{"file":"music.wav","gain":0.15},"sfx":[{"file":"click.wav","at":4.2,"gain":0.35}]}
```

Music is optional if at least one SFX is supplied, and `sfx` can be empty if music is supplied. `<SKILL_DIR>` is this skill's installed folder:

```bash
python3 <SKILL_DIR>/scripts/mix.py path/to/mix.json --out path/to/new-video.mp4
```

Output must not already exist. Inspect the result at the beginning, dialogue, loud sound effects and end; check sync, clipping, music ducking and any necessary credits. Revise gains or placements and render to a new file if needed. Report the path and any missing source/licence information. The mixer makes a flat rendered file, not editable editor tracks. On ffmpeg failure, report it and treat any partial output as incomplete.
