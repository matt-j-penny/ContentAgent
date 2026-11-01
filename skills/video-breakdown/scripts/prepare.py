#!/usr/bin/env python3
"""Mechanical half of a short-form video breakdown: download, probe, Deepgram transcript,
cuts, flashes and frames. Writes everything to one folder plus prepared.json for the agent.

  prepare.py <url-or-file> [--work contentagent-work/video-analysis] [--scene 0.25]
  prepare.py frames <folder> <t> [<t> ...]                         # extra frames at given seconds
  prepare.py crop <folder> <t> <w:h:x:y> <name>                    # upscaled crop of small text
"""
import json, math, os, re, subprocess, sys, urllib.request
from pathlib import Path

FLASH_JUMP = 40       # YAVG change over one or two frames that counts as a flash or dip
FLASH_RETURN_S = 0.5  # flash must come back within this long
FADE_TOTAL = 60       # total YAVG change for a fade
FADE_MAX_S = 1.5
PAUSE_S = 0.15
LOW_CONF = 0.85


def run(*cmd, check=True):
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def video_id(src):
    m = re.search(r"/(?:reel|reels|p|shorts|video)/([A-Za-z0-9_-]+)", src)
    if m:
        return m.group(1)
    if src.startswith("http"):
        return re.sub(r"[^A-Za-z0-9_-]", "", src.rstrip("/").split("/")[-1].split("?")[0]) or "video"
    return Path(src).stem


def download(src, d):
    if not src.startswith("http"):
        run("ffmpeg", "-y", "-i", src, "-c", "copy", str(d / "source.mp4"))
        return
    r = run("yt-dlp", "-f", "bv*+ba/b", "-S", "res:1080,vcodec:h264", "--merge-output-format", "mp4", "--write-info-json",
            "-o", str(d / "source.%(ext)s"), src, check=False)
    if r.returncode or not (d / "source.mp4").exists():
        sys.exit(f"DOWNLOAD_FAILED: yt-dlp could not get the video.\n{r.stderr[-800:]}\n"
                 f"Get a direct video URL another way, then run: curl -L -o {d}/source.mp4 '<url>' "
                 f"and rerun this script with {d}/source.mp4")


def probe(d):
    out = json.loads(run("ffprobe", "-v", "error", "-show_entries",
                         "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate",
                         "-of", "json", str(d / "source.mp4")).stdout)
    (d / "probe.json").write_text(json.dumps(out, indent=2))
    v = next(s for s in out["streams"] if s["codec_type"] == "video")
    num, den = map(int, v["r_frame_rate"].split("/"))
    w, h = v["width"], v["height"]
    return {
        "duration_seconds": round(float(out["format"]["duration"]), 2),
        "resolution": f"{w}x{h}",
        "aspect_ratio": "9:16" if abs(w / h - 9 / 16) < 0.02 else "16:9" if abs(w / h - 16 / 9) < 0.02 else f"{w}:{h}",
        "fps": round(num / den, 2),
        "video_codec": v["codec_name"],
        "has_audio": any(s["codec_type"] == "audio" for s in out["streams"]),
    }


def transcribe(d, language):
    run("ffmpeg", "-y", "-i", str(d / "source.mp4"), "-vn", "-ac", "1", "-ar", "16000", str(d / "audio.wav"))
    key = os.environ.get("DEEPGRAM_API_KEY")
    if not key:
        sys.exit("NO_DEEPGRAM_KEY: set DEEPGRAM_API_KEY and rerun.")
    lang = "detect_language=true" if language == "auto" else f"language={language}"
    req = urllib.request.Request(
        "https://api.deepgram.com/v1/listen?model=nova-3&smart_format=true&punctuate=true"
        f"&utterances=true&paragraphs=true&diarize=true&{lang}",
        data=(d / "audio.wav").read_bytes(),
        headers={"Authorization": f"Token {key}", "Content-Type": "audio/wav"})
    raw = json.loads(urllib.request.urlopen(req, timeout=300).read())
    (d / "deepgram-raw.json").write_text(json.dumps(raw, indent=2))
    alt = raw["results"]["channels"][0]["alternatives"][0]
    words = [{k: w.get(k) for k in ("word", "punctuated_word", "start", "end", "confidence", "speaker")}
             for w in alt.get("words", [])]
    silence = run("ffmpeg", "-i", str(d / "audio.wav"), "-af", "silencedetect=noise=-35dB:d=0.12",
                  "-f", "null", "-").stderr
    (d / "silence.txt").write_text(silence)
    return {
        "full_text_raw": alt.get("transcript", ""),
        "words": words,
        "low_confidence_words": [w for w in words if (w["confidence"] or 0) < LOW_CONF],
        "pauses": [{"start": a["end"], "end": b["start"], "length": round(b["start"] - a["end"], 2)}
                   for a, b in zip(words, words[1:]) if b["start"] - a["end"] >= PAUSE_S],
        "silences": [{"start": float(s), "end": float(e)} for s, e in
                     zip(re.findall(r"silence_start: ([\d.]+)", silence), re.findall(r"silence_end: ([\d.]+)", silence))],
    }


def scene_cuts(d, threshold):
    out = run("ffmpeg", "-i", str(d / "source.mp4"), "-vf", f"select='gt(scene,{threshold})',showinfo",
              "-fps_mode", "vfr", "-f", "null", "-").stderr
    cuts = [round(float(t), 3) for t in re.findall(r"pts_time:([\d.]+)", out)]
    (d / "scenes.txt").write_text("\n".join(map(str, cuts)))
    return cuts


def brightness(d):
    run("ffmpeg", "-i", str(d / "source.mp4"), "-vf",
        f"signalstats,metadata=print:key=lavfi.signalstats.YAVG:file={d / 'yavg.txt'}", "-f", "null", "-")
    text = (d / "yavg.txt").read_text()
    times = [float(t) for t in re.findall(r"pts_time:([\d.]+)", text)]
    vals = [float(v) for v in re.findall(r"YAVG=([\d.]+)", text)]
    return list(zip(times, vals))


def transitions(series):
    found, i = [], 2
    while i < len(series):
        t0, base = series[i - 2]
        t, y = series[i]
        if abs(y - base) >= FLASH_JUMP:
            j = i
            while j < len(series) and series[j][0] - t <= FLASH_RETURN_S and abs(series[j][1] - base) >= FLASH_JUMP / 2:
                j += 1
            if j < len(series) and series[j][0] - t <= FLASH_RETURN_S:
                found.append({"type": "white_flash" if y > base else "black_dip",
                              "start": round(t0, 3), "end": round(series[j][0], 3)})
                i = j + 1
                continue
        i += 1
    # fades: a steady one-direction ramp with no single big jump
    i = 0
    while i < len(series) - 1:
        j, sign = i, 0
        while j + 1 < len(series):
            step = series[j + 1][1] - series[j][1]
            s = (step > 0.5) - (step < -0.5)
            if s == 0 or (sign and s != sign) or abs(step) >= FLASH_JUMP:
                break
            sign, j = s, j + 1
        total = series[j][1] - series[i][1]
        if abs(total) >= FADE_TOTAL and series[j][0] - series[i][0] <= FADE_MAX_S:
            found.append({"type": "fade_up" if total > 0 else "fade_down",
                          "start": round(series[i][0], 3), "end": round(series[j][0], 3)})
        i = max(j, i + 1)
    return sorted(found, key=lambda x: x["start"])


def grab(d, t, source):
    name = f"frames/f_{t:05.2f}.jpg"
    run("ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", str(d / "source.mp4"), "-frames:v", "1", "-q:v", "2", str(d / name))
    return {"t": round(t, 2), "file": name, "source": source}


def save_frames(d, new):
    index = d / "frames.json"
    frames = {f["file"]: f for f in (json.loads(index.read_text()) if index.exists() else [])}
    frames.update({f["file"]: f for f in new})
    index.write_text(json.dumps(sorted(frames.values(), key=lambda f: f["t"]), indent=2))
    return sorted(frames.values(), key=lambda f: f["t"])


def extract_frames(d, duration, cuts, trans):
    (d / "frames").mkdir(exist_ok=True)
    fps = 1 if duration <= 180 else 0.5
    step = 1 / fps
    picks = [(t, "1fps") for t in [step / 2 + k * step for k in range(int(duration / step + 0.5))] if t < duration]
    picks += [(min(c + 0.08, duration - 0.05), "scene_change") for c in cuts]
    picks += [((x["start"] + x["end"]) / 2, "transition") for x in trans]
    frames = save_frames(d, [grab(d, t, s) for t, s in picks])
    run("ffmpeg", "-y", "-i", str(d / "source.mp4"), "-vf", f"fps=1,scale=270:-1,tile=6x{math.ceil(duration / 6)}",
        "-frames:v", "1", str(d / "contact_sheet.jpg"))
    return frames


def prepare(src, work, threshold, language):
    d = Path(work) / video_id(src)
    d.mkdir(parents=True, exist_ok=True)
    if not (d / "source.mp4").exists():
        download(src, d)
    meta = probe(d)
    if meta["video_codec"] in ("vp9", "av1"):
        run("ffmpeg", "-y", "-i", str(d / "source.mp4"), "-c:v", "libx264", "-crf", "20", "-c:a", "aac", str(d / "source_h264.mp4"))
        os.replace(d / "source_h264.mp4", d / "source.mp4")
        meta = probe(d)
    info = next(d.glob("source*.info.json"), None)
    if info:
        i = json.loads(info.read_text())
        meta.update({"caption": i.get("description"), "author": i.get("uploader_id") or i.get("uploader"),
                     "views": i.get("view_count"), "likes": i.get("like_count"),
                     "comments": i.get("comment_count"), "upload_date": i.get("upload_date")})
    transcript = transcribe(d, language) if meta["has_audio"] else None
    words = transcript["words"] if transcript else []
    meta["has_speech"] = bool(words)
    if words:
        meta["speech_end_seconds"] = words[-1]["end"]
        span = words[-1]["end"] - words[0]["start"]
        meta["words_per_minute"] = round(len(words) / span * 60) if span else None
    cuts = scene_cuts(d, threshold)
    trans = transitions(brightness(d))
    shots = len(cuts) + 1
    meta.update({"scene_cuts": cuts, "transitions": trans, "shot_count": shots,
                 "avg_shot_length_s": round(meta["duration_seconds"] / shots, 2),
                 "cuts_per_10s": round(len(cuts) / meta["duration_seconds"] * 10, 2)})
    frames = extract_frames(d, meta["duration_seconds"], cuts, trans)
    out = {"source_url": src if src.startswith("http") else None, "folder": str(d), "meta": meta,
           "transcript": transcript, "frames": frames}
    (d / "prepared.json").write_text(json.dumps(out, indent=2))
    print(f"Prepared {d}: {meta['duration_seconds']}s, {len(cuts)} cuts, {len(trans)} transitions, "
          f"{len(words)} words, {len(frames)} frames. Read {d / 'prepared.json'}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "frames":
        d = Path(a[1])
        save_frames(d, [grab(d, float(t), "dense") for t in a[2:]])
        print("\n".join(f"frames/f_{float(t):05.2f}.jpg" for t in a[2:]))
    elif a and a[0] == "crop":
        d, t, box, name = Path(a[1]), float(a[2]), a[3], a[4]
        run("ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", str(d / "source.mp4"), "-frames:v", "1",
            "-vf", f"crop={box},scale=iw*2:ih*2", str(d / f"frames/crop_{name}.jpg"))
        print(f"frames/crop_{name}.jpg")
    elif a:
        opt = lambda k, default: a[a.index(k) + 1] if k in a else default
        prepare(a[0], opt("--work", "contentagent-work/video-analysis"), opt("--scene", "0.25"), opt("--language", "en"))
    else:
        sys.exit(__doc__)
