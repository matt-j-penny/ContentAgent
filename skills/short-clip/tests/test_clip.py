#!/usr/bin/env python3
"""Exercise short-clip output and input preservation using generated media."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
script=Path(__file__).resolve().parents[1]/'scripts'/'clip.py'
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp);src=d/'source.mp4';out=d/'short.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc=size=320x180:rate=15','-f','lavfi','-i','sine=frequency=440:sample_rate=44100','-t','2','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(src)],check=True)
 before=hashlib.sha256(src.read_bytes()).digest()
 base=['python3',str(script),str(src),'--start','0.3','--duration','1','--width','180','--height','320','--out',str(out)]
 subprocess.run(base,check=True,capture_output=True)
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]))
 v=next(x for x in info['streams'] if x['codec_type']=='video')
 assert (v['width'],v['height'])==(180,320) and abs(float(info['format']['duration'])-1)<0.15
 assert any(x['codec_type']=='audio' for x in info['streams'])
 assert hashlib.sha256(src.read_bytes()).digest()==before
 assert subprocess.run(base,capture_output=True).returncode!=0
 assert subprocess.run(['python3',str(script),str(src),'--start','1.8','--duration','1','--out',str(d/'bad.mp4')],capture_output=True).returncode!=0
print('Portrait clip, timing, audio and overwrite protection passed')
