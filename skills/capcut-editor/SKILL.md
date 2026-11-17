---
name: capcut-editor
description: Create a new editable CapCut rough-cut draft from an existing single-video keep-list on macOS. Use when the user wants their transcript-based rough cut assembled as a CapCut draft.
---

# CapCut editor

Follow [references/before-you-start.md](references/before-you-start.md) to choose Content OS or standalone mode. This bridge creates an editable CapCut draft locally; it does not publish or save drafts into Content OS. It supports **new, single-video rough-cut drafts only**. Editing existing drafts, captions, overlays, keyframes and export are not enabled in this integration.

Requirements: macOS, CapCut desktop, `uv`, Python 3.10+, `ffprobe` and `ffmpeg`. `uv run` installs the script's PyObjC dependencies if needed. This draft format was previously tested on CapCut 8.9.0; compatibility with another version needs verification. The creator's footage and draft remain local. Do not overwrite source media or an existing draft.

## Prepare a rough cut

Use `rough-cut` and `transcribe` to build a word-timed plan. If a local `video-manifest` exists, choose the relevant format profile and apply its pacing preferences. From the user's project folder create:

```
projects/<job>/raw/<source-file>
projects/<job>/transcript/cuts.json
```

The JSON contains `fps` and ordered, non-overlapping `segments`, each with source-relative `start`, `end` and `clip` filename; see [references/input-contract.md](references/input-contract.md). Segments are the portions to **keep**, not remove. Only one source clip is supported. Default canvas dimensions match the source. Show the user the cut plan and use the original footage read-only. If the creator wants a different canvas or an existing project edited, explain that this bridge does not yet support it.

## Validate, then create

`<SKILL_DIR>` is this skill's installed directory, for example `~/.contentagent/skills/capcut-editor`. From the project folder, first check the plan without touching CapCut:

```bash
uv run <SKILL_DIR>/scripts/capcut-bridge.py replay <job> --name <new-draft-name> --check
```

After it passes, the user should save their open work and close CapCut. The bridge refuses to write while CapCut is running. Create the draft with the same command without `--check`. The name must be new; the bridge rejects existing drafts. It creates a copy or hardlink of the source under CapCut's draft folder. If there is no initialized CapCut draft registry, open CapCut once first. Set `CONTENTAGENT_PROJECT_ROOT` only when the project folder differs from the current working directory.

Open the draft in CapCut and verify the sequence, cut points, audio sync and source media. This is a compatibility check, not proof that the editor version is universally supported. If validation or verification fails, retain the original video and cut plan, explain the issue, and do not delete or overwrite an existing project.
