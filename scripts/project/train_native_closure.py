"""Matched native-boundary learning and legacy-adapter crossover."""
import argparse
import json
from pathlib import Path
import interface_discovery_pilot as lean
import run_policy_improvement as runtime
from policy_update_math import response_log_probs
from compiler_credit_objective import loss_terms
from run_compiler_credit import probe
import universal_constructor as contracts

ARMS=['base','hindsight','executable','transport','legacy_executable','legacy_transport']
CONFIG=dict(steps=32,learning_rate=1e-4,weight_decay=0,gradient_norm_cap=1,lora_rank=8,lora_alpha=16,
    adapter_seed=20261120,reference_anchor=.02,samples_per_task=16,max_new_tokens=768,
    sampling_seed_base=20261127,temperature=1,top_p=1,top_k=0,dtype='float32',tf32=False,
    prompt_interface='native',implicit_special_tokens=False,new_trained_adapters=3,reused_adapters=2)


from train_contract_closure import training,panel,fixtures
from proof_prompt_interface import prompt as interface_prompt,ExplicitTokenizer

TRAINED=['hindsight','executable','transport']
LEGACY_HASHES={'legacy_executable':'e8db215e98540feaf892f20d2dfa05a67dc000f33a02637a511ceae1372fc05a',
               'legacy_transport':'6922fd9bfbe4e6ff7e6a143d6a73cfacfae6611805bff97c8bc8e77b6ca3cbc2'}


def native_prompt(statement):return interface_prompt(statement,'native')


def prior(bundle):return bundle/'runs/contract-closure-20261124-1400174/experiment'


def prepare(a):
    a.out.mkdir(parents=True,exist_ok=False)
    train=training(a.bundle);tasks=panel(a.bundle)
    assert train==json.loads((prior(a.bundle)/'train.json').read_text()) and tasks==json.loads((prior(a.bundle)/'test.json').read_text())
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
    model,tok=runtime.load_model(a.bundle,a.bundle/'models/c1-final');tok=ExplicitTokenizer(tok)
    if a.arm in TRAINED:
        train=json.loads((a.out/'train.json').read_text())[a.arm];records=[]
        for r in train:
            response=tok.encode(r['response'],add_special_tokens=False);assert tok.decode(response,skip_special_tokens=True)==r['response']
            records.append(dict(id=r['id'],prompt_token_ids=tok.encode(native_prompt(r['statement'])),response_token_ids=response))
            assert records[-1]['prompt_token_ids'][-1]==100000 and records[-1]['prompt_token_ids'][0]!=100000 and response[0]!=100000
            assert tok.encode(native_prompt(r['statement'])+r['response'])==records[-1]['prompt_token_ids']+response
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
    elif a.arm in LEGACY_HASHES:
        source=prior(a.bundle)/a.arm.removeprefix('legacy_');adapter=source/'adapter'
        assert lean.sha((adapter/'adapter_model.safetensors').read_bytes())==LEGACY_HASHES[a.arm]
        model=runtime.add_adapter(model,adapter)
        assert probe(model,json.loads((source/'tokens.json').read_text()))==json.loads((source/'reload-probes.json').read_text())
        lean.write(dest/'legacy-reload.json',dict(adapter_sha256=LEGACY_HASHES[a.arm],exact_probe_match=True,updates=0,
            original_training_sha256=lean.sha((source/'tokens.json').read_bytes())))
    for ti,t in enumerate(tasks):
        prompt=native_prompt(t['statement']);ids=tok.encode(prompt);assert ids[-1]==100000 and ids[0]!=100000
        rows=runtime.sample(model,tok,prompt,CONFIG['sampling_seed_base']+ti,768,False)
        lean.write(dest/(t['id'].replace('/','_')+'.json'),dict(id=t['id'],prompt=prompt,rows=rows))
    lean.write(dest/'complete.json',dict(arm=a.arm,tasks=[t['id'] for t in tasks]))


def outcomes(cells):
    new=[v+'/'+str(s) for v in ['cubic','quartic','opaque','renamed'] for s in [-1,1]]
    opaque=[v+'/'+str(s) for v in ['opaque','renamed'] for s in [-1,1]]
    wins={arm:[k for k in new if cells[arm][k]['accepted']>=8 and all(cells[c][k]['accepted']<=1 for c in ['base','hindsight'])] for arm in ['executable','transport']}
    resolved=all(c['unresolved']==0 for a in cells.values() for c in a.values())
    closure=any(len(ws)>=3 and any(k.startswith('opaque/') for k in ws) and any(k.startswith('renamed/') for k in ws) for ws in wins.values())
    abstraction=sum(cells['transport'][k]['accepted']>=8 for k in opaque)>=3 and sum(cells['transport'][k]['accepted']-cells['executable'][k]['accepted']>=4 for k in opaque)>=2
    interface_wins={arm:[k for k in new if cells[arm][k]['accepted']>=cells['legacy_'+arm][k]['accepted']+4] for arm in ['executable','transport']}
    interface=any(len(ks)>=2 and any(k in opaque for k in ks) for ks in interface_wins.values())
    return dict(closure_winning_cells=wins,closure_gate=closure and resolved,abstraction_gate=abstraction and resolved,
        interface_winning_cells=interface_wins,training_interface_gate=interface and resolved,all_resolved=resolved)


def verify(a):
    tasks=json.loads((a.out/'test.json').read_text());jobs={};edges=[]
    for arm in ARMS:
        assert json.loads((a.out/arm/'complete.json').read_text())['tasks']==[t['id'] for t in tasks]
        for ti,t in enumerate(tasks):
            batch=json.loads((a.out/arm/(t['id'].replace('/','_')+'.json')).read_text());assert batch['prompt']==native_prompt(t['statement']) and len(batch['rows'])==16
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
