#!/usr/bin/env python3
"""Compare frozen-block-free concentration on matched C2/C3 training rollouts."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
from statistics import mean

SOURCE = Path('results/c2_unlikeliness_vs_c3_training_seed42.json')

def digest(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

def summarize(counts, blocked, known):
    correct=sum(counts.values())
    alternatives={k:v for k,v in counts.items() if k!=blocked}
    n=sum(alternatives.values())
    top=max(alternatives.values(),default=0)
    return dict(correct=correct,blocked=counts.get(blocked,0),alternatives=n,
                alternative_modes=len(alternatives),top_alt=top,
                top_novel=max((v for k,v in alternatives.items() if k not in known),default=0),
                top_share=top/n if n else None,
                collision=sum(v*(v-1) for v in alternatives.values())/(n*(n-1)) if n>=2 else None)

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args()
    sources=json.loads(SOURCE.read_text())['sources']
    archive_file=next(a.root.rglob('mode_archive.json'))
    assert digest(archive_file)==sources['c0_archive']['sha256']
    archive=json.loads(archive_file.read_text())['counts']
    eligible={}
    for theorem,counts in archive.items():
        total=sum(counts.values())
        if total>=4:
            k,v=max(counts.items(),key=lambda item:item[1])
            if v/total>.5:eligible[theorem]=k
    assert len(eligible)==1014
    data={}
    for c in ('c2','c3'):
        run=Path(sources[c]['run_dir']).name
        path=next(a.root.rglob(run+'/artifacts/proofs/global_step_604.jsonl'))
        assert digest(path)==sources[c]['proof_log_sha256']
        seen=Counter();counts=defaultdict(Counter);steps={};physical=0
        with path.open() as f:
            for line in f:
                r=json.loads(line);physical+=1;name=r['theorem_name']
                if seen[name]>=32: continue
                seen[name]+=1
                if name not in eligible:continue
                step=int(re.search(r':step-(\d+)',r['batch_id']).group(1))
                assert steps.setdefault(name,step)==step
                if not r.get('correct'): continue
                mode=r.get('tactic_prefix_signature') or r.get('mode_id')
                assert mode
                if c=='c3':assert bool(r.get('blocked_correct'))==(mode==eligible[name])
                counts[name][mode]+=1
        assert physical==308992 and len(seen)==9655 and set(seen.values())=={32}
        assert set(steps)==set(eligible)
        data[c]={name:dict(step=steps[name],**summarize(counts[name],eligible[name],archive[name]))
                 for name in eligible}
    assert sum(r['blocked'] for r in data['c3'].values())==sources['c3']['blocked_correct_zero_advantage']
    assert all(data['c2'][n]['step']==data['c3'][n]['step'] for n in eligible)
    def aggregate(names):
        out={'n':len(names),'metrics':{},'paired':{}}
        for metric in ('correct','blocked','alternatives','top_alt','top_novel','alternative_modes','top_share','collision'):
            subset=[n for n in names if all(data[c][n][metric] is not None for c in data)]
            mult=1/32 if metric in ('correct','blocked','alternatives','top_alt','top_novel') else 1
            if not subset:continue
            vals={c:[data[c][n][metric]*mult for n in subset] for c in data}
            diffs=[a-b for a,b in zip(vals['c3'],vals['c2'])]
            out['metrics'][metric]={'n':len(subset),'c2':mean(vals['c2']),'c3':mean(vals['c3']),'delta':mean(diffs)}
            out['paired'][metric]={'positive':sum(d>0 for d in diffs),'negative':sum(d<0 for d in diffs),'tie':sum(d==0 for d in diffs)}
        return out
    result={'sources':sources,'overall':aggregate(list(eligible)),'windows':{},
            'per_theorem':{n:{c:data[c][n] for c in data} for n in sorted(eligible)}}
    for start in range(1,605,100):
        names=[n for n in eligible if start<=data['c2'][n]['step']<start+100]
        result['windows'][str(start)]=aggregate(names)
    with a.output.open('x') as f:json.dump(result,f,indent=2,sort_keys=True)
    print(json.dumps(result['overall'],indent=2))
    for k,w in result['windows'].items():
        print(k,w['n'],{m:w['metrics'][m] for m in ('top_alt','collision') if m in w['metrics']})
if __name__=='__main__':main()
