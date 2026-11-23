"""Paired finite witness-discovery gate with certified Lean outputs and literal pair tracking."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

import interface_discovery_pilot as lean
import run_policy_improvement as policy

PAIR = re.compile(r"(?:^\s*use\s+|^\s*(?:exact|refine'?)\s+⟨)\s*(\d+)\s*,\s*(\d+)",re.MULTILINE)


def statement(blocks):
    conditions=['0 < a','a < b','a^2+b^2 = 65^2']+[f'a ≠ {x}' for x,y in blocks]
    return ('-- Give explicit numerical witnesses.\n'
            'theorem target : ∃ a b : ℕ, '+' ∧ '.join(conditions)+' := by\n')


def run_group(model,tokenizer,bundle,out,blocks,seed):
    out.mkdir()
    source=lean.HEADER+statement(blocks)
    rows=policy.sample(model,tokenizer,lean.PREFIX+source,seed,256,False)
    lean.write(out/'samples.json',dict(prompt=lean.PREFIX+source,rows=rows))
    jobs={}
    detail=[]
    for r in rows:
        body,error=lean.completion_code(r['text'])
        key=None
        if not error:
            code=source+body+'\n#print axioms target'
            key=lean.sha(code)
            jobs[key]=dict(id=key,code=code,lake=str(bundle/'lean/elan/bin/lake'),
                           verifier=str(bundle/'verifier/DeepSeek-Prover-V1.5'))
        detail.append(dict(sample=r['sample_index'],key=key,error=error,witness=None))
    lean.write(out/'sources.json',{k:v['code'] for k,v in jobs.items()})
    checked=lean.verify_jobs(list(jobs.values()),out/'verdicts.jsonl',workers=6)
    if any(v.get('system_errors') for v in checked):
        raise RuntimeError('Unresolved Lean verdict')
    accepted={v['id'] for v in checked if v['accepted']}
    for row,d in zip(rows,detail):
        d['accepted']=d['key'] in accepted
        if d['accepted']:
            pairs=PAIR.findall(row['text'])
            if len(pairs)==1:
                x,y=map(int,pairs[0])
                if 0<x<y and x*x+y*y==65**2 and (x,y) not in blocks:
                    d['witness']=[x,y]
    lean.write(out/'detail.json',detail)
    return detail


def promotion(rows):
    counts=Counter(tuple(r['witness']) for r in rows if r['witness']).most_common()
    if not counts or (len(counts)>1 and counts[0][1]==counts[1][1]):
        return None
    key,n=counts[0]
    return key if n>=max(2,.4*sum(r['accepted'] for r in rows)) else None


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('bundle',type=Path)
    p.add_argument('out',type=Path)
    a=p.parse_args()
    model,tok=policy.load_model(a.bundle)
    model=policy.add_adapter(model,a.bundle/'runs/recursive-grpo-20261123-1398215/recursive/adapter')
    previous=run_group(model,tok,a.bundle,a.out/'discovery',[],20261126)
    blocks=[]
    for depth in (1,2):
        top=promotion(previous)
        if top is None:
            break
        blocks.append(top)
        lean.write(a.out/'blocks.json',blocks)
        run_group(model,tok,a.bundle,a.out/f'control-{depth}',[],20261126+depth)
        previous=run_group(model,tok,a.bundle,a.out/f'blocked-{depth}',blocks,20261126+depth)
    lean.write(a.out/'complete.json',dict(blocks=blocks,groups=1+2*len(blocks)))


if __name__=='__main__':
    main()
