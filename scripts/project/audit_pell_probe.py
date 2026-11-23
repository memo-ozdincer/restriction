"""Reconcile all Pell prompts, emitted responses, Lean hashes and witness counts."""
import argparse
from collections import Counter
import json
from pathlib import Path
from probe_pell_witnesses import HINT, NAME, PAIR, lean


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path)
    parser.add_argument('out',type=Path)
    a=parser.parse_args()
    summary=json.loads((a.run/'results.json').read_text())
    groups=json.loads((a.run/'complete.json').read_text())['groups']
    assert groups==list(summary)
    active=[1]
    output={}
    for name in groups:
        root=a.run/name
        data=json.loads((root/'samples.json').read_text())
        depth=2 if name.endswith('-2') else 1
        exclusions=([1,5] if name.startswith('map-') else active if name.startswith('blocked-') else [])
        assert data['blocks']==exclusions
        cond=['x^2 - 6*y^2 = 1']+[f'x.natAbs ≠ {v}' for v in exclusions]
        source=lean.HEADER+f'theorem {NAME} : ∃ x y : ℤ, '+' ∧ '.join(cond)+'   := by\n'
        assert data['prompt']==lean.PREFIX+(HINT if name=='map-hint' else '')+source
        seed=20261130 if name.startswith('map-') else 20261127+depth
        assert data['seed']==seed
        records=json.loads((root/'records.json').read_text())
        sources=json.loads((root/'sources.json').read_text())
        vs=lean.rows(root/'verdicts.jsonl')
        assert len(sources)==len(vs) and {v['id'] for v in vs}==set(sources)
        by_key={v['id']:v for v in vs}
        for v in vs:
            assert lean.sha(sources[v['id']])==v['id']==v['code_sha256'] and not v['system_errors']
            if v['accepted']:
                assert v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS
        counts=Counter()
        rejected=Counter()
        assert len(records)==len(data['rows'])==16
        for i,(rec,r) in enumerate(zip(records,data['rows'])):
            assert i==r['sample_index']==rec['index'] and r['seed']==seed
            body,error=lean.completion_code(r['text'])
            key=None if error else lean.sha(source+body+'\n#print axioms '+NAME)
            ok=bool(by_key[key]['accepted']) if key else False
            assert (key,error,ok)==(rec['key'],rec['error'],rec['accepted'])
            pairs=PAIR.findall(r['text'])
            if len(pairs)==1:
                x,y=map(int,pairs[0])
                if ok:
                    assert x*x-6*y*y==1 and abs(x) not in exclusions and rec['witness']==[x,y]
                    counts[abs(x)]+=1
                else:
                    rejected['forbidden_solution' if x*x-6*y*y==1 and abs(x) in exclusions
                             else 'admissible_pair' if x*x-6*y*y==1 else 'wrong_equation']+=1
        assert summary[name]['accepted']==sum(r['accepted'] for r in records)
        assert counts=={int(k):v for k,v in summary[name]['counts'].items()}
        output[name]=dict(accepted=summary[name]['accepted'],identified=counts,rejected_literal_pairs=rejected,
            distinct_sources=len(vs),unidentified_successes=sum(r['accepted'] and not r['witness'] for r in records))
        if name=='blocked-1':
            leader=counts.most_common(2)
            eligible=bool(leader and leader[0][1]>=max(2,.4*summary[name]['accepted']) and
                          (len(leader)==1 or leader[0][1]>leader[1][1]))
            assert eligible==('blocked-2' in groups)
            if eligible:
                active.append(leader[0][0])
    lean.write(a.out,output)


if __name__=='__main__':
    main()
