#!/usr/bin/env python3
"""Fetch public YouTube comments into new local Markdown files."""
import argparse,json,os,re,subprocess,sys,urllib.parse,urllib.request
from pathlib import Path

ID=re.compile(r'^[A-Za-z0-9_-]{11}$')

def via_api(vid,key,limit):
    out=[];token=None
    while len(out)<limit:
        q={'part':'snippet','videoId':vid,'order':'relevance','maxResults':min(100,limit-len(out)),'textFormat':'plainText','key':key}
        if token:q['pageToken']=token
        with urllib.request.urlopen('https://www.googleapis.com/youtube/v3/commentThreads?'+urllib.parse.urlencode(q),timeout=30) as r:data=json.load(r)
        for item in data.get('items',[]):
            snippet=item['snippet']['topLevelComment']['snippet']
            out.append((snippet.get('likeCount',0),item['snippet'].get('totalReplyCount',0),snippet.get('textDisplay','')))
        token=data.get('nextPageToken')
        if not token:break
    return out


def via_ytdlp(vid,limit):
    result=subprocess.run(['yt-dlp','--ignore-config','--no-playlist','-J','--skip-download','--write-comments','--extractor-args',f'youtube:comment_sort=top;max_comments={limit},all,0',f'https://www.youtube.com/watch?v={vid}'],capture_output=True,text=True,timeout=300,check=True)
    comments=json.loads(result.stdout or '{}').get('comments') or []
    return [(c.get('like_count') or 0,0,c.get('text','')) for c in comments if c.get('parent')=='root'][:limit]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('out_dir');parser.add_argument('ids',nargs='+');parser.add_argument('--max',type=int,default=100);args=parser.parse_args()
    if not 1<=args.max<=1000:parser.error('--max must be between 1 and 1000')
    if any(not ID.fullmatch(vid) for vid in args.ids):parser.error('Each video ID must be an 11-character YouTube video ID')
    if len(set(args.ids)) != len(args.ids):parser.error('Video IDs must be unique')
    out=Path(args.out_dir).expanduser()
    if any((out/f'{vid}.md').exists() for vid in args.ids):parser.error('Output already exists; choose a new directory')
    out.mkdir(parents=True,exist_ok=True);key=os.environ.get('YOUTUBE_API_KEY');failures=0
    for vid in args.ids:
        try:
            rows=via_api(vid,key,args.max) if key else via_ytdlp(vid,args.max)
            rows.sort(key=lambda x:-x[0])
            with (out/f'{vid}.md').open('x',encoding='utf-8') as f:
                f.write(f'# Public comments for {vid} ({len(rows)})\n\n')
                for likes,replies,text in rows:f.write(f'- [{likes} likes, {replies} replies] {" ".join(text.split())}\n')
            print(f'{vid}: {len(rows)} comments')
        except (OSError,ValueError,KeyError,subprocess.SubprocessError) as e:
            failures+=1
            print(f'{vid}: comments unavailable ({type(e).__name__})',file=sys.stderr)
    if failures:sys.exit(1)


if __name__=='__main__':main()
