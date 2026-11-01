#!/usr/bin/env python3
"""Join the Deepgram words with the agent's visual beats into the synced timeline, and check it.

  timeline.py <folder>

Reads prepared.json and beats.json (the agent's visual_beats list) from the folder and writes
timeline.json: spoken segments with their words, overlapping beats, on-screen text and nearest
frame, plus visual-only entries for stretches with no speech. `relationship` and `note` are left
empty for the agent to fill. Prints any checklist problems.
"""
import json, sys
from pathlib import Path

PAUSE_S = 0.15
CUT_TOLERANCE_S = 0.1


def overlap(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


def segments(words, boundaries):
    segs, cur = [], []
    for w in words:
        if cur:
            gap = w["start"] - cur[-1]["end"]
            ends_sentence = cur[-1]["punctuated_word"][-1:] in ".?!"
            cut_between = any(cur[-1]["start"] < b <= w["start"] for b in boundaries)
            if gap >= PAUSE_S or ends_sentence or cut_between:
                segs.append(cur)
                cur = []
        cur.append(w)
    return segs + [cur] if cur else segs


def main(folder):
    d = Path(folder)
    prep = json.loads((d / "prepared.json").read_text())
    beats = json.loads((d / "beats.json").read_text())
    meta, frames = prep["meta"], prep["frames"]
    words = prep["transcript"]["words"] if prep["transcript"] else []
    boundaries = [b["start"] for b in beats[1:]]

    def nearest_frame(t):
        return min(frames, key=lambda f: abs(f["t"] - t))["file"]

    def beats_over(s, e):
        hits = [(overlap(s, e, b["start"], b["end"]), b) for b in beats]
        hits = [h for h in hits if h[0] > 0] or [(0, min(beats, key=lambda b: abs(b["start"] - s)))]
        return max(hits, key=lambda h: h[0])[1], [b for _, b in hits]

    timeline, last = [], 0.0
    for seg in segments(words, boundaries):
        s, e = seg[0]["start"], seg[-1]["end"]
        if s - last >= 0.5:
            main_beat, spanned = beats_over(last, s)
            timeline.append({"start": round(last, 2), "end": round(s, 2), "spoken": None, "words": [],
                             "visual_beat_id": main_beat["id"], "visual_beat_ids_spanned": [b["id"] for b in spanned],
                             "on_screen_text": main_beat.get("on_screen_text", []),
                             "relationship": "independent", "note": "", "nearest_frame": nearest_frame((last + s) / 2)})
        main_beat, spanned = beats_over(s, e)
        timeline.append({"start": round(s, 2), "end": round(e, 2),
                         "spoken": " ".join(w["punctuated_word"] for w in seg),
                         "words": [{"word": w["punctuated_word"], "start": w["start"], "end": w["end"]} for w in seg],
                         "visual_beat_id": main_beat["id"], "visual_beat_ids_spanned": [b["id"] for b in spanned],
                         "on_screen_text": main_beat.get("on_screen_text", []),
                         "relationship": "", "note": "", "nearest_frame": nearest_frame((s + e) / 2)})
        last = e
    if meta["duration_seconds"] - last >= 0.1:
        main_beat, spanned = beats_over(last, meta["duration_seconds"])
        timeline.append({"start": round(last, 2), "end": meta["duration_seconds"], "spoken": None, "words": [],
                         "visual_beat_id": main_beat["id"], "visual_beat_ids_spanned": [b["id"] for b in spanned],
                         "on_screen_text": main_beat.get("on_screen_text", []),
                         "relationship": "independent", "note": "", "nearest_frame": nearest_frame((last + meta["duration_seconds"]) / 2)})
    for i, entry in enumerate(timeline, 1):
        entry["id"] = f"s{i}"
    (d / "timeline.json").write_text(json.dumps(timeline, indent=2))

    problems = []
    if abs(beats[0]["start"]) > 0.05 or abs(beats[-1]["end"] - meta["duration_seconds"]) > 0.1:
        problems.append("Beats must run from 0 to the full duration.")
    for a, b in zip(beats, beats[1:]):
        if abs(a["end"] - b["start"]) > 0.05:
            problems.append(f"Gap or overlap between {a['id']} and {b['id']}.")
    marks = meta["scene_cuts"] + [t[k] for t in meta["transitions"] for k in ("start", "end")]
    for b in beats[1:]:
        if not any(abs(b["start"] - m) <= CUT_TOLERANCE_S for m in marks) and not b.get("boundary_reason"):
            problems.append(f"{b['id']} starts at {b['start']}, not on a cut or transition; add boundary_reason if it's a layout change or new element.")
    for b in beats:
        if b.get("motion") and b.get("motion_confidence") not in ("observed", "inferred"):
            problems.append(f"{b['id']} has motion without motion_confidence observed/inferred.")
    print(f"Wrote {d / 'timeline.json'}: {len(timeline)} entries.")
    print("\n".join(problems) or "Checks passed.")


if __name__ == "__main__":
    main(sys.argv[1]) if len(sys.argv) > 1 else sys.exit(__doc__)
