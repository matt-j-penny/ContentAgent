#!/usr/bin/env python3
"""Validate public-comment output without making network requests."""
import importlib.util,os,sys,tempfile
from pathlib import Path
from unittest.mock import patch
script=Path(__file__).resolve().parents[1]/'scripts'/'fetch-comments.py'
spec=importlib.util.spec_from_file_location('fetch_comments',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as tmp:
 vid='aBcDeFgH_12';dest=Path(tmp)/'comments'
 with patch.dict(os.environ,{'YOUTUBE_API_KEY':''}),patch.object(m,'via_ytdlp',return_value=[(1,0,'second'),(4,0,'first')]),patch.object(sys,'argv',['fetch-comments',str(dest),vid]):m.main()
 out=dest/f'{vid}.md';text=out.read_text();assert text.index('first')<text.index('second')
 with patch.object(sys,'argv',['fetch-comments',str(dest),vid]):
  try:m.main()
  except SystemExit as e:assert e.code != 0
  else:raise AssertionError('existing output was overwritten')
 assert out.read_text()==text
print('Comment sorting and overwrite protection passed')
