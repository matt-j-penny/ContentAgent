---
name: storyboard
description: "Build a review storyboard for a video's motion graphics, checked against the creator's Video Manifest: one static frame per graphic with Accept, Revise (with a note) and New idea, answers saved locally, and an Apply comments button that turns notes into new options. Then build the graphics from the accepted frames. Use whenever the user asks to create, make or build a storyboard, storyboard a video, intro or section, plan graphics as a storyboard, or work through storyboard comments or review answers."
metadata:
  version: 1.0.0
  last_updated: 2026-11-22
---

# Storyboard

A local review page: one card per graphic (B1, B2...), each showing only its ID, a still of the frame, the spoken line, three buttons (Accept, Revise with comment, New idea) and a note box. Every answer saves to `review.json`. The page checks every frame against the creator's Video Manifest.

`S = <folder containing this SKILL.md>/scripts`

- `$S/storyboard.py`: `serve`, `check`, `next`, `apply`, `selftest`. The board format is in its docstring: read it before writing `board.json`.
- `$S/revise.py`: the Apply comments button. Runs the Claude Code CLI sealed (no tools, no MCP, minimal environment), validates the JSON it returns, backs up to `<board>/history/`.
- `$S/proxy.py`: low-res `media/cam.mp4` and `media/screen.mp4` from a Palmier Pro timeline, on the timeline clock.
- `assets/launcher.applescript`: the double-click app that opens a board.

Needs `python3`, `ffmpeg`, a Deepgram key (`DEEPGRAM_API_KEY`) and, for Apply, the `claude` CLI.

## Before starting

1. **Find the Video Manifest** (`manifest.json`, made by the `video-manifest` skill) and the profile for this video (e.g. `youtube`, `shorts`). If you can't find it, ask for the path. If there is none, offer to run `video-manifest` first.
2. **Scope.** Storyboard only what the user asked for (an intro, one section, the whole video). Nothing else goes on the board.

## Build the board

Make a board folder next to the project's media: `<project> media/storyboard/`.

1. **`timeline.json`**: `fps` and `totalFrames` are required.
   - Palmier Pro: save `get_timeline`.
   - A plain video file: write `{"fps": <fps>, "totalFrames": <frames>}`.
2. **`words.json`**: a Deepgram `nova-2` response (`smart_format`, `punctuate`, `paragraphs`, `utterances`, `words`), on the same clock as `timeline.json`.
   - Palmier: rebuild the timeline's mic audio from its clips and transcribe that.
   - A plain video: transcribe the file.
3. **`media/`**: the stills are cut from these files.
   - Palmier: write `sources.json` (`{mediaRef: file}` for the Webcam and Screen clips), then run `python3 $S/proxy.py timeline.json sources.json <board>`.
   - A plain video: `ffmpeg -i <video> -an -vf scale=960:540 -c:v libx264 -g 15 media/cam.mp4`. Add `media/screen.mp4` for a screen recording.
4. **`board.json`**, following the format in the docstring:
   - Take the visuals from the manifest's template bank, layouts and placement rules. Set `ref` to the template it follows.
   - Cue each animated element to the word that introduces it.
   - Use the creator's real footage wherever it can show what's being said: a real clip beats a drawn stand-in such as an empty phone, screen or play button.
   - Give the board a `footage` list of checked moments, as `[{at, crop, shows}]`.
   - Give each part a measured `hairTop` `[min, max]`, so graphics stay clear of the speaker's head.
   - Any asset the creator hasn't made yet is a placeholder item with an asset ID and ratio (`B1-1`, `9:16`).
5. **Check.** Run `python3 $S/storyboard.py check <board>` until there are no `ERROR` lines. Tell the user every `ASSET` line it prints: those are the files they need to send.
6. **Open it for the user.**
   - Fill in `assets/launcher.applescript`: KIT = `$S/storyboard.py`, BOARD = the board folder, PORT = a free port (8774 upward, one per board).
   - Build it with `osacompile -o "<project> media/<Video> Storyboard.app" <filled copy>`, then `open` it.
   - Never use a `.command` file or anything that opens a Terminal window.
   - To restart after changing the scripts, stop the server on that port and `open` the app again.

## Review rounds

The user reviews on the page and either presses **Apply comments** or asks in chat.

- **When they ask in chat:**
  - Back up `board.json` and `review.json` first.
  - Run `python3 $S/storyboard.py next <board>` to list the jobs.
  - Re-read `review.json` just before writing.
  - Append new options with a higher `round`. Set `replaces` for a revision, and add `fresh` for a new idea.
  - Never rename or delete an option ID: the review is keyed on it.
  - Then run `check`.
- **New idea** means a completely different concept, not a restyle of the old frame.
- **Revise** follows the note exactly. The note beats the manifest and every default.
- **When a comment can't be done:** widen what the page and `revise.py` can do rather than explaining the limit. The page already does free-form HTML/CSS, camera pan and zoom, a webcam card, retiming and splitting.
- **What comes back to the chat:** only work that needs files on the computer, brand new footage or images, or editor changes. `apply.json` says which.

## Build from the board

Build only the accepted option for each part. Elements appear on their spoken word, and video of the speaker inside a graphic is live footage, not a still. Render the graphics following the creator's own motion-graphics workflow or the manifest's AI edit workflow.

If the board kept pre-cut times, work out the mapping to the finished timeline before placing anything.

Known gotcha: a word-box caption template loses its word boxes when its text variable is set (the split runs before the fill). Split the words after filling.

## Testing changes to the scripts

Run `python3 $S/storyboard.py selftest`. To try a board, copy the scripts, the manifest and the board to a scratch folder and serve from there. Never launch a throwaway `.app` that reads `~/Documents`: it raises a macOS permission prompt.
