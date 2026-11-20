#!/usr/bin/env python3
"""Matched full/mapped/rotated supervision and scaffold-free root evaluation."""
import argparse
import json
from pathlib import Path
import time
import compiler_credit_data as data
import interface_discovery_pilot as lean
import run_policy_improvement as runtime
from policy_update_math import response_log_probs
from compiler_credit_objective import loss_terms
from archive_policy_update_training import sha

C=data.CONFIG


def tokenize(a):
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(str(a.bundle/'models/base'),local_files_only=True)
    assert tok.is_fast
    examples=json.loads((a.panel/'train.json').read_text());records=[]
    for x in examples:
        prompt=lean.PREFIX+lean.HEADER+x['statement'];response=x['body']+'\n```'
        encoded=tok(response,add_special_tokens=False,return_offsets_mapping=True)
        ids=encoded['input_ids'];offsets=encoded['offset_mapping']
        assert tok.decode(ids,skip_special_tokens=True)==response
        mapped=[int(any(end>s['start'] and start<s['end'] for s in x['spans'])) for start,end in offsets]
        assert 0<sum(mapped)<len(ids)
        shift=len(ids)//2;rotated=mapped[-shift:]+mapped[:-shift]
        assert sum(mapped)==sum(rotated) and mapped!=rotated
        prompt_ids=tok(prompt)['input_ids'];assert len(prompt_ids)+len(ids)<2048
        records.append(dict(id=x['id'],prompt=prompt,response=response,prompt_token_ids=prompt_ids,
            response_token_ids=ids,offsets=offsets,spans=x['spans'],mapped=mapped,rotated=rotated,
            supervised_tokens=sum(mapped),mask_overlap=sum(m*r for m,r in zip(mapped,rotated)),rotation=shift))
    a.output.mkdir(parents=True,exist_ok=False)
    lean.write(a.output/'tokens.json',records)
    lean.write(a.output/'token-audit.json',dict(passed=True,examples=8,tokens_sha256=sha(a.output/'tokens.json'),
        train_sha256=sha(a.panel/'train.json'),counts=[dict(id=x['id'],response_tokens=len(x['response_token_ids']),
        supervised_tokens=x['supervised_tokens'],overlap=x['mask_overlap']) for x in records]))


def inputs(a):
    audit=json.loads((a.input/'token-audit.json').read_text())
    assert audit['passed'] and audit['tokens_sha256']==sha(a.input/'tokens.json')
    assert audit['train_sha256']==sha(a.panel/'train.json')
    assert json.loads((a.panel/'validation-summary.json').read_text())['passed']
    return json.loads((a.input/'tokens.json').read_text())


def probe(model,examples):
    import torch
    with torch.no_grad():
        return [response_log_probs(model,x['prompt_token_ids'],x['response_token_ids'],'cuda').detach().cpu().tolist() for x in examples]


def train(a):
    import torch
    examples=inputs(a);a.output.mkdir(parents=True,exist_ok=False);start=time.time()
    model,tok=runtime.load_model(a.bundle);base=probe(model,examples)
    model=runtime.add_adapter(model);model.eval()
    params=[p for p in model.parameters() if p.requires_grad]
    initial=[p.detach().cpu().clone() for p in params]
    opt=torch.optim.AdamW(params,lr=C['learning_rate'],weight_decay=0.)
    step=0
    with (a.output/'metrics.jsonl').open('x') as f:
        for epoch in range(C['epochs']):
            for i,x in enumerate(examples):
                opt.zero_grad(set_to_none=True)
                logp=response_log_probs(model,x['prompt_token_ids'],x['response_token_ids'],'cuda')
                mask=torch.ones_like(logp) if a.arm=='full' else torch.tensor(x[a.arm],device='cuda',dtype=logp.dtype)
                ref=torch.tensor(base[i],device='cuda',dtype=logp.dtype)
                loss,nll,anchor=loss_terms(logp,ref,mask,C['anchor_coefficient'])
                if not torch.isfinite(loss):raise FloatingPointError('Nonfinite training loss')
                loss.backward();norm=torch.nn.utils.clip_grad_norm_(params,C['gradient_clip'])
                if not torch.isfinite(norm):raise FloatingPointError('Nonfinite gradient norm')
                opt.step();step+=1
                runtime.append(f,dict(step=step,epoch=epoch,example=x['id'],arm=a.arm,nll=float(nll.detach()),
                    anchor=float(anchor.detach()),gradient_norm=float(norm),supervised_tokens=int(mask.sum()),
                    response_tokens=len(x['response_token_ids']),seconds=time.time()-start))
                if step%8==0:print(json.dumps(dict(arm=a.arm,step=step,seconds=time.time()-start)),flush=True)
    final=probe(model,examples)
    with model.disable_adapter():unchanged=probe(model,examples)==base
    assert unchanged
    changed=sum(bool((p.detach().cpu()!=q).any()) for p,q in zip(params,initial));assert changed and step==80
    model.save_pretrained(a.output/'adapter',safe_serialization=True)
    lean.write(a.output/'reload-probes.json',final)
    lean.write(a.output/'reference-probes.json',base)
    lean.write(a.output/'complete.json',dict(arm=a.arm,optimizer_steps=step,changed_tensors=changed,
        trainable_parameters=sum(p.numel() for p in params),frozen_reference_bitwise_unchanged=unchanged,
        adapter_sha256=sha(a.output/'adapter/adapter_model.safetensors'),tokens_sha256=sha(a.input/'tokens.json'),
        config=C,seconds=time.time()-start))


def evaluate(a):
    import torch
    examples=inputs(a);model,tok=runtime.load_model(a.bundle);difference=None
    if a.arm!='base':
        cert=json.loads((a.adapter/'complete.json').read_text())
        assert cert['arm']==a.arm and cert['optimizer_steps']==80 and cert['config']==C
        assert cert['tokens_sha256']==sha(a.input/'tokens.json')
        assert sha(a.adapter/'adapter/adapter_model.safetensors')==cert['adapter_sha256']
        model=runtime.add_adapter(model,a.adapter/'adapter');model.eval()
        actual=probe(model,examples);saved=json.loads((a.adapter/'reload-probes.json').read_text())
        assert len(actual)==len(saved)==8 and all(len(x)==len(y) for x,y in zip(actual,saved))
        difference=max(abs(v-w) for x,y in zip(actual,saved) for v,w in zip(x,y));assert difference<=1e-4
    tasks=json.loads((a.panel/'evaluation.json').read_text());start=time.time()
    with a.output.open('x') as f:
        for task in tasks:
            prompt=lean.PREFIX+lean.HEADER+task['statement']
            seed=C['evaluation_seed']+int(lean.sha(task['id'])[:6],16)
            for row in runtime.sample(model,tok,prompt,seed,C['max_response_tokens'],False):
                runtime.append(f,dict(**row,id=f"{a.arm}/{task['id']}/{row['sample_index']}",model=a.arm,
                    target=task['id'],prompt=prompt,split=task['split'],family=task['family'],transition=task['transition']))
            print(json.dumps(dict(arm=a.arm,evaluated=task['id'],seconds=time.time()-start)),flush=True)
    lean.write(a.output.with_suffix('.complete.json'),dict(arm=a.arm,proposals=len(tasks)*16,
        sha256=sha(a.output),reload_max_abs=difference,seconds=time.time()-start))


def verify(a):
    tasks={x['id']:x for x in json.loads((a.panel/'evaluation.json').read_text())};edges=[];unique={}
    for arm in ['base']+C['arms']:
        p=a.input/(arm+'.jsonl');records=lean.rows(p)
        assert sha(p)==json.loads(p.with_suffix('.complete.json').read_text())['sha256']
        assert len(records)==704 and {x['id'] for x in records}=={f'{arm}/{tid}/{i}' for tid in tasks for i in range(16)}
        for x in records:
            t=tasks[x['target']];assert x['prompt']==lean.PREFIX+lean.HEADER+t['statement']
            body,error=lean.completion_code(x['text']);code=lean.HEADER+t['statement']+(body or '')+'\n#print axioms '+t['theorem']+'\n'
            key=lean.sha(code) if not error else None
            if key:unique.setdefault(key,dict(id=key,code=code,verifier=str(a.bundle/'verifier/DeepSeek-Prover-V1.5'),lake=str(a.bundle/'lean/elan/bin/lake')))
            edges.append(dict(id=x['id'],model=arm,target=t['id'],split=t['split'],family=t['family'],transition=t['transition'],code_sha256=key,parse_error=error))
    a.output.mkdir(exist_ok=False);lean.write(a.output/'edges.json',edges);lean.write(a.output/'sources.json',list(unique.values()))
    vs={x['id']:x for x in lean.verify_jobs(list(unique.values()),a.output/'verdicts.jsonl',workers=8)}
    cells={}
    for e in edges:
        key=(e['model'],e['target']);v=vs.get(e['code_sha256'])
        c=cells.setdefault(key,dict(model=e['model'],target=e['target'],split=e['split'],family=e['family'],transition=e['transition'],proposals=0,accepted=0,unresolved=0))
        c['proposals']+=1;c['accepted']+=int(bool(v and v['accepted']))
        c['unresolved']+=int(not e['parse_error'] and (not v or bool(v.get('system_errors'))))
    scores={arm:{split:sum(c['accepted'] for c in cells.values() if c['model']==arm and c['split']==split)/(384 if split=='composition' else 320)
                 for split in ['composition','retention']} for arm in ['base']+C['arms']}
    qualifying=[c for c in cells.values() if c['model']=='mapped' and c['split']=='composition' and c['family'] in ['nonzero','witness']
        and c['accepted']>=4 and all(cells[arm,c['target']]['accepted']<=1 for arm in ['base','full','rotated'])]
    margin=scores['mapped']['composition']-max(scores[x]['composition'] for x in ['full','rotated'])
    retention=scores['mapped']['retention']-scores['base']['retention'];errors=sum(c['unresolved'] for c in cells.values())
    lean.write(a.output/'analysis.json',dict(cells=list(cells.values()),scores=scores,qualifying_roots=[c['target'] for c in qualifying],
        margin=margin,retention_change=retention,unresolved=errors,physical_checks=len(vs),proposals=len(edges),
        registered_outcome=not errors and margin>=.10 and retention>=-.05 and len({c['transition'] for c in qualifying})>=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['tokenize','train','evaluate','verify'])
    for n in ['bundle','panel','input','output','adapter']:p.add_argument('--'+n,type=Path)
    p.add_argument('--arm',choices=['base']+C['arms']);a=p.parse_args();data.authenticate(a.panel);globals()[a.mode](a)
