#!/usr/bin/env python3
"""Reconstruct scope-only edits, original rejections and every ablation verdict."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def rows(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['run','original-run','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();r=a.run;o=a.original_run
    import interface_discovery_pilot as instrument
    manifest=json.loads((r/'manifest.json').read_text())
    assert sha(r/'proposals.json')==manifest['proposal_sha256']
    for name,h in manifest['input_sha256'].items():assert sha(o/name)==h
    proposals=json.loads((r/'proposals.json').read_text())
    original={x['id']:x for x in rows(o/'evaluation/base.jsonl')}
    old_checks={x['id']:x for x in rows(o/'judgments/verdicts.jsonl')}
    sources={};checks={}
    for phase in ['primary','ablation']:
        ps=json.loads((r/(phase+'-sources.json')).read_text());vs=rows(r/(phase+'-verdicts.jsonl'))
        assert len(ps)==len(vs)==len({x['id'] for x in ps})==len({x['id'] for x in vs})
        assert {x['id'] for x in ps}=={x['id'] for x in vs}
        for x in ps:assert digest(x['code'])==x['id'];sources[x['id']]=x['code']
        for v in vs:
            assert v['code_sha256']==v['id']
            if v['accepted']:
                assert v['lean_complete'] and v['axiom_audit_found'] and not v.get('system_errors')
                assert set(v['axioms'])<={'propext','Classical.choice','Quot.sound'}
            checks[v['id']]=v
    accepted=[];expected_ablations={}
    for x in proposals:
        raw=original[x['id']];body,error=instrument.completion_code(raw['text'])
        assert body==x['original_body'] and raw['target']==x['target']
        prefix=instrument.HEADER+x['statement'];suffix='\n#print axioms '+x['theorem']+'\n'
        if not error:
            key=digest(prefix+body+suffix);assert key==x['original_code_sha256']
            assert not old_checks[key]['accepted'] and not old_checks[key].get('system_errors')
        if x['skip_reason']:continue
        clause=' generalizing '+' '.join(x['variables'])
        assert x['repaired_body'].count(clause)==1
        assert x['repaired_body'].replace(clause,'',1)==body
        fixed=prefix+x['repaired_body']+suffix;key=digest(fixed)
        assert sources[key]==fixed
        if not checks[key]['accepted']:continue
        accepted.append(x)
        for omitted in x['variables']:
            kept=[v for v in x['variables'] if v!=omitted]
            replacement=' generalizing '+' '.join(kept) if kept else ''
            text=prefix+x['repaired_body'].replace(clause,replacement,1)+suffix
            expected_ablations[x['id'],omitted]=(digest(text),text)
    edges=json.loads((r/'ablation-edges.json').read_text())
    assert len(edges)==len(expected_ablations)
    for e in edges:
        key,text=expected_ablations.pop((e['proposal_id'],e['omitted']))
        assert key==e['code_sha256']
        if e['reused_original']:assert key in old_checks and not old_checks[key]['accepted']
        else:assert sources[key]==text
    assert not expected_ablations
    analysis=json.loads((r/'analysis.json').read_text())
    assert len(analysis['rows'])==len(proposals)==256
    accepted_ids={x['id'] for x in accepted}
    assert {x['id'] for x in analysis['rows'] if x['accepted']}==accepted_ids
    assert analysis['accepted_proposals']==len(accepted)
    assert analysis['accepted_roots']==sorted({x['target'] for x in accepted})
    assert analysis['accepted_schemas']==sorted({x['family'] for x in accepted})
    distinct=len({x['repaired_body'] for x in accepted})
    unresolved=sum(bool(v.get('system_errors')) for v in checks.values())
    assert analysis['distinct_repaired_bodies']==distinct and analysis['unresolved_physical_checks']==unresolved
    for row in analysis['rows']:
        es=[e for e in edges if e['proposal_id']==row['id']]
        assert len(row['ablations'])==len(es)
        for e,v in zip(es,row['ablations']):
            check=old_checks[e['code_sha256']] if e['reused_original'] else checks[e['code_sha256']]
            assert v['accepted']==check['accepted'] and v['unresolved']==bool(check.get('system_errors'))
    assert analysis['training_feasibility_gate']==(distinct>=4 and len({x['family'] for x in accepted})>=2 and unresolved==0)
    result=dict(passed=True,original_proposals=256,scope_only_repairs=manifest['eligible'],
        accepted_repairs=len(accepted),accepted_schemas=analysis['accepted_schemas'],
        primary_and_ablation_physical_checks=len(checks),unresolved_checks=unresolved,
        training_feasibility_gate=analysis['training_feasibility_gate'],analysis_sha256=sha(r/'analysis.json'))
    with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result))


if __name__=='__main__':main()
