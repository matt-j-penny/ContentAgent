---
name: short-clip
description: Create a vertical short or Reel from a selected interval of a local longer video. Use when the user asks to cut and reframe a long-form video into a short clip.
---

# Short clip from a longer video

Follow [references/before-you-start.md](references/before-you-start.md) to choose Content OS or standalone mode. Use `repurpose` to identify moments that stand alone and the creator's local video-manifest short-form profile if available. Use a transcript or source footage to verify the chosen start, end and meaning; never invent quotes. Establish the source file and selected interval.

The local renderer below creates a single vertical MP4 from a local source, re-encodes video and audio, and uses a static center crop with an optional horizontal focus. It requires Python 3, ffmpeg and ffprobe. It does not track moving faces, add captions, add a hook overlay, publish, or make an editable timeline. When those are requested, use a capable connected tool if available or clearly report what remains.

```bash
python3 <SKILL_DIR>/scripts/clip.py /path/to/source.mp4 --start 45.0 --duration 20.0 --focus-x 0.5 --out /path/to/new-short.mp4
```

`--focus-x` selects the horizontal focus from 0 (left) to 1 (right); default 0.5. Use even portrait dimensions (`--width` / `--height`) if different from 1080×1920. Output must not already exist. Inspect frames throughout the clip for framing, missing visual context and the subject moving outside the crop; listen for clean audio and check the beginning and end. If a static crop cannot keep important content visible, deliver a cut plan for an editor that can reframe dynamically rather than claiming the result is complete. Preserve the original and never post automatically.
