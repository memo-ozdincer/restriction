"""Audit frozen/fresh trials and test a one-coordinate reflection with sign controls."""
import argparse
import json
from pathlib import Path
import re

from pell_coordinates import NAME, lean, source

USE=re.compile(r'^(\s*use\s+)(\d+)(,\s*)(\d+)(?=\s*\n)')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('bundle',type=Path)
    p.add_argument('experiment',type=Path)
    p.add_argument('prior',type=Path)
    a=p.parse_args()
    jobs={}
    def add(code,theorem):
        full=code+'\n#print axioms '+theorem
        key=lean.sha(full)
        jobs[key]=dict(id=key,code=full,lake=str(a.bundle/'lean/elan/bin/lake'),verifier=str(a.bundle/'verifier/DeepSeek-Prover-V1.5'))
        return key
    mapping={}
    transports={}
    audit={}
    equiv=(a.experiment/'equivalence.lean').read_text()
    for trial in ('replay','fresh'):
        folder=a.experiment/trial
        accepted={}
        vs=lean.rows(folder/'verdicts.jsonl')
        sources=json.loads((folder/'sources.json').read_text())
        assert len(vs)==len(sources) and {v['id'] for v in vs}==set(sources)
        for v in vs:
            assert v['code_sha256']==v['id']==lean.sha(sources[v['id']]) and not v['system_errors']
            assert not v['accepted'] or (v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS)
            accepted[v['id']]=v['accepted']
        totals={}
        for cell,records in json.loads((folder/'cells.json').read_text()).items():
            group,arm=cell.split('/')
            batch=json.loads(((folder/(arm+'.json')) if trial=='fresh' else (a.prior/group/'samples.json')).read_text())
            if trial=='fresh':
                assert batch['prompt']==lean.PREFIX+source(arm)
            assert len(records)==len(batch['rows'])==16
            n=0
            for i,(record,row) in enumerate(zip(records,batch['rows'])):
                if trial=='fresh':
                    assert row['seed']==20261201
                body,error=lean.completion_code(row['text'])
                assert record['index']==row['sample_index']==i and record['error']==error
                key=None if error else lean.sha(source(arm)+body+'\n#print axioms '+NAME)
                assert key==record['key']
                ok=accepted[key] if key is not None else False
                n+=ok
                if trial!='fresh' or arm not in ('forward','inverse'):
                    continue
                if ok and key not in transports:
                    code=sources[key]+'\n'+equiv.partition('import Mathlib\n')[2]
                    code+='\ntheorem transported : ∃ x y : ℤ, x^2-6*y^2=1 ∧ x.natAbs ≠ 1 ∧ x.natAbs ≠ 5 := by\n'
                    code+=f'  exact {arm}_equiv.mp {NAME}\n'
                    transports[key]=add(code,'transported')
                match=USE.match(body)
                assert match is not None
                x,y=int(match[2]),int(match[4])
                for label,xx,yy in [('negate_y',x,-y),('negate_both',-x,-y)]:
                    changed=match[1]+str(xx)+match[3]+str(yy)+body[match.end():]
                    mapping.setdefault(arm+'/'+label,[]).append(add(source(arm)+changed,NAME))
            totals[cell]=n
        assert totals==json.loads((folder/'summary.json').read_text())
        audit[trial]=totals
    dest=a.experiment/'reflection'
    dest.mkdir()
    lean.write(dest/'sources.json',{k:v['code'] for k,v in jobs.items()})
    lean.write(dest/'mapping.json',dict(edits=mapping,transports=transports))
    verdicts=lean.verify_jobs(list(jobs.values()),dest/'verdicts.jsonl',workers=3)
    assert all(not v.get('system_errors') for v in verdicts)
    passed={v['id'] for v in verdicts if v['accepted']}
    audit['reflection']={k:sum(key in passed for key in keys) for k,keys in mapping.items()}
    audit['transported']=sum(k in passed for k in transports.values())
    assert len(transports)==audit['transported']
    lean.write(a.experiment/'audit.json',audit)
    print(json.dumps(audit))


if __name__=='__main__':
    main()
