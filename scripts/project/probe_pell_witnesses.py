"""Run matched, sign-invariant exclusions on a train-selected Pell theorem."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

import interface_discovery_pilot as lean
import run_policy_improvement as policy


PAIR=re.compile(r"^\s*(?:use\s+|(?:exact|refine'?)\s+⟨)\s*\(?\s*(-?\d+)\s*\)?\s*,\s*\(?\s*(-?\d+)\s*\)?(?=\s*(?:,|⟩|\n|$))",re.MULTILINE)
HINT='-- From an integer solution (x,y), another is (5*x+12*y,2*x+5*y).\n'
NAME='lean_workbook_plus_49287'


def group(model,tok,b,out,blocks,seed,hint=False):
    out.mkdir()
    conditions=['x^2 - 6*y^2 = 1']+[f'x.natAbs ≠ {v}' for v in blocks]
    source=lean.HEADER+f'theorem {NAME} : ∃ x y : ℤ, '+' ∧ '.join(conditions)+'   := by\n'
    prompt=lean.PREFIX+(HINT if hint else '')+source
    rows=policy.sample(model,tok,prompt,seed,512,False)
    lean.write(out/'samples.json',dict(prompt=prompt,blocks=blocks,seed=seed,rows=rows))
    jobs={}
    records=[]
    for row in rows:
        body,error=lean.completion_code(row['text'])
        key=None
        if not error:
            code=source+body+'\n#print axioms '+NAME
            key=lean.sha(code)
            jobs[key]=dict(id=key,code=code,lake=str(b/'lean/elan/bin/lake'),verifier=str(b/'verifier/DeepSeek-Prover-V1.5'))
        records.append(dict(index=row['sample_index'],key=key,error=error))
    lean.write(out/'sources.json',{k:v['code'] for k,v in jobs.items()})
    vs=lean.verify_jobs(list(jobs.values()),out/'verdicts.jsonl',workers=6)
    assert all(not v.get('system_errors') for v in vs)
    accepted={v['id'] for v in vs if v['accepted']}
    counts=Counter()
    for row,r in zip(rows,records):
        r.update(accepted=r['key'] in accepted,witness=None)
        pairs=PAIR.findall(row['text'])
        if r['accepted'] and len(pairs)==1:
            x,y=map(int,pairs[0])
            if x*x-6*y*y==1 and abs(x) not in blocks:
                r['witness']=[x,y]
                counts[abs(x)]+=1
    lean.write(out/'records.json',records)
    return dict(accepted=sum(r['accepted'] for r in records),counts=dict(counts),identified=sum(counts.values()))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('bundle',type=Path)
    p.add_argument('out',type=Path)
    a=p.parse_args()
    model,tok=policy.load_model(a.bundle,a.bundle/'models/c1-final')
    summary={}
    blocks=[1]
    for depth in (1,2):
        for arm in ['plain','blocked']:
            name=f'{arm}-{depth}'
            summary[name]=group(model,tok,a.bundle,a.out/name,blocks if arm=='blocked' else [],20261127+depth)
            lean.write(a.out/'results.json',summary)
        r=summary[f'blocked-{depth}']
        best=Counter(r['counts']).most_common()
        if not best or best[0][1]<max(2,.4*r['accepted']) or (len(best)>1 and best[0][1]==best[1][1]):
            break
        blocks.append(best[0][0])
    for hint in (False,True):
        name='map-hint' if hint else 'map-control'
        summary[name]=group(model,tok,a.bundle,a.out/name,[1,5],20261130,hint)
        lean.write(a.out/'results.json',summary)
    lean.write(a.out/'complete.json',dict(groups=list(summary)))


if __name__=='__main__':
    main()
