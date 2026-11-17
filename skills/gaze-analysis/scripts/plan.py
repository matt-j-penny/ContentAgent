#!/usr/bin/env python3
"""Create a reviewable camera/screen plan from explicit cues and optional head pose."""
import argparse,bisect,json,math,sys
from pathlib import Path


def finite(value):
    return not isinstance(value,bool) and isinstance(value,(int,float)) and math.isfinite(value)


def intervals(items,duration,labels=None):
    if not isinstance(items,list):raise ValueError('Intervals must be lists')
    result=[]
    for x in items:
        if not isinstance(x,dict) or not finite(x.get('start')) or not finite(x.get('end')) or not 0<=x['start']<x['end']<=duration+0.001:raise ValueError('Invalid interval')
        if labels is not None and x.get('label') not in labels:raise ValueError('Cue label must be camera or screen')
        result.append(x)
    return result


def cursor_intervals(path,duration,near):
    data=json.loads(Path(path).expanduser().read_text());samples=data.get('samples')
    if not isinstance(samples,list):raise ValueError('Cursor file must contain samples')
    out=[]
    for prev,cur in zip(samples,samples[1:]):
        if not isinstance(prev,dict) or not isinstance(cur,dict):continue
        if not all(finite(v) for v in (prev.get('cx'),prev.get('cy'),cur.get('cx'),cur.get('cy'),cur.get('timeMs'))):continue
        if prev['cy']>=0.98 or cur['cy']>=0.98:continue
        active=cur.get('interactionType') in ('click','double-click') or math.hypot(cur['cx']-prev['cx'],cur['cy']-prev['cy'])>0.02
        if active:
            t=cur['timeMs']/1000
            if 0<=t<=duration:out.append({'start':max(0,t-near),'end':min(duration,t+near)})
    return out


def build(data,pose=None,cursor=None,fps=2,min_separation=7):
    duration=data.get('duration')
    if not finite(duration) or not 0<duration<=43200:raise ValueError('duration must be positive and at most 12 hours')
    if not finite(fps) or not 0.1<=fps<=10 or duration*fps>200000:raise ValueError('Invalid sampling rate')
    cues=intervals(data.get('transcript_cues',[]),duration,{'camera','screen'})
    cursors=intervals(data.get('cursor_activity',[]),duration)+(cursor or [])
    reliable=False;times=[];samples=[];camera=screen=None
    if pose:
        if data.get('webcam') and Path(data['webcam']).expanduser().resolve()!=Path(pose.get('source','')).expanduser().resolve():raise ValueError('Pose file belongs to another webcam video')
        camera=pose.get('camera_yaw');screen=pose.get('screen_yaw')
        reliable=finite(camera) and finite(screen) and abs(camera-screen)>=min_separation
        raw=pose.get('samples',[])
        if not isinstance(raw,list):raise ValueError('Invalid pose samples')
        for s in raw:
            if not isinstance(s,dict) or not finite(s.get('t')):raise ValueError('Invalid pose timestamp')
            yaw=s.get('yaw')
            if yaw is not None and not finite(yaw):raise ValueError('Invalid yaw')
            if times and s['t']<=times[-1]:raise ValueError('Pose timestamps must increase')
            times.append(s['t']);samples.append(yaw)
    rows=[]
    for i in range(math.ceil(duration*fps)):
        start=i/fps;end=min(duration,(i+1)/fps);t=(start+end)/2
        active={x['label'] for x in cues if x['start']<=t<x['end']}
        cursor_on=any(x['start']<=t<x['end'] for x in cursors)
        if len(active)>1:label,reason='unknown','conflicting transcript cues'
        elif 'screen' in active:label,reason='screen','transcript cue'
        elif 'camera' in active and cursor_on:label,reason='unknown','camera cue conflicts with cursor activity'
        elif 'camera' in active:label,reason='camera','transcript cue'
        elif cursor_on:label,reason='screen','cursor activity'
        else:label,reason='unknown','no clear cue'
        if label=='camera' and reliable and times:
            at=bisect.bisect_left(times,t); candidates=[j for j in (at-1,at) if 0<=j<len(times)]
            j=min(candidates,key=lambda n:abs(times[n]-t))
            max_gap=1/max(float(pose.get('fps',2)),0.1)
            yaw=samples[j] if abs(times[j]-t)<=max_gap else None
            if yaw is not None and abs(yaw-screen)+2<abs(yaw-camera):label,reason='unknown','head pose conflicts with camera cue'
        if rows and rows[-1]['label']==label and rows[-1]['reason']==reason:
            rows[-1]['end']=round(end,3)
        else:rows.append({'start':round(start,3),'end':round(end,3),'label':label,'reason':reason})
    return {'duration':duration,'pose_reference_distinct':bool(reliable),'intervals':rows,'note':'Proposals require visual review; head pose is not eye gaze.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('cues');p.add_argument('--pose');p.add_argument('--cursor',help='optional Recordly cursor JSON');p.add_argument('--fps',type=float,default=2);p.add_argument('--min-separation',type=float,default=7);p.add_argument('--out',required=True);a=p.parse_args()
    out=Path(a.out).expanduser().resolve()
    if out.exists():p.error('Output already exists')
    if not finite(a.min_separation) or a.min_separation<=0:p.error('min-separation must be positive')
    data=json.loads(Path(a.cues).expanduser().read_text());pose=json.loads(Path(a.pose).expanduser().read_text()) if a.pose else None
    if not isinstance(data,dict) or not finite(data.get('duration')) or not 0<data['duration']<=43200:p.error('duration must be positive and at most 12 hours')
    cursor=cursor_intervals(a.cursor,data.get('duration',0),1.5) if a.cursor else None
    result=build(data,pose,cursor,a.fps,a.min_separation);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(f'Layout proposals: {out}')

if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError,json.JSONDecodeError) as e:sys.exit(f'Layout planning failed: {e}')
