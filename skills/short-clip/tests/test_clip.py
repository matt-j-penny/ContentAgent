#!/usr/bin/env python3
"""Exercise short-clip output and input preservation using generated media."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
script=Path(__file__).resolve().parents[1]/'scripts'/'clip.py'
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp);src=d/'source.mp4';out=d/'short.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc=size=320x180:rate=15','-f','lavfi','-i','sine=frequency=440:sample_rate=44100','-t','2','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(src)],check=True)
 before=hashlib.sha256(src.read_bytes()).digest()
 base=['python3',str(script),str(src),'--start','0.3','--duration','1','--width','180','--height','320','--out',str(out)]
 subprocess.run(base,check=True,capture_output=True)
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]))
 v=next(x for x in info['streams'] if x['codec_type']=='video')
 assert (v['width'],v['height'])==(180,320) and abs(float(info['format']['duration'])-1)<0.15
 assert any(x['codec_type']=='audio' for x in info['streams'])
 assert hashlib.sha256(src.read_bytes()).digest()==before
 assert subprocess.run(base,capture_output=True).returncode!=0
 assert subprocess.run(['python3',str(script),str(src),'--start','1.8','--duration','1','--out',str(d/'bad.mp4')],capture_output=True).returncode!=0
print('Portrait clip, timing, audio and overwrite protection passed')

# Test face-following and rejection of incomplete or mismatched tracking data.
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp);src=d/'source.mp4';out=d/'tracked.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc=size=320x180:rate=15','-t','2','-c:v','libx264','-pix_fmt','yuv420p',str(src)],check=True)
 track={'source':str(src),'start':0,'end':2,'interval':0.5,'samples':[{'t':t,'face':{'cx':x}} for t,x in [(0,0.2),(0.5,0.3),(1,0.5),(1.5,0.7),(1.95,0.8)]]}
 tr=d/'track.json';tr.write_text(json.dumps(track))
 cmd=['python3',str(script),str(src),'--start','0.3','--duration','1','--width','180','--height','320','--track',str(tr),'--out',str(out)]
 subprocess.run(cmd,check=True,capture_output=True)
 assert out.is_file()
 static=d/'static.mp4'
 subprocess.run(['python3',str(script),str(src),'--start','0.3','--duration','1','--width','180','--height','320','--out',str(static)],check=True,capture_output=True)
 def frame(path):
  return subprocess.check_output(['ffmpeg','-v','error','-ss','0.5','-i',str(path),'-frames:v','1','-f','framemd5','-'])
 assert frame(out)!=frame(static), 'tracked crop did not change framing'
 track['samples'][1]['face']=None;tr.write_text(json.dumps(track))
 cmd[-1]=str(d/'missing.mp4');assert subprocess.run(cmd,capture_output=True).returncode!=0
 track['samples'][1]['face']={'cx':0.3};track['source']=str(d/'other.mp4');tr.write_text(json.dumps(track))
 cmd[-1]=str(d/'wrong.mp4');assert subprocess.run(cmd,capture_output=True).returncode!=0
print('Face-following and incomplete/wrong-source track rejection passed')
