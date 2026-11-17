#!/usr/bin/env python3
"""Check cutaway timing and preservation using generated media."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

script=Path(__file__).resolve().parents[1]/'scripts'/'assemble.py'
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    def ff(*args): subprocess.run(['ffmpeg','-v','error','-y',*args],check=True)
    ff('-f','lavfi','-i','color=blue:size=160x120:rate=15','-f','lavfi','-i','sine=frequency=440:sample_rate=44100','-t','2','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(root/'source.mp4'))
    ff('-f','lavfi','-i','color=red:size=160x120:rate=15','-t','1','-c:v','libx264','-pix_fmt','yuv420p',str(root/'clip.mp4'))
    manifest={'video':'source.mp4','cutaways':[{'file':'clip.mp4','at':0.5,'duration':1}]}
    (root/'edit.json').write_text(json.dumps(manifest))
    digest=hashlib.sha256((root/'source.mp4').read_bytes()).digest()
    subprocess.run(['python3',str(script),str(root/'edit.json'),'--out',str(root/'result.mp4')],check=True,capture_output=True)
    def pixel(t):
        return subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(root/'result.mp4'),'-vf','scale=1:1','-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
    assert pixel(0.2)[2] > 200 and pixel(0.8)[0] > 200 and pixel(1.8)[2] > 200
    def audio_hash(name):
        return subprocess.check_output(['ffmpeg','-v','error','-i',str(root/name),'-map','0:a:0','-f','md5','-'])
    assert audio_hash('source.mp4')==audio_hash('result.mp4')
    assert hashlib.sha256((root/'source.mp4').read_bytes()).digest()==digest
    assert subprocess.run(['python3',str(script),str(root/'edit.json'),'--out',str(root/'result.mp4')],capture_output=True).returncode!=0
    manifest['cutaways'][0]['duration']=10;(root/'edit.json').write_text(json.dumps(manifest))
    assert subprocess.run(['python3',str(script),str(root/'edit.json'),'--out',str(root/'invalid.mp4')],capture_output=True).returncode!=0
print('Cutaway timing, audio preservation and overwrite protection passed')
