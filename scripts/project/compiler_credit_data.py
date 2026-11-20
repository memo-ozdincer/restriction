#!/usr/bin/env python3
"""Prepare verified compiler-derived demonstrations and untouched fresh root tasks."""
import argparse
import json
from pathlib import Path
import sys
import interface_discovery_pilot as lean
from archive_policy_update_training import sha


CONFIG = dict(arms=['full', 'mapped', 'rotated'], epochs=10, optimizer_steps=80,
    learning_rate=1e-4, anchor_coefficient=.02, gradient_clip=1., evaluation_seed=20261124,
    samples_per_task=16, max_response_tokens=512, adapter_seed=20261120,
    maximum_allocation_seconds=7200, claim_scope='Off-policy compiler-derived supervision; scaffold-free related-task evaluation')


def invariant(op):
    call=f'({op} n a b c d)'
    return f'{call}.1*{call}.2.2.2 - {call}.2.1*{call}.2.2.1 = a*d-b*c'


def fresh():
    variants=[('constant',1,4),('constant',4,1),('reverse',1,3),('reverse',4,2),
              ('time',2,1),('time',1,3),('rotation',2,1),('rotation',1,3)]
    tasks=[]; witnesses={}
    for i,(kind,k,l) in enumerate(variants):
        op=f'evolve_{i:02d}'
        kk=f'((n : Int)+{k})' if kind=='time' else str(k)
        aa=f'(a+{kk}*c)';bb=f'(b+{kk}*d)'
        cc=f'(c+{l}*{aa})';dd=f'(d+{l}*{bb})'
        if kind=='reverse':
            cc=f'(c+{l}*a)';dd=f'(d+{l}*b)';aa=f'(a+{k}*{cc})';bb=f'(b+{k}*{dd})'
        if kind=='rotation': aa,bb,cc,dd=cc,dd,f'(-{aa})',f'(-{bb})'
        definition=f'def {op} : Nat → Int → Int → Int → Int → Int × Int × Int × Int\n  | 0, a, b, c, d => (a,b,c,d)\n  | n+1, a, b, c, d => {op} n {aa} {bb} {cc} {dd}\n\n'
        inv=invariant(op);call=f'({op} n a b c d)'
        # Authoring-only witnesses are never included in train/evaluation records.
        proof=f'  induction n generalizing a b c d with\n  | zero => simp [{op}]\n  | succ n ih =>\n    rw [{op}, ih]\n    ring\n'
        lemma=f'  have cert (n : Nat) (a b c d : Int) : {inv} := by\n'+''.join('  '+s+'\n' for s in proof.splitlines())
        for schema in ['invariant','nonzero','witness']:
            tid=f'fresh_{i:02d}_{schema}';h='';goal=inv;body=proof
            if schema=='nonzero':
                h=' (h : a*d-b*c ≠ 0)';goal=f'{call}.1 ≠ 0 ∨ {call}.2.1 ≠ 0'
                body=lemma+'  have hc := cert n a b c d\n  by_contra hn\n  push_neg at hn\n  rcases hn with ⟨ha,hb⟩\n  apply h\n  simpa only [ha,hb,zero_mul,sub_zero] using hc.symm\n'
            if schema=='witness':
                h=' (h : a*d-b*c = 1)';goal=f'∃ u v : Int, u*{call}.1+v*{call}.2.1 = 1'
                body=lemma+f'  refine ⟨{call}.2.2.2, -{call}.2.2.1, ?_⟩\n  have hc := cert n a b c d\n  nlinarith [hc]\n'
            statement=definition+f'theorem target (n : Nat) (a b c d : Int){h} :\n    {goal} := by\n'
            tasks.append(dict(id=tid,statement=statement,theorem='target',split='composition',family=schema,transition=kind))
            witnesses[tid]=body
    return tasks,witnesses


def prepare(a):
    b=a.bundle;repair=b/'runs/causal-state-repair-20261119'
    assert json.loads((repair/'independent-audit.json').read_text())['passed']
    panel=b/'runs/repaired-library-panel-20261119-final'
    assert sha(panel/'manifest.json')=='a2130075a8b0dd7bf6728fa0be9865722755c5504f1a79e4ac2d83aa5a4f4cf6'
    records={x['id']:x for x in json.loads((panel/'records.json').read_text())}
    props={x['id']:x for x in json.loads((repair/'proposals.json').read_text())}
    composed=b/'runs/typed-procedure-composition-20261119-runtime-fixed'
    assert json.loads((composed/'independent-audit.json').read_text())['explicit_successes']==4
    trace=json.loads((composed/'constructor-origin.json').read_text())
    cb,error=lean.completion_code(trace['text']);assert error is None
    constructor='have witness_constructor'+trace['prompt'].split('theorem target',1)[1]+cb+'\n'
    train=[]
    for i in range(4):
        rec=records[f'pt_{i+8:02d}/linked'];producer=props[rec['producer_id']]
        for kind in ['invariant','witness']:
            if kind=='invariant':
                statement=producer['statement'];body=producer['repaired_body'];theorem=f'pt_{i:02d}'
            else:
                statement=rec['definition']+rec['target_theorem'];theorem=rec['target']
                inv=rec['library'].replace('theorem linked_contract','have linked_contract',1)
                body=''.join('  '+s+'\n' for s in (inv+constructor).splitlines())
                body+='  exact witness_constructor _ _ _ _ (Eq.trans (linked_contract n a b c d) h)\n'
            spans=[]
            for label,needle in [('binding','generalizing a b c d')]+([
                ('constructor',cb.strip()),('connection','exact witness_constructor _ _ _ _ (Eq.trans (linked_contract n a b c d) h)')]
                if kind=='witness' else []):
                assert body.count(needle)==1;start=body.index(needle)
                spans.append(dict(label=label,start=start,end=start+len(needle)))
            train.append(dict(id=f'train_{i:02d}_{kind}',statement=statement,theorem=theorem,body=body,
                spans=spans,producer_id=producer['id'],constructor_id=trace['id'] if kind=='witness' else None))
    tasks,witnesses=fresh()
    old=json.loads((b/'runs/policy-improvement-panel-20261119-fp32/train-tasks.json').read_text())
    retention=[dict(x,transition='retention') for x in old]
    assert len(retention)==20 and all(x['split']=='retention' for x in retention)
    a.output.mkdir(parents=True,exist_ok=False)
    for name,data in [('train.json',train),('evaluation.json',tasks+retention),('authoring-witnesses.json',witnesses),('config.json',CONFIG)]:lean.write(a.output/name,data)
    inputs=[repair/'proposals.json',panel/'records.json',composed/'constructor-origin.json',composed/'independent-audit.json']
    lean.write(a.output/'manifest.json',dict(source_sha256=sha(Path(__file__)),
        files={n:sha(a.output/n) for n in ['train.json','evaluation.json','authoring-witnesses.json','config.json']},
        input_sha256={str(p.relative_to(b)):sha(p) for p in inputs},train_examples=8,fresh_roots=24,retention_roots=20))


def authenticate(panel):
    m=json.loads((panel/'manifest.json').read_text());assert sha(Path(__file__))==m['source_sha256']
    for n,h in m['files'].items():assert sha(panel/n)==h
    assert json.loads((panel/'config.json').read_text())==CONFIG
    return m


def validate(a):
    authenticate(a.output);jobs=[];expected={}
    train=json.loads((a.output/'train.json').read_text());tasks=json.loads((a.output/'evaluation.json').read_text())
    witnesses=json.loads((a.output/'authoring-witnesses.json').read_text())
    for x in train+[x for x in tasks if x['split']=='composition']:
        body=x['body'] if 'body' in x else witnesses[x['id']]
        for suffix,proof,accept in [('positive',body,True),('empty','',False)]:
            key=x['id']+'/'+suffix;expected[key]=accept
            jobs.append(dict(id=key,code=lean.HEADER+x['statement']+proof+'\n#print axioms '+x['theorem']+'\n',
                verifier=str(a.bundle/'verifier/DeepSeek-Prover-V1.5'),lake=str(a.bundle/'lean/elan/bin/lake')))
    jobs.append(dict(jobs[0],id='invalid',code=lean.HEADER+'theorem target : False := by sorry\n#print axioms target\n'));expected['invalid']=False
    sys.path.insert(0,str(a.bundle/'verifier/DeepSeek-Prover-V1.5'))
    from prover.lean.verifier import verify_lean4_file
    warm=verify_lean4_file('import Mathlib\nimport Aesop\nopen BigOperators\ntheorem warm (x : Int) : x+0=x := by ring\n',
        lake_path=str(a.bundle/'lean/elan/bin/lake'),lean_workspace=str(a.bundle/'verifier/DeepSeek-Prover-V1.5/mathlib4'),timeout=300)
    lean.write(a.output/'warmup.json',warm);assert warm.get('complete')
    lean.write(a.output/'validation-sources.json',jobs)
    checked=lean.verify_jobs(jobs,a.output/'validation.jsonl',workers=2)
    result=dict(passed=len(checked)==65 and all(v['accepted']==expected[v['id']] and not v.get('system_errors') for v in checked),
        checks=len(checked),errors=[v['id'] for v in checked if v['accepted']!=expected[v['id']] or v.get('system_errors')])
    lean.write(a.output/'validation-summary.json',result);print(json.dumps(result))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['prepare','validate'])
    for n in ['bundle','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();globals()[a.mode](a)
