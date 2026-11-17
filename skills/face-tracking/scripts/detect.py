#!/usr/bin/env python3
"""Sample face positions in a video using the bundled YuNet detector."""
import argparse,json,math,sys
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('video');p.add_argument('--start',type=float,default=0);p.add_argument('--end',type=float,required=True);p.add_argument('--interval',type=float,default=0.5);p.add_argument('--out',required=True);a=p.parse_args()
    if not all(math.isfinite(v) for v in (a.start,a.end,a.interval)) or a.start<0 or a.end<=a.start or a.interval<0.1 or (a.end-a.start)/a.interval>5000:p.error('Use a valid range, interval of at least 0.1 seconds and at most 5000 samples')
    source=Path(a.video).expanduser().resolve();out=Path(a.out).expanduser().resolve()
    if not source.is_file():p.error('Video does not exist')
    if out.exists():p.error('Output already exists')
    try:import cv2
    except ImportError:p.error('OpenCV is required: install opencv-python or opencv-python-headless')
    cap=cv2.VideoCapture(str(source))
    if not cap.isOpened():p.error('Could not open video')
    fps=cap.get(cv2.CAP_PROP_FPS);frames=cap.get(cv2.CAP_PROP_FRAME_COUNT)
    if fps<=0 or frames<=0:p.error('Video duration is unavailable')
    duration=frames/fps
    if a.end>duration+0.05:p.error('End exceeds source duration')
    width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    model=Path(__file__).resolve().parents[1]/'models'/'face_detection_yunet_2023mar.onnx'
    detector=cv2.FaceDetectorYN.create(str(model),'',(width,height),0.6)
    samples=[];prev=None;count=math.ceil((a.end-a.start)/a.interval)+1
    for i in range(count):
        t=min(a.start+i*a.interval,max(a.start,a.end-1/fps))
        if samples and t<=samples[-1]['t']:break
        cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,frame=cap.read();face=None
        if ok:
            h,w=frame.shape[:2];detector.setInputSize((w,h));_,faces=detector.detect(frame)
            if faces is not None and len(faces):
                options=[]
                for box in faces:
                    x,y,bw,bh=map(float,box[:4]);cx=(x+bw/2)/w;cy=(y+bh/2)/h
                    if 0<=cx<=1 and 0<=cy<=1 and bw>0 and bh>0:options.append((cx,cy,bw/w,bh/h,float(box[-1])))
                if options:
                    pick=max(options,key=lambda v:v[2]*v[3]) if prev is None else min(options,key=lambda v:(v[0]-prev[0])**2+(v[1]-prev[1])**2)
                    if prev is None or math.hypot(pick[0]-prev[0],pick[1]-prev[1])<=0.35:
                        prev=pick;face={'cx':round(pick[0],5),'cy':round(pick[1],5),'w':round(pick[2],5),'h':round(pick[3],5),'confidence':round(pick[4],4)}
        samples.append({'t':round(t,4),'face':face})
    cap.release();result={'source':str(source),'width':width,'height':height,'interval':a.interval,'start':a.start,'end':a.end,'samples':samples,'detected':sum(s['face'] is not None for s in samples)}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(f"Detected faces in {result['detected']} of {len(samples)} samples: {out}")

if __name__=='__main__':
    try:main()
    except (OSError,ValueError) as e:sys.exit(f'Face tracking failed: {e}')
