#!/usr/bin/env python3
"""Reconstruct the published tracking summaries and frequency strata from records."""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path


def support_strata(records):
    output={}
    for mode in ('exact','family'):
        bins=defaultdict(list)
        for r in records:
            if mode=='family' and not r['strict']:
                continue
            n=len({x for s in r['siblings'] for x in s['ids']})
            assert n>=1
            bins['1' if n==1 else '2-3' if n<=3 else '4+'].append(r)
        for b,items in bins.items():
            output[f'{mode}/{b}']={'units':len(items),'conditions':{
                c:dict(Counter(r['outcomes'][c][mode] for r in items))
                for c in items[0]['outcomes']}}
    return output


def summarize(data):
    out={}
    for part,v in data.items():
        records=v['records']
        item=out[part]={'units':len(records),'strict_units':sum(r['strict'] for r in records),
                        'counts':v['counts'],'category_counts':dict(Counter(r['category'] for r in records)),
                        'root_weighted':{},'paired_vs_c0':{}}
        for mode in ('exact','family'):
            rs=[r for r in records if mode=='exact' or r['strict']]
            roots=defaultdict(list)
            for r in rs:
                roots[r['theorem']].append(r)
            item['root_weighted'][mode]={'root_count':len(roots),'conditions':{}}
            if not rs:
                continue
            for c in rs[0]['outcomes']:
                by=defaultdict(float)
                for group in roots.values():
                    for r in group:
                        by[r['outcomes'][c][mode]]+=1/len(group)/len(roots)
                item['root_weighted'][mode]['conditions'][c]=dict(by)
                if 'c0_holdout' in rs[0]['outcomes'] and c!='c0_holdout':
                    x=Counter((r['outcomes']['c0_holdout'][mode],r['outcomes'][c][mode]) for r in rs)
                    item['paired_vs_c0'][mode+'/'+c]={' -> '.join(k):v for k,v in x.items()}
    return out


def independent(data):
    s={'source_stats':data['source_stats'],
       'comparisons':{k:{'eligible_groups':v['eligible_groups'],'units':len(v['records']),
                         'roots':len({r['theorem'] for r in v['records']}),'counts':v['counts']}
                      for k,v in data['comparisons'].items()}}
    if 'within_records' in data:
        s['within_category_counts']={k:dict(Counter(next(iter(c)) if len(c)==1 else 'ambiguous'
                                                    for r in rs for c in [{x['category'] for x in r['siblings']}]))
                                     for k,rs in data['within_records'].items()}
    return s


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('directory',type=Path)
    args=parser.parse_args()
    for p in sorted(args.directory.glob('*.json.gz')):
        raw=p.read_bytes()
        data=json.loads(gzip.decompress(raw))
        result=independent(data) if 'source_stats' in data else summarize(data)
        result['record_archive_sha256']=hashlib.sha256(raw).hexdigest()
        expected=json.loads(p.with_name(p.name.replace('.json.gz','-summary.json')).read_text())
        assert result==expected,p
        if p.name=='near-miss-tracking.json.gz':
            assert support_strata(data['split']['records'])==json.loads((p.parent/'support-strata.json').read_text())
        print('Verified:',p.name)
