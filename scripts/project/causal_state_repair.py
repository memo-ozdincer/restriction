#!/usr/bin/env python3
"""Counterfactual scope repair of every saved base attempt on the old roots."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import time

try:
    from . import interface_discovery_pilot as lean
except ImportError:
    import interface_discovery_pilot as lean

MATCH = re.compile(r"(?m)^[ \t]*induction(?P<prime>')?[ \t]+n(?=$|[ \t;<])")


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def lift(body, variables):
    if not variables: return body, None
    if '/-' in body: return None, 'block_comment'
    if re.search(r'\bgeneralizing\b',body): return None, 'already_generalized'
    matches=list(MATCH.finditer(body))
    if len(matches)!=1: return None, 'induction_match_count_'+str(len(matches))
    m=matches[0]
    end=body.find('\n',m.end())
    if end<0:end=len(body)
    rest=body[m.end():end].strip()
    position=m.end()
    if m['prime'] and rest.startswith('with '):
        if not re.fullmatch(r"with[ \t]+[A-Za-z_][\w']*(?:[ \t]+[A-Za-z_][\w']*)*",rest):
            return None,'unsupported_prime_case_binders'
        position=end
    elif rest and not (rest.startswith('<;>') or rest.startswith(';') or
                       (not m['prime'] and re.match(r'with\b',rest))):
        return None,'unsupported_induction_syntax'
    return body[:position]+' generalizing '+' '.join(variables)+body[position:],None


def prepare(a):
    a.output.mkdir(exist_ok=False,parents=True)
    panel=json.loads((a.panel/'evaluation-tasks.json').read_text())
    tasks={r['id']:r for r in panel if r['id'].startswith('pt_')}
    assert len(tasks)==16
    raw=[r for r in lean.rows(a.run/'evaluation/base.jsonl') if r['target'] in tasks]
    assert len(raw)==256 and {r['id'] for r in raw}=={f'base/{t}/{i}' for t in tasks for i in range(16)}
    audit=json.loads((a.run/'independent-audit.json').read_text())
    assert audit['passed'] and audit['analysis_sha256']==sha(a.run/'judgments/analysis.json')
    edges={r['id']:r for r in json.loads((a.run/'judgments/edges.json').read_text())}
    checked={r['id']:r for r in lean.rows(a.run/'judgments/verdicts.jsonl')}
    proposals=[]
    for r in raw:
        task=tasks[r['target']]
        assert r['prompt']==lean.PREFIX+lean.HEADER+task['statement']
        body,error=lean.completion_code(r['text'])
        e=edges[r['id']]
        original=lean.HEADER+task['statement']+(body or '')+'\n#print axioms '+task['theorem']+'\n'
        digest=lean.sha(original) if not error else None
        assert e['code_sha256']==digest and e['parse_error']==error
        v=checked.get(digest)
        assert error or (v and not v['accepted'] and not v.get('system_errors') and v['code_sha256']==digest)
        variables=['x'] if task['family'].startswith('rational_updates/') else ['a','b','c','d']
        changed,reason=lift(body,variables) if not error else (None,error)
        record=dict(id=r['id'],target=task['id'],family=task['family'],original_body=body,
            original_code_sha256=digest,original_rejected=True,variables=variables,skip_reason=reason,
            statement=task['statement'],theorem=task['theorem'],repaired_body=changed)
        proposals.append(record)
    lean.write(a.output/'proposals.json',proposals)
    lean.write(a.output/'manifest.json',dict(source_sha256=sha(Path(__file__)),instrument_sha256=sha(Path(lean.__file__)),
        input_sha256={str(p.relative_to(a.run)):sha(p) for p in [a.run/'evaluation/base.jsonl',
            a.run/'independent-audit.json',a.run/'judgments/analysis.json',a.run/'judgments/edges.json',a.run/'judgments/verdicts.jsonl']},
        panel_manifest_sha256=sha(a.panel/'manifest.json'),proposal_sha256=sha(a.output/'proposals.json'),
        source_proposals=256,eligible=sum(not r['skip_reason'] for r in proposals),
        skips=dict(Counter(r['skip_reason'] for r in proposals if r['skip_reason'])),
        scope='Post-hoc inspected-root causal diagnosis; no new sampling or training',
        verifier_seconds=60,workers=8,maximum_primary_logical_checks=256,maximum_ablation_logical_checks=1024,
        training_gate=dict(distinct_bodies=4,distinct_schemas=2,unresolved=0)))


def authenticate(directory):
    m=json.loads((directory/'manifest.json').read_text())
    assert m['source_sha256']==sha(Path(__file__)) and m['instrument_sha256']==sha(Path(lean.__file__))
    assert m['proposal_sha256']==sha(directory/'proposals.json')
    return m,json.loads((directory/'proposals.json').read_text())


def code(row,body):
    return lean.HEADER+row['statement']+body+'\n#print axioms '+row['theorem']+'\n'


def execute(a):
    manifest,proposals=authenticate(a.output)
    assert not (a.output/'primary-verdicts.jsonl').exists()
    sys.path.insert(0,str(a.bundle/'verifier/DeepSeek-Prover-V1.5'))
    from prover.lean.verifier import verify_lean4_file
    warm=verify_lean4_file('import Mathlib\nimport Aesop\ntheorem warmup : True := by trivial\n',
        lake_path=str(a.bundle/'lean/elan/bin/lake'),lean_workspace=str(a.bundle/'verifier/DeepSeek-Prover-V1.5/mathlib4'),timeout=300)
    lean.write(a.output/'warmup.json',warm)
    if not warm.get('complete'):raise RuntimeError('Warmup failed')
    started=time.time()
    def job(source):
        return dict(id=lean.sha(source),code=source,verifier=str(a.bundle/'verifier/DeepSeek-Prover-V1.5'),
                    lake=str(a.bundle/'lean/elan/bin/lake'))
    unique={}
    for row in proposals:
        if not row['skip_reason']:
            j=job(code(row,row['repaired_body']));unique[j['id']]=j
    lean.write(a.output/'primary-sources.json',list(unique.values()))
    checked={r['id']:r for r in lean.verify_jobs(list(unique.values()),a.output/'primary-verdicts.jsonl',workers=8)}
    accepted=[r for r in proposals if not r['skip_reason'] and checked[lean.sha(code(r,r['repaired_body']))]['accepted']]
    ablations=[];unique_ablation={}
    for row in accepted:
        for variable in row['variables']:
            remaining=[v for v in row['variables'] if v!=variable]
            body,reason=lift(row['original_body'],remaining);assert reason is None
            source=code(row,body);key=lean.sha(source)
            reused=key==row['original_code_sha256']
            if not reused and key not in checked:unique_ablation[key]=job(source)
            ablations.append(dict(proposal_id=row['id'],omitted=variable,code_sha256=key,reused_original=reused))
    lean.write(a.output/'ablation-edges.json',ablations)
    lean.write(a.output/'ablation-sources.json',list(unique_ablation.values()))
    ablation_checked={r['id']:r for r in lean.verify_jobs(list(unique_ablation.values()),a.output/'ablation-verdicts.jsonl',workers=8)}
    verdicts=checked|ablation_checked
    result_rows=[]
    for row in proposals:
        v=checked.get(lean.sha(code(row,row['repaired_body']))) if not row['skip_reason'] else None
        dropouts=[]
        for edge in [e for e in ablations if e['proposal_id']==row['id']]:
            other=verdicts.get(edge['code_sha256'])
            dropouts.append(dict(**edge,accepted=False if edge['reused_original'] else other['accepted'],
                unresolved=False if edge['reused_original'] else bool(other.get('system_errors'))))
        result_rows.append(dict(id=row['id'],target=row['target'],family=row['family'],skip_reason=row['skip_reason'],
            accepted=bool(v and v['accepted']),unresolved=bool(v and v.get('system_errors')),ablations=dropouts))
    schemas=sorted({r['family'] for r in accepted});bodies={r['repaired_body'] for r in accepted}
    unresolved=sum(bool(v.get('system_errors')) for v in verdicts.values())
    lean.write(a.output/'analysis.json',dict(rows=result_rows,source_proposals=256,eligible=manifest['eligible'],
        accepted_proposals=len(accepted),accepted_roots=sorted({r['target'] for r in accepted}),accepted_schemas=schemas,
        distinct_repaired_bodies=len(bodies),primary_physical_checks=len(checked),ablation_logical_checks=len(ablations),
        ablation_physical_checks=len(ablation_checked),unresolved_physical_checks=unresolved,
        training_feasibility_gate=len(bodies)>=4 and len(schemas)>=2 and unresolved==0,
        elapsed_seconds=time.time()-started,new_model_proposals=0,parameter_updates=0,
        claim_scope=manifest['scope']))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['prepare','execute'])
    for name in ['run','panel','bundle','output']:p.add_argument('--'+name,type=Path)
    a=p.parse_args();globals()[a.mode](a)


if __name__=='__main__':main()
