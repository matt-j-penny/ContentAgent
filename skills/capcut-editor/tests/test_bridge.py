import importlib.util,json,os,sys,tempfile,types
from pathlib import Path
from unittest.mock import patch
class FakeModule(types.ModuleType):
 def __getattr__(self,name): return lambda *a,**k: None
sys.modules['ApplicationServices']=FakeModule('ApplicationServices')
sys.modules['Quartz']=FakeModule('Quartz')
p=Path(__file__).resolve().parents[1]/'scripts'/'capcut-bridge.py'
spec=importlib.util.spec_from_file_location('bridge',p);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);job=root/'projects'/'demo';(job/'raw').mkdir(parents=True);(job/'transcript').mkdir();(job/'raw'/'source.mp4').write_bytes(b'synthetic source')
 plan={'fps':24,'segments':[{'clip':'source.mp4','start':0.1,'end':0.5},{'clip':'source.mp4','start':1,'end':1.5}]}; (job/'transcript'/'cuts.json').write_text(json.dumps(plan));os.environ['CONTENTAGENT_PROJECT_ROOT']=tmp
 b.probe=lambda path: (320,240,2000000,True)
 raw,cuts,w,h=b.inspect_job('demo','draft');assert (w,h)==(320,240) and len(cuts['segments'])==2
 for bad in ('../demo','.', 'a/b'):
  try:b.inspect_job(bad)
  except ValueError:pass
  else:raise AssertionError('unsafe name accepted')
 plan['segments'][1]['start']=0.3;(job/'transcript'/'cuts.json').write_text(json.dumps(plan))
 try:b.inspect_job('demo')
 except ValueError:pass
 else:raise AssertionError('overlapping cuts accepted')
 plan['segments'][1]['start']=1;(job/'transcript'/'cuts.json').write_text(json.dumps(plan));b.DRAFT_ROOT=root/'drafts';b.DRAFT_ROOT.mkdir();(b.DRAFT_ROOT/'root_meta_info.json').write_text(json.dumps({'all_draft_store':[],'draft_ids':0}))
 with patch.object(b,'app_pid',return_value=None), patch.object(b.subprocess,'run'):
  b.cmd_replay('demo','Test draft')
 data=json.loads((b.DRAFT_ROOT/'Test draft'/'draft_info.json').read_text());assert data['fps']==24 and len(data['tracks'][0]['segments'])==2 and data['duration']==900000
 assert len(json.loads((b.DRAFT_ROOT/'root_meta_info.json').read_text())['all_draft_store'])==1
 with patch.object(b,'app_pid',return_value=123):
  try:b.cmd_replay('demo','Other draft')
  except SystemExit:pass
  else:raise AssertionError('open app accepted')
 assert not (b.DRAFT_ROOT/'Other draft').exists()
 print('Validation, synthetic draft, registry update and open-app protection passed')
