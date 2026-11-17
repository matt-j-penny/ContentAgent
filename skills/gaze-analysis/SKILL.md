---
name: gaze-analysis
description: Analyse camera-versus-screen layout cues using transcript, cursor activity and optional calibrated head pose. Use when planning when to show the camera full-screen or a screen recording.
---

# Camera and screen layout cues

Follow [references/before-you-start.md](references/before-you-start.md) to choose Content OS or standalone mode. Ask for the synchronized webcam and screen sources and the relevant transcript or cursor data. The goal is an editable layout plan; do not change a timeline automatically.

Use explicit transcript or visual cues first, then corroborating cursor or computer-audio activity. Head orientation is only a weak veto against a proposed camera-facing section: it does not prove eye gaze or attention. When camera and screen are close together, yaw alone may not distinguish them; mark uncertain moments for review. A missing face is unknown, not a camera or screen decision. Inspect representative frames before applying any layout changes.

## Optional local head-pose measurement

The user must identify a real camera-facing reference interval; never assume the first seconds are suitable. If available, also identify a known screen-facing interval. Requires Python 3, MediaPipe, OpenCV and a compatible `face_landmarker.task` model supplied by the user. The model is not bundled; the [official MediaPipe example](https://github.com/google-ai-edge/mediapipe-samples-web/blob/main/src/tasks/face-landmarker.ts) identifies an official model download. Use an existing compatible model when available. Analyze local footage only:

```bash
python3 <SKILL_DIR>/scripts/measure.py webcam.mp4 --model /path/to/face_landmarker.task --camera-start 10 --camera-end 15 --screen-start 30 --screen-end 35 --out pose.json
```

Omit both screen times if there is no reliable reference. The output contains sampled head yaw, detected/missing samples and the median separation between references, not a claim about eye gaze. If the camera and screen baselines differ by less than about seven degrees, treat orientation as inconclusive rather than labeling the footage. The threshold is a heuristic, not a guaranteed accuracy level.

## Build a reviewable plan

Use `scripts/plan.py` with a JSON file of timestamped transcript cues and optional cursor-activity intervals, plus the optional pose JSON. All times must be synchronized source-video seconds; it does not map through an edited timeline. Transcript cues are considered first; cursor activity corroborates or flags conflicts; reliable head pose can veto a proposed camera segment to `unknown`, not assert a screen view. Unknown and conflicting intervals require review. The planner does not edit the video or infer a speaker's gaze.

```bash
python3 <SKILL_DIR>/scripts/plan.py cues.json --pose pose.json --out layout-plan.json
```

Input format and a worked example are in [references/layout-input.md](references/layout-input.md). Without pose, omit `--pose`. Review the proposed intervals against video, then use an actually connected editor only when the user asks for changes.
