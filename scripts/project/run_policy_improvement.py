#!/usr/bin/env python3
"""Exact-token collection, matched adapter updates and blind root evaluation."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import random
import time

try:
    from . import policy_improvement_data as data
    from . import policy_update_math as objective
    from . import cross_context_credit as credit
except ImportError:
    import policy_improvement_data as data
    import policy_update_math as objective
    import cross_context_credit as credit

lean, C = data.lean, data.CONFIG


def append(stream, row):
    stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    stream.flush()


def load_model(bundle):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    if not torch.cuda.is_available(): raise RuntimeError('Scientific work requires the allocated GPU')
    model = AutoModelForCausalLM.from_pretrained(str(bundle/'models/base'),
        torch_dtype=torch.bfloat16, attn_implementation='sdpa', local_files_only=True).cuda()
    tokenizer = AutoTokenizer.from_pretrained(str(bundle/'models/base'), local_files_only=True)
    model.requires_grad_(False)
    model.eval()
    return model, tokenizer


def add_adapter(model, path=None):
    import torch
    from peft import LoraConfig, get_peft_model, set_peft_model_state_dict
    from safetensors.torch import load_file
    torch.manual_seed(C['seed'])
    model = get_peft_model(model, LoraConfig(task_type='CAUSAL_LM', r=C['lora_rank'],
        lora_alpha=C['lora_alpha'], lora_dropout=0., target_modules=C['lora_modules']))
    for name, parameter in model.named_parameters():
        if 'lora_' in name: parameter.data = parameter.data.float()
        elif parameter.requires_grad: raise RuntimeError('Nonadapter parameter trainable')
    if path is not None:
        result = set_peft_model_state_dict(model, load_file(str(path/'adapter_model.safetensors')))
        if result.unexpected_keys or any('lora_' in key for key in result.missing_keys):
            raise RuntimeError('Incomplete adapter reload')
    return model


def response_end(tokens, tokenizer):
    """Preserve exact sampled IDs, stopping at the first fence-containing token."""
    for i, token in enumerate(tokens):
        if token == tokenizer.eos_token_id: return i+1, 'eos'
        if '```' in tokenizer.decode(tokens[:i+1], skip_special_tokens=True): return i+1, 'fence'
    return len(tokens), 'length'


def sample(model, tokenizer, prompt, seed, max_tokens, traces):
    import torch
    from transformers import GenerationConfig, StoppingCriteria, StoppingCriteriaList
    prompt_ids = tokenizer.encode(prompt)
    if len(prompt_ids) > C['max_prompt_tokens']: raise ValueError('Prompt too long')
    class Fence(StoppingCriteria):
        def __call__(self, input_ids, scores, **kwargs):
            return torch.tensor(['```' in tokenizer.decode(row[len(prompt_ids):], skip_special_tokens=True)
                for row in input_ids], dtype=torch.bool, device=input_ids.device)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    ids = torch.tensor([prompt_ids], device='cuda')
    cfg = GenerationConfig(do_sample=True, temperature=1., top_p=1., top_k=0,
        repetition_penalty=1., num_return_sequences=16, max_new_tokens=max_tokens,
        bos_token_id=tokenizer.bos_token_id, eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id, use_cache=True)
    model.eval()
    with torch.no_grad():
        output = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
            generation_config=cfg, stopping_criteria=StoppingCriteriaList([Fence()]),
            return_dict_in_generate=True, output_scores=traces)
        records = []
        for i, sequence in enumerate(output.sequences):
            tokens = sequence[len(prompt_ids):].tolist()
            length, reason = response_end(tokens, tokenizer)
            tokens = tokens[:length]
            decoded = tokenizer.decode(tokens, skip_special_tokens=True)
            text = decoded.split('```', 1)[0]+'```' if '```' in decoded else decoded
            row = dict(sample_index=i, prompt_token_ids=prompt_ids, response_token_ids=tokens,
                full_decoded_response=decoded, text=text, generated_tokens=len(tokens),
                prompt_tokens=len(prompt_ids), finish_reason=reason, seed=seed)
            if traces:
                old = [float(output.scores[j][i].float().log_softmax(-1)[token]) for j,token in enumerate(tokens)]
                reference = objective.response_log_probs(model, prompt_ids, tokens, 'cuda').tolist()
                difference = [abs(x-y) for x,y in zip(old,reference)]
                row.update(behavior_log_probs=old, reference_log_probs=reference,
                    behavior_reference_mean_abs=sum(difference)/len(difference),
                    behavior_reference_max_abs=max(difference))
                if row['behavior_reference_mean_abs'] > C['behavior_reference_mean_abs_tolerance'] or max(difference) > C['behavior_reference_max_abs_tolerance']:
                    raise RuntimeError('Cached generation/full-sequence probability mismatch: '+str(row['behavior_reference_max_abs']))
            records.append(row)
    return records


def collect(args):
    tasks = json.loads((args.panel/'train-tasks.json').read_text())
    model, tokenizer = load_model(args.bundle)
    start = time.time()
    with args.output.open('x') as stream:
        for request in credit.requests(tasks):
            seed = C['seed']+int(lean.sha(request['id'])[:6],16)
            records = sample(model,tokenizer,request['prompt'],seed,C['collection_max_tokens'],True)
            for row in records:
                append(stream, {**request, **row, 'id':f"base/{request['id']}/{row['sample_index']}", 'model':'base'})
            print(json.dumps(dict(collected=request['id'], seconds=time.time()-start)), flush=True)
    lean.write(args.output.with_suffix('.complete.json'), dict(proposals=320, seconds=time.time()-start,
        sha256=data.sha(args.output), backend='transformers SDPA', config=C))


def training_inputs(args):
    traces = lean.rows(args.input)
    tasks = json.loads((args.panel/'train-tasks.json').read_text())
    expected = {f"base/{r['id']}/{i}" for r in tasks for i in range(16)}
    by_id = {r['id']:r for r in traces}
    if len(traces) != 320 or set(by_id) != expected: raise ValueError('Incomplete fresh trace bank')
    provenance = json.loads((args.matrix/'provenance.json').read_text())
    if provenance['input_sha256'] != data.sha(args.input): raise ValueError('Rewards not from these traces')
    analysis = json.loads((args.matrix/'analysis.json').read_text())
    if analysis['unique_system_errors']: raise ValueError('Unresolved reward matrix')
    groups = defaultdict(list)
    if {r['id'] for r in analysis['proposals']} != expected or len(analysis['proposals']) != 320:
        raise ValueError('Incomplete reward matrix')
    for r in analysis['proposals']: groups[r['source']].append(r)
    for rows in groups.values(): rows.sort(key=lambda r:by_id[r['id']]['sample_index'])
    for r in traces:
        n = len(r['response_token_ids'])
        if not n or len(r['behavior_log_probs']) != n or len(r['reference_log_probs']) != n:
            raise ValueError('Missing exact behavior/reference trace')
        if not all(math.isfinite(x) for key in ('behavior_log_probs','reference_log_probs') for x in r[key]):
            raise ValueError('Nonfinite trace probabilities')
    rewards = {key:objective.reward_vectors(rows, by_id) for key,rows in groups.items()}
    return traces, by_id, groups, rewards


def probes(model, traces):
    import torch
    model.eval()
    with torch.no_grad():
        return [dict(id=r['id'], prompt_token_ids=r['prompt_token_ids'], response_token_ids=r['response_token_ids'],
                     log_probs=objective.response_log_probs(model,r['prompt_token_ids'],r['response_token_ids'],'cuda').tolist())
                for r in traces[:3]]


def train(args):
    import torch
    traces, by_id, groups, rewards = training_inputs(args)
    args.output.mkdir(exist_ok=False)
    model, _ = load_model(args.bundle)
    base_probe = probes(model,traces)
    model = add_adapter(model)
    initial_probe = probes(model,traces)
    if base_probe != initial_probe: raise RuntimeError('Adapter initialization changes base')
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
    model.config.use_cache = False
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(params, lr=C['learning_rate'], weight_decay=0.)
    initial = [p.detach().clone() for p in params]
    start = time.time()
    step = 0
    with (args.output/'metrics.jsonl').open('x') as stream:
        for epoch in range(C['epochs']):
            order = sorted(groups)
            random.Random(C['seed']+epoch).shuffle(order)
            for source in order:
                model.train()
                optimizer.zero_grad(set_to_none=True)
                rs = rewards[source][args.arm]
                advs = objective.advantages(rs)
                metrics = []
                for row, reward, adv in zip(groups[source],rs,advs):
                    r = by_id[row['id']]
                    logp = objective.response_log_probs(model,r['prompt_token_ids'],r['response_token_ids'],'cuda')
                    old = torch.tensor(r['behavior_log_probs'],device='cuda')
                    ref = torch.tensor(r['reference_log_probs'],device='cuda')
                    loss, actor, penalty, clipped = objective.loss_terms(logp,old,ref,adv,reward,args.arm,
                        C['ppo_clip'],C['kl_coefficient'])
                    (loss/16).backward()
                    metrics.append([float(x.detach()) for x in (loss,actor,penalty,clipped)])
                norm = torch.nn.utils.clip_grad_norm_(params,C['gradient_clip'],error_if_nonfinite=True)
                optimizer.step()
                step += 1
                record = dict(step=step,epoch=epoch,source=source,arm=args.arm,
                    mean_reward=sum(rs)/16, nonzero_advantages=sum(x!=0 for x in advs),
                    loss=sum(x[0] for x in metrics)/16, actor=sum(x[1] for x in metrics)/16,
                    sampled_k3_penalty=sum(x[2] for x in metrics)/16, clipped_fraction=sum(x[3] for x in metrics)/16,
                    gradient_norm=float(norm), seconds=time.time()-start)
                append(stream, record)
                print(json.dumps(record),flush=True)
    final_probe = probes(model,traces)
    with model.disable_adapter(): frozen_probe = probes(model,traces)
    if frozen_probe != base_probe: raise RuntimeError('Frozen reference changed')
    changed = sum(bool((p.detach()!=q).any()) for p,q in zip(params,initial))
    if step != C['optimizer_steps_per_arm'] or not changed: raise RuntimeError('Updates did not complete')
    model.save_pretrained(args.output/'adapter',safe_serialization=True)
    lean.write(args.output/'reload-probes.json',final_probe)
    lean.write(args.output/'complete.json',dict(arm=args.arm,optimizer_steps=step,candidate_passes=step*16,
        trainable_parameters=sum(p.numel() for p in params),changed_parameter_tensors=changed,
        frozen_reference_bitwise_unchanged=True,seconds=time.time()-start,config=C,
        trace_sha256=data.sha(args.input),reward_sha256=data.sha(args.matrix/'analysis.json'),
        adapter_sha256=data.sha(args.output/'adapter/adapter_model.safetensors'),
        checkpoint_scope='Final adapter weights; optimizer state is not archived'))


def evaluate(args):
    import torch
    tasks = json.loads((args.panel/'train-tasks.json').read_text())+json.loads((args.panel/'evaluation-tasks.json').read_text())
    model, tokenizer = load_model(args.bundle)
    reload_difference = None
    if args.arm != 'base':
        certificate = json.loads((args.adapter/'complete.json').read_text())
        if certificate['arm'] != args.arm or certificate['optimizer_steps'] != 40 or data.sha(args.adapter/'adapter/adapter_model.safetensors') != certificate['adapter_sha256']:
            raise RuntimeError('Adapter certificate mismatch')
        model = add_adapter(model,args.adapter/'adapter')
        model.eval()
        saved = json.loads((args.adapter/'reload-probes.json').read_text())
        with torch.no_grad():
            differences = [float((objective.response_log_probs(model,r['prompt_token_ids'],r['response_token_ids'],'cuda')-
                torch.tensor(r['log_probs'],device='cuda')).abs().max()) for r in saved]
        reload_difference = max(differences)
        if reload_difference > C['adapter_reload_tolerance']: raise RuntimeError('Adapter reload changed probabilities')
    start=time.time()
    with args.output.open('x') as stream:
        for task in tasks:
            prompt=lean.PREFIX+lean.HEADER+task['statement']
            seed=C['evaluation_seed']+int(lean.sha(task['id'])[:6],16)
            for row in sample(model,tokenizer,prompt,seed,C['evaluation_max_tokens'],False):
                append(stream,{**row,'id':f"{args.arm}/{task['id']}/{row['sample_index']}",
                    'model':args.arm,'target':task['id'],'family':task['family'],'split':task['split'],'prompt':prompt})
            print(json.dumps(dict(evaluated=task['id'],arm=args.arm,seconds=time.time()-start)),flush=True)
    lean.write(args.output.with_suffix('.complete.json'),dict(proposals=640,arm=args.arm,
        sha256=data.sha(args.output),reload_max_abs=reload_difference,seconds=time.time()-start))


def verify(args):
    tasks = json.loads((args.panel/'train-tasks.json').read_text())+json.loads((args.panel/'evaluation-tasks.json').read_text())
    tasks = {r['id']:r for r in tasks}
    unique, edges = {}, []
    for arm in ['base']+C['arms']:
        path=args.input/(arm+'.jsonl')
        rows=lean.rows(path)
        expected={f'{arm}/{tid}/{i}' for tid in tasks for i in range(16)}
        if len(rows)!=640 or {r['id'] for r in rows}!=expected: raise RuntimeError('Incomplete evaluation')
        cert=json.loads(path.with_suffix('.complete.json').read_text())
        if cert['sha256']!=data.sha(path): raise RuntimeError('Evaluation file changed')
        for row in rows:
            task=tasks[row['target']]
            if row['prompt']!=lean.PREFIX+lean.HEADER+task['statement']: raise RuntimeError('Root prompt changed')
            body,error=lean.completion_code(row['text'])
            code=lean.HEADER+task['statement']+(body or '')+'\n#print axioms '+task['theorem']+'\n'
            digest=lean.sha(code) if not error else None
            if digest: unique.setdefault(digest,dict(id=digest,code=code,
                verifier=str(args.bundle/'verifier/DeepSeek-Prover-V1.5'),lake=str(args.bundle/'lean/elan/bin/lake')))
            edges.append(dict(id=row['id'],model=arm,target=task['id'],family=task['family'],split=task['split'],
                code_sha256=digest,parse_error=error))
    args.output.mkdir(exist_ok=False)
    lean.write(args.output/'edges.json',edges)
    lean.write(args.output/'unique-sources.json',list(unique.values()))
    lean.verify_jobs(list(unique.values()),args.output/'verdicts.jsonl',workers=8)
    analyze(args.output)


def analyze(out):
    edges=json.loads((out/'edges.json').read_text())
    verdicts={r['id']:r for r in lean.rows(out/'verdicts.jsonl')}
    cells=defaultdict(lambda:dict(proposals=0,accepted=0,unresolved=0))
    for edge in edges:
        v=verdicts.get(edge['code_sha256'])
        cell=cells[(edge['model'],edge['split'],edge['family'],edge['target'])]
        cell['proposals']+=1
        cell['accepted']+=int(bool(v and v['accepted']))
        cell['unresolved']+=int(not edge['parse_error'] and (v is None or bool(v.get('system_errors'))))
    rows=[dict(model=k[0],split=k[1],family=k[2],target=k[3],**v) for k,v in sorted(cells.items())]
    macro={}
    for arm in ['base']+C['arms']:
        macro[arm]={}
        for split in ['retention','composition']:
            family=defaultdict(list)
            for r in rows:
                if r['model']==arm and r['split']==split: family[r['family']].append(r['accepted']/16)
            macro[arm][split]=sum(sum(v)/len(v) for v in family.values())/len(family)
    by={(r['model'],r['target']):r for r in rows}
    examples=[r['target'] for r in rows if r['model']=='cross' and r['split']=='composition' and r['accepted']>=4
        and by['base',r['target']]['accepted']==0 and all(by[a,r['target']]['accepted']<=1 for a in ['local','length','replay'])]
    unresolved=sum(r['unresolved'] for r in rows)
    margin=macro['cross']['composition']-max(macro[a]['composition'] for a in ['local','length','replay'])
    retention=macro['cross']['retention']-macro['base']['retention']
    lean.write(out/'analysis.json',dict(cells=rows,macro=macro,concrete_cross_only_tasks=examples,
        cross_margin_over_controls=margin,retention_change=retention,unresolved=unresolved,
        registered_exciting_result=not unresolved and margin>=.10 and len(examples)>=2 and retention>=-.05,
        logical_checks=len(edges),physical_checks=len(verdicts),
        claim_scope=C['claim_scope']))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['collect','train','evaluate','verify'])
    for name in ['bundle','panel','input','matrix','output','adapter']: p.add_argument('--'+name,type=Path)
    p.add_argument('--arm',choices=['base']+C['arms'])
    args=p.parse_args()
    data.authenticate(args.panel)
    globals()[args.mode](args)


if __name__=='__main__': main()
