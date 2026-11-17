#!/usr/bin/env python3
"""Render a vertical image sequence, optionally with narration, to a new MP4."""
import argparse,json,math,shutil,subprocess,sys
from pathlib import Path


def asset(value,root):
    p=Path(value).expanduser()
    return (root/p).resolve() if not p.is_absolute() else p.resolve()


def run(manifest_path,output):
    path=Path(manifest_path).resolve();m=json.loads(path.read_text());root=path.parent
    out=Path(output).expanduser().resolve()
    if out.exists():raise ValueError('Output already exists; choose a new path')
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):raise ValueError('ffmpeg and ffprobe are required')
    width=m.get('width',1080);height=m.get('height',1920);fps=m.get('fps',30)
    if any(isinstance(x,bool) or not isinstance(x,int) for x in (width,height,fps)) or min(width,height)<16 or width%2 or height%2 or width>=height or not 1<=fps<=120:
        raise ValueError('Use even portrait dimensions of at least 16 pixels and 1–120 fps')
    scenes=m.get('scenes')
    if not isinstance(scenes,list) or not 1<=len(scenes)<=30:raise ValueError('Provide 1–30 image scenes')
    cmd=['ffmpeg','-nostdin','-v','error','-n'];filters=[];duration_total=0
    for i,scene in enumerate(scenes):
        duration=scene.get('duration')
        if isinstance(duration,bool) or not isinstance(duration,(int,float)) or not math.isfinite(duration) or not 0<duration<=60:raise ValueError('Each scene duration must be greater than 0 and at most 60 seconds')
        image=asset(scene['image'],root)
        if not image.is_file() or image.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):raise ValueError(f'Image missing or unsupported: {image}')
        cmd+=['-loop','1','-t',str(duration),'-i',str(image)]
        filters.append(f'[{i}:v:0]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1,fps={fps},trim=duration={duration},setpts=PTS-STARTPTS[v{i}]')
        duration_total+=duration
    filters.append(''.join(f'[v{i}]' for i in range(len(scenes)))+f'concat=n={len(scenes)}:v=1:a=0[vout]')
    voice=m.get('narration')
    if voice:
        voice=asset(voice,root)
        if not voice.is_file():raise ValueError(f'Narration not found: {voice}')
        voice_info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type','-of','json',str(voice)]))
        if not any(s.get('codec_type')=='audio' for s in voice_info.get('streams',[])):raise ValueError('Narration needs an audio stream')
        if float(voice_info['format']['duration']) > duration_total+0.05:raise ValueError('Narration is longer than the scene sequence; extend the scenes')
        cmd+=['-i',str(voice)]
        filters.append(f'[{len(scenes)}:a:0]apad,atrim=duration={duration_total},asetpts=PTS-STARTPTS[aout]')
    cmd+=['-filter_complex',';'.join(filters),'-map','[vout]']
    cmd+=['-map','[aout]','-c:a','aac'] if voice else ['-an']
    cmd+=['-t',str(duration_total),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
    out.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(cmd,check=True)
    print(f'Short video: {out}')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest');p.add_argument('--out',required=True);a=p.parse_args()
    try:run(a.manifest,a.out)
    except (KeyError,ValueError,OSError,subprocess.CalledProcessError,json.JSONDecodeError) as e:sys.exit(f'Short render failed: {e}')
