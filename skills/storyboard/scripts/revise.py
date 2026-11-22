"""The Apply comments button: turns review comments into new storyboard options through the Claude Code CLI.

Claude runs sealed: no tools, no MCP, no settings, plugins or hooks, an empty working folder and a minimal environment.
It can only return JSON. This module checks that JSON and storyboard.py is the only thing that writes files.
"""
import base64
import copy
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

MODEL, EFFORT, TIMEOUT = "opus", "medium", 420
HEAD = (.422, .052, .615, .5)  # his head as fractions of the webcam picture
COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}|transparent|rgba?\([\d., %]+\)")
LOADS = re.compile(r"url\s*\((?!\s*#)|image-set|@import|\\", re.I)
ACTIVE = re.compile(r"<\s*/?\s*(script|meta|link|base|iframe|frame|object|embed|form|img|video|audio|source)\b"
                    r"|\son\w+\s*=|(\bsrc|\bsrcset|\baction)\s*=|href\s*=\s*[\"']?(?!#)[^\s\"']", re.I)


SCHEMA = {
    "type": "object", "required": ["changes"],
    "properties": {"changes": {"type": "array", "items": {
        "type": "object", "required": ["part", "status", "summary"],
        "properties": {
            "part": {"type": "string"},
            "status": {"enum": ["changed", "removed", "needs_chat"]},
            "summary": {"type": "string"},
            "title": {"type": "string"},
            "layout": {"type": "string"},
            "visual": {"type": "object"},
            "start": {"type": "number"},
            "end": {"type": "number"},
            "extra": {"type": "array", "items": {"type": "object"}},
        }}}}}

SYSTEM = """You revise motion-graphics storyboards for a video creator. You get their editing manifest, the board, the
spoken words with times, and their comment on each frame to change. Return exactly one change for every job.

How to work
- action "revise": do what the comment asks, all of it, and nothing else. Keep everything the comment doesn't mention as
  it is: copy, layout, cues, asset ids, crops, css and framing. `earlier_comments` were already applied, so don't undo
  them. Never drop, rename or renumber existing asset ids unless the comment removes them.
- action "new_idea": they want it completely redone. Throw the frame away and invent a different concept for the same
  spoken words: a different layout, focal point and way of showing it, not the same thing restyled or reworded. It must
  be unlike everything in `previous_ideas` and unlike the neighbouring frames. Don't carry over old copy, assets or
  styling. The comment, when there is one, steers the idea. Aim for one bold idea that reads in a second.
  Where their real footage can show what's being said, use it rather than a drawing of it: never an empty phone, screen
  or play button standing in for footage. Fill the frame with intent and keep every layer clear of his face.
- The comment is the creator's instruction and beats the manifest and every default below, including zoom levels,
  layouts and placement. Where the comment is silent, follow the manifest.
- Nearly everything on the canvas can be changed. If no template or simple shape does it, build it with a free html item.
  Never say a control is missing before trying camera, speaker, css and html.
- Fix obvious typos in words the comment asks you to put on screen. Never use em dashes in on-screen copy. Never invent
  numbers, statistics, quotes or claims.
- Every element lands on the word that names it: each cue is a phrase copied exactly from that part's spoken words.
- Content the creator will supply later is a placeholder with a ratio and an asset id. Number new ones on from the
  highest for that part.
- Footage comes from their own recording. `footage` lists checked times and crops. The screen contact sheet shows what
  else is there (tile k, counting from 0 left to right then down, is k * 15 seconds). Don't guess beyond what you see.
- `start` and `end` are optional. Send them only when the timing has to change, and stay clear of the other parts.
- To split a frame or add one, also send `extra`: [{title, layout, visual, start, end}], shortening this part if needed.

Status
- changed: send layout, title and the complete new visual, not a diff.
- removed: only when the comment clearly asks for that frame to be dropped.
- needs_chat: only for what is outside the storyboard (files on their Mac, assets they say they have sent, editing the
  Palmier timeline, making brand new footage or images) or a question. Never fake it or do half. In summary say in one
  plain sentence what it needs, or answer the question. This page takes no uploads, so never ask them to send or upload
  anything "here".

summary is one short plain sentence, addressed to them, saying what changed.

Visual format (canvas 1920x1080, stills show everything already revealed)
{format}
    free      items [{shape, x, y, w, h, cue, rotate?, opacity?, ...}] in canvas pixels, drawn in list order
              shape text: text, size (px, 24 or more), color?, background?, radius?, align? (left|center|right)
              shape box: background, radius?
              shape placeholder: placeholder "9:16", asset, label? (w/h must match the ratio)
              shape footage: at, crop, radius?, track? ("screen" is the default, "cam" is their webcam)
              shape html: html, css? a sealed box of static HTML, CSS and inline SVG at exactly w by h, transparent, with
                box-sizing border-box and no margin. It clips at its edge, so leave
                room inside it for any shadow. Use it for any design the shapes can't do: gradients, outlines, mixed
                type, shadows, icons, masks, diagrams. Cabinet Grotesk and Satoshi are loaded. No scripts, links or files.
              colours are hex or rgba. Items other than text may bleed off the canvas. The layout still draws the
              background and the webcam.
    on any visual
      still    the second whose picture the storyboard shows
      speaker  false to hide the webcam card, or {x, y, w, h, radius?, crop?, behind?} to put it anywhere at any size
               (not on full). crop is [x, y, w, h] fractions of the webcam picture, filled to the card without stretching.
      punch    on full: {scale 1 to 3, cue, x?, top?}. x is the point across the webcam picture to centre (his face is
               0.512). top is the point down the webcam picture that lands on the top edge of the frame, so for no room
               above the hair use the smallest hair top in the part, less 0.003. Edges can never show, so top can be at
               most 1 - 1/scale.
Use whatever makes the best frame: a bank template, clips or free. A template needs every one of its variables. css may
restyle or move a template's own elements (no url(), @import or backslashes).
When you lay out free items, match the other frames: headlines 76-90 px on one line where they fit (the key word can be
its own item in #7c3aed on the next line), labels 38 px in #1a1a2e centred in a text item directly under their box (not
the placeholder's label, which draws small inside it). Make boxes as large as the space allows, with 30 px gaps and
equal margins, and centre the whole group in the space that layout leaves for graphics.
Space: in right-third, graphics stay within x 44-1246 as the webcam card has the rest, unless speaker moves it. In full,
keep graphics off his head, which is at x 810-1180, y 60-540 until a punch moves it. graphic-full has no webcam.
screen-pip allows zooms only. Nothing important sits under the webcam card.
"""


def number(v, low=-1e4, high=1e5):
    return type(v) in (int, float) and math.isfinite(v) and low <= v <= high


def head(punch):
    """Where his head lands on the canvas, following the same camera maths as index.html."""
    k = (punch or {}).get("scale", 1.08)
    x = min(0, max(1920 - 1920 * k, 960 - (punch or {}).get("x", .512) * 1920 * k))
    y = min(0, max(1080 - 1080 * k, -(punch or {}).get("top", 0) * 1080 * k))
    return [v * (1080 if i % 2 else 1920) * k + (y if i % 2 else x) for i, v in enumerate(HEAD)]


def problems(layout, visual):
    """Shape and safety checks on a visual Claude sent back, before compile_board reads it."""
    if not isinstance(visual, dict) or visual.get("kind") not in ("template", "clips", "zoom", "none", "free"):
        return ["visual.kind must be template, clips, zoom, none or free"]
    kind, bad = visual["kind"], []
    css = visual.get("css", "")
    if not isinstance(css, str) or "<" in css or LOADS.search(css):
        bad.append("css may not load anything or contain < or a backslash")
    for key in ("title", "kicker", "highlight", "titleCue", "cue"):
        if key in visual and not isinstance(visual[key], str):
            bad.append(f"{key} must be text")

    def footage(m):
        crop = m.get("crop", [0, 0, 1, 1])
        if not number(m.get("at", 0), 0) or not number(m.get("still", 0), 0) or m.get("track", "screen") not in ("screen", "cam"):
            bad.append("footage needs a time in seconds on the screen or cam track")
        if not (isinstance(crop, list) and len(crop) == 4 and all(number(n, 0, 1) for n in crop) and crop[2] > 0 and crop[3] > 0):
            bad.append("crop is [x, y, w, h] as fractions")

    punch = visual.get("punch")
    if punch is not None:
        if not (isinstance(punch, dict) and number(punch.get("scale"), 1, 3) and isinstance(punch.get("cue", ""), str)
                and number(punch.get("x", .5), 0, 1) and number(punch.get("top", 0), 0, 1)):
            return bad + ["punch is {scale 1 to 3, cue, x?, top?}"]
        if punch.get("top", 0) > 1 - 1 / punch["scale"] + .002:
            bad.append(f"at scale {punch['scale']} top can be at most {1 - 1 / punch['scale']:.3f}: zoom further or lower top")
    if "still" in visual and not number(visual["still"], 0):
        bad.append("still is a time in seconds")
    speaker = visual.get("speaker")
    if speaker is not None and speaker is not False:
        if not (isinstance(speaker, dict) and all(number(speaker.get(k)) for k in "xywh") and speaker["w"] > 0 and speaker["h"] > 0
                and number(speaker.get("radius", 0), 0)):
            return bad + ["speaker is false or {x, y, w, h, radius?, crop?, behind?} in pixels"]
        c = speaker.get("crop", [0, 0, 1, 1])
        if not (isinstance(c, list) and len(c) == 4 and all(number(n, 0, 1) for n in c) and c[2] > 0 and c[3] > 0):
            return bad + ["speaker crop is [x, y, w, h] as fractions"]
        if layout == "full":
            bad.append("full has no webcam card: frame him with punch, or use another layout")
    keep = None
    if layout == "full":
        keep = head(punch), "covers his head"
    elif isinstance(speaker, dict) and not speaker.get("behind"):
        keep = [speaker["x"], speaker["y"], speaker["x"] + speaker["w"], speaker["y"] + speaker["h"]], "runs under the webcam card"
    elif layout == "right-third" and speaker is None:
        keep = [1246, 0, 1920, 1080], "runs under the webcam card"

    if kind == "template":
        if not isinstance(visual.get("id"), str):
            bad.append("template needs an id")
        values, cues = visual.get("vars", {}), visual.get("cues", [""])
        if not isinstance(values, dict) or not all(isinstance(v, str) for v in values.values()):
            bad.append("vars must be text values")
        if not isinstance(cues, list) or not cues or not all(isinstance(c, str) for c in cues):
            bad.append("cues must be a list of phrases")
        media = visual.get("media", [])
        if not isinstance(media, list) or not all(isinstance(m, dict) for m in media):
            bad.append("media must be a list of objects")
        else:
            for m in media:
                footage(m)
    if kind == "zoom":
        b = visual.get("box")
        if not (isinstance(b, list) and len(b) == 4 and all(number(n, 0, 1) for n in b) and b[2] > 0 and b[3] > 0):
            bad.append("zoom box is [x, y, w, h] as fractions")
    if kind in ("clips", "free"):
        items, chips = visual.get("items"), visual.get("chips", [])
        if not isinstance(items, list) or not items or not all(isinstance(m, dict) for m in items):
            return bad + [f"{kind} needs a list of items"]
        if not isinstance(chips, list) or not all(isinstance(c, dict) and isinstance(c.get("text"), str) for c in chips):
            return bad + ["chips are {text, cue}"]
        rows = visual.get("rows")
        if rows is not None and not (isinstance(rows, list) and rows and all(type(n) is int and n > 0 for n in rows)):
            bad.append("rows is a list of counts")
        for m in items + chips:
            for key in ("cue", "label", "text", "asset", "placeholder"):
                if key in m and not isinstance(m[key], str):
                    bad.append(f"{key} must be text")
        for m in items:
            if kind == "clips":
                if "placeholder" not in m:
                    if "at" not in m and "still" not in m:
                        bad.append("a clips item is a placeholder or footage with a time")
                    footage(m)
                continue
            shape = m.get("shape")
            if shape not in ("text", "box", "placeholder", "footage", "html") or not all(number(m.get(k)) for k in "xywh"):
                bad.append("free items need a shape and numeric x, y, w, h")
                continue
            x, y, w, h = [m[k] for k in "xywh"]
            off = x < 0 or y < 0 or x + w > 1920 or y + h > 1080 if shape == "text" else x >= 1920 or y >= 1080 or x + w <= 0 or y + h <= 0
            if w <= 0 or h <= 0 or off:
                bad.append(f"{shape} at {x},{y} is off the canvas")
            # a full-bleed html layer is mostly empty, so only the solid shapes are checked against him
            if keep and shape != "html":
                (l, t, right, low), why = keep
                if x < right and x + w > l and y < low and y + h > t:
                    bad.append(f"{shape} at {x},{y} {why} at x {l:.0f}-{right:.0f}, y {t:.0f}-{low:.0f}")
            if any(k in m and not (isinstance(m[k], str) and COLOUR.fullmatch(m[k])) for k in ("color", "background")):
                bad.append("colours must be hex or rgba")
            if not number(m.get("rotate", 0), -360, 360) or not number(m.get("opacity", 1), 0, 1):
                bad.append("rotate is degrees and opacity is 0 to 1")
            if shape == "html":
                body, style = m.get("html"), m.get("css", "")
                if not isinstance(body, str) or not body or ACTIVE.search(body) or LOADS.search(body):
                    bad.append("html must be static markup with no scripts, media, links, handlers or url()")
                if not isinstance(style, str) or "<" in style or LOADS.search(style):
                    bad.append("html css may not load anything or contain < or a backslash")
            if "radius" in m and not number(m["radius"], 0):
                bad.append("radius must be a number")
            if m.get("align", "center") not in ("left", "center", "right"):
                bad.append("align is left, center or right")
            if shape == "text" and (not m.get("text") or not number(m.get("size"), 24, 400)):
                bad.append("text needs words and a size from 24 to 400")
            if shape == "placeholder" and not m.get("placeholder"):
                bad.append("a placeholder needs a ratio")
            if shape == "footage":
                footage(m)
    return bad


def current(part):
    replaced = {o.get("replaces") for o in part["options"]}
    return [o for o in part["options"] if o["id"] not in replaced][-1]


def jobs(board, review):
    """The one rule for what the Apply button does: Accept is never touched, New idea always is, a comment is a revision."""
    said, out = review.get("options", {}), []
    for part in board["parts"]:
        if part.get("removed"):
            continue
        option = current(part)
        answer = said.get(option["id"], {})
        note, verdict = answer.get("note", "").strip(), answer.get("verdict")
        job = dict(part=part["id"], option=option["id"], note=note, verdict=verdict)
        if verdict == "no":
            out.append(dict(job, action="new_idea", previous_ideas=[
                {k: o.get(k) for k in ("title", "layout", "visual")} for o in part["options"]]))
        elif note and verdict != "yes":
            since = part["options"][max([0] + [i for i, o in enumerate(part["options"]) if o.get("fresh")]):-1]
            out.append(dict(job, action="revise", earlier_comments=[
                said[o["id"]]["note"] for o in since if said.get(o["id"], {}).get("note", "").strip()]))
    return out


def ask_claude(system, message, images=()):
    cli = shutil.which("claude") or str(Path.home() / ".local/bin/claude")
    if not os.access(cli, os.X_OK):
        raise RuntimeError("The Claude command line app isn't installed on this Mac.")
    env = {k: os.environ[k] for k in ("HOME", "USER", "LOGNAME", "TMPDIR") if k in os.environ}
    env.update(PATH="/usr/bin:/bin", LANG="en_US.UTF-8")
    cmd = [cli, "-p", "--safe-mode", "--restricted", "--tools", "", "--strict-mcp-config", "--no-session-persistence",
           "--model", MODEL, "--effort", EFFORT, "--system-prompt", system,
           "--input-format", "stream-json", "--output-format", "stream-json", "--verbose", "--json-schema", json.dumps(SCHEMA)]
    content = [dict(type="text", text=message)]
    for caption, jpeg in images:
        content += [dict(type="text", text=caption),
                    dict(type="image", source=dict(type="base64", media_type="image/jpeg", data=base64.b64encode(jpeg).decode()))]
    sent = json.dumps(dict(type="user", message=dict(role="user", content=content))) + "\n"
    with tempfile.TemporaryDirectory(prefix="storyboard-claude-") as empty:
        try:
            done = subprocess.run(cmd, input=sent, capture_output=True, text=True, timeout=TIMEOUT, cwd=empty, env=env)
        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude took too long. Nothing was changed, press the button to try again.")
    try:
        out = next(m for m in map(json.loads, done.stdout.splitlines()) if m.get("type") == "result")
    except (ValueError, StopIteration):
        raise RuntimeError("Claude didn't answer: " + (done.stderr or done.stdout or "no output").strip()[:300])
    answer = out.get("structured_output")
    if out.get("is_error") or not isinstance(answer, dict):
        raise RuntimeError("Claude couldn't do it: " + str(out.get("result") or out.get("subtype"))[:300])
    return answer["changes"]


def context(raw, compiled, root, rules, bank, todo, words, fmt):
    templates = []
    for t in bank.values():
        page = root / t["path"]
        if page.is_file():  # setTime-driven templates carry their own content, so they can't be filled from here
            templates.append(dict({k: t.get(k) for k in ("id", "use", "layouts", "variables", "avg", "said")},
                                  html=page.read_text()))
    parts, redo = [], {j["part"] for j in todo if j["action"] == "new_idea"}
    for p in raw["parts"]:
        if not p.get("removed"):
            spoken = [[w["punctuated_word"], round(w["start"], 2)] for w in words if p["start"] - .1 <= w["start"] < p["end"] - .15]
            around = [w["punctuated_word"] for w in words if p["start"] - 8 <= w["start"] < p["end"] + 8]
            old = p["id"] in redo  # a new idea mustn't be anchored on the frame it replaces
            parts.append(dict(id=p["id"], start=p["start"], end=p["end"], intent=None if old else p.get("intent"),
                              current=None if old else current(p), hair_top=p.get("hairTop"), words=spoken, surrounding_speech=" ".join(around)))
    message = dict(manifest={k: rules[k] for k in ("identity", "brand", "pacing", "motionGraphics") if k in rules},
                   layouts=compiled["layouts"], templates=templates, footage=raw.get("footage", []),
                   video_seconds=compiled["total"], parts=parts, jobs=todo)
    return SYSTEM.replace("{format}", fmt), json.dumps(message, ensure_ascii=False)


def revise(raw, review, compile_fn, rules_fn, words, fmt, ask=ask_claude, images=()):
    """Returns {part: dict(change, job)} that passed every check, and {part: reason} for the rest. Writes nothing."""
    todo = jobs(raw, review)
    compiled, _ = compile_fn(copy.deepcopy(raw))
    root, _, rules, bank = rules_fn(raw["manifest"])
    good, why = {}, {}
    left = todo
    for attempt in range(2):
        system, message = context(raw, compiled, root, rules, bank, left, words, fmt)
        if attempt:
            message += "\nYour last answer failed these checks. Return corrected changes for these jobs only:\n" + json.dumps(why)
        answers = {c.get("part"): c for c in ask(system, message, images) if isinstance(c, dict)}
        for job in left:
            pid, change = job["part"], answers.get(job["part"])
            why.pop(pid, None)
            if not change:
                why[pid] = ["no change came back for this part"]
            elif change.get("status") == "removed":
                if job["note"]:
                    good[pid] = dict(change, job=job)
                else:
                    why[pid] = ["only remove a part when the comment asks for it: give a replacement"]
            elif change.get("status") == "needs_chat":
                good[pid] = dict(change, job=job)
            else:
                visual, extra = change.get("visual"), change.get("extra", [])
                bad = problems(change.get("layout"), visual)
                for key in ("start", "end"):
                    if key in change and not number(change[key], 0, compiled["total"]):
                        bad.append(f"{key} must be inside the video")
                if not isinstance(extra, list) or not all(
                        isinstance(e, dict) and all(number(e.get(k), 0, compiled["total"]) for k in ("start", "end")) for e in extra):
                    bad.append("extra frames need title, layout, visual, start and end")
                else:
                    for e in extra:
                        bad += problems(e.get("layout"), e.get("visual"))
                if not bad:
                    old = current(next(p for p in raw["parts"] if p["id"] == pid))
                    retimed = extra or "start" in change or "end" in change
                    same = change.get("layout") == old["layout"]
                    if same and visual == old["visual"] and not retimed:
                        bad.append("that is identical to the current frame")
                    elif job["action"] == "new_idea" and not job["note"] and same and visual["kind"] != "free":
                        if (visual["kind"], visual.get("id")) == (old["visual"]["kind"], old["visual"].get("id")):
                            bad.append("same layout and format as the frame they rejected: give a completely different idea")
                if not bad:
                    trial = copy.deepcopy(raw)
                    touched = add(trial, change, job)
                    for part in touched if retimed else ():
                        for other in trial["parts"]:
                            if other is not part and not other.get("removed"):
                                if part["start"] < other["end"] - .05 and other["start"] < part["end"] - .05:
                                    bad.append(f"timing of {part['id']} overlaps {other['id']}")
                    ids = tuple(p["id"] + mark for p in touched for mark in ".:")
                    try:
                        bad += [e for e in compile_fn(trial)[0]["errors"] if e.startswith(ids)]
                    except (KeyError, TypeError, ValueError, AttributeError) as e:
                        bad.append(f"the visual is malformed ({type(e).__name__}: {e})")
                if bad:
                    why[pid] = bad
                else:
                    good[pid] = dict(change, job=job)
        left = [j for j in left if j["part"] in why]
        if not left:
            break
    return good, why


def add(board, change, job):
    """Appends the new option, and any extra frames. Returns the parts it touched."""
    part = next(p for p in board["parts"] if p["id"] == job["part"])
    if change["status"] == "removed":
        part["removed"] = True
        return [part]
    old = current(part)
    for key in ("start", "end"):
        if key in change:
            part[key] = change[key]
    new = dict(id=f"{part['id']}.{len(part['options']) + 1}", round=max(o.get("round", 1) for o in part["options"]) + 1,
               replaces=old["id"], title=str(change.get("title") or old["title"]), layout=change["layout"], visual=change["visual"])
    if job["action"] == "new_idea":
        new["fresh"] = True
    elif old.get("ref"):
        new["ref"] = old["ref"]
    part["options"].append(new)
    touched, prefix = [part], part["id"].rstrip("0123456789")
    for frame in change.get("extra", []):
        taken = [int(n) for p in board["parts"] if p["id"].startswith(prefix) and (n := p["id"][len(prefix):]).isdigit()]
        pid = f"{prefix}{max(taken + [0]) + 1}"
        touched.append(dict(id=pid, start=frame["start"], end=frame["end"], intent="", options=[
            dict(id=f"{pid}.1", round=1, title=str(frame.get("title") or pid), layout=frame["layout"], visual=frame["visual"])]))
        board["parts"].append(touched[-1])
    if len(touched) > 1:
        board["parts"].sort(key=lambda p: p["start"])
    return touched
