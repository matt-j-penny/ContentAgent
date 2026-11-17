#!/usr/bin/env python3
"""Verify no-face detection and output protection with generated media."""
import importlib.util,json,subprocess,sys,tempfile
from pathlib import Path
if importlib.util.find_spec('cv2') is None:
 print('SKIP: OpenCV is not installed');sys.exit(0)
script=Path(__file__).resolve().parents[1]/'scripts'/'detect.py'
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp);src=d/'blue.mp4';out=d/'track.json'
 subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=blue:size=320x240:rate=10','-t','1','-c:v','libx264','-pix_fmt','yuv420p',str(src)],check=True)
 cmd=[sys.executable,str(script),str(src),'--start','0','--end','1','--interval','0.5','--out',str(out)]
 subprocess.run(cmd,check=True,capture_output=True)
 data=json.loads(out.read_text());assert data['detected']==0 and data['samples'] and all(x['face'] is None for x in data['samples'])
 assert subprocess.run(cmd,capture_output=True).returncode!=0
print('No-face tracking and overwrite protection passed')
