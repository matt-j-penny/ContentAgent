---
name: face-tracking
description: Detect and track a visible face in a local video for reframing or graphics placement. Use when a short or crop should follow the speaker's face.
---

# Face tracking

Follow [references/before-you-start.md](references/before-you-start.md) to choose Content OS or standalone mode. The local YuNet detector finds face boxes, not identities or gaze. It starts with the largest detected face and follows the nearest face; check the samples visually, especially when multiple people appear, the camera cuts or the face is obscured. Missing detections are unknown, never proof that a person is absent.

Requires Python 3, OpenCV (`opencv-python` or `opencv-python-headless`) and the bundled [YuNet model](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet), distributed under its accompanying MIT license. Use a local video and a new output file. Times are source-video seconds.

```bash
python3 <SKILL_DIR>/scripts/detect.py source.mp4 --start 10 --end 30 --interval 0.5 --out face-track.json
```

The JSON contains normalized face boxes and source timestamps. If requested, pass the resulting file to `short-clip --track`; the crop refuses incomplete coverage rather than inventing a path. Inspect the resulting clip across cuts and movement. If detection fails or tracks the wrong person, use a different range or manual framing. The input is processed locally; do not upload it just to locate a face.

This is not gaze tracking. For camera-vs-screen layout decisions, use `gaze-analysis` with additional evidence rather than inferring attention from a face box.
