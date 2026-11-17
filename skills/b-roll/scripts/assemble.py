#!/usr/bin/env python3
"""Render full-frame B-roll cutaways over a video, preserving original audio."""
import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path


def asset_path(value, root):
    path = Path(value).expanduser()
    return (root / path).resolve() if not path.is_absolute() else path.resolve()


def number(value, name):
    if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value) or value < 0:
        raise ValueError(f'{name} must be a non-negative finite number')
    return float(value)


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height','-of','json',str(path)]))


def run(manifest_path, output_path):
    manifest_path=Path(manifest_path).resolve()
    m=json.loads(manifest_path.read_text())
    root=manifest_path.parent
    source=asset_path(m['video'],root)
    output=Path(output_path).expanduser().resolve()
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise ValueError('ffmpeg and ffprobe are required')
    if not source.is_file():
        raise ValueError(f'Video not found: {source}')
    if output.exists():
        raise ValueError(f'Output already exists: {output}')
    src_info=probe(source)
    stream=next((s for s in src_info.get('streams',[]) if s['codec_type']=='video'),None)
    if stream is None:
        raise ValueError('Input has no video stream')
    width,height=stream['width'],stream['height']
    if width%2 or height%2:
        raise ValueError('Source dimensions must be even for H.264 output')
    length=float(src_info['format']['duration'])
    cuts=m.get('cutaways')
    if not isinstance(cuts,list) or not cuts:
        raise ValueError('cutaways must be a non-empty list')
    cmd=['ffmpeg','-nostdin','-loglevel','error','-n','-i',str(source)]
    filters=[]
    previous_end=0.0
    for i,cut in enumerate(cuts):
        start=number(cut['at'],'at')
        clip_start=number(cut.get('source_start',0),'source_start')
        duration=number(cut['duration'],'duration')
        if not duration or start < previous_end or start+duration > length+0.001:
            raise ValueError('Cutaways must be ordered, non-overlapping and inside the original video')
        asset=asset_path(cut['file'],root)
        if not asset.is_file():
            raise ValueError(f'B-roll not found: {asset}')
        info=probe(asset)
        if not any(s['codec_type']=='video' for s in info.get('streams',[])):
            raise ValueError(f'B-roll has no video stream: {asset}')
        if clip_start+duration > float(info['format']['duration'])+0.001:
            raise ValueError(f'B-roll is too short: {asset}')
        cmd.extend(['-i',str(asset)])
        filters.append(f'[{i+1}:v:0]trim=start={clip_start}:duration={duration},setpts=PTS-STARTPTS+{start}/TB,scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}[cut{i}]')
        base='[0:v:0]' if i==0 else f'[v{i-1}]'
        filters.append(f"{base}[cut{i}]overlay=0:0:eof_action=pass:repeatlast=0:enable='between(t,{start},{start+duration})'[v{i}]")
        previous_end=start+duration
    cmd.extend(['-filter_complex',';'.join(filters),'-map',f'[v{len(cuts)-1}]','-map','0:a?','-map_metadata','0','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','copy',str(output)])
    output.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(cmd,check=True)
    print(f'B-roll edit: {output}')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    try:
        run(args.manifest,args.out)
    except (KeyError,ValueError,OSError,subprocess.CalledProcessError,json.JSONDecodeError) as e:
        sys.exit(f'B-roll assembly failed: {e}')
