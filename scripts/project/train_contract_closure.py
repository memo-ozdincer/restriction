"""Learn from executable versus abstract-contract closure of a failed program."""
import argparse
import json
from pathlib import Path
import re
import textwrap
import interface_discovery_pilot as lean
import run_policy_improvement as runtime
from policy_update_math import response_log_probs
from compiler_credit_objective import loss_terms
from run_compiler_credit import probe
from constructor_certificates import certificate
from compile_contract_transport import logical_body
import universal_constructor as contracts

ARMS=['base','hindsight','executable','transport']
CONFIG=dict(steps=32,learning_rate=1e-4,weight_decay=0,gradient_norm_cap=1,lora_rank=8,lora_alpha=16,
    adapter_seed=20261120,reference_anchor=.02,samples_per_task=16,max_new_tokens=768,
    sampling_seed_base=20261127,temperature=1,top_p=1,top_k=0,dtype='float32',tf32=False)


def training(bundle):
    root=bundle/'runs/contract-transport-20261124-v2'
    assert json.loads((root/'results.json').read_text())['criterion_passed']
    assert json.loads((root/'independent-audit.json').read_text())['passed']
    inputs=json.loads((root/'inputs.json').read_text());plans=json.loads((root/'plans.json').read_text())
    source=inputs['source'];body,error=lean.completion_code(source['response']);assert not error
    local=source['positive'].replace('theorem target','  have source_contract',1)+textwrap.indent(body,'  ')+'\n'
    chosen=json.loads((bundle/'runs/hindsight-contracts-mining-20261124/selected.json').read_text())
    data={'hindsight':[dict(id=r['id'],statement=r['positive'],response=r['response']) for r in chosen], 'executable':[], 'transport':[]}
    for t,p in zip(inputs['targets'],plans):
        assert t['id']==p['task'] and p['original_function']==inputs['function']
        prefix=lean.HEADER+t['statement'];code=certificate(dict(id='quadratic-composition',statement=t['statement']),p['executable_wrapper'])
        assert code.startswith(prefix) and code.endswith('\n#print axioms target\n')
        executable=code[len(prefix):-len('\n#print axioms target\n')]
        transport=local+logical_body(p['names'],p['lean_binding'])
        for arm,response in [('executable',executable),('transport',transport)]:
            data[arm].append(dict(id=t['id'],statement=t['statement'],response=response+'\n```'))
    assert all(len(rs)==8 for rs in data.values())
    return data


def new_task(variant,sign):
    opaque=variant in ['opaque','renamed'];renamed=variant=='renamed'
    w,d,a,b,x,y,f=('metric','rho','u','v','p','q','combine') if renamed else ('w','d','a','b','x','y','f')
    coefficient={'cubic':f'{d}^3-2*{d}+3','quartic':f'({d}^2+2*{d}+2)^2+1','opaque':f'{w} {d}','renamed':f'{w} {d}'}[variant]
    c=f'({coefficient})' if sign==1 else f'(-({coefficient}))'
    pre=f'({w} : ℤ → ℤ) ' if opaque else ''
    args=(w+' ' if opaque else '')+f'{d} {a} {b} {x} {y}'
    base=(w+' ' if opaque else '')+f'{d} {a} {b}'
    typ='(ℤ → ℤ) → ' if opaque else ''
    statement=(f'theorem target :\n    ∃ {f} : {typ}ℤ → ℤ → ℤ → ℤ → ℤ → ℤ × ℤ,\n'
        f'      (∀ {pre}({d} {a} {b} {x} {y} : ℤ),\n'
        f'        ({f} {args}).1 ^ 2 + {c} * ({f} {args}).2 ^ 2 =\n'
        f'          ({a}^2+{c}*{b}^2)*({x}^2+{c}*{y}^2)) ∧\n'
        f'      (∀ {pre}({d} {a} {b} : ℤ), {f} {base} 1 0 = ({a},{b})) ∧\n'
        f'      (∀ {pre}({d} {a} {b} : ℤ), {f} {base} 0 1 = (-{c}*{b},{a})) := by\n')
    function=f'fun {args} => ({a}*{x}-{c}*{b}*{y}, {b}*{x}+{a}*{y})'
    invalid='fun '+' '.join('_' for _ in args.split())+' => (0,0)'
    return dict(id=f'{variant}/{sign}',variant=variant,sign=sign,statement=statement,
        witness_source=certificate(dict(id='quadratic-composition',statement=statement),function),
        invalid_source=certificate(dict(id='quadratic-composition',statement=statement),invalid))


def panel(bundle):
    tasks=[new_task(v,s) for v in ['cubic','quartic','opaque','renamed'] for s in [-1,1]]
    old=json.loads((bundle/'runs/contract-transport-20261124-v2/inputs.json').read_text())['targets'][:2]
    plans=json.loads((bundle/'runs/contract-transport-20261124-v2/plans.json').read_text())[:2]
    for t,p in zip(old,plans):
        tasks.append(dict(**t,variant='original',sign=int(t['id'].split('/')[1]),
            witness_source=certificate(dict(id='quadratic-composition',statement=t['statement']),p['executable_wrapper']),
            invalid_source=certificate(dict(id='quadratic-composition',statement=t['statement']),'fun _ _ _ _ _ => (0,0)')))
    return tasks


def fixtures(bundle,train,tasks):
    jobs={};edges=[]
    def add(eid,code,expected):
        j=contracts.job(bundle,code);jobs[j['id']]=j;edges.append(dict(id=eid,key=j['id'],expected=expected))
    for arm,rs in train.items():
        for r in rs:
            body,error=lean.completion_code(r['response']);assert not error
            add(arm+'/'+r['id'],lean.HEADER+r['statement']+body+'\n#print axioms target\n',True)
    for t in tasks:
        for kind in ['witness','invalid']:add(t['id']+'/'+kind,t[kind+'_source'],kind=='witness')
    return jobs,edges


def prepare(a):
    a.out.mkdir(parents=True,exist_ok=False)
    train=training(a.bundle);tasks=panel(a.bundle)
    lean.write(a.out/'train.json',train);lean.write(a.out/'test.json',tasks);lean.write(a.out/'config.json',CONFIG)
    jobs,edges=fixtures(a.bundle,train,tasks);lean.write(a.out/'fixture-edges.json',edges)
    lean.write(a.out/'fixture-sources.json',{k:j['code'] for k,j in jobs.items()})
    vs=lean.verify_jobs(list(jobs.values()),a.out/'fixture-verdicts.jsonl',workers=4);verdicts={v['id']:v for v in vs}
    failures=[e['id'] for e in edges if verdicts[e['key']]['accepted']!=e['expected'] or verdicts[e['key']].get('system_errors')]
    lean.write(a.out/'ready.json',dict(passed=not failures,failures=failures,fixture_edges=len(edges),unique_checks=len(vs),
        train_sha256=lean.sha((a.out/'train.json').read_bytes()),test_sha256=lean.sha((a.out/'test.json').read_bytes())))
    assert not failures,failures


def run(a):
    import torch
    ready=json.loads((a.out/'ready.json').read_text());assert ready['passed']
    for f in ['train','test']:assert lean.sha((a.out/(f+'.json')).read_bytes())==ready[f+'_sha256']
    assert json.loads((a.out/'config.json').read_text())==CONFIG
    assert runtime.C['lora_rank']==8 and runtime.C['lora_alpha']==16 and runtime.C['seed']==20261120 and set(runtime.C['lora_modules'])=={'q_proj','v_proj'}
    tasks=json.loads((a.out/'test.json').read_text());dest=a.out/a.arm;dest.mkdir(exist_ok=False)
    model,tok=runtime.load_model(a.bundle,a.bundle/'models/c1-final')
    if a.arm!='base':
        train=json.loads((a.out/'train.json').read_text())[a.arm];records=[]
        for r in train:
            response=tok.encode(r['response'],add_special_tokens=False);assert tok.decode(response,skip_special_tokens=True)==r['response']
            records.append(dict(id=r['id'],prompt_token_ids=tok.encode(lean.PREFIX+lean.HEADER+r['statement']),response_token_ids=response))
        lean.write(dest/'tokens.json',records);refs=probe(model,records);lean.write(dest/'reference-probes.json',refs)
        model=runtime.add_adapter(model);assert probe(model,records)==refs
        params=[p for p in model.parameters() if p.requires_grad];opt=torch.optim.AdamW(params,lr=1e-4,weight_decay=0.);model.eval()
        with (dest/'metrics.jsonl').open('x') as stream:
            for step in range(32):
                idx=step%8;r=records[idx];opt.zero_grad(set_to_none=True)
                lp=response_log_probs(model,r['prompt_token_ids'],r['response_token_ids'],'cuda');ref=torch.tensor(refs[idx],device='cuda',dtype=lp.dtype)
                loss,nll,anchor=loss_terms(lp,ref,torch.ones_like(lp));loss.backward()
                grad=torch.nn.utils.clip_grad_norm_(params,1.,error_if_nonfinite=True);opt.step()
                runtime.append(stream,dict(step=step+1,id=r['id'],nll=float(nll.detach()),anchor=float(anchor.detach()),grad_norm=float(grad),tokens=len(lp)))
        final=probe(model,records);assert final!=refs
        with model.disable_adapter():assert probe(model,records)==refs
        lean.write(dest/'reload-probes.json',final);model.save_pretrained(dest/'adapter',safe_serialization=True)
        from peft import get_peft_model_state_dict
        from safetensors.torch import load_file
        saved=load_file(str(dest/'adapter/adapter_model.safetensors'));current=get_peft_model_state_dict(model)
        assert set(saved)==set(current) and all(torch.equal(saved[k],current[k].detach().cpu()) for k in saved)
        lean.write(dest/'training-complete.json',dict(steps=32,reference_unchanged=True,initial_adapter_equal_reference=True,
            serialized_weights_exact=True,adapter_tensors=len(saved),train_sha256=ready['train_sha256'],
            adapter_sha256=lean.sha((dest/'adapter/adapter_model.safetensors').read_bytes())))
    for ti,t in enumerate(tasks):
        prompt=lean.PREFIX+lean.HEADER+t['statement'];rows=runtime.sample(model,tok,prompt,CONFIG['sampling_seed_base']+ti,768,False)
        lean.write(dest/(t['id'].replace('/','_')+'.json'),dict(id=t['id'],prompt=prompt,rows=rows))
    lean.write(dest/'complete.json',dict(arm=a.arm,tasks=[t['id'] for t in tasks]))


def outcomes(cells):
    new=[v+'/'+str(s) for v in ['cubic','quartic','opaque','renamed'] for s in [-1,1]]
    opaque=[v+'/'+str(s) for v in ['opaque','renamed'] for s in [-1,1]]
    wins={arm:[k for k in new if cells[arm][k]['accepted']>=8 and all(cells[c][k]['accepted']<=1 for c in ['base','hindsight'])] for arm in ['executable','transport']}
    resolved=all(c['unresolved']==0 for a in cells.values() for c in a.values())
    closure=any(len(ws)>=3 and any(k.startswith('opaque/') for k in ws) and any(k.startswith('renamed/') for k in ws) for ws in wins.values())
    abstraction=sum(cells['transport'][k]['accepted']>=8 for k in opaque)>=3 and sum(cells['transport'][k]['accepted']-cells['executable'][k]['accepted']>=4 for k in opaque)>=2
    return dict(closure_winning_cells=wins,closure_gate=closure and resolved,abstraction_gate=abstraction and resolved,all_resolved=resolved)


def verify(a):
    tasks=json.loads((a.out/'test.json').read_text());jobs={};edges=[]
    for arm in ARMS:
        assert json.loads((a.out/arm/'complete.json').read_text())['tasks']==[t['id'] for t in tasks]
        for ti,t in enumerate(tasks):
            batch=json.loads((a.out/arm/(t['id'].replace('/','_')+'.json')).read_text());assert batch['prompt']==lean.PREFIX+lean.HEADER+t['statement'] and len(batch['rows'])==16
            for i,r in enumerate(batch['rows']):
                assert r['sample_index']==i and r['seed']==CONFIG['sampling_seed_base']+ti
                body,error=lean.completion_code(r['text']);key=None
                if not error:
                    j=contracts.job(a.bundle,lean.HEADER+t['statement']+body+'\n#print axioms target\n');jobs[j['id']]=j;key=j['id']
                edges.append(dict(arm=arm,task=t['id'],index=i,key=key,parse_error=error))
    lean.write(a.out/'sources.json',{k:j['code'] for k,j in jobs.items()});lean.write(a.out/'edges.json',edges)
    vs=lean.verify_jobs(list(jobs.values()),a.out/'verdicts.jsonl',workers=4);verdicts={v['id']:v for v in vs};cells={}
    for e in edges:
        c=cells.setdefault(e['arm'],{}).setdefault(e['task'],dict(proposals=0,accepted=0,parse_errors=0,unresolved=0));c['proposals']+=1;c['parse_errors']+=bool(e['parse_error'])
        if e['key']:c['accepted']+=bool(verdicts[e['key']]['accepted']);c['unresolved']+=bool(verdicts[e['key']].get('system_errors'))
    result=dict(cells=cells,proposals=len(edges),unique_checks=len(vs),**outcomes(cells));lean.write(a.out/'results.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['prepare','run','verify']);p.add_argument('bundle',type=Path);p.add_argument('out',type=Path);p.add_argument('--arm',choices=ARMS);a=p.parse_args();globals()[a.mode](a)
