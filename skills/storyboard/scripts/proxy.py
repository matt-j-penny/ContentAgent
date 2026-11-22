"""Low-res footage the storyboard cuts its stills from, rebuilt from a Palmier timeline without exporting it.

usage: python3 proxy.py <get_timeline.json> <sources.json> <board dir>
sources.json = {mediaRef: file path} for every clip on the Webcam and Screen tracks.
Writes media/cam.mp4 and media/screen.mp4, both on the timeline clock.
"""
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

W, H = 960, 540
H264 = ["-c:v", "h264_videotoolbox", "-g", "15", "-pix_fmt", "yuv420p"]

def track(tl, name):
    return sorted(next((t["clips"] for t in tl["tracks"] if t.get("name") == name), []), key=lambda c: c["frames"][0])

def small(src, dst, fps):
    if not dst.exists():
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-hwaccel", "videotoolbox", "-i", src, "-an", "-vf",
                        f"fps={fps}:start_time=0:round=up,scale={W}:{H}", *H264, "-b:v", "3M", str(dst)], check=True)

def cam_look(c):
    # ponytail: rough gains stand in for Palmier's grade; judge colour in Palmier, not on the board
    g = c.get("color", {})
    ev, temp = 2 ** (g.get("exposure", 0) / 2.2), g.get("temperature", 0) / 1000
    r, b = ev * (1 + .1 * temp), ev * (1 - .1 * temp)
    return f"colorchannelmixer=rr={r:.3f}:gg={ev:.3f}:bb={b:.3f}"

def screen_look(c):
    e, t = c.get("crop", {}), c.get("transform", {})
    top = e.get("top", 0); w, h = t.get("width", 1), t.get("height", 1)
    x, y = t.get("centerX", .5) - w / 2, t.get("centerY", .5) - h / 2
    vh = round(H * h * (1 - top) / 2) * 2; vw = round(W * w / 2) * 2
    return (f"crop=iw:ih*{1 - top:.5f}:0:ih*{top:.5f},scale={vw}:{vh},"
            f"pad={W}:{H}:{max(0, round(x * W))}:{max(0, round((y + top * h) * H))}:color=0xFAFAFA")

def picture(tl, name, src, low, look, out):
    fps, size = tl["fps"], W * H * 3 // 2
    enc = subprocess.Popen(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "yuv420p",
                            "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", *H264, "-b:v", "1100k", "-movflags", "+faststart", str(out)],
                           stdin=subprocess.PIPE)
    blank, at = b"\xf8" * (W * H) + b"\x80" * (W * H // 2), 0
    for c in track(tl, name):
        a, b = c["frames"]
        enc.stdin.write(blank * (a - at))
        raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{c.get('trimStartFrame', 0) / fps:.5f}", "-i", str(low[c["mediaRef"]]),
                              "-vf", look(c) + ",format=yuv420p", "-frames:v", str(b - a), "-f", "rawvideo", "-"],
                             capture_output=True, check=True).stdout
        have = len(raw) // size
        enc.stdin.write(raw + (raw[-size:] if have else blank) * (b - a - have))
        at = b
    enc.stdin.close()
    assert enc.wait() == 0, f"encoding {out} failed"

if __name__ == "__main__":
    tl, src = json.loads(Path(sys.argv[1]).read_text()), json.loads(Path(sys.argv[2]).read_text())
    media = Path(sys.argv[3]) / "media"; tmp = media / "tmp"; tmp.mkdir(parents=True, exist_ok=True)
    low = {r: tmp / f"{r}.mp4" for n in ("Webcam", "Screen") for r in {c["mediaRef"] for c in track(tl, n)}}
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(lambda r: small(src[r], low[r], tl["fps"]), low))
    with ThreadPoolExecutor(2) as ex:
        jobs = [ex.submit(picture, tl, "Webcam", src, low, cam_look, media / "cam.mp4"),
                ex.submit(picture, tl, "Screen", src, low, screen_look, media / "screen.mp4")]
        for j in jobs: j.result()
    for f in low.values(): f.unlink()
    tmp.rmdir()
    print("preview media ready", media)
