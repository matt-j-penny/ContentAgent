#!/usr/bin/env python3
import importlib.util
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'scripts'/'rank.py';spec=importlib.util.spec_from_file_location('rank',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
items=[{'ownerUsername':'Test','type':'Video','productType':'clips','likesCount':n,'url':str(n)} for n in (10,20,100)]
items += [{'ownerUsername':'Test','type':'Video','productType':'clips','likesCount':999,'isPinned':True}, {'ownerUsername':'Test','type':'Image','likesCount':300}, {'ownerUsername':'Test','type':'Image','likesCount':-1}]
rows=m.rank(items);assert len(rows)==4
best=next(r for r in rows if r['likes']==100);assert best['median_likes']==20 and best['sample_size']==3 and best['outlier_multiple']==5
image=next(r for r in rows if r['format']=='image');assert image['outlier_multiple'] is None
print('Comparable-format medians, pinned and hidden posts verified')
import json,subprocess,tempfile
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp);src=d/'posts.json';out=d/'rank.json';src.write_text(json.dumps(items))
 cmd=['python3',str(p),str(src),'--out',str(out)]
 subprocess.run(cmd,check=True,capture_output=True)
 before=out.read_text();assert len(json.loads(before))==4
 assert subprocess.run(cmd,capture_output=True).returncode!=0 and out.read_text()==before
print('Dataset output and overwrite protection passed')
