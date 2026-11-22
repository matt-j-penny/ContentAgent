#!/usr/bin/env python3
"""Standard review storyboard, built on a Video Manifest: one static frame per graphic with Accept, Revise and New idea.

  python3 storyboard.py serve <board dir> [port]   open the board; every answer and note saves to review.json
  python3 storyboard.py check <board dir>          validate board.json against the manifest and transcript
  python3 storyboard.py apply <board dir>          what the Apply comments button does (revise.py), from the shell
  python3 storyboard.py next  <board dir>          what pressing Apply would do, from review.json
  python3 storyboard.py selftest

A board dir holds board.json (written by the agent), words.json (Deepgram, on the timeline clock), timeline.json,
media/{cam.mp4,screen.mp4} (proxy.py, stills are cut from these) and review.json (written by this server only).

board.json
  video, segment? (a manifest structure segment, for its graphics-per-minute target), manifest {dir, profile}
  layouts {id: {role: region}} (project overrides), flags [..]
  footage? [{at, crop?, shows}] (checked moments for Apply, which also sees stills and a contact sheet)
  parts [{id, start, end, intent, hairTop?, removed?, options [{id, round, replaces?, fresh?, title, layout, ref?, visual}]}]
  Only put parts on the board for what he asked to storyboard. title and intent are for the agent: never shown.
  visual kinds
    template  id, vars, cues (one phrase per animated element, "" = part start), media? [{at?, crop?, cue?}], css?
    clips     kicker?, title?, highlight?, titleCue?, items [{at?, crop?, cue?, label?}], chips? [{text, cue}]
              an item he will supply later is {placeholder "16:9" | "9:16" | "1:1", asset "<part>-<n>", cue, label?}
              rows? [3, 1] stacks the items in rows of one shared width, top row first
    zoom      box [x, y, w, h] as fractions of the canvas, cue
    none      layout only
    free      items placed by pixel, see revise.py
  The page shows each option as a still with everything revealed. Cues are kept for the build.
A new round appends options with a higher round (`replaces` for a revision). Never rename or delete an option id:
the review is keyed on it.
"""
import copy
import html
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

import revise

HERE = Path(__file__).resolve().parent
LOCK = threading.Lock()


def load(path, default=None):
    if default is not None and not path.exists():
        return default
    return json.loads(path.read_text())


def save(path, data):
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".review-")
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def merge(base, over):
    if isinstance(base, dict) and isinstance(over, dict):
        return {**base, **{k: merge(base.get(k), v) for k, v in over.items()}}
    return base if over is None else over


# review ---------------------------------------------------------------------------------------------------------

def apply_patch(board, review, patch):
    """One field per request, so two tabs cannot overwrite each other's answers. Raises ValueError on bad input."""
    if not isinstance(patch, dict):
        raise ValueError("expected an object")
    options = review.setdefault("options", {})
    owner = {o["id"]: p for p in board["parts"] for o in p["options"]}
    if patch.keys() == {"option", "verdict"}:
        oid, v = patch["option"], patch["verdict"]
        if not isinstance(oid, str) or oid not in owner or v not in ("yes", "revise", "no", None):
            raise ValueError("bad option or verdict")
        if v == "yes":  # one winner per part
            for o in owner[oid]["options"]:
                if options.get(o["id"], {}).get("verdict") == "yes":
                    options[o["id"]]["verdict"] = None
        options.setdefault(oid, {})["verdict"] = v
    elif patch.keys() == {"option", "note"}:
        oid, text = patch["option"], patch["note"]
        if not isinstance(oid, str) or oid not in owner or not isinstance(text, str) or len(text) > 5000:
            raise ValueError("bad option or note")
        options.setdefault(oid, {})["note"] = text
    else:
        raise ValueError("unknown change")
    return review


# manifest + timing ----------------------------------------------------------------------------------------------

def norm(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def find_cue(words, phrase, start, end):
    if not phrase:
        return start
    want = [norm(w) for w in phrase.split()]
    window = [w for w in words if start - 0.3 <= w["start"] < end]
    for i in range(len(window) - len(want) + 1):
        if [w["n"] for w in window[i:i + len(want)]] == want:
            return max(start, window[i]["start"])
    return None


def solve_zoom(box, levels, avoid):
    """Largest manifest zoom that keeps the target on screen and clear of the webcam PiP."""
    x, y, w, h = box
    ax, ay, aw, ah = avoid
    for s in sorted([v / 100 for v in levels] + [1.0], reverse=True):
        if w * s > 0.94 or h * s > 0.94:
            continue
        clamp = lambda v: min(0, max(1 - s, v))
        tx, ty = clamp(0.5 - (x + w / 2) * s), clamp(0.5 - (y + h / 2) * s)
        for px, py in ((tx, ty), (clamp(ax - 0.015 - (x + w) * s), ty), (tx, clamp(ay - 0.015 - (y + h) * s)),
                       (clamp(ax + aw + 0.015 - x * s), ty), (tx, clamp(ay + ah + 0.015 - y * s))):
            l, t, r, b = px + x * s, py + y * s, px + (x + w) * s, py + (y + h) * s
            inside = l >= 0 and t >= 0 and r <= 1 and b <= 1
            clear = r <= ax or l >= ax + aw or b <= ay or t >= ay + ah
            if inside and clear:
                return dict(s=s, x=px, y=py)
    return None


def resolve_manifest(ref):
    root = Path(ref["dir"]).expanduser()
    raw = load(root / "manifest.json")
    rules = merge(raw["base"], raw["profiles"][ref["profile"]])
    bank = {}
    for t in raw["templates"]:
        scores = [r["score"] for r in t.get("ratings", []) if "score" in r]
        bank[t["id"]] = dict(t, avg=scores and round(sum(scores) / len(scores), 1) or None,
                             said=[r["note"] for r in t.get("ratings", []) if r.get("note")])
    return root, raw, rules, bank


def compile_board(folder, board=None):
    board = board or load(folder / "board.json")
    board["parts"] = [p for p in board["parts"] if not p.get("removed")]
    every = [o["id"] for p in board["parts"] for o in p["options"]]
    for part in board["parts"]:
        part["options"] = [revise.current(part)]  # replaced options keep cues from timings the part may have left
    root, raw, m, bank = resolve_manifest(board["manifest"])
    profile = board["manifest"]["profile"]
    words = [dict(text=w["punctuated_word"], n=norm(w["word"]), start=w["start"], end=w["end"])
             for u in load(folder / "words.json")["results"]["utterances"] for w in u["words"]]
    tl = load(folder / "timeline.json")
    fps, total = tl["fps"], tl["totalFrames"] / tl["fps"]

    layouts = {}
    for lay in m["layouts"]["library"]:
        own = board.get("layouts", {}).get(lay["id"], {})
        layouts[lay["id"]] = dict(lay, regions=[{**r, **own.get(r["role"], {})} for r in lay["regions"]])
    pip = next(r for r in layouts["screen-pip"]["regions"] if r["role"] == "speaker")
    avoid = [pip[k] / 100 for k in ("x", "y", "w", "h")]
    limits, switching, mg = m["motionGraphics"]["maxOnScreen"], m["layouts"]["switching"], m["motionGraphics"]
    levels = m["pacing"]["screenZooms"]["levels"]
    errors = [f"{oid}: option id used twice" for oid in {i for i in every if every.count(i) > 1}]

    for part in board["parts"]:
        a, b = part["start"], part["end"]
        if not 0 <= a < b <= total:
            errors.append(f"{part['id']}: {a}-{b} is outside the {total:.1f}s cut")
            continue
        part["words"] = [w for w in words if a - 0.1 <= w["start"] < b - 0.15]
        for o in part["options"]:
            notes, v = [], o["visual"]
            lay = layouts.get(o["layout"])
            if not lay:
                errors.append(f"{o['id']}: layout {o['layout']} is not in the manifest")
                continue

            def cue(phrase):
                t = find_cue(words, phrase, a, b)
                if t is None:
                    errors.append(f"{o['id']}: '{phrase}' is not said between {a}s and {b}s")
                    return a
                return t

            kind, shown, copy = v["kind"], [], [o["title"]]
            if kind == "template":
                t = bank.get(v["id"])
                if not t:
                    errors.append(f"{o['id']}: template {v['id']} is not in the bank")
                    continue
                missing = set(t["variables"]) - set(v.get("vars", {}))
                if missing:  # an unset variable would show the template's demo copy
                    errors.append(f"{o['id']}: set {', '.join(sorted(missing))} for {v['id']}")
                if profile not in t["profiles"]:
                    notes.append(["warn", f"{v['id']} is not in the {m['label']} profile"])
                if o["layout"] not in t["layouts"]:
                    notes.append(["warn", f"Template is meant for {', '.join(t['layouts'])}"])
                v["times"] = shown = [cue(c) for c in v.get("cues", [""])]
                v["src"] = "/" + t["path"]
                copy += map(str, v.get("vars", {}).values())
                for item in v.get("media", []):
                    item["t"] = cue(item.get("cue", ""))
                if t["avg"] is not None and t["avg"] < 3:
                    notes.append(["warn", f"You rated this template {t['avg']}/5"])
            elif kind == "clips":
                for item in v["items"] + v.get("chips", []):
                    item["t"] = cue(item.get("cue", ""))
                    shown.append(item["t"])
                    copy += [item.get("label", ""), item.get("text", "")]
                v["titleT"] = cue(v.get("titleCue", ""))
                if v.get("title"):
                    shown.append(v["titleT"])
                copy += [v.get("title", ""), v.get("kicker", ""), v.get("highlight", "")]
                if len(v["items"]) > limits:
                    notes.append(["warn", f"{len(v['items'])} items, your limit is {limits}"])
                if "new-type" in board.get("mustAsk", ["new-type"]):
                    notes.append(["ask", "New graphic type, not in your bank. A tick approves building it"])
                for item in v["items"]:
                    if "placeholder" in item:
                        if not re.fullmatch(r"[1-9]\d*:[1-9]\d*", item["placeholder"]) or not item.get("asset"):
                            errors.append(f"{o['id']}: a placeholder needs a ratio like 9:16 and an asset id")
                if "rows" in v and sum(v["rows"]) != len(v["items"]):
                    errors.append(f"{o['id']}: rows must add up to the {len(v['items'])} items")
                if o.get("ref") and o["ref"] not in bank:
                    errors.append(f"{o['id']}: reference {o['ref']} is not in the bank")
            elif kind == "zoom":
                v["t"] = cue(v.get("cue", ""))
                v["zoom"] = solve_zoom(v["box"], levels, avoid)
                if not v["zoom"]:  # target sits under the webcam, so the webcam slides to the top-left for this zoom
                    corner = [1 - avoid[0] - avoid[2], 1 - avoid[1] - avoid[3], avoid[2], avoid[3]]
                    v["zoom"] = solve_zoom(v["box"], levels, corner)
                    if v["zoom"]:
                        v["zoom"]["pip"] = corner[:2]
                        notes.append(["note", "Webcam slides to the top-left for this zoom"])
                if not v["zoom"]:
                    errors.append(f"{o['id']}: no zoom keeps the target clear of the webcam")
                if v["zoom"] and v["zoom"]["s"] == 1:
                    notes.append(["warn", "Target is too big to zoom into"])
                if o["layout"] != "screen-pip":
                    errors.append(f"{o['id']}: zooms need the screen-pip layout")
            elif kind == "free":
                for item in v["items"]:
                    item["t"] = cue(item.get("cue", ""))
                    shown.append(item["t"])
                    copy += [item.get("label", ""), item.get("text", ""), html.unescape(item.get("html", ""))]
                    if item["shape"] == "placeholder":
                        if not re.fullmatch(r"[1-9]\d*:[1-9]\d*", item.get("placeholder", "")) or not item.get("asset"):
                            errors.append(f"{o['id']}: a placeholder needs a ratio like 9:16 and an asset id")
                        else:
                            rw, rh = map(int, item["placeholder"].split(":"))
                            if abs(item["w"] / item["h"] / (rw / rh) - 1) > 0.04:
                                errors.append(f"{o['id']}: {item['asset']} is not drawn at {item['placeholder']}")
            elif kind != "none":
                errors.append(f"{o['id']}: unknown visual kind {kind}")

            if punch := v.get("punch"):
                punch["t"] = cue(punch.get("cue", ""))
                if o["layout"] != "full":
                    errors.append(f"{o['id']}: a punch-in needs the full layout")
                if round(punch["scale"] * 100) not in m["pacing"]["punchIn"]["levels"]:
                    notes.append(["warn", f"Punch-in {punch['scale']} is not a manifest level"])
            if o["layout"] == "screen-pip" and kind not in ("zoom", "none"):
                notes.append(["warn", "Your manifest allows only zooms over a screen share"])
            if o["layout"] in ("graphic-full", "right-third") and shown and min(shown) > a + 0.6:
                notes.append(["warn", "Graphic is empty before the first word cue"])
            if b - a < switching["minHoldSec"]:
                notes.append(["warn", f"Shorter than your {switching['minHoldSec']}s minimum hold"])
            if b - a > switching["maxHoldSec"] and o["layout"] not in ("screen-pip", "demo-frame"):
                notes.append(["warn", f"Held {b - a:.0f}s, your maximum is {switching['maxHoldSec']}s"])
            if any(chr(0x2014) in c for c in copy):
                errors.append(f"{o['id']}: no em dashes in on-screen copy")

            o["checks"] = notes

    parts = [p for p in board["parts"] if p.get("options")]
    spans = sorted((p["start"], p["end"]) for p in parts)
    first, last = (spans[0][0], max(b for _, b in spans)) if spans else (0, total)  # measured over what is on the board, not the whole video
    gaps, at = [], first
    for a, b in spans:
        if a - at > mg["frequency"]["maxGapSec"]:
            gaps.append([round(at, 1), round(a, 1)])
        at = max(at, b)
    covering = ("graphic-full", "right-third", "demo-frame", "compare-2up", "compare-3up")
    covered = sum(p["end"] - p["start"] for p in parts if p["options"][-1]["layout"] in covering)
    segment = next((x for x in m["structure"]["segmentTypes"] if x["id"] == board.get("segment")), {})
    board["summary"] = dict(perMin=round(len(parts) / ((last - first) / 60), 1),
                            wantPerMin=segment.get("graphicsPerMin", mg["frequency"]["perMin"]),
                            coverage=round(100 * covered / (last - first)), wantCoverage=mg["frequency"]["fullScreenCoveragePct"],
                            gaps=gaps, maxGap=mg["frequency"]["maxGapSec"])
    board.update(fps=fps, total=total, layouts=layouts, errors=errors, colors=m["brand"]["colors"],
                 manifestInfo=dict(name=raw["meta"]["name"], version=raw["meta"]["version"], updated=raw["meta"]["updated"],
                                   label=m["label"], rules=m["identity"]["rules"], sync=mg["sync"]["landOn"],
                                   placement=mg["speakerInteraction"], path=str(root / "manifest.json")))
    return board, root


# footage --------------------------------------------------------------------------------------------------------

def cut(folder, name, track, *args):
    """A picture cut from a proxy, made again when the proxy is newer. None when there is nothing there."""
    video, out = folder / "media" / f"{track}.mp4", folder / "media" / "stills" / name
    if not video.exists():
        return None
    if not out.exists() or out.stat().st_mtime < video.stat().st_mtime:
        out.parent.mkdir(exist_ok=True)
        tmp = out.with_name(f"{threading.get_ident()}-{out.name}")
        args = [str(video) if a == "VIDEO" else a for a in args]
        done = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *args, "-q:v", "4", str(tmp)])
        if done.returncode or not tmp.exists():
            return None
        os.replace(tmp, out)
    return out


def still(folder, track, frame):
    fps = load(folder / "timeline.json")["fps"]
    return cut(folder, f"{track}-{frame}.jpg", track, "-ss", f"{frame / fps:.4f}", "-i", "VIDEO", "-frames:v", "1")


def pictures(folder, board, todo):
    """What Claude gets to look at: each commented frame's footage, and a contact sheet of the screen recording."""
    fps, found = load(folder / "timeline.json")["fps"], []
    for part in (p for p in board["parts"] if p["id"] in {j["part"] for j in todo}):
        a, b, tracks = part["start"], part["end"], ["cam"] + ["screen"] * (revise.current(part)["layout"] == "screen-pip")
        for track in tracks:
            for at in (a + .2, (a + b) / 2, b - .05):
                found.append((f"{part['id']}: whole {track} picture at {at:.2f}s", still(folder, track, round(at * fps))))
    tl = load(folder / "timeline.json")
    side = math.ceil(math.sqrt(tl["totalFrames"] / fps / 15 + 1))
    found.append((f"Screen recording contact sheet, {side} across, one tile every 15 seconds", cut(
        folder, f"screen-sheet-{side}.jpg", "screen", "-i", "VIDEO", "-vf",
        f"select='isnan(prev_selected_t)+gte(t-prev_selected_t\\,15)',scale=320:180,tile={side}x{side}", "-frames:v", "1")))
    return [(caption, path.read_bytes()) for caption, path in found if path]


# apply button ---------------------------------------------------------------------------------------------------

JOB = {"state": "idle"}


def job_state(folder):
    return JOB if JOB["state"] != "idle" else load(folder / "apply.json", {"state": "idle"})


def begin():
    with LOCK:
        if JOB["state"] == "running":
            return False
        JOB.clear()
        JOB.update(state="running", parts=[], started=time.time())
        return True


def run_apply(folder, ask=revise.ask_claude):
    """begin() first. Claude works on a copy; a part is written only if its comment and frame didn't change meanwhile."""
    try:
        with LOCK:
            board, review = load(folder / "board.json"), load(folder / "review.json", {"options": {}})
            todo = revise.jobs(board, review)
            JOB["parts"] = [j["part"] for j in todo]
        if not todo:
            raise RuntimeError("There are no comments to apply.")
        words = [w for u in load(folder / "words.json")["results"]["utterances"] for w in u["words"]]
        fmt = __doc__[__doc__.index("  visual kinds"):__doc__.index("  The page shows")]
        good, failed = revise.revise(board, review, lambda b: compile_board(folder, copy.deepcopy(b)), resolve_manifest, words, fmt, ask,
                                     pictures(folder, board, todo))

        results, changed = {}, False
        with LOCK:
            board, review = load(folder / "board.json"), load(folder / "review.json", {"options": {}})
            before, now = copy.deepcopy(board), {j["part"]: j for j in revise.jobs(board, review)}
            for job in todo:
                pid, change = job["part"], good.get(job["part"])
                result = results[pid] = dict(note=job["note"], option=job["option"])
                same = pid in now and all(now[pid][k] == job[k] for k in ("option", "note", "verdict"))
                if not same:
                    result.update(status="not_done", summary="You changed this while Claude was working, so press Apply comments again.")
                elif not change:
                    print("apply: rejected", pid, failed.get(pid), file=sys.stderr, flush=True)
                    result.update(status="not_done", summary="Claude couldn't make a frame that fits. Reword it, or ask for it in the Claude chat.")
                elif change["status"] == "needs_chat":
                    result.update(status="needs_chat", summary=str(change["summary"])[:400])
                else:
                    revise.add(board, change, job)
                    changed = True
                    result.update(status=change["status"], summary=str(change["summary"])[:400])
            if changed:
                history = folder / "history"
                history.mkdir(exist_ok=True)
                stamp = f"{time.strftime('%Y%m%d-%H%M%S')}-{time.time_ns() % 1000000:06d}"
                save(history / f"board-{stamp}.json", before)
                save(history / f"review-{stamp}.json", review)
                save(folder / "board.json", board)
            done = dict(state="done", finished=time.time(), changed=changed, results=results)
            save(folder / "apply.json", done)
            JOB.clear()
            JOB.update(done)
    except Exception as e:  # the page is the only place he will see this, and a stuck "running" would lock the button
        print("apply failed:", repr(e), file=sys.stderr, flush=True)
        with LOCK:
            JOB.clear()
            JOB.update(state="failed", finished=time.time(), changed=False, results={},
                       error=str(e) if isinstance(e, RuntimeError) else "Something went wrong. Nothing was changed.")


# server ---------------------------------------------------------------------------------------------------------

TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".json": "application/json",
         ".jpg": "image/jpeg", ".png": "image/png", ".svg": "image/svg+xml"}


def make_handler(folder, port):
    _, root = compile_board(folder)
    hosts = {f"localhost:{port}", f"127.0.0.1:{port}"}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, code, body, kind="application/json"):
            data = body if isinstance(body, bytes) else json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def version(self):
            return str(max((p.stat().st_mtime for p in (folder / "board.json", root / "manifest.json"))))

        def send_file(self, base, rel):
            path = (base / rel).resolve()
            if base.resolve() not in path.parents or path.suffix not in TYPES or not path.is_file():
                return self.reply(404, {"error": "not found"})
            self.reply(200, path.read_bytes(), TYPES[path.suffix])

        def still(self, track, frame):
            out = still(folder, track, frame)
            if not out:
                return self.reply(404, {"error": "no frame there"})
            self.send_file(folder / "media", f"stills/{out.name}")

        def do_GET(self):
            if self.headers.get("Host") not in hosts:
                return self.reply(403, {"error": "local only"})
            path = unquote(urlsplit(self.path).path)
            if path == "/":
                return self.reply(200, (HERE / "index.html").read_bytes(), TYPES[".html"])
            if path == "/api/version":
                return self.reply(200, dict(version=self.version(), job=job_state(folder)))
            if path == "/api/board":
                board, _ = compile_board(folder)
                review = load(folder / "review.json", {"options": {}})
                return self.reply(200, dict(board=board, review=review, job=job_state(folder), version=self.version()))
            if found := re.fullmatch(r"/still/(cam|screen)/(\d{1,7})\.jpg", path):
                return self.still(found[1], int(found[2]))
            if path.startswith("/templates/"):
                return self.send_file(root / "templates", path[len("/templates/"):])
            self.reply(404, {"error": "not found"})

        def do_POST(self):
            origin = self.headers.get("Origin")
            if (self.headers.get("Host") not in hosts or (origin and origin not in {f"http://{h}" for h in hosts})
                    or self.headers.get("Content-Type") != "application/json" or self.path not in ("/api/review", "/api/apply")):
                return self.reply(403, {"error": "not allowed"})
            if self.path == "/api/apply":
                self.rfile.read(min(40000, max(0, int(self.headers.get("Content-Length") or 0))))
                if not begin():
                    return self.reply(409, {"error": "already running"})
                threading.Thread(target=run_apply, args=(folder,), daemon=True).start()
                return self.reply(202, {"ok": True})
            try:
                size = int(self.headers.get("Content-Length", 0))
                if not 0 < size <= 40000:
                    raise ValueError("bad size")
                patch = json.loads(self.rfile.read(size))
                with LOCK:
                    board = load(folder / "board.json")
                    review = apply_patch(board, load(folder / "review.json", {"options": {}}), patch)
                    save(folder / "review.json", review)
            except ValueError as e:
                return self.reply(400, {"error": str(e)})
            self.reply(200, {"ok": True})

    return Handler


# cli ------------------------------------------------------------------------------------------------------------

def selftest():
    part = {"id": "A", "options": [{"id": "A.1"}]}
    board = {"parts": [part]}
    r = {}
    action = lambda: [j["action"] for j in revise.jobs(board, r)]
    assert action() == []
    apply_patch(board, r, {"option": "A.1", "note": "bigger"})
    assert action() == ["revise"]
    for verdict, expect in (("yes", []), ("revise", ["revise"]), ("no", ["new_idea"])):
        apply_patch(board, r, {"option": "A.1", "verdict": verdict})
        assert action() == expect
    apply_patch(board, r, {"option": "A.1", "note": ""})
    assert action() == ["new_idea"]
    apply_patch(board, r, {"option": "A.1", "verdict": "revise"})
    assert action() == []
    part["options"] += [{"id": "A.2", "replaces": "A.1", "fresh": True}, {"id": "A.3", "replaces": "A.2"}]
    r["options"].update({"A.1": dict(note="old idea"), "A.2": dict(note="kept"), "A.3": dict(note="now")})
    assert revise.jobs(board, r)[0]["earlier_comments"] == ["kept"]
    box = dict(x=100, y=100, w=400, h=200)
    sealed = lambda **m: revise.problems("graphic-full", dict(kind="free", items=[dict(box, shape="html", **m)]))
    assert not sealed(html='<svg><path fill="url(#g)"/></svg><b>Hi</b>', css="b{color:red}")
    for body in ("<script>x</script>", '<b onclick="x">', '<img src="//evil">', '<a href="//evil">', '<b style="background:url(//evil)">',
                 '<meta http-equiv="refresh">', "<style>@import 'x'</style>"):
        assert sealed(html=body), body
    assert sealed(html="<b>", css="b{background:url(//evil)}")
    zoomed = lambda top: revise.problems("full", dict(kind="none", punch=dict(scale=1.6, top=top)))
    assert not zoomed(.06) and zoomed(.5) and revise.head(dict(scale=1.6, top=.06))[1] < 0
    words = [dict(n=n, start=float(i), end=i + 1.0) for i, n in enumerate(["short", "dramas", "are", "dramas"])]
    assert find_cue(words, "Dramas", 0, 4) == 1 and find_cue(words, "dramas", 2, 4) == 3 and find_cue(words, "cats", 0, 4) is None
    pip = [0.794, 0.5975, 0.18, 0.32]
    z = solve_zoom([0.6, 0.6, 0.15, 0.2], [140, 160, 200, 220], pip)
    r_edge, b_edge = z["x"] + 0.75 * z["s"], z["y"] + 0.8 * z["s"]
    assert r_edge <= pip[0] or b_edge <= pip[1]
    assert merge({"a": {"b": 1, "c": [1, 2]}}, {"a": {"c": [3]}}) == {"a": {"b": 1, "c": [3]}}
    with tempfile.TemporaryDirectory() as tmp:  # the Apply button's write path, with a stand-in for Claude
        d, bank_dir = Path(tmp) / "board", Path(tmp) / "manifest"
        d.mkdir(), bank_dir.mkdir()
        region = dict(role="speaker", x=79.4, y=59.75, w=18, h=32)
        save(bank_dir / "manifest.json", dict(meta=dict(name="T", version=1, updated=""), templates=[], profiles={"p": {"label": "P"}}, base=dict(
            identity={"rules": []}, brand={"colors": {}}, pacing={"screenZooms": {"levels": [140]}, "punchIn": {"levels": [130]}},
            motionGraphics=dict(maxOnScreen=3, sync={"landOn": ""}, speakerInteraction="", frequency=dict(perMin=5, maxGapSec=20, fullScreenCoveragePct=[0, 100])),
            structure={"segmentTypes": []}, layouts=dict(switching=dict(minHoldSec=2, maxHoldSec=20),
            library=[dict(id="screen-pip", name="", regions=[region]), dict(id="graphic-full", name="", regions=[])]))))
        save(d / "timeline.json", dict(fps=30, totalFrames=900))
        save(d / "words.json", dict(results=dict(utterances=[dict(words=[dict(word="hello", punctuated_word="Hello", start=1.0, end=1.4)])])))
        frame = dict(kind="free", items=[dict(shape="text", x=100, y=100, w=600, h=120, text="Hello", size=80, cue="hello")])
        save(d / "board.json", dict(video="T", manifest=dict(dir=str(bank_dir), profile="p"), parts=[dict(id="A", start=1, end=4, intent="", options=[
            dict(id="A.1", title="t", layout="graphic-full", visual=frame)])]))

        def attempt(note, *answers):
            save(d / "review.json", dict(options={revise.current(load(d / "board.json")["parts"][0])["id"]: dict(note=note)}))
            queue = list(answers)
            assert begin()
            run_apply(d, lambda *_: queue.pop(0)())
            return len(load(d / "board.json")["parts"][0]["options"]), JOB["state"], JOB["results"].get("A", {}).get("status")

        def ok(size=70):
            items = [dict(frame["items"][0], size=size)]
            return [dict(part="A", status="changed", summary="s", layout="graphic-full", visual=dict(frame, items=items))]

        unsafe = lambda: [dict(part="A", status="changed", summary="s", layout="graphic-full", visual=dict(frame, css="x{background:url(//evil)}"))]
        unsaid = lambda: [dict(part="A", status="changed", summary="s", layout="graphic-full", visual=dict(frame, items=[dict(frame["items"][0], cue="never said")]))]

        def down():
            raise RuntimeError("offline")

        def he_edits():
            save(d / "review.json", dict(options={"A.2": dict(note="actually, smaller")}))
            return ok(75)

        assert attempt("bigger", ok) == (2, "done", "changed")
        assert attempt("bigger", unsafe, unsaid) == (2, "done", "not_done")
        assert attempt("bigger", down) == (2, "failed", None)
        assert attempt("bigger", he_edits) == (2, "done", "not_done")
        assert attempt("use my file", lambda: [dict(part="A", status="needs_chat", summary="s")]) == (2, "done", "needs_chat")
        assert attempt("bigger", ok, lambda: ok(72)) == (3, "done", "changed")  # identical is sent back
        split = lambda: [dict(ok(74)[0], end=3, extra=[dict(title="two", layout="graphic-full", start=3, end=4, visual=dict(kind="none"))])]
        assert attempt("split it", split) == (4, "done", "changed")
        assert [p["id"] for p in load(d / "board.json")["parts"]] == ["A", "A1"]
        later = lambda: [dict(ok()[0], start=2, end=3, visual=dict(kind="none"))]
        assert attempt("start later", later) == (5, "done", "changed")  # past the word the older options are cued on
        assert not compile_board(d)[0]["errors"]
        assert len(list((d / "history").glob("board-*.json"))) == 4
    print("selftest ok")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "selftest":
        return selftest()
    if cmd not in ("serve", "check", "next", "apply") or len(sys.argv) < 3:
        sys.exit(__doc__)
    folder = Path(sys.argv[2]).expanduser().resolve()
    if cmd == "serve":
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 8774
        print(f"storyboard on http://localhost:{port}", flush=True)
        return ThreadingHTTPServer(("127.0.0.1", port), make_handler(folder, port)).serve_forever()
    if cmd == "apply":
        begin()
        run_apply(folder)
        print(json.dumps(JOB, indent=1))
        sys.exit(JOB["state"] != "done")
    board, _ = compile_board(folder)
    if cmd == "check":
        for e in board["errors"]:
            print("ERROR", e)
        for p in board["parts"]:
            for o in p["options"]:
                for level, text in o.get("checks", []):
                    print(level.upper(), o["id"], text)
            replaced = {o.get("replaces") for o in p["options"]}
            for o in p["options"]:
                if o["id"] not in replaced:
                    for item in o["visual"].get("items", []):
                        if "placeholder" in item:
                            print("ASSET", item["asset"], item["placeholder"], item.get("label") or item.get("cue"))
        print(len(board["parts"]), "parts", json.dumps(board["summary"]))
        sys.exit(bool(board["errors"]))
    todo = revise.jobs(load(folder / "board.json"), load(folder / "review.json", {"options": {}}))
    print(json.dumps([{k: j[k] for k in ("part", "option", "action", "note")} for j in todo], indent=1))


if __name__ == "__main__":
    main()
