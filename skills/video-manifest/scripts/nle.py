#!/usr/bin/env python3
"""Read an NLE project and measure how it was edited.

  nle.py <project> --out <dir>

<project> can be:
  - a CapCut draft folder (or its draft_info.json / draft_content.json)
  - an FCP7 XML export (.xml, Premiere: File > Export > Final Cut Pro XML)
  - an FCPXML export (.fcpxml / .fcpxmld, DaVinci Resolve, Final Cut Pro, and others)
  - a Palmier Pro project (.palmier package). --timeline NAME picks a timeline (default: the active one).
    --dialogue also writes <dir>/dialogue.mp3 (the kept speech, in order) for measure.py
Writes <dir>/nle.json (summary + normalised timeline) and prints the headline numbers.
DaVinci Resolve can also be read live through the davinci-resolve MCP (see SKILL.md).
"""
import json, math, re, statistics, sys
import xml.etree.ElementTree as ET
from collections import Counter
from fractions import Fraction
from pathlib import Path


def seg(start, dur, name="", scale=1.0, x=0.0, y=0.0, volume=1.0, **extra):
    # x/y are the clip centre as % of frame (50,50 = centred); extra: kind (bin folder / role), w, h (% of frame)
    return {"start": round(start, 3), "dur": round(dur, 3), "name": name, "scale": round(scale, 3),
            "x": round(x, 1), "y": round(y, 1), "volume": round(volume, 3), **extra}


def timeline(tool, fps, w, h, duration):
    return {"tool": tool, "fps": fps, "width": w, "height": h, "duration": round(duration, 3),
            "video": [], "audio": [], "texts": [], "transitions": [], "effects": [], "keyframes": Counter()}


# ---------- CapCut ----------
def rgb_hex(c):
    return "#" + "".join(f"{round(v * 255):02X}" for v in c[:3]) if c else None


def capcut(p):
    p = Path(p)
    if p.is_dir():
        p = next((p / n for n in ("draft_info.json", "draft_content.json") if (p / n).exists()), None)
        if not p:
            sys.exit("no draft_info.json or draft_content.json in that folder (newer CapCut versions may encrypt drafts)")
    d = json.loads(p.read_text())
    mats = {m["id"]: (cat, m) for cat, lst in d["materials"].items() if isinstance(lst, list) for m in lst if isinstance(m, dict) and "id" in m}
    cv = d.get("canvas_config") or {}
    tl = timeline("capcut", d.get("fps"), cv.get("width"), cv.get("height"), d["duration"] / 1e6)
    for ti, tr in enumerate(d["tracks"]):
        lane = []
        for s in tr["segments"]:
            st, du = s["target_timerange"]["start"] / 1e6, s["target_timerange"]["duration"] / 1e6
            cat, m = mats.get(s.get("material_id"), (None, {}))
            for k in s.get("common_keyframes") or []:
                tl["keyframes"][k.get("property_type", "?")] += 1
            for r in s.get("extra_material_refs") or []:
                rc, rm = mats.get(r, (None, {}))
                if rc == "transitions":
                    tl["transitions"].append({"name": rm.get("name") or "transition", "dur": round(rm.get("duration", 0) / 1e6, 3)})
                elif rc == "material_animations":
                    for an in rm.get("animations") or []:
                        tl["effects"].append(f"anim:{an.get('type')}:{an.get('name') or an.get('resource_id')}")
            clip = s.get("clip") or {}
            sc = (clip.get("scale") or {}).get("x", 1.0)
            tx, ty = (clip.get("transform") or {}).get("x", 0.0), (clip.get("transform") or {}).get("y", 0.0)
            # ponytail: CapCut transform is -1..1 from centre with y up; converted to % from top-left
            cx, cy = 50 + tx * 50, 50 - ty * 50
            if tr["type"] in ("video", "audio"):
                name = m.get("material_name") or m.get("name") or Path(m.get("path", "")).name
                lane.append(seg(st, du, name, sc, cx, cy, s.get("volume", 1.0) or 0))
            elif tr["type"] == "text" and cat == "texts":
                c = json.loads(m.get("content") or "{}")
                sty = (c.get("styles") or [{}])[0]
                tl["texts"].append({"lane": ti, "start": round(st, 3), "dur": round(du, 3), "text": c.get("text", "")[:80],
                                    "font": Path((sty.get("font") or {}).get("path", "")).stem or None,
                                    "size": sty.get("size"),
                                    "color": rgb_hex(((sty.get("fill") or {}).get("content") or {}).get("solid", {}).get("color")),
                                    "stroke": bool(sty.get("strokes")), "shadow": bool(sty.get("shadows")),
                                    "x": round(cx, 1), "y": round(cy, 1), "scale": round(sc, 3)})
            elif tr["type"] in ("effect", "filter"):
                tl["effects"].append(m.get("name") or m.get("type") or tr["type"])
        if tr["type"] in ("video", "audio") and lane:
            tl[tr["type"]].append(lane)
    return tl


# ---------- FCP7 XML (Premiere export) ----------
def xmeml(p):
    root = ET.parse(p).getroot()
    sq = max(root.iter("sequence"), key=lambda s: int(s.findtext("duration") or 0))
    fps = int(sq.findtext("rate/timebase") or 30)
    fmt = sq.find("media/video/format/samplecharacteristics")
    w, h = (int(fmt.findtext("width")), int(fmt.findtext("height"))) if fmt is not None else (None, None)
    tl = timeline("premiere-xml", fps, w, h, int(sq.findtext("duration") or 0) / fps)

    def param(item, pid):
        for prm in item.iter("parameter"):
            if prm.findtext("parameterid") == pid:
                return prm.find("value")

    def items(track, kind):
        lane, prev = [], 0
        for el in track:
            if el.tag == "transitionitem":
                tl["transitions"].append({"name": el.findtext("effect/name") or "transition",
                                          "dur": round((int(el.findtext("end")) - int(el.findtext("start"))) / fps, 3)})
                prev = int(el.findtext("end"))
                continue
            if el.tag not in ("clipitem", "generatoritem"):
                continue
            s, e = int(el.findtext("start")), int(el.findtext("end"))
            if s < 0:
                s = prev
            if e < 0:
                e = s + int(el.findtext("out") or 0) - int(el.findtext("in") or 0)
            prev = e
            eff = el.findtext("effect/name") or ""
            if el.tag == "generatoritem" or "text" in eff.lower() or "title" in eff.lower():
                txt = param(el, "str")
                tl["texts"].append({"start": round(s / fps, 3), "dur": round((e - s) / fps, 3),
                                    "text": (txt.text if txt is not None else el.findtext("name") or "")[:80],
                                    "font": (param(el, "fontname").text if param(el, "fontname") is not None else None),
                                    "size": (param(el, "fontsize").text if param(el, "fontsize") is not None else None)})
                continue
            sc = param(el, "scale")
            ce = param(el, "center")
            lvl = param(el, "level")
            for f in el.findall("filter/effect/name"):
                if f.text not in ("Basic Motion", "Audio Levels", "Crop", "Opacity"):
                    tl["effects"].append(f.text)
            for kf in el.iter("keyframe"):
                tl["keyframes"]["keyframe"] += 1
            # ponytail: FCP7 centre is -1..1 half-frame offsets like CapCut; treat positions as approximate
            hx = float(ce.findtext("horiz")) if ce is not None and ce.findtext("horiz") else 0.0
            vy = float(ce.findtext("vert")) if ce is not None and ce.findtext("vert") else 0.0
            vol = float(lvl.text) if lvl is not None and lvl.text and kind == "audio" else 1.0
            lane.append(seg(s / fps, (e - s) / fps, el.findtext("name") or "",
                            float(sc.text) / 100 if sc is not None and sc.text else 1.0, 50 + hx * 50, 50 + vy * 50, vol))
        return lane

    for kind in ("video", "audio"):
        for track in sq.findall(f"media/{kind}/track"):
            lane = items(track, kind)
            if lane:
                tl[kind].append(lane)
    return tl


# ---------- FCPXML (Resolve, Final Cut, others) ----------
def ft(v):
    if not v:
        return 0.0
    return float(Fraction(v.rstrip("s")))


def db_to_lin(v):
    m = re.match(r"(-?[\d.]+)dB", v or "")
    return 10 ** (float(m.group(1)) / 20) if m else 1.0


def fcpxml(p):
    p = Path(p)
    if p.is_dir():
        p = p / "Info.fcpxml"
    root = ET.parse(p).getroot()
    fmts = {f.get("id"): f for f in root.iter("format")}
    sq = root.find(".//sequence")
    f = fmts.get(sq.get("format"))
    fd = ft(f.get("frameDuration")) if f is not None and f.get("frameDuration") else 1 / 30
    w, h = (int(f.get("width")), int(f.get("height"))) if f is not None and f.get("width") else (1920, 1080)
    tl = timeline("fcpxml", round(1 / fd, 3), w, h, ft(sq.get("duration")))
    main, dialog, lanes = [], [], {}
    CLIPS = {"asset-clip", "clip", "ref-clip", "mc-clip", "sync-clip", "video", "title", "audio"}

    def xform(e):
        t = e.find("adjust-transform")
        if t is None:
            return 1.0, 50.0, 50.0
        sx = float((t.get("scale") or "1 1").split()[0])
        px, py = (float(v) for v in (t.get("position") or "0 0").split())
        # FCPXML position is in % of frame height from centre, y up
        return sx, 50 + px / 100 * h / w * 100, 50 - py

    def text_of(e):
        ts = e.find(".//text-style-def/text-style")
        return {"text": "".join(e.find("text").itertext())[:80] if e.find("text") is not None else e.get("name", ""),
                "font": ts.get("font") if ts is not None else None, "size": ts.get("fontSize") if ts is not None else None,
                "color": ts.get("fontColor") if ts is not None else None}

    for e in sq.find("spine"):
        off, du, st = ft(e.get("offset")), ft(e.get("duration")), ft(e.get("start"))
        if e.tag == "transition":
            tl["transitions"].append({"name": e.get("name") or "transition", "dur": round(du, 3)})
            continue
        if e.tag == "title":
            tl["texts"].append({"start": round(off, 3), "dur": round(du, 3), **text_of(e)})
        elif e.tag in CLIPS:
            sc, x, y = xform(e)
            main.append(seg(off, du, e.get("name", ""), sc, x, y))
            if e.get("audioStart") or e.get("audioDuration"):
                a0 = off + ft(e.get("audioStart") or e.get("start")) - st
                dialog.append(seg(a0, ft(e.get("audioDuration") or e.get("duration")), e.get("name", "")))
            else:
                dialog.append(seg(off, du, e.get("name", "")))
        for c in e:
            if c.get("lane") is None or c.tag not in CLIPS:
                continue
            lane = int(c.get("lane"))
            co, cd = off + ft(c.get("offset")) - st, ft(c.get("duration"))
            if c.tag == "title":
                tl["texts"].append({"start": round(co, 3), "dur": round(cd, 3), **text_of(c)})
                continue
            vol = c.find("adjust-volume")
            sc, x, y = xform(c)
            lanes.setdefault(lane, []).append(seg(co, cd, c.get("name", ""), sc, x, y, db_to_lin(vol.get("amount")) if vol is not None else 1.0))
        for fx in e.iter("filter-video"):
            tl["effects"].append(fx.get("name") or "filter")
        for kf in e.iter("keyframe"):
            tl["keyframes"]["keyframe"] += 1
    tl["video"] = [main] + [lanes[k] for k in sorted(k for k in lanes if k > 0)]
    tl["audio"] = [dialog] + [lanes[k] for k in sorted(k for k in lanes if k < 0)]
    return tl


# ---------- Palmier Pro ----------
def rgba_hex(c):
    return "#" + "".join(f"{round(c.get(k, 0) * 255):02X}" for k in "rgb") if c else None


def palmier(p, timeline_name=None):
    p = Path(p)
    d = json.loads((p / "project.json").read_text())
    media = json.loads((p / "media.json").read_text()) if (p / "media.json").exists() else {}
    folders = {f["id"]: f["name"] for f in media.get("folders", [])}
    entries = {e["id"]: e for e in media.get("entries", [])}
    tls = {t["id"]: t for t in d["timelines"]}
    end = lambda t: max([c["startFrame"] + c["durationFrames"] for tr in t["tracks"] for c in tr["clips"]] or [0])
    root = next((t for t in d["timelines"] if t["name"] == timeline_name), None) if timeline_name else tls.get(d.get("activeTimelineId"))
    root = root or max(d["timelines"], key=end)
    fps = root["fps"]
    tl = timeline("palmier", fps, root["width"], root["height"], end(root) / fps)
    tl.update({"timelineName": root["name"], "timelines": [f"{t['name']} ({round(end(t) / t['fps'])}s)" for t in d["timelines"]],
               "markers": [m.get("name") or m.get("comment") for m in root.get("markers") or []],
               "framing": {}, "rampFrames": [], "colorParams": {}, "speed": Counter()})

    def kind(c):
        if c["mediaType"] == "sequence":
            return "sequence"
        e = entries.get(c.get("mediaRef")) or {}
        return folders.get(e.get("folderId"), "(root)")

    def name(c):
        if c["mediaType"] == "sequence":
            return "sequence:" + (tls.get(c["mediaRef"]) or {}).get("name", "?")
        return (entries.get(c.get("mediaRef")) or {}).get("name") or c.get("textContent", "")[:40]

    def vol(c):
        kf = (c.get("volumeTrack") or {}).get("keyframes")
        if kf:
            return 10 ** (statistics.median(k["value"] for k in kf) / 20)
        return c.get("volume", 1)

    def text(c, start, lane):
        st = c.get("textStyle") or {}
        t = c["transform"]
        an = c.get("textAnimation") or {}
        ws = c.get("wordStyles") or {}
        return {"lane": lane, "start": round(start, 3), "dur": round(c["durationFrames"] / fps, 3),
                "text": (c.get("textContent") or "")[:80], "font": st.get("fontName"), "size": st.get("fontSize"),
                "color": rgba_hex(st.get("color")), "stroke": (st.get("border") or {}).get("enabled", False),
                "shadow": (st.get("shadow") or {}).get("enabled", False),
                "background": (st.get("background") or {}).get("enabled", False) or any((w.get("background") or {}).get("enabled") for w in ws.values()),
                "highlight": next((rgba_hex(w["background"]["color"]) for w in ws.values() if (w.get("background") or {}).get("enabled")), None),
                "case": st.get("fontCase"), "bold": st.get("isBold"),
                "anim": an.get("preset") or "/".join(str(an.get(k)) for k in ("delivery", "effect") if an.get(k)) or None,
                "x": round(t["centerX"] * 100, 1), "y": round(t["centerY"] * 100, 1), "w": round(t["width"] * 100, 1)}

    def nested_texts(tid, offset, lo, hi, depth):
        t = tls.get(tid)
        if not t or depth > 3:
            return
        for i, tr in enumerate(t["tracks"]):
            for c in tr["clips"]:
                a, b = c["startFrame"], c["startFrame"] + c["durationFrames"]
                if b <= lo or a >= hi:
                    continue
                if c["mediaType"] == "text":
                    tl["texts"].append(text(c, (offset + max(a, lo) - lo) / fps, f"seq{depth}:{i}"))
                elif c["mediaType"] == "sequence":
                    nested_texts(c["mediaRef"], offset + max(a, lo) - lo, c["trimStartFrame"], c["trimStartFrame"] + c["durationFrames"], depth + 1)

    vtracks, links = [], {}
    for i, tr in enumerate(root["tracks"]):
        if tr.get("hidden") or tr.get("muted") and tr["type"] == "audio":
            continue
        lane = []
        for c in tr["clips"]:
            st, du = c["startFrame"] / fps, c["durationFrames"] / fps
            for k in ("positionTrack", "scaleTrack", "cropTrack", "opacityTrack", "rotationTrack", "volumeTrack"):
                if c.get(k):
                    tl["keyframes"][k] += len(c[k].get("keyframes", []))
            for e in c.get("effects") or []:
                tl["effects"].append(e.get("type"))
                if e.get("type", "").startswith("color."):
                    for pk, pv in (e.get("params") or {}).items():
                        tl["colorParams"].setdefault(f"{e['type']}.{pk}", []).append(pv.get("value"))
            for m in c.get("masks") or []:
                tl["effects"].append(f"mask:{(m.get('seed') or {}).get('type')}")
            if c.get("speed", 1) != 1:
                tl["speed"][str(c["speed"])] += 1
            if c.get("speedCurve"):
                tl["speed"]["speedRamp"] += 1
            for side in ("In", "Out"):
                if c.get(f"fade{side}Frames"):
                    tl["transitions"].append({"name": f"fade {side.lower()} ({c['mediaType']})", "dur": round(c[f"fade{side}Frames"] / fps, 3)})
            if c["mediaType"] == "text":
                tl["texts"].append(text(c, st, "caption" if c.get("captionGroupId") or c.get("wordTimings") else i))
                continue
            if c["mediaType"] == "sequence":
                nested_texts(c["mediaRef"], c["startFrame"], c["trimStartFrame"], c["trimStartFrame"] + c["durationFrames"], 1)
            t = c["transform"]
            src = ((entries.get(c.get("mediaRef")) or {}).get("source") or {})
            path = (src.get("external") or {}).get("absolutePath") or (src.get("project") and str(p / src["project"]["relativePath"]))
            sg = seg(st, du, name(c), math.sqrt(t["width"] * t["height"]), t["centerX"] * 100, t["centerY"] * 100, vol(c),
                     kind=kind(c), w=round(t["width"] * 100, 1), h=round(t["height"] * 100, 1), link=c.get("linkGroupId"),
                     media=c["mediaType"], clip=c, src=path, trim=round(c.get("trimStartFrame", 0) / fps, 4))
            lane.append(sg)
        if lane:
            (vtracks if tr["type"] == "video" else tl["audio"]).append(lane)
    # main track = the video lane holding the most linked (A-roll with sound) footage
    score = lambda lane: sum(s["dur"] for s in lane if s["media"] == "video" and s["link"])
    vtracks.sort(key=score, reverse=True)
    tl["video"] = vtracks
    main_links = {s["link"] for s in vtracks[0]} if vtracks else set()
    for lane in tl["audio"]:
        for s in lane:
            if s["link"] and s["link"] in main_links:
                s["kind"] = "dialog"
    # synced sources = lanes cut in lockstep with the main track (screen recording, second camera)
    starts = {round(x["start"], 2) for x in (vtracks[0] if vtracks else [])}
    synced = [l for l in vtracks[1:] if len(l) >= 5 and sum(round(x["start"], 2) in starts for x in l) / len(l) > 0.8]
    for l in synced:
        for x in l:
            x["kind"] = "synced:" + x["name"]
    # framing states: visible box of each keyed state, in % of frame. Palmier keyframes are absolute:
    # scale = size as a fraction of frame width, position = top-left corner, crop = fraction of the source trimmed.
    for x in [x for l in (vtracks[:1] + synced) for x in l]:
        c = x["clip"]
        tf, base_crop = c["transform"], c["crop"]
        sk = {k["frame"]: k["value"]["a"] for k in (c.get("scaleTrack") or {}).get("keyframes", [])}
        pk = {k["frame"]: (k["value"]["a"], k["value"]["b"]) for k in (c.get("positionTrack") or {}).get("keyframes", [])}
        ck = {k["frame"]: k["value"] for k in (c.get("cropTrack") or {}).get("keyframes", [])}
        held = lambda D, f, dflt: D[max(k for k in D if k <= f)] if any(k <= f for k in D) else dflt
        frames = sorted(set(sk) | set(pk) | set(ck)) or [0]
        e = entries.get(c.get("mediaRef")) or {}
        src_ar = (e.get("sourceWidth") or 16) / (e.get("sourceHeight") or 9)
        frame_ar = root["width"] / root["height"]
        for f in frames:
            sz = held(sk, f, tf["width"])
            hgt = sz * frame_ar / src_ar
            px, py = held(pk, f, (tf["centerX"] - sz / 2, tf["centerY"] - hgt / 2))
            cr = held(ck, f, base_crop)
            l, r = px + cr["left"] * sz, px + sz * (1 - cr["right"])
            t, b = py + cr["top"] * hgt, py + hgt * (1 - cr["bottom"])
            l, t, r, b = (round(max(0, min(100, v * 100))) for v in (l, t, r, b))
            box = (f"zoom {round(sz * 100)}% " if sz > 1.1 else "") + f"x{l}-{r} y{t}-{b} (w{r - l} h{b - t})" + (f" round{c['edgeRounding']}" if c.get("edgeRounding") else "")
            tl["framing"].setdefault(x["name"], Counter())[box] += 1
        for kf in (list(sk.items()), list(pk.items()), list(ck.items())):
            kf.sort()
            for (fa, va), (fb, vb) in zip(kf, kf[1:]):
                if va != vb:
                    tl["rampFrames"].append(fb - fa)
    for lane in tl["video"] + tl["audio"]:
        for s in lane:
            s.pop("clip", None)
    return tl


# ---------- summary ----------
def pct(xs, p):
    if not xs:
        return None
    xs = sorted(xs)
    return round(xs[min(len(xs) - 1, int(round(p / 100 * (len(xs) - 1))))], 3)


def union(segs):
    tot, end = 0.0, -1.0
    for s in sorted(segs, key=lambda s: s["start"]):
        a, b = s["start"], s["start"] + s["dur"]
        if b > end:
            tot += b - max(a, end)
            end = b
    return tot


def db(v):
    return round(20 * math.log10(v), 1) if v and v > 0 else None


def jl(main, audio, fps):
    """Compare main video cut points with dialogue audio cut points. Audio cut earlier = J, later = L."""
    if not audio:
        return {"detectable": False, "note": "no separate dialogue audio track"}
    frame = 1 / (fps or 30)
    vcuts = [s["start"] for s in main[1:]]
    starts = [s["start"] for s in audio]
    ends = [s["start"] + s["dur"] for s in audio]
    near = lambda xs, t: min(xs, key=lambda a: abs(a - t))
    j, l, offs = 0, 0, []
    for t in vcuts:
        a_in, a_out = near(starts, t), near(ends, t)
        if t - 1.0 <= a_in < t - frame * 1.5:      # incoming audio starts before the picture
            j += 1
            offs.append(round((t - a_in) / frame))
        elif t + frame * 1.5 < a_out <= t + 1.0:   # outgoing audio runs past the picture
            l += 1
            offs.append(round((a_out - t) / frame))
    return {"detectable": True, "videoCuts": len(vcuts), "jCuts": j, "lCuts": l, "straightCuts": len(vcuts) - j - l,
            "medianOffsetFrames": pct(offs, 50)}


def text_stats(ts, dur, dedupe=False):
    samples = [t["text"] for t in ts]
    if dedupe:
        samples = [x for i, x in enumerate(samples) if not i or x != samples[i - 1]]
    return {
        "count": len(ts), "perMin": round(len(ts) / dur * 60, 1),
        "medianSec": pct([t["dur"] for t in ts], 50),
        "wordsPerItem": pct([len(t["text"].split()) for t in ts], 50),
        "fonts": dict(Counter(t.get("font") for t in ts).most_common(5)),
        "sizes": dict(Counter(str(t.get("size")) for t in ts).most_common(5)),
        "colors": dict(Counter(t.get("color") for t in ts).most_common(5)),
        "stroke": sum(1 for t in ts if t.get("stroke")), "shadow": sum(1 for t in ts if t.get("shadow")),
        "verticalPositions": dict(Counter(f"y{round(t['y'] / 5) * 5}" for t in ts if "y" in t).most_common(5)),
        "horizontalPositions": dict(Counter(f"x{round(t['x'] / 5) * 5}" for t in ts if "x" in t).most_common(5)),
        "animations": dict(Counter(t.get("anim") for t in ts if t.get("anim")).most_common(6)),
        "background": sum(1 for t in ts if t.get("background")),
        "highlightColors": dict(Counter(t.get("highlight") for t in ts if t.get("highlight")).most_common(3)),
        "case": dict(Counter(t.get("case") for t in ts if t.get("case")).most_common(3)),
        "samples": samples[:12],
    }


def summarize(tl):
    dur = tl["duration"] or 1
    vids, auds = tl["video"], tl["audio"]
    main = vids[0] if vids else []
    shots = [s["dur"] for s in main]
    # caption lanes = many short text items on one lane (word/phrase captions); kept out of "visual changes"
    by_lane = {}
    for t in tl["texts"]:
        by_lane.setdefault(t.get("lane", 0), []).append(t)
    cap_lanes = {k for k, v in by_lane.items() if k == "caption" or len(v) >= 15 and statistics.median([t["dur"] for t in v]) < 1.5}
    caps = [t for t in tl["texts"] if t.get("lane", 0) in cap_lanes]
    texts = [t for t in tl["texts"] if t.get("lane", 0) not in cap_lanes]
    bounds = sorted({round(s["start"], 2) for lane in vids for s in lane} | {round(t["start"], 2) for t in texts})
    changes = [round(b - a, 2) for a, b in zip(bounds, bounds[1:])]
    syn = [l for l in vids[1:] if l and str(l[0].get("kind", "")).startswith("synced:")]
    over = [s for lane in vids[1:] if lane not in syn for s in lane]
    is_full = lambda s: (s["w"] >= 95 and s["h"] >= 95) if "w" in s else (s["scale"] >= 0.95 and abs(s["x"] - 50) < 5 and abs(s["y"] - 50) < 5)
    full = [s for s in over if is_full(s)]
    pip = [s for s in over if not is_full(s)]
    geo = lambda s: f"w{round(s['w'])}% h{round(s['h'])}% at x{round(s['x'])} y{round(s['y'])}" if "w" in s else f"scale {round(s['scale'] * 100)}% at x{round(s['x'])} y{round(s['y'])}"
    by_kind = lambda segs: {k: {"clips": len(v), "coveragePct": round(union(v) / dur * 100, 1), "medianSec": pct([s["dur"] for s in v], 50)}
                            for k, v in sorted(((k, [s for s in segs if s.get("kind") == k]) for k in {s.get("kind") for s in segs if s.get("kind")}), key=lambda kv: -len(kv[1]))}
    # dialogue = audio lane that reuses the main video's source files (a detached A-roll track)
    srcs = {s["name"] for s in main}
    cand = [a for a in auds if a and sum(s["name"] in srcs for s in a) / len(a) > 0.5]
    dialog = auds[0] if tl["tool"] == "fcpxml" and auds else max(cand, key=len, default=None)
    if any(s.get("kind") == "dialog" for a in auds for s in a):
        dialog = max(auds, key=lambda a: sum(s.get("kind") == "dialog" for s in a))
        rest = [s for a in auds for s in a if s.get("kind") != "dialog"]
        music = [[s for s in rest if "music" in (s.get("kind") or "").lower() or s["dur"] >= 20]]
        music = [m for m in music if m]
        sfx_segs = [s for s in rest if s not in music[0]] if music else rest
    else:
        music = [a for a in auds if a is not dialog and (statistics.median([s["dur"] for s in a]) >= 20 or union(a) > dur * 0.5)]
        sfx_segs = [s for a in auds if a is not dialog and a not in music for s in a]
    tr = tl["transitions"]
    return {
        "tool": tl["tool"], "duration": dur, "fps": tl["fps"], "resolution": f"{tl['width']}x{tl['height']}",
        "aspect": "9:16" if (tl["height"] or 0) > (tl["width"] or 1) * 1.4 else "16:9" if tl["width"] and tl["width"] > tl["height"] * 1.4 else "other",
        "tracks": {"video": len(vids), "audio": len(auds), "syncedSources": [l[0]["name"] for l in syn]},
        "mainTrack": {"clips": len(main), "cutsPerMin": round(max(len(main) - 1, 0) / dur * 60, 1),
                      "shotSec": {"median": pct(shots, 50), "p10": pct(shots, 10), "p90": pct(shots, 90), "max": max(shots, default=None)},
                      "scales": dict(Counter(f"{round(s['scale'] * 100)}%" for s in main).most_common(6))},
        "visualChanges": {"perMin": round(len(bounds) / dur * 60, 1), "medianGapSec": pct(changes, 50), "maxGapSec": max(changes, default=None)},
        "overlays": {
            "note": "full-frame overlays can be B-roll OR rendered full-screen graphics - classify from names/frames",
            "fullFrameClips": len(full), "fullFrameCoveragePct": round(union(full) / dur * 100, 1),
            "fullFrameClipSec": {"median": pct([s["dur"] for s in full], 50), "p90": pct([s["dur"] for s in full], 90)},
            "fullFrameMuted": sum(1 for s in full if not s["volume"]),
            "fullFrameNames": [s["name"] for s in full][:25],
            "fullFrameByBin": by_kind(full),
            "pipClips": len(pip), "pipCoveragePct": round(union(pip) / dur * 100, 1),
            "pipByBin": by_kind(pip),
            "pipPositions": dict(Counter(geo(s) for s in pip).most_common(10)),
        },
        "jlCuts": jl(main, dialog, tl["fps"]),
        "audio": {
            "dialogVolumeDb": db(statistics.median([s["volume"] for s in dialog])) if dialog else None,
            "musicTracks": len(music), "musicVolumeDb": [db(statistics.median([s["volume"] for s in a])) for a in music],
            "sfxCount": len(sfx_segs), "sfxPerMin": round(len(sfx_segs) / dur * 60, 1),
            "sfxNames": dict(Counter(s["name"] for s in sfx_segs).most_common(12)),
            "sfxByBin": dict(Counter(s.get("kind") for s in sfx_segs if s.get("kind")).most_common(6)),
            "sfxVolumeDb": db(statistics.median([s["volume"] for s in sfx_segs])) if sfx_segs else None,
        },
        "captions": text_stats(caps, dur, dedupe=True),
        "text": text_stats(texts, dur),
        "transitions": {"count": len(tr), "names": dict(Counter(t["name"] for t in tr).most_common(8)),
                        "medianSec": pct([t["dur"] for t in tr], 50)},
        "effects": dict(Counter(tl["effects"]).most_common(15)),
        "keyframes": dict(tl["keyframes"]),
        **({"palmier": {
            "timeline": tl["timelineName"], "allTimelines": tl["timelines"], "markers": tl["markers"][:30],
            "framing": {k: dict(v.most_common(8)) for k, v in sorted(tl["framing"].items(), key=lambda kv: -sum(kv[1].values()))[:4]},
            "moveRampFrames": {"median": pct(tl["rampFrames"], 50), "p10": pct(tl["rampFrames"], 10), "p90": pct(tl["rampFrames"], 90)},
            "colorParamsMedian": {k: pct([v for v in vs if isinstance(v, (int, float))], 50) for k, vs in tl["colorParams"].items()},
            "speed": dict(tl["speed"]),
        }} if tl["tool"] == "palmier" else {}),
    }


def load(p, timeline_name=None):
    p = Path(p).expanduser()
    if p.suffix == ".palmier" or (p / "project.json").exists():
        return palmier(p, timeline_name)
    if p.is_dir() and (p / "Info.fcpxml").exists() or p.suffix in (".fcpxml", ".fcpxmld"):
        return fcpxml(p)
    if p.is_dir() or p.suffix == ".json":
        return capcut(p)
    if p.suffix == ".prproj":
        sys.exit("Premiere .prproj can't be read directly. In Premiere: File > Export > Final Cut Pro XML, then pass the .xml")
    if p.suffix == ".drp":
        sys.exit("Resolve .drp can't be read directly. Use the davinci-resolve MCP, or File > Export > Timeline > FCPXML")
    root = ET.parse(p).getroot()
    return xmeml(p) if root.tag == "xmeml" else fcpxml(p)


def dialogue(tl, out):
    """Concatenate the kept dialogue spans into one audio file, so measure.py can check pauses and fillers."""
    segs = sorted([s for lane in tl["audio"] for s in lane if s.get("kind") == "dialog" and s.get("src")], key=lambda s: s["start"])
    if not segs:
        return print("no linked dialogue found")
    srcs = Counter(s["src"] for s in segs)
    src = next((x for x in srcs if Path(x).stem.lower().startswith("mic")), srcs.most_common(1)[0][0])
    segs = [s for s in segs if s["src"] == src]
    fc = "".join(f"[0:a]atrim=start={s['trim']}:duration={s['dur']},asetpts=PTS-STARTPTS[a{i}];" for i, s in enumerate(segs))
    fc += "".join(f"[a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1[o]"
    import subprocess
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", fc, "-map", "[o]", "-ac", "1", "-b:a", "64k", str(out)], check=True)
    print(f"dialogue ({len(segs)} spans from {Path(src).name}) -> {out}  (next: measure.py {out} --out <dir>)")


def main():
    a = sys.argv[1:]
    if not a or "--out" not in a:
        sys.exit(__doc__)
    out = Path(a[a.index("--out") + 1]).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    tl = load(a[0], a[a.index("--timeline") + 1] if "--timeline" in a else None)
    s = summarize(tl)
    tl["keyframes"] = dict(tl["keyframes"])
    tl["framing"] = {k: dict(v) for k, v in tl.get("framing", {}).items()}
    for k in ("speed",):
        if k in tl:
            tl[k] = dict(tl[k])
    (out / "nle.json").write_text(json.dumps({"summary": s, "timeline": tl}, indent=2))
    m, o, j = s["mainTrack"], s["overlays"], s["jlCuts"]
    print(f"{s['tool']} {s['resolution']} {s['duration']}s | main track {m['clips']} clips, {m['cutsPerMin']} cuts/min, median shot {m['shotSec']['median']}s")
    print(f"visual change every {s['visualChanges']['medianGapSec']}s (max gap {s['visualChanges']['maxGapSec']}s) | full-frame overlays {o['fullFrameCoveragePct']}% | PIP {o['pipCoveragePct']}%")
    print(f"J/L: {j if not j.get('detectable') else str(j['jCuts']) + ' J, ' + str(j['lCuts']) + ' L of ' + str(j['videoCuts'])} | captions {s['captions']['count']} | text {s['text']['count']} | SFX {s['audio']['sfxCount']} | transitions {s['transitions']['count']}")
    print(f"-> {out}/nle.json")
    if "--dialogue" in a:
        dialogue(tl, out / "dialogue.mp3")


if __name__ == "__main__":
    main()
