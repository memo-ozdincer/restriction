"""Factor the failure of fixed bridge completions into context and preceding tactics."""
import argparse
import json
from pathlib import Path
import re

from run_collision_hint import lean, HEADER, BRIDGE


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('bundle',type=Path)
    p.add_argument('source',type=Path)
    p.add_argument('out',type=Path)
    p.add_argument('--finish',action='store_true',help='finish an existing check from the saved verdicts')
    a=p.parse_args()
    general=(a.source/'bridge-witness.txt').read_text().split('  have h := total U hu')[0]
    states=dict(empty='',irrelevant='  have hu0 : (∑ x in U, x) = ∑ x in U, x := rfl\n'
                '  have hv0 : (∑ x in V, x) = ∑ x in V, x := rfl\n',
                general=general, instances=general+'  have left_total := total U hu\n  have right_total := total V hv\n')
    jobs={}
    def add(state,body):
        code=HEADER+BRIDGE+states[state]+body+'\n#print axioms target'
        key=lean.sha(code)
        jobs[key]=dict(id=key,code=code,lake=str(a.bundle/'lean/elan/bin/lake'),
                       verifier=str(a.bundle/'verifier/DeepSeek-Prover-V1.5'))
        return key
    controls={s:{'open':add(s,'  skip'),'arithmetic':add(s,'  omega')} for s in states}
    rows=[]
    for arm in ('plain','hint'):
        for r in json.loads((a.source/f'bridge-{arm}.json').read_text())['rows']:
            body,error=lean.completion_code(r['text'])
            keys={}
            terminal=None
            if not error:
                lines=[l for l in body.splitlines() if l.strip() and not l.lstrip().startswith('--')]
                last=lines[-1] if lines else ''
                if re.match(r'^  (?:linarith|nlinarith|omega|aesop|simp(?:_all)?|ring(?:_nf)?|rfl|exact|simpa|assumption|norm_num)\b',last):
                    terminal=last
                for s in states:
                    keys[s]={'whole':add(s,body)}
                    if terminal:
                        keys[s]['terminal']=add(s,terminal)
            rows.append(dict(arm=arm,index=r['sample_index'],parse_error=error,terminal=terminal,keys=keys))
    lean.write(a.out/'mapping.json',dict(rows=rows,controls=controls))
    lean.write(a.out/'sources.json',{k:v['code'] for k,v in jobs.items()})
    primary=a.out/'verdicts.jsonl'
    verdicts=lean.rows(primary) if a.finish else lean.verify_jobs(list(jobs.values()),primary,workers=6)
    assert len(verdicts)==len(jobs) and {v['id'] for v in verdicts}==set(jobs)
    latest={v['id']:v for v in verdicts}
    retry_jobs=[jobs[k] for k,v in latest.items() if v.get('system_errors')]
    if retry_jobs:
        retry_path=a.out/'retry.jsonl'
        retry=lean.rows(retry_path) if retry_path.exists() else lean.verify_jobs(retry_jobs,retry_path,workers=1)
        assert {v['id'] for v in retry}=={j['id'] for j in retry_jobs}
        latest.update({v['id']:v for v in retry})
    verdicts=list(latest.values())
    unresolved={v['id'] for v in verdicts if v.get('system_errors')}
    accepted={v['id'] for v in verdicts if v['accepted']}
    assert not any(v['open'] in accepted for v in controls.values())
    totals={s:{kind:sum(r['keys'].get(s,{}).get(kind) in accepted for r in rows)
               for kind in ('whole','terminal')} for s in states}
    lean.write(a.out/'summary.json',dict(proposals=len(rows),parseable=sum(not r['parse_error'] for r in rows),
        extracted=sum(bool(r['terminal']) for r in rows),unique_sources=len(verdicts),physical_checks=len(verdicts)+len(retry_jobs),unresolved=sorted(unresolved),totals=totals,
        omega={s:v['arithmetic'] in accepted for s,v in controls.items()}))


if __name__=='__main__':
    main()
