#!/usr/bin/env python3
"""Rank public Instagram posts from a supplied dataset, using comparable medians."""
import argparse,json,statistics,sys
from pathlib import Path


def classify(item):
    typ=(item.get('type') or '').lower();product=(item.get('productType') or '').lower()
    if typ=='sidecar':return 'carousel'
    if typ=='image':return 'image'
    if typ=='video':return 'reel' if product=='clips' else 'video'
    return 'unknown'


def rank(items):
    groups={}
    for item in items:
        if not isinstance(item,dict) or item.get('isPinned') or item.get('pinned'):continue
        handle=(item.get('ownerUsername') or '').strip().lower()
        likes=item.get('likesCount')
        if not handle or isinstance(likes,bool) or not isinstance(likes,int) or likes<0:continue
        kind=classify(item)
        groups.setdefault((handle,kind),[]).append(item)
    rows=[]
    for (handle,kind),posts in groups.items():
        baseline=statistics.median(p['likesCount'] for p in posts)
        for post in posts:
            rows.append({'handle':handle,'format':kind,'url':post.get('url'),'date':post.get('timestamp'),'likes':post['likesCount'],'median_likes':baseline,'sample_size':len(posts),'outlier_multiple':round(post['likesCount']/baseline,2) if kind!='unknown' and baseline>0 and len(posts)>=3 else None,'caption':post.get('caption') or ''})
    return sorted(rows,key=lambda r:(r['outlier_multiple'] is None,-(r['outlier_multiple'] or 0),-r['likes']))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('dataset');p.add_argument('--out',required=True);a=p.parse_args()
    src=Path(a.dataset).expanduser().resolve();out=Path(a.out).expanduser().resolve()
    if out.exists():p.error('Output already exists; choose a new path')
    data=json.loads(src.read_text());items=data.get('items') if isinstance(data,dict) else data
    if not isinstance(items,list):p.error('Dataset must be a list or an object with an items list')
    rows=rank(items)
    if not rows:p.error('No usable posts with a creator and visible like counts')
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8') as f:json.dump(rows,f,ensure_ascii=False,indent=2);f.write('\n')
    print(f'Ranked {len(rows)} posts: {out}')


if __name__=='__main__':
    try:main()
    except (OSError,ValueError,json.JSONDecodeError) as e:sys.exit(f'Instagram ranking failed: {e}')
