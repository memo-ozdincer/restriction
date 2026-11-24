"""Separate the name and declaration-order changes in the held-out Pell interface."""
import argparse
import json
from pathlib import Path
from train_pell_construction import ALIASES, NAMES, lean, panel, probe, runtime


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('bundle',type=Path)
    p.add_argument('out',type=Path)
    a=p.parse_args()
    prior=a.bundle/'runs/pell-training-20261123-1399226/expression'
    model,tok=runtime.load_model(a.bundle,a.bundle/'models/c1-final')
    model=runtime.add_adapter(model,prior/'adapter')
    expected=json.loads((prior/'reload-probes.json').read_text())
    actual=probe(model,json.loads((prior/'tokens.json').read_text()))
    assert [len(x) for x in actual]==[len(x) for x in expected]
    diff=max(abs(v-w) for x,y in zip(actual,expected) for v,w in zip(x,y))
    assert diff<=1e-4
    jobs={}
    cells={}
    for t in panel()[1]:
        if t['id'] not in ('d6-level3-named','d10-level3-named'):
            continue
        decl,root=t['statement'].split('\n\n')
        lines=decl.splitlines()
        for arm in ('rename_only','reorder_only'):
            if arm=='rename_only':
                changes=[line.replace(old,new) for line,old,new in zip(lines,NAMES,ALIASES,strict=True)]
            else:
                changes=[lines[i] for i in (4,0,1,3,2)]
            source=lean.HEADER+'\n'.join(changes)+'\n\n'+root
            prefix=t['id'].rsplit('-',1)[0]
            seed=20261203+int(lean.sha(prefix)[:6],16)
            cell=prefix+'-'+arm
            rows=runtime.sample(model,tok,lean.PREFIX+source,seed,256,False)
            lean.write(a.out/(cell+'.json'),dict(prompt=lean.PREFIX+source,rows=rows))
            cells[cell]=[]
            for row in rows:
                body,error=lean.completion_code(row['text'])
                key=None
                if not error:
                    code=source+body+'\n#print axioms target';key=lean.sha(code)
                    jobs[key]=dict(id=key,code=code,lake=str(a.bundle/'lean/elan/bin/lake'),verifier=str(a.bundle/'verifier/DeepSeek-Prover-V1.5'))
                cells[cell].append(dict(index=row['sample_index'],key=key,error=error))
    lean.write(a.out/'cells.json',cells)
    lean.write(a.out/'sources.json',{k:v['code'] for k,v in jobs.items()})
    vs=lean.verify_jobs(list(jobs.values()),a.out/'verdicts.jsonl',workers=6)
    assert all(not v.get('system_errors') for v in vs)
    ok={v['id'] for v in vs if v['accepted']}
    lean.write(a.out/'audit.json',dict(reload_max_abs=diff,counts={n:sum(r['key'] in ok for r in rs) for n,rs in cells.items()}))


if __name__=='__main__':
    main()
