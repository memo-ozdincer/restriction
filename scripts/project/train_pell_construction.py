"""Matched expression/literal Pell supervision and verified transfer across proof interfaces."""
import argparse
import json
from pathlib import Path
import time

import interface_discovery_pilot as lean
import run_policy_improvement as runtime
from compiler_credit_objective import loss_terms
from policy_update_math import response_log_probs
from run_compiler_credit import probe

UNITS={2:(3,2),3:(2,1),5:(9,4),7:(8,3),6:(5,2),10:(19,6)}
NAMES=('pellD','genX','genY','seedX','seedY')
ALIASES=('radicand','unitFirst','unitSecond','currentFirst','currentSecond')


def task(d,level,surface):
    a,b=UNITS[d]
    chain=[(1,0),(a,b)]
    for _ in range(level):
        u,v=chain[-1]
        chain.append((a*u+d*b*v,b*u+a*v))
    u,v=chain[level-1]
    x,y=chain[level]
    blocked=[c for c,_ in chain[:level]]
    names=ALIASES if surface=='renamed' else NAMES
    order=(4,0,1,3,2) if surface=='renamed' else range(5)
    vals=(d,a,b,u,v)
    definitions='' if surface=='bare' else ''.join(f'def {names[i]} : ℤ := {vals[i]}\n' for i in order)+'\n'
    equation=f'x^2 - {d}*y^2 = 1'
    statement=definitions+'theorem target : ∃ x y : ℤ, '+' ∧ '.join([equation]+[f'x.natAbs ≠ {q}' for q in blocked])+' := by\n'
    radical,gx,gy,sx,sy=names
    tactic='\n  norm_num'+(' ['+', '.join(names)+']' if definitions else '')
    literal=f'  use {x}, {y}'+tactic
    expr=f'  use {gx}*{sx}+{radical}*{gy}*{sy}, {gy}*{sx}+{gx}*{sy}'+tactic
    assert x*x-d*y*y==1 and x not in blocked
    return dict(id=f'd{d}-level{level}-{surface}',statement=statement,answer=[x,y],literal=literal,
                expression=expr if definitions else None,blocked=blocked)


def panel():
    train=[task(d,n,'named') for d in (2,3,5,7) for n in (2,3)]
    test=[task(6,2,'named')]+[task(d,3,s) for d in (6,10) for s in ('named','renamed','bare')]
    return train,test


def prepare(a):
    train,test=panel()
    lean.write(a.out/'train.json',train)
    lean.write(a.out/'test.json',test)
    jobs=[]
    for t in train+test:
        for kind in ('literal','expression','invalid'):
            body='  exact ⟨1,0, by norm_num⟩' if kind=='invalid' else t[kind]
            if body is None:
                continue
            code=lean.HEADER+t['statement']+body+'\n#print axioms target'
            jobs.append(dict(id=t['id']+'/'+kind,code=code,lake=str(a.bundle/'lean/elan/bin/lake'),
                             verifier=str(a.bundle/'verifier/DeepSeek-Prover-V1.5')))
    vs=lean.verify_jobs(jobs,a.out/'panel-checks.jsonl',workers=4)
    assert all(not v.get('system_errors') and v['accepted'] != v['id'].endswith('/invalid') for v in vs)
    lean.write(a.out/'panel-ready.json',dict(checks=len(vs),passed=True))


def run(a):
    import torch
    train,test=panel()
    assert json.loads((a.out/'panel-ready.json').read_text())['passed']
    assert train==json.loads((a.out/'train.json').read_text()) and test==json.loads((a.out/'test.json').read_text())
    target=a.out/a.arm
    target.mkdir()
    model,tok=runtime.load_model(a.bundle,a.bundle/'models/c1-final')
    if a.arm!='base':
        records=[]
        for t in train:
            prompt=lean.PREFIX+lean.HEADER+t['statement']
            response=t[a.arm]+'\n```'
            tokens=tok.encode(response,add_special_tokens=False)
            assert tok.decode(tokens,skip_special_tokens=True)==response
            records.append(dict(id=t['id'],prompt_token_ids=tok.encode(prompt),response_token_ids=tokens))
        lean.write(target/'tokens.json',records)
        refs=probe(model,records)
        model=runtime.add_adapter(model)
        assert probe(model,records)==refs
        params=[p for p in model.parameters() if p.requires_grad]
        optimizer=torch.optim.AdamW(params,lr=1e-4,weight_decay=0.)
        model.eval()
        with (target/'metrics.jsonl').open('x') as stream:
            for step in range(32):
                idx=step%len(records)
                r=records[idx]
                optimizer.zero_grad(set_to_none=True)
                lp=response_log_probs(model,r['prompt_token_ids'],r['response_token_ids'],'cuda')
                ref=torch.tensor(refs[idx],device='cuda',dtype=lp.dtype)
                loss,nll,anchor=loss_terms(lp,ref,torch.ones_like(lp))
                loss.backward()
                grad=torch.nn.utils.clip_grad_norm_(params,1.,error_if_nonfinite=True)
                optimizer.step()
                runtime.append(stream,dict(step=step+1,id=r['id'],nll=float(nll.detach()),anchor=float(anchor.detach()),norm=float(grad),tokens=len(lp)))
        final=probe(model,records)
        assert final!=refs
        with model.disable_adapter():
            assert probe(model,records)==refs
        lean.write(target/'reload-probes.json',final)
        model.save_pretrained(target/'adapter',safe_serialization=True)
    samples=[]
    for t in test:
        prompt=lean.PREFIX+lean.HEADER+t['statement']
        seed=20261203+int(lean.sha(t['id'].rsplit('-',1)[0])[:6],16)
        rows=runtime.sample(model,tok,prompt,seed,256,False)
        lean.write(target/(t['id']+'.json'),dict(prompt=prompt,rows=rows))
        samples.append(t['id'])
    lean.write(target/'complete.json',dict(arm=a.arm,tasks=samples))


def verify(a):
    _,test=panel()
    jobs={}
    edges=[]
    for arm in ('base','literal','expression'):
        assert json.loads((a.out/arm/'complete.json').read_text())['tasks']==[t['id'] for t in test]
        for t in test:
            batch=json.loads((a.out/arm/(t['id']+'.json')).read_text())
            source=lean.HEADER+t['statement']
            assert batch['prompt']==lean.PREFIX+source and len(batch['rows'])==16
            for i,row in enumerate(batch['rows']):
                assert row['sample_index']==i
                body,error=lean.completion_code(row['text'])
                key=None
                if not error:
                    code=source+body+'\n#print axioms target'
                    key=lean.sha(code)
                    jobs[key]=dict(id=key,code=code,lake=str(a.bundle/'lean/elan/bin/lake'),
                                   verifier=str(a.bundle/'verifier/DeepSeek-Prover-V1.5'))
                edges.append(dict(arm=arm,task=t['id'],index=i,key=key,error=error))
    lean.write(a.out/'edges.json',edges)
    lean.write(a.out/'sources.json',{k:v['code'] for k,v in jobs.items()})
    vs=lean.verify_jobs(list(jobs.values()),a.out/'verdicts.jsonl',workers=8)
    checked={v['id']:v for v in vs}
    result={}
    for row in edges:
        v=checked.get(row['key'],{})
        cell=result.setdefault(row['arm'],{}).setdefault(row['task'],dict(accepted=0,unresolved=0,parse_errors=0))
        cell['accepted']+=int(bool(v.get('accepted')))
        cell['unresolved']+=int(bool(v.get('system_errors')))
        cell['parse_errors']+=int(bool(row['error']))
    lean.write(a.out/'results.json',result)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=('prepare','run','verify'))
    p.add_argument('bundle',type=Path)
    p.add_argument('out',type=Path)
    p.add_argument('--arm',choices=('base','literal','expression'))
    args=p.parse_args()
    {'prepare':prepare,'run':run,'verify':verify}[args.mode](args)
