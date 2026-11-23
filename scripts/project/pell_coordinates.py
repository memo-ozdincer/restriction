"""Cross frozen and fresh proof bodies with equivalent Pell witness coordinates."""
import argparse
import json
from pathlib import Path
import interface_discovery_pilot as lean
import run_policy_improvement as policy
from probe_pell_witnesses import NAME

DEFS = '''def advance (x y : ℤ) : ℤ × ℤ := (5*x+12*y, 2*x+5*y)
def retreat (x y : ℤ) : ℤ × ℤ := (5*x-12*y, -2*x+5*y)

'''
X = dict(direct='x',menu='x',forward='(5*x+12*y)',inverse='(5*x-12*y)')


def source(arm):
    x=X[arm]
    return (lean.HEADER+(DEFS if arm=='menu' else '')+
            f'theorem {NAME} : ∃ x y : ℤ, x^2 - 6*y^2 = 1 ∧ {x}.natAbs ≠ 1 ∧ {x}.natAbs ≠ 5   := by\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('bundle',type=Path)
    p.add_argument('out',type=Path)
    p.add_argument('--replay',type=Path)
    a=p.parse_args()
    jobs={}
    cells={}
    if not a.replay:
        model,tok=policy.load_model(a.bundle,a.bundle/'models/c1-final')
    for arm in X:
        if a.replay and arm=='menu':
            continue
        prompt=lean.PREFIX+source(arm)
        if a.replay:
            batches={g:json.loads((a.replay/g/'samples.json').read_text())['rows']
                     for g in ('plain-2','blocked-2')}
        else:
            rows=policy.sample(model,tok,prompt,20261201,512,False)
            lean.write(a.out/(arm+'.json'),dict(prompt=prompt,rows=rows))
            batches={'fresh':rows}
        for group,rows in batches.items():
            records=[]
            for r in rows:
                body,error=lean.completion_code(r['text'])
                key=None
                if not error:
                    code=source(arm)+body+'\n#print axioms '+NAME
                    key=lean.sha(code)
                    jobs[key]=dict(id=key,code=code,lake=str(a.bundle/'lean/elan/bin/lake'),
                                   verifier=str(a.bundle/'verifier/DeepSeek-Prover-V1.5'))
                records.append(dict(index=r['sample_index'],key=key,error=error))
            cells[group+'/'+arm]=records
    lean.write(a.out/'sources.json',{k:v['code'] for k,v in jobs.items()})
    lean.write(a.out/'cells.json',cells)
    vs=lean.verify_jobs(list(jobs.values()),a.out/'verdicts.jsonl',workers=4)
    assert all(not v.get('system_errors') for v in vs)
    accepted={v['id'] for v in vs if v['accepted']}
    lean.write(a.out/'summary.json',{cell:sum(r['key'] in accepted for r in rows) for cell,rows in cells.items()})


if __name__=='__main__':
    main()
