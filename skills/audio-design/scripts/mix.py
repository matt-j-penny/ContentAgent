#!/usr/bin/env python3
"""Mix supplied music and timed sound effects under a video's existing audio."""
import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path


def path_for(value, root):
    p = Path(value).expanduser()
    return (root / p).resolve() if not p.is_absolute() else p.resolve()


def finite(value, name, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not minimum <= value <= maximum:
        raise ValueError(f'{name} must be a finite number between {minimum} and {maximum}')
    return value


def run(manifest_path, output):
    manifest_path = Path(manifest_path).resolve()
    m = json.loads(manifest_path.read_text())
    root = manifest_path.parent
    video = path_for(m['video'], root)
    output = Path(output).expanduser().resolve()
    if not video.is_file():
        raise ValueError(f'Video not found: {video}')
    if output.exists():
        raise ValueError(f'Output already exists: {output}')
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise ValueError('ffmpeg and ffprobe are required')
    info = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(video)]))
    streams = info.get('streams', [])
    if not any(s.get('codec_type') == 'video' for s in streams) or not any(s.get('codec_type') == 'audio' for s in streams):
        raise ValueError('Input needs a video stream and an audio stream')
    events = m.get('sfx', [])
    if not isinstance(events, list):
        raise ValueError('sfx must be a list')
    music = m.get('music')
    if music is None and not events:
        raise ValueError('Provide music or at least one sound effect')
    args = ['ffmpeg','-nostdin','-loglevel','error','-n','-i',str(video)]
    filters = []
    mix_inputs = []
    next_index = 1
    if music:
        track = path_for(music['file'], root)
        if not track.is_file():
            raise ValueError(f'Music not found: {track}')
        gain = finite(music.get('gain',0.15),'music gain',0,2)
        args += ['-stream_loop','-1','-i',str(track)]
        filters.extend(['[0:a:0]asplit=2[voice][sidechain]',f'[{next_index}:a:0]volume={gain}[music]', '[music][sidechain]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=500[ducked]'])
        mix_inputs = ['[voice]','[ducked]']
        next_index += 1
    else:
        filters.append('[0:a:0]anull[voice]')
        mix_inputs = ['[voice]']
    for i,event in enumerate(events):
        if not isinstance(event,dict):
            raise ValueError('Each sound effect must be an object')
        sound = path_for(event['file'], root)
        if not sound.is_file():
            raise ValueError(f'Sound effect not found: {sound}')
        at = finite(event.get('at',0),'sound effect start',0,86400)
        gain = finite(event.get('gain',0.5),'sound effect gain',0,2)
        args += ['-i',str(sound)]
        delay = round(at*1000)
        filters.append(f'[{next_index}:a:0]volume={gain},adelay={delay}:all=1[sfx{i}]')
        mix_inputs.append(f'[sfx{i}]')
        next_index += 1
    filters.append(''.join(mix_inputs)+f'amix=inputs={len(mix_inputs)}:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[aout]')
    args += ['-filter_complex',';'.join(filters),'-map','0:v:0','-map','[aout]','-map_metadata','0','-c:v','copy','-c:a','aac','-b:a','192k','-shortest',str(output)]
    output.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(args,check=True)
    print(f'Mixed audio: {output}')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',help='JSON with video, optional music and timed sfx')
    parser.add_argument('--out',required=True,help='new output video path')
    args=parser.parse_args()
    try:
        run(args.manifest,args.out)
    except (KeyError, ValueError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as e:
        sys.exit(f'Audio mix failed: {e}')
