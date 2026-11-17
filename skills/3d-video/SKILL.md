---
name: 3d-video
description: Create an editable 3D object turntable video from a supplied GLB, glTF or OBJ model using Blender. Use for simple product, object or logo turntables when a local Blender render is appropriate.
---

# 3D object video

Follow [references/before-you-start.md](references/before-you-start.md) for Content OS or standalone mode. Use the creator's brand and relevant local video-manifest profile when available. Determine the object, aspect ratio, duration and background. Use the creator's own model or one they can use; do not claim an AI-generated model was provided. This is a turntable starting point, not a general character-animation or 3D modelling system.

Requires Python 3, Blender and ffmpeg. It imports a local GLB, glTF or OBJ, centers and scales it, creates a lit orthographic camera and rotates the object. It writes a new output directory containing an editable `.blend`, PNG frames and an MP4. It does not overwrite an existing output directory. A cube is available only when the user requests a demo.

```bash
python3 <SKILL_DIR>/scripts/render.py --model /path/to/model.glb --out /path/to/new-folder --width 1280 --height 720 --frames 72 --fps 24
```

Use `--primitive cube` instead of `--model` for a demo. Set `--blender /path/to/blender` if Blender is not on PATH. Rendering can take time; verify the first, middle and last frames, check framing, model materials, lighting and rotation, and report the video and editable project. The script uses Blender's Eevee renderer; some Blender versions or GPUs may need adjustments. If a render fails, report the error and keep any partial output clearly marked as incomplete.
