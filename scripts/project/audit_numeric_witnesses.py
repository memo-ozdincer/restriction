"""Independently reconcile the numeric witness panel, Lean checks, and promotion sequence."""
import argparse
from collections import Counter
import json
from pathlib import Path

from block_numeric_witnesses import lean, statement


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('run',type=Path)
    p.add_argument('output',type=Path)
    a=p.parse_args()
    possible={(x,y) for x in range(1,65) for y in range(x+1,65) if x*x+y*y==65*65}
    assert len(possible)==4
    complete=json.loads((a.run/'complete.json').read_text())
    blocks=[tuple(w) for w in complete['blocks']]
    counts={}
    for depth in range(len(blocks)+1):
        groups=['discovery'] if depth==0 else [f'control-{depth}',f'blocked-{depth}']
        for g in groups:
            folder=a.run/g
            active=blocks[:depth] if g.startswith('blocked') else []
            batch=json.loads((folder/'samples.json').read_text())
            src=json.loads((folder/'sources.json').read_text())
            verdicts=lean.rows(folder/'verdicts.jsonl')
            assert set(src)=={v['id'] for v in verdicts} and len(src)==len(verdicts)
            assert all(lean.sha(src[v['id']])==v['id']==v['code_sha256'] and not v['system_errors'] for v in verdicts)
            accepted={v['id'] for v in verdicts if v['accepted']}
            assert all(v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS
                       for v in verdicts if v['accepted'])
            detail=json.loads((folder/'detail.json').read_text())
            assert batch['prompt']==lean.PREFIX+lean.HEADER+statement(active)
            assert len(batch['rows'])==len(detail)==16
            witnesses=Counter()
            wins=0
            for i,(r,d) in enumerate(zip(batch['rows'],detail)):
                assert r['sample_index']==i==d['sample'] and r['seed']==20261126+depth
                body,error=lean.completion_code(r['text'])
                key=None if error else lean.sha(lean.HEADER+statement(active)+body+'\n#print axioms target')
                assert (key,error,key in accepted)==(d['key'],d['error'],d['accepted'])
                if key:
                    assert key in src
                wins+=d['accepted']
                if d['witness']:
                    w=tuple(d['witness'])
                    assert d['accepted'] and w in possible-set(active)
                    witnesses[w]+=1
            counts[g]=dict(accepted=wins,identified=sum(witnesses.values()),verified_sources=len(accepted),
                           witnesses={f'{x},{y}':n for (x,y),n in sorted(witnesses.items())})
            if g=='discovery' or g.startswith('blocked'):
                ranked=witnesses.most_common()
                promote=bool(ranked and ranked[0][1]>=max(2,.4*wins) and
                             (len(ranked)==1 or ranked[0][1]>ranked[1][1]))
                if depth<len(blocks):
                    assert promote and ranked[0][0]==blocks[depth]
                elif depth<2:
                    assert not promote
    lean.write(a.output,dict(admissible=sorted(possible),blocks=blocks,groups=counts))


if __name__=='__main__':
    main()
