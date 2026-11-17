#!/usr/bin/env python3
"""Exercise the mixer against generated media without touching user files."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

script = Path(__file__).resolve().parents[1] / 'scripts' / 'mix.py'
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    def ff(*args):
        subprocess.run(['ffmpeg','-loglevel','error','-y',*args],check=True)
    ff('-f','lavfi','-i','testsrc=size=160x120:rate=10','-f','lavfi','-i','sine=frequency=440:sample_rate=44100','-t','1','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(root/'video.mp4'))
    ff('-f','lavfi','-i','sine=frequency=220:sample_rate=44100','-t','0.4',str(root/'music.wav'))
    ff('-f','lavfi','-i','sine=frequency=880:sample_rate=44100','-t','0.1',str(root/'sfx.wav'))
    (root/'mix.json').write_text(json.dumps({'video':'video.mp4','music':{'file':'music.wav'},'sfx':[{'file':'sfx.wav','at':0.3}]}))
    digest=hashlib.sha256((root/'video.mp4').read_bytes()).digest()
    subprocess.run(['python3',str(script),str(root/'mix.json'),'--out',str(root/'out.mp4')],check=True,capture_output=True)
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(root/'out.mp4')]))
    assert {x['codec_type'] for x in info['streams']} >= {'video','audio'}
    assert abs(float(info['format']['duration'])-1)<0.15
    assert hashlib.sha256((root/'video.mp4').read_bytes()).digest()==digest
    assert subprocess.run(['python3',str(script),str(root/'mix.json'),'--out',str(root/'out.mp4')],capture_output=True).returncode != 0
    assert subprocess.run(['python3',str(script),str(root/'mix.json'),'--out',str(root/'video.mp4')],capture_output=True).returncode != 0
print('Synthetic music/SFX mix, duration and source/overwrite protection passed')
