#!/usr/bin/env python3
"""Validate programmatic short rendering with generated assets."""
import json,subprocess,tempfile
from pathlib import Path
script=Path(__file__).resolve().parents[1]/'scripts'/'render.py'
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp)
 subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=red:size=160x120:rate=1','-frames:v','1','-update','1',str(d/'image.png')],check=True)
 subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','sine=frequency=440:sample_rate=44100','-t','0.5',str(d/'voice.wav')],check=True)
 m={'width':180,'height':320,'fps':10,'narration':'voice.wav','scenes':[{'image':'image.png','duration':0.5},{'image':'image.png','duration':0.5}]}
 (d/'short.json').write_text(json.dumps(m));cmd=['python3',str(script),str(d/'short.json'),'--out',str(d/'out.mp4')]
 subprocess.run(cmd,check=True,capture_output=True)
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(d/'out.mp4')]))
 v=next(s for s in info['streams'] if s['codec_type']=='video');assert (v['width'],v['height'])==(180,320)
 assert any(s['codec_type']=='audio' for s in info['streams']) and abs(float(info['format']['duration'])-1)<0.15
 assert subprocess.run(cmd,capture_output=True).returncode!=0
 m['scenes']=[{'image':'image.png','duration':0.1}];(d/'short.json').write_text(json.dumps(m))
 assert subprocess.run(['python3',str(script),str(d/'short.json'),'--out',str(d/'invalid.mp4')],capture_output=True).returncode!=0
print('Image short, audio, narration protection and overwrite protection passed')
