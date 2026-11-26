"""Matched GRPO on a fixed reversible circuit: identity vs uniform random resets."""
import argparse
from collections import Counter
import hashlib
import importlib.metadata
import json
from math import comb
from pathlib import Path
import random
import subprocess
import time

from environment import distances, identity
from local_screen import panel, prompt, score

SEED = 20261127


def training_rows(arm, groups, seed=SEED):
    if arm not in {"identity", "exploratory"} or groups < 1:
        raise ValueError("Invalid arm or group count")
    goal = tuple(next(panel())["target"])
    depths = distances(3, goal)
    population = sorted(p for p in depths if p != goal)
    rng = random.Random(seed)
    rows = []
    for i in range(groups):
        start = identity(3) if arm == "identity" else rng.choice(population)
        row = dict(current=start, target=goal, budget=8, exact_distance=depths[start], group_id=i)
        rows.append(dict(prompt=[{"role": "user", "content": prompt(row)}], circuit_json=json.dumps(row)))
    return rows


def completion_text(completion):
    if isinstance(completion, str):
        return completion
    if isinstance(completion, list) and len(completion) == 1 and isinstance(completion[0], dict) and completion[0].get("role") == "assistant":
        content = completion[0].get("content", "")
        return content if isinstance(content, str) else ""
    return ""


def reward_records(completions, circuit_json):
    if len(completions) != len(circuit_json):
        raise ValueError("Reward metadata length mismatch")
    records = []
    for completion, serialized in zip(completions, circuit_json):
        row = json.loads(serialized)
        answer = completion_text(completion)
        records.append(dict(row, answer=answer, **score(row, answer)))
    return records


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2) + "\n")


def summarize(rows):
    n = len(rows)
    c = sum(r["reward"] for r in rows)
    return dict(proposals=n, correct=c,
                pass_at_1=c/n if n else None,
                by_distance={str(d): dict(proposals=len(rs), correct=sum(r["reward"] for r in rs))
                             for d in sorted({r["exact_distance"] for r in rows})
                             if (rs := [r for r in rows if r["exact_distance"] == d])})


def evaluate(model, tok, out, count, batch_size, max_completion, seed):
    import torch
    row = json.loads(training_rows("identity", 1)[0]["circuit_json"])
    rendered = tok.apply_chat_template([{"role":"user", "content":prompt(row)}], tokenize=False, add_generation_prompt=True)
    rows = []
    model.eval()
    torch.manual_seed(seed)
    with out.open("x") as f, torch.inference_mode():
        for i in range(0, count, batch_size):
            size = min(batch_size, count-i)
            inputs = tok([rendered]*size, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
            generated = model.generate(**inputs, max_new_tokens=max_completion, do_sample=True,
                                       temperature=0.7, top_p=0.95, top_k=0, pad_token_id=tok.pad_token_id,
                                       use_cache=True)
            for j, answer in enumerate(tok.batch_decode(generated[:, inputs.input_ids.shape[1]:], skip_special_tokens=True)):
                result = dict(row, index=i+j, answer=answer, **score(row, answer))
                rows.append(result)
                f.write(json.dumps(result)+"\n")
            f.flush()
    result = summarize(rows)
    result['any_success'] = any(r['reward'] for r in rows)
    n, c = result['proposals'], result['correct']
    result['pass_at_k'] = {str(k): 1 - (comb(n-c,k)/comb(n,k) if n-c >= k else 0)
                           for k in (1,8,32,128) if k <= n}
    return result


def make_config(out, groups, generations, max_completion, seed, *, cpu=False):
    from trl import GRPOConfig
    return GRPOConfig(output_dir=str(out/'checkpoints'), learning_rate=5e-6, max_steps=groups,
                     per_device_train_batch_size=1, gradient_accumulation_steps=generations,
                     num_generations=generations, num_iterations=1, max_completion_length=max_completion,
                     bf16=not cpu, use_cpu=cpu, gradient_checkpointing=True, loss_type='dr_grpo', scale_rewards='none', beta=0.01,
                     temperature=0.7, top_p=0.95, top_k=0, use_vllm=False, mask_truncated_completions=True,
                     remove_unused_columns=False, logging_steps=1, save_steps=max(1,groups//8),
                     save_total_limit=2, report_to='none', seed=seed, data_seed=seed)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--arm", required=True, choices=["identity", "exploratory"])
    p.add_argument("--model", type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--groups", type=int, default=512)
    p.add_argument("--generations", type=int, default=8)
    p.add_argument("--eval-rollouts", type=int, default=128)
    p.add_argument("--max-completion", type=int, default=384)
    p.add_argument("--seed", type=int, default=SEED)
    p.add_argument("--preview", action="store_true")
    args = p.parse_args()
    if args.groups < 1 or args.generations < 2 or args.eval_rollouts < 1 or args.max_completion < 32:
        p.error("Invalid rollout budget")
    rows = training_rows(args.arm, args.groups, args.seed)
    plan = dict(arm=args.arm, seed=args.seed, groups=args.groups, generations=args.generations,
                training_proposals=args.groups*args.generations, evaluation_proposals_per_phase=args.eval_rollouts,
                max_completion=args.max_completion, target=json.loads(rows[0]['circuit_json'])['target'],
                start_distance_histogram=dict(Counter(json.loads(r['circuit_json'])['exact_distance'] for r in rows)),
                rows_sha256=hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest())
    if args.preview:
        print(json.dumps(plan, indent=2)); return
    if args.model is None or args.out is None:
        p.error("--model and --out required")
    import torch
    from datasets import Dataset
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
    from trl import GRPOTrainer
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1 or not torch.cuda.is_bf16_supported():
        raise RuntimeError("One allocated BF16-capable GPU is required")
    args.out.mkdir(parents=True, exist_ok=False)
    out = args.out.resolve()
    started = time.monotonic()
    set_seed(args.seed)
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True, trust_remote_code=False)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = 'left'
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True, trust_remote_code=False,
                                                dtype=torch.bfloat16, device_map={"": 0}, attn_implementation="sdpa")
    cfg = make_config(out, args.groups, args.generations, args.max_completion, args.seed)
    adapter = LoraConfig(r=16, lora_alpha=32, target_modules='all-linear', task_type='CAUSAL_LM')
    plan.update(model=str(args.model.resolve()), model_config_sha256=hashlib.sha256((args.model/'config.json').read_bytes()).hexdigest(),
                git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                git_dirty=subprocess.check_output(['git','status','--porcelain'],text=True),
                gpu=torch.cuda.get_device_name(), cuda=torch.version.cuda,
                packages={n:importlib.metadata.version(n) for n in ('torch','transformers','trl','peft','accelerate','datasets')},
                grpo_config=cfg.to_dict(), adapter_config=adapter.to_dict())
    # PEFT config includes sets in some versions; normalize via JSON default.
    (out/'manifest.json').write_text(json.dumps(plan, indent=2, default=lambda o: sorted(o) if isinstance(o,set) else str(o)))
    write_json(out/'training_rows.json', rows)
    before = evaluate(model,tok,out/'identity-before.jsonl',args.eval_rollouts,args.generations,args.max_completion,args.seed+100000)
    write_json(out/'identity-before.json',before)
    set_seed(args.seed)
    history = []
    grouped = []
    def circuit_reward(completions, circuit_json, trainer_state, completion_ids, **kwargs):
        records = reward_records(completions, circuit_json)
        if len(records) != args.generations or len({r['group_id'] for r in records}) != 1:
            raise RuntimeError('Expected exactly one complete GRPO rollout group per step')
        with (out/'rollouts.jsonl').open('a') as f:
            for r, ids in zip(records, completion_ids, strict=True):
                r['optimizer_step_before'] = trainer_state.global_step
                r['completion_tokens'] = len(ids)
                r['truncated'] = not ids or ids[-1] not in {tok.eos_token_id, tok.pad_token_id}
                f.write(json.dumps(r)+'\n')
        history.extend(records)
        grouped.append(dict(group_id=records[0]['group_id'], step=trainer_state.global_step,
                            distance=records[0]['exact_distance'], correct=sum(r['reward'] for r in records),
                            mixed=len({r['reward'] for r in records})>1))
        with (out/'groups.jsonl').open('a') as f:
            f.write(json.dumps(grouped[-1])+'\n')
        return [r['reward'] for r in records]
    trainer = GRPOTrainer(model=model, args=cfg, processing_class=tok, reward_funcs=circuit_reward,
                          train_dataset=Dataset.from_list(rows), peft_config=adapter)
    initial = {n:hashlib.sha256(p.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()
               for n,p in trainer.model.named_parameters() if p.requires_grad}
    write_json(out/'initial_adapter_fingerprints.json', initial)
    result = trainer.train()
    if (len(history)!=args.groups*args.generations or len(grouped)!=args.groups or trainer.state.global_step!=args.groups
            or {g['group_id'] for g in grouped} != set(range(args.groups))):
        raise RuntimeError('Physical rollout/step budget mismatch')
    final = {n:hashlib.sha256(p.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()
             for n,p in trainer.model.named_parameters() if p.requires_grad}
    write_json(out/'final_adapter_fingerprints.json', final)
    trainer.save_model(str(out/'adapter'))
    tok.save_pretrained(str(out/'adapter'))
    after = evaluate(trainer.model,tok,out/'identity-after.jsonl',args.eval_rollouts,args.generations,args.max_completion,args.seed+100000)
    write_json(out/'identity-after.json',after)
    write_json(out/'completed.json',dict(training=summarize(history), mixed_groups=sum(g['mixed'] for g in grouped),
                                         all_zero_groups=sum(g['correct']==0 for g in grouped),
                                         all_success_groups=sum(g['correct']==args.generations for g in grouped),
                                         optimizer_steps=trainer.state.global_step, truncated_rollouts=sum(r['truncated'] for r in history),
                                         changed_adapter_tensors=sum(initial[n]!=final[n] for n in initial),
                                         identity_before=before,identity_after=after,metrics=result.metrics,
                                         elapsed_seconds=time.monotonic()-started,peak_gpu_bytes=torch.cuda.max_memory_allocated()))


if __name__ == '__main__':
    main()
