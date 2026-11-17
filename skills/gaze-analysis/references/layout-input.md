# Layout planner input

All times use synchronized source-video seconds, not an edited timeline. Create transcript cues only where the words or a reviewed visual make the intended camera/screen layout clear. Cursor activity can be supplied as intervals or through `--cursor` with a Recordly cursor JSON file. Neither means the speaker is definitely looking at the screen.

```json
{
  "webcam": "/path/to/webcam.mp4",
  "duration": 20,
  "transcript_cues": [
    {"start": 0, "end": 4, "label": "camera"},
    {"start": 4, "end": 12, "label": "screen"}
  ],
  "cursor_activity": [{"start": 13, "end": 15}]
}
```

`webcam` is optional but, when provided alongside `--pose`, must match the pose file's source. With `--cursor`, click/double-click or movement exceeding 2% within 1.5 seconds counts as activity; a cursor at the bottom edge is ignored. These are heuristics and should be checked against the actual screen. Overlapping opposing transcript cues or camera cues with active cursor become `unknown`. Head pose is ignored unless both reference poses differ by at least seven degrees by default; then a pose closer to the screen reference can veto a camera cue to `unknown`. It never labels a segment screen by itself. Empty evidence yields `unknown`, not camera.
