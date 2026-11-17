---
name: programmatic-short
description: Create a simple vertical faceless short from a sequence of supplied images and optional narration. Use when the user asks for an image-based short video assembled programmatically.
---

# Programmatic short

Follow [references/before-you-start.md](references/before-you-start.md) for Content OS or standalone mode. Use the creator's brand, voice and relevant video-manifest short-form profile when available. Develop or reuse a script, then create a shot list with one meaningful visual per beat. Use supplied media or a connected image/voice generation tool when available; respect source licences and never claim an unavailable generator ran.

The included offline renderer makes a vertical MP4 from local PNG, JPEG or WebP images and an optional local narration track. It cuts between stills. It does not generate images or speech, add captions, animate images, produce editor tracks, or publish. Use a connected tool for those requested capabilities when actually available, or explain the limitation. Requires Python 3, ffmpeg and ffprobe.

Write a manifest with paths relative to the manifest file. Scene durations are in seconds, from greater than zero to 60; the sequence may contain up to 30 images. Shorter narration is padded to the sequence length; narration longer than the scene sequence is rejected so that speech is not cut off.

```json
{"width":1080,"height":1920,"fps":30,"narration":"voice.wav","scenes":[{"image":"scene-1.png","duration":3},{"image":"scene-2.png","duration":4}]}
```

Omit `narration` for a silent video. Render to a new filename:

```bash
python3 <SKILL_DIR>/scripts/render.py path/to/short.json --out path/to/new-short.mp4
```

Inspect each transition and check image framing and narration timing. If audio is longer than the scene sequence, extend scenes rather than silently truncating meaningful speech. Use `audio-design` for supplied music or sound effects. If captions or motion are requested, add them using a verified compatible tool; do not claim they are present otherwise. Retain the manifest, source assets, credits and final output in the project, and preserve original files.
