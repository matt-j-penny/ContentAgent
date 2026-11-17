#!/usr/bin/env python3
"""Verify layout decisions remain conservative with weak or conflicting evidence."""
import importlib.util,json,tempfile
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'scripts'/'plan.py';spec=importlib.util.spec_from_file_location('plan',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base={'duration':4,'transcript_cues':[{'start':0,'end':1,'label':'camera'},{'start':2,'end':3,'label':'screen'}], 'cursor_activity':[{'start':1,'end':2}]}
pose={'camera_yaw':0,'screen_yaw':5,'fps':2,'samples':[{'t':i/2,'yaw':5} for i in range(8)]}
r=m.build(base,pose);assert not r['pose_reference_distinct']
assert [(x['label'],x['start'],x['end']) for x in r['intervals']]==[('camera',0,1),('screen',1,2),('screen',2,3),('unknown',3,4)]
pose['screen_yaw']=15;pose['samples'][0]['yaw']=15;pose['samples'][1]['yaw']=15
r=m.build(base,pose);assert r['pose_reference_distinct'] and r['intervals'][0]['label']=='unknown'
r=m.build({'duration':1,'transcript_cues':[{'start':0,'end':1,'label':'camera'}],'cursor_activity':[{'start':0,'end':1}]});assert r['intervals'][0]['label']=='unknown'
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'cursor.json';p.write_text(json.dumps({'samples':[{'timeMs':0,'cx':0.2,'cy':0.4},{'timeMs':500,'cx':0.3,'cy':0.4,'interactionType':'click'}]}))
 events=m.cursor_intervals(p,4,0.5);assert events==[{'start':0,'end':1.0}]
print('Ambiguous pose, conflicts, transcript, cursor and unknown handling verified')
import subprocess
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);c=root/'cues.json';out=root/'out.json';c.write_text(json.dumps({'duration':1,'transcript_cues':[]}))
 cmd=['python3',str(Path(__file__).resolve().parents[1]/'scripts'/'plan.py'),str(c),'--out',str(out)]
 subprocess.run(cmd,check=True,capture_output=True)
 assert json.loads(out.read_text())['intervals'][0]['label']=='unknown'
 assert subprocess.run(cmd,capture_output=True).returncode!=0
print('CLI output and overwrite protection verified')
