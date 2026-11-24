"""Matched hindsight replay and valid-versus-invalid context contrast."""
import argparse
import json
from pathlib import Path
import re
import interface_discovery_pilot as lean
import run_policy_improvement as runtime
from policy_update_math import response_log_probs
from run_compiler_credit import probe
from mine_hindsight_contracts import signed_statement
from constructor_certificates import certificate
import universal_constructor as contracts

ARMS=['base','replay','contrast']


def panel():
    tasks=[]
    aliases=dict(d='rho',a='u',b='v',x='p',y='q',f='combine')
    for variant,coefficient in [('original','d'),('renamed','d'),('scaled','2*d'),('nonlinear','d^2+1')]:
        for sign in [-1,1]:
            statement=signed_statement(sign)
            if variant in ['scaled','nonlinear']:
                statement=statement.replace(' d *',f' ({coefficient}) *').replace('d*b',f'({coefficient})*b').replace('d*y',f'({coefficient})*y')
            op='+' if sign==-1 else '-'
            function=f'fun d a b x y => (a*x {op} ({coefficient})*b*y, b*x+a*y)'
            if variant=='renamed':
                def rename(s):return re.sub(r'\b(?:d|a|b|x|y|f)\b',lambda m:aliases[m[0]],s)
                statement=rename(statement);function=rename(function)
            source=certificate(dict(id='quadratic-composition',statement=statement),function)
            tasks.append(dict(id=f'{variant}/{sign}',variant=variant,sign=sign,statement=statement,witness_source=source))
    return tasks


def part_loss(current,ref,other_mean,other_ref_mean,positive,contrast):
    import torch
    delta=current.mean()-ref.mean();other_delta=other_mean-other_ref_mean
    margin=(delta-other_delta) if positive else (other_delta-delta)
    preference=torch.nn.functional.softplus(1-margin)
    anchor=(current-ref).square().mean()
    loss=(-current.mean() if positive else current.sum()*0)+float(contrast)*preference+0.01*anchor
    return loss,preference,anchor


def prepare(a):
    a.out.mkdir(parents=True,exist_ok=False)
    mining=a.bundle/'runs/hindsight-contracts-mining-20261124'
    assert json.loads((mining/'results.json').read_text())['ready']
    train=json.loads((mining/'selected.json').read_text());assert len(train)==8
    test=panel();lean.write(a.out/'train.json',train);lean.write(a.out/'test.json',test)
    assert runtime.C['lora_rank']==8 and set(runtime.C['lora_modules'])=={'q_proj','v_proj'}
    lean.write(a.out/'config.json',dict(steps=32,learning_rate=1e-4,weight_decay=0,gradient_norm_cap=1,
        lora_rank=8,lora_alpha=runtime.C['lora_alpha'],adapter_seed=runtime.C['seed'],
        reference_anchor=0.02,contrast_margin=1,contrast_weight=1,samples_per_task=16,max_new_tokens=768,
        sampling_seed_base=20261126,temperature=1,top_p=1,top_k=0,dtype='float32',tf32=False))
    jobs={};expected={};edges=[]
    for r in train:
        body,error=lean.completion_code(r['response']);assert not error
        assert r['positive']==signed_statement(1) and r['negative']==signed_statement(-1)
        for context in ['positive','negative']:
            code=lean.HEADER+r[context]+body+'\n#print axioms target\n';j=contracts.job(a.bundle,code)
            jobs[j['id']]=j;expected[j['id']]=context=='positive';edges.append(dict(id=r['id']+'/'+context,key=j['id']))
    for t in test:
        for kind in ['witness','invalid']:
            code=t['witness_source'] if kind=='witness' else lean.HEADER+t['statement']+'  refine ⟨fun _ _ _ _ _ => (0,0), ?_⟩\n  norm_num\n#print axioms target\n'
            j=contracts.job(a.bundle,code);jobs[j['id']]=j;expected[j['id']]=kind=='witness';edges.append(dict(id=t['id']+'/'+kind,key=j['id']))
    lean.write(a.out/'fixture-sources.json',{k:j['code'] for k,j in jobs.items()});lean.write(a.out/'fixture-edges.json',edges)
    vs=lean.verify_jobs(list(jobs.values()),a.out/'fixture-verdicts.jsonl',workers=4)
    assert all(not v.get('system_errors') and v['accepted']==expected[v['id']] for v in vs)
    lean.write(a.out/'ready.json',dict(passed=True,fixture_edges=len(edges),unique_checks=len(vs),
        train_sha256=lean.sha((a.out/'train.json').read_bytes()),test_sha256=lean.sha((a.out/'test.json').read_bytes()),
        mining_selection_sha256=lean.sha((mining/'selected.json').read_bytes())))


def run(a):
    import torch
    ready=json.loads((a.out/'ready.json').read_text());assert ready['passed']
    for f,key in [('train.json','train_sha256'),('test.json','test_sha256')]:assert lean.sha((a.out/f).read_bytes())==ready[key]
    train=json.loads((a.out/'train.json').read_text());test=json.loads((a.out/'test.json').read_text());assert test==panel()
    dest=a.out/a.arm;dest.mkdir(exist_ok=False)
    model,tok=runtime.load_model(a.bundle,a.bundle/'models/c1-final')
    if a.arm!='base':
        records=[]
        for r in train:
            response=tok.encode(r['response'],add_special_tokens=False);assert tok.decode(response,skip_special_tokens=True)==r['response']
            for context in ['positive','negative']:
                records.append(dict(id=r['id']+'/'+context,prompt_token_ids=tok.encode(lean.PREFIX+lean.HEADER+r[context]),response_token_ids=response))
        lean.write(dest/'tokens.json',records);refs=probe(model,records);lean.write(dest/'reference-probes.json',refs)
        model=runtime.add_adapter(model);assert probe(model,records)==refs
        params=[p for p in model.parameters() if p.requires_grad]
        opt=torch.optim.AdamW(params,lr=1e-4,weight_decay=0.);model.eval()
        with (dest/'metrics.jsonl').open('x') as stream:
            for step in range(32):
                idx=2*(step%8);pos,neg=records[idx:idx+2];rp,rn=[torch.tensor(refs[j],device='cuda') for j in [idx,idx+1]]
                opt.zero_grad(set_to_none=True)
                with torch.no_grad():
                    negative_mean=response_log_probs(model,neg['prompt_token_ids'],neg['response_token_ids'],'cuda').mean()
                lp=response_log_probs(model,pos['prompt_token_ids'],pos['response_token_ids'],'cuda')
                positive_mean=lp.detach().mean()
                pl,preference,pa=part_loss(lp,rp,negative_mean,rn.mean(),True,a.arm=='contrast')
                positive_anchor=float(pa.detach());preference_value=float(preference.detach());pl.backward()
                ln=response_log_probs(model,neg['prompt_token_ids'],neg['response_token_ids'],'cuda')
                negative_recompute_delta=float((ln.detach().mean()-negative_mean).abs())
                assert negative_recompute_delta<=1e-5
                nl,_,na=part_loss(ln,rn,positive_mean,rp.mean(),False,a.arm=='contrast');nl.backward()
                grad=torch.nn.utils.clip_grad_norm_(params,1.,error_if_nonfinite=True);opt.step()
                runtime.append(stream,dict(step=step+1,id=train[step%8]['id'],positive_nll=float(-positive_mean),negative_nll=float(-negative_mean),
                    preference=preference_value,positive_anchor=positive_anchor,negative_anchor=float(na.detach()),grad_norm=float(grad),
                    negative_recompute_delta=negative_recompute_delta,positive_tokens=len(lp),negative_tokens=len(ln)))
        final=probe(model,records);assert final!=refs
        with model.disable_adapter():assert probe(model,records)==refs
        lean.write(dest/'reload-probes.json',final);model.save_pretrained(dest/'adapter',safe_serialization=True)
        from peft import get_peft_model_state_dict
        from safetensors.torch import load_file
        saved=load_file(str(dest/'adapter/adapter_model.safetensors'))
        current=get_peft_model_state_dict(model)
        assert set(saved)==set(current) and all(torch.equal(saved[k],current[k].detach().cpu()) for k in saved)
        lean.write(dest/'training-complete.json',dict(steps=32,reference_unchanged=True,initial_adapter_equal_reference=True,
            serialized_weights_exact=True,adapter_tensors=len(saved),train_sha256=ready['train_sha256'],
            adapter_sha256=lean.sha((dest/'adapter/adapter_model.safetensors').read_bytes())))
    for ti,t in enumerate(test):
        prompt=lean.PREFIX+lean.HEADER+t['statement'];rows=runtime.sample(model,tok,prompt,20261126+ti,768,False)
        lean.write(dest/(t['id'].replace('/','_')+'.json'),dict(id=t['id'],prompt=prompt,rows=rows))
    lean.write(dest/'complete.json',dict(arm=a.arm,tasks=[t['id'] for t in test]))


def verify(a):
    tasks=json.loads((a.out/'test.json').read_text());jobs={};edges=[]
    for arm in ARMS:
        assert json.loads((a.out/arm/'complete.json').read_text())['tasks']==[t['id'] for t in tasks]
        for ti,t in enumerate(tasks):
            batch=json.loads((a.out/arm/(t['id'].replace('/','_')+'.json')).read_text())
            assert batch['prompt']==lean.PREFIX+lean.HEADER+t['statement'] and len(batch['rows'])==16
            for i,r in enumerate(batch['rows']):
                assert r['sample_index']==i and r['seed']==20261126+ti
                body,error=lean.completion_code(r['text']);key=None
                if not error:
                    code=lean.HEADER+t['statement']+body+'\n#print axioms target\n';j=contracts.job(a.bundle,code);jobs[j['id']]=j;key=j['id']
                edges.append(dict(arm=arm,task=t['id'],index=i,key=key,parse_error=error))
    lean.write(a.out/'sources.json',{k:j['code'] for k,j in jobs.items()});lean.write(a.out/'edges.json',edges)
    vs=lean.verify_jobs(list(jobs.values()),a.out/'verdicts.jsonl',workers=4);verdicts={v['id']:v for v in vs};cells={}
    for e in edges:
        c=cells.setdefault(e['arm'],{}).setdefault(e['task'],dict(proposals=0,accepted=0,parse_errors=0,unresolved=0))
        c['proposals']+=1;c['parse_errors']+=bool(e['parse_error'])
        if e['key']:c['accepted']+=bool(verdicts[e['key']]['accepted']);c['unresolved']+=bool(verdicts[e['key']].get('system_errors'))
    strong=all(cells['contrast'][v+'/-1']['accepted']>=8 and cells['base'][v+'/-1']['accepted']<=1 and cells['replay'][v+'/-1']['accepted']<=1 for v in ['renamed','scaled','nonlinear'])
    retention=all(cells['contrast'][v+'/1']['accepted']>=cells['replay'][v+'/1']['accepted']-2 for v in ['original','renamed','scaled','nonlinear'])
    resolved=all(c['unresolved']==0 for arm in cells.values() for c in arm.values())
    lean.write(a.out/'results.json',dict(cells=cells,proposals=len(edges),unique_checks=len(vs),target_criterion=strong,retention_criterion=retention,
        registered_outcome=strong and retention and resolved,all_resolved=resolved))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['prepare','run','verify']);p.add_argument('bundle',type=Path);p.add_argument('out',type=Path)
    p.add_argument('--arm',choices=ARMS);a=p.parse_args();globals()[a.mode](a)
