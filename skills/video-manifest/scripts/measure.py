#!/usr/bin/env python3
"""Measure the editing of a finished video (or an audio-only dialogue export): cuts, pace, silence kept, loudness, fillers, frames.

  measure.py <video-file-or-url> --out <dir> [--scene 0.25] [--every SEC] [--no-transcribe]

Writes <dir>/stats.json, <dir>/frames/*.jpg and (with Deepgram) <dir>/transcript.json + transcript.txt.
Needs ffmpeg/ffprobe, yt-dlp for URLs, DEEPGRAM_API_KEY (env or ~/.claude/settings.json) for transcription.
"""
import json, os, re, subprocess, sys, urllib.request
from pathlib import Path

FILLERS = {"uh", "um", "mhm", "mm", "hmm", "uh-huh", "er", "ah"}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def pct(xs, p):
    if not xs:
        return None
    xs = sorted(xs)
    return round(xs[min(len(xs) - 1, int(round(p / 100 * (len(xs) - 1))))], 3)


def fetch(src, out):
    if not re.match(r"https?://", src):
        return Path(src).expanduser()
    dest = out / "source.mp4"
    if not dest.exists():
        r = run(["yt-dlp", "-f", "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b", "--merge-output-format", "mp4", "-o", str(dest), src])
        if r.returncode:
            sys.exit(r.stderr[-2000:])
    return dest


def probe(f):
    r = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(f)]).stdout)
    dur = round(float(r["format"]["duration"]), 2)
    if not r.get("streams"):
        return {"duration": dur, "width": None, "height": None, "fps": None}
    s = r["streams"][0]
    n, d = map(int, s["r_frame_rate"].split("/"))
    return {"duration": dur, "width": s["width"], "height": s["height"], "fps": round(n / d, 3)}


def cuts(f, scene):
    # ponytail: scene-change threshold; same-framing jump cuts can slip under it. Lower --scene if cuts look undercounted.
    err = run(["ffmpeg", "-hide_banner", "-i", str(f), "-an", "-vf", f"scale=320:-2,select='gt(scene,{scene})',showinfo", "-f", "null", "-"]).stderr
    return [float(x) for x in re.findall(r"pts_time:([\d.]+)", err)]


def audio(f):
    err = run(["ffmpeg", "-hide_banner", "-i", str(f), "-vn", "-af", "silencedetect=noise=-35dB:d=0.15,ebur128=peak=true", "-f", "null", "-"]).stderr
    sil = [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", err)]
    summ = err[err.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", summ)
    p = re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ)
    return sil, (float(i.group(1)) if i else None), (float(p.group(1)) if p else None)


def frames(f, out, every):
    d = out / "frames"
    d.mkdir(exist_ok=True)
    run(["ffmpeg", "-hide_banner", "-y", "-i", str(f), "-vf", f"fps=1/{every},scale=480:-2", "-q:v", "4", str(d / "%04d.jpg")])
    return sorted(d.glob("*.jpg"))


def deepgram_key():
    k = os.environ.get("DEEPGRAM_API_KEY")
    if k:
        return k
    s = json.loads((Path.home() / ".claude/settings.json").read_text())
    return (s.get("env") or {}).get("DEEPGRAM_API_KEY") or s.get("DEEPGRAM_API_KEY")


def transcribe(f, out):
    mp3 = out / "audio.mp3"
    run(["ffmpeg", "-hide_banner", "-y", "-i", str(f), "-vn", "-ac", "1", "-b:a", "64k", str(mp3)])
    q = "model=nova-2&smart_format=true&punctuate=true&paragraphs=true&utterances=true&filler_words=true"
    req = urllib.request.Request(f"https://api.deepgram.com/v1/listen?{q}", data=mp3.read_bytes(),
                                 headers={"Authorization": f"Token {deepgram_key()}", "Content-Type": "audio/mpeg"})
    res = json.loads(urllib.request.urlopen(req, timeout=600).read())
    mp3.unlink()
    (out / "transcript.json").write_text(json.dumps(res))
    alt = res["results"]["channels"][0]["alternatives"][0]
    (out / "transcript.txt").write_text(alt.get("paragraphs", {}).get("transcript") or alt["transcript"])
    return alt["words"]


def speech_stats(words, duration):
    if not words:
        return {}
    gaps = [max(0, round((b["start"] - a["end"]) * 1000)) for a, b in zip(words, words[1:])]
    fill = [w for w in words if w["word"].lower().strip(".,") in FILLERS]
    spoken = words[-1]["end"] - words[0]["start"]
    return {
        "words": len(words),
        "wpm": round(len(words) / spoken * 60) if spoken else None,
        "fillers": len(fill),
        "fillersPerMin": round(len(fill) / duration * 60, 2),
        "fillerExamples": [f"{w['word']}@{w['start']:.1f}s" for w in fill[:10]],
        "gapMs": {"p50": pct(gaps, 50), "p90": pct(gaps, 90), "max": max(gaps) if gaps else None},
        "longPauses": [f"{a['end']:.1f}s ({(b['start'] - a['end']):.2f}s)" for a, b in zip(words, words[1:]) if b["start"] - a["end"] > 0.6][:15],
    }


def main():
    a = sys.argv[1:]
    if not a or "--out" not in a:
        sys.exit(__doc__)
    opt = lambda f, d=None: a[a.index(f) + 1] if f in a else d
    out = Path(opt("--out")).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    src = fetch(a[0], out)
    info = probe(src)
    dur = info["duration"]
    video = info["width"] is not None
    cut_t = cuts(src, float(opt("--scene", 0.25))) if video else []
    bounds = [0.0] + cut_t + [dur]
    shots = [round(b - a_, 3) for a_, b in zip(bounds, bounds[1:]) if b - a_ > 0.04]
    sil, lufs, peak = audio(src)
    every = float(opt("--every", max(2, min(15, round(dur / 40)))))
    fr = frames(src, out, every) if video else []
    w, h = info["width"] or 16, info["height"] or 9
    aspect = None if not video else "9:16" if h > w * 1.4 else "1:1" if abs(h - w) < w * 0.1 else "4:5" if h > w else "16:9"
    stats = {
        "source": a[0], **info, "aspect": aspect,
        "cuts": {"count": len(cut_t), "perMin": round(len(cut_t) / dur * 60, 1),
                 "shotSec": {"median": pct(shots, 50), "p10": pct(shots, 10), "p90": pct(shots, 90), "max": max(shots) if shots else None},
                 "times": [round(t, 2) for t in cut_t]},
        "audio": {"integratedLufs": lufs, "truePeakDb": peak,
                  "silencesOver150ms": len(sil), "silenceSec": {"median": pct(sil, 50), "p90": pct(sil, 90), "max": max(sil) if sil else None}},
        "frames": {"every": every, "count": len(fr), "dir": "frames"},
    }
    if "--no-transcribe" not in a:
        stats["speech"] = speech_stats(transcribe(src, out), dur)
    (out / "stats.json").write_text(json.dumps(stats, indent=2))
    c, s = stats["cuts"], stats.get("speech", {})
    print(f"{dur}s {aspect} {info['fps']}fps | {c['count']} cuts, {c['perMin']}/min, median shot {c['shotSec']['median']}s, longest {c['shotSec']['max']}s")
    print(f"loudness {lufs} LUFS, peak {peak} dB | {len(fr)} frames every {every}s")
    if s:
        print(f"{s['wpm']} wpm, {s['fillers']} fillers, word gap p50 {s['gapMs']['p50']}ms p90 {s['gapMs']['p90']}ms")
    print(f"-> {out}/stats.json")


if __name__ == "__main__":
    main()
