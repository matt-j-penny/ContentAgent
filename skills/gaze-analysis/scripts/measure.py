#!/usr/bin/env python3
"""Measure head yaw against a user-confirmed camera-facing reference."""
import argparse,json,math,statistics,sys
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('video');p.add_argument('--model',required=True,help='MediaPipe face_landmarker.task path')
    p.add_argument('--camera-start',type=float,required=True);p.add_argument('--camera-end',type=float,required=True)
    p.add_argument('--screen-start',type=float);p.add_argument('--screen-end',type=float)
    p.add_argument('--fps',type=float,default=2);p.add_argument('--out',required=True);a=p.parse_args()
    if not math.isfinite(a.fps) or not 0.1<=a.fps<=10:p.error('fps must be between 0.1 and 10')
    if (a.screen_start is None)!=(a.screen_end is None):p.error('Specify both screen reference times or neither')
    out=Path(a.out).expanduser().resolve();video=Path(a.video).expanduser().resolve();model=Path(a.model).expanduser().resolve()
    if out.exists():p.error('Output already exists')
    if not video.is_file() or not model.is_file():p.error('Video and MediaPipe model must exist')
    try:
        import cv2,mediapipe as mp
        from mediapipe.tasks.python import vision,BaseOptions
    except ImportError:p.error('Install MediaPipe and OpenCV in the selected Python environment')
    cap=cv2.VideoCapture(str(video))
    if not cap.isOpened():p.error('Could not open the video')
    fps=cap.get(cv2.CAP_PROP_FPS);frames=cap.get(cv2.CAP_PROP_FRAME_COUNT)
    if fps<=0 or frames<=0:p.error('Video duration is unavailable')
    duration=frames/fps
    def valid_range(start,end):return all(math.isfinite(v) for v in (start,end)) and 0<=start<end<=duration+0.01
    if not valid_range(a.camera_start,a.camera_end):p.error('Camera reference range must be inside the video')
    if a.screen_start is not None and not valid_range(a.screen_start,a.screen_end):p.error('Screen reference range must be inside the video')
    if duration*a.fps>20000:p.error('Too many samples; reduce the sampling rate or use a shorter video')
    detector=vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=str(model)),output_facial_transformation_matrixes=True,num_faces=1))
    samples=[]
    for i in range(math.ceil(duration*a.fps)):
        t=i/a.fps;cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,frame=cap.read();yaw=None
        if ok:
            result=detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)))
            if result.facial_transformation_matrixes:
                matrix=result.facial_transformation_matrixes[0];yaw=round(math.degrees(math.atan2(matrix[0,2],matrix[2,2])),3)
        samples.append({'t':round(t,3),'yaw':yaw})
    cap.release();detector.close()
    def median(start,end):
        values=[s['yaw'] for s in samples if start<=s['t']<end and s['yaw'] is not None]
        if not values:raise ValueError('No faces detected in a reference range')
        return round(statistics.median(values),3)
    camera=median(a.camera_start,a.camera_end);screen=median(a.screen_start,a.screen_end) if a.screen_start is not None else None
    result={'source':str(video),'fps':a.fps,'camera_yaw':camera,'screen_yaw':screen,'separation_degrees':round(abs(screen-camera),3) if screen is not None else None,'samples':samples,'note':'Head orientation is not eye gaze. Layout decisions require corroborating evidence.'}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(f"Measured head orientation in {sum(s['yaw'] is not None for s in samples)} of {len(samples)} samples: {out}")

if __name__=='__main__':
    try:main()
    except (OSError,ValueError) as e:sys.exit(f'Head-pose analysis failed: {e}')
