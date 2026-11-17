#!/usr/bin/env python3
"""Render an original Blender object turntable to a new output folder."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    source=p.add_mutually_exclusive_group(required=True)
    source.add_argument('--model',help='local GLB, glTF or OBJ file')
    source.add_argument('--primitive',choices=['cube'],help='demo primitive')
    p.add_argument('--out',required=True,help='new output directory')
    p.add_argument('--blender',default='blender')
    p.add_argument('--frames',type=int,default=72)
    p.add_argument('--fps',type=int,default=24)
    p.add_argument('--width',type=int,default=1280)
    p.add_argument('--height',type=int,default=720)
    a=p.parse_args()
    if not shutil.which(a.blender) or not shutil.which('ffmpeg'):
        p.error('Blender and ffmpeg must be installed and on PATH, or pass --blender')
    if not 2 <= a.frames <= 3600 or not 1 <= a.fps <= 120 or min(a.width,a.height)<16 or a.width%2 or a.height%2:
        p.error('Use 2–3600 frames, 1–120 fps and even dimensions of at least 16 pixels')
    model=Path(a.model).expanduser().resolve() if a.model else None
    if model and (not model.is_file() or model.suffix.lower() not in ('.glb','.gltf','.obj')):
        p.error('Provide an existing GLB, glTF or OBJ model')
    out=Path(a.out).expanduser().resolve()
    if out.exists():
        p.error('Output directory already exists; choose a new one')
    out.mkdir(parents=True)
    scene=Path(__file__).resolve().parent/'scene.py'
    cmd=[a.blender,'--background','--factory-startup','--python-exit-code','1','--python',str(scene),'--','--out',str(out),'--frames',str(a.frames),'--fps',str(a.fps),'--width',str(a.width),'--height',str(a.height)]
    cmd+=['--model',str(model)] if model else ['--primitive',a.primitive]
    subprocess.run(cmd,check=True)
    subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-n','-framerate',str(a.fps),'-i',str(out/'frames'/'frame_%04d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(out/'turntable.mp4')],check=True)
    print(f'Rendered video: {out / "turntable.mp4"}\nEditable Blender project: {out / "scene.blend"}')


if __name__=='__main__':
    try: main()
    except (OSError,subprocess.CalledProcessError) as e: sys.exit(f'3D rendering failed: {e}')
