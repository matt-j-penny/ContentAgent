---
name: screen-recording
description: Plan, record or edit a screen-share video with an available screen-recording app or connected editor. Use for software demos, screen recordings and webcam-over-screen clips.
---

# Screen recording

Follow [references/before-you-start.md](references/before-you-start.md) for Content OS or standalone mode. Use the current outline and the creator's video-manifest profile where available. Identify the demonstration, target app or display, audio, webcam, aspect ratio and whether the user wants a recording, an edited existing recording, or only a plan. Preserve private windows and notifications; do not start a recording without the user asking for one.

## Record

Use an available host screen-recording tool or the user's installed recorder. Check its actual capabilities and required permissions; do not claim an integration exists when it is unavailable. If the recorder needs interactive display selection, let the user select the intended screen or window. Check microphone and system-audio choices, then record only the requested content. If recording cannot be controlled from the host, provide a concise capture plan and let the user record manually.

## Edit

For proposed camera-versus-screen layouts, use `gaze-analysis` when available. Its head-orientation measurement is only supporting evidence; it does not establish eye gaze.

If the user has Matt's Recordly installed with its `matts-editor` CLI, discover the CLI with `command -v matts-editor`, or use the packaged launcher in the app if present. Inspect `--help` and `app capabilities --json` for the installed version before using commands. Its documented features include opening a recording, previewing, suggesting or applying zooms, captions, project save and export. The exact command schemas come from the running app, and the CLI needs an available editor instance. Do not imply ordinary Recordly installations include this fork's CLI.

For another editor, use only the connected tools it actually exposes. Preserve the source and existing project; prefer a new project or copy when editing. Use the current user preferences and video-manifest profile for framing, zoom, captions and audio, then verify timing and output visually. If no compatible editor is available, return a timestamped edit plan with the missing capability explained.
