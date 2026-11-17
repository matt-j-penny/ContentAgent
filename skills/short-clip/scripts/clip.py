#!/usr/bin/env python3
"""Create a vertical clip from a local source video."""
import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source');p.add_argument('--out',required=True);p.add_argument('--start',type=float,required=True);p.add_argument('--duration',type=float,required=True)
    p.add_argument('--focus-x',type=float,default=0.5,help='horizontal focus from 0 (left) to 1 (right)')
    p.add_argument('--width',type=int,default=1080);p.add_argument('--height',type=int,default=1920)
    a=p.parse_args()
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):p.error('ffmpeg and ffprobe are required')
    src=Path(a.source).expanduser().resolve();out=Path(a.out).expanduser().resolve()
    if not src.is_file():p.error('Source file does not exist')
    if out.exists():p.error('Output already exists; choose a new file')
    if not all(math.isfinite(x) for x in (a.start,a.duration,a.focus_x)) or a.start<0 or a.duration<=0 or not 0<=a.focus_x<=1:
        p.error('Start must be non-negative, duration positive, and focus-x between 0 and 1')
    if min(a.width,a.height)<16 or a.width%2 or a.height%2 or a.width>=a.height:p.error('Use even portrait output dimensions of at least 16 pixels')
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type','-of','json',str(src)]))
    if not any(s.get('codec_type')=='video' for s in info.get('streams',[])):p.error('Source needs a video stream')
    duration=float(info['format']['duration'])
    if a.start+a.duration>duration+0.001:p.error('Clip exceeds source duration')
    ratio=f'{a.width}/{a.height}'
    vf=(f"crop=w='trunc(min(iw,ih*{ratio})/2)*2':h='trunc(min(ih,iw/({ratio}))/2)*2':"
        f"x='max(0,min(iw-ow,iw*{a.focus_x}-ow/2))':y='(ih-oh)/2',scale={a.width}:{a.height}")
    out.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(['ffmpeg','-nostdin','-v','error','-n','-ss',str(a.start),'-i',str(src),'-t',str(a.duration),'-map','0:v:0','-map','0:a:0?','-vf',vf,'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',str(out)],check=True)
    print(f'Vertical clip: {out}')


if __name__=='__main__':
    try:main()
    except (OSError,ValueError,subprocess.CalledProcessError,json.JSONDecodeError) as e:sys.exit(f'Clip creation failed: {e}')
