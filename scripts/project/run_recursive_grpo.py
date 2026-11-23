"""Matched online adapter GRPO with per-theorem recursive tactic-signature exclusion."""
import argparse
from collections import Counter
from pathlib import Path
import json
import time

import interface_discovery_pilot as lean
import run_policy_improvement as policy

TRANSFER = {
    'square_transfer': '(a b : ℝ) : 16*a^2*b^2 + (a-b)^2 ≥ -8*a*b*(a-b)',
    'weighted_cube_transfer': '(a b : ℝ) (ha : 0 < a) (hb : 0 < b) : 3*a^2*b ≤ 2*a^3+b^3',
    'abs_transfer': '(t : ℝ) : t^2 + |t+1| + t ≥ 0',
    'finite_witness_transfer': '(s : Finset ℕ) : ∃ u v : Finset ℕ, Disjoint u s ∧ Disjoint v s ∧ Disjoint u v ∧ u.card = v.card',
}


def promote(modes, blocked):
    counts = Counter(m for m in modes if m is not None and m not in blocked)
    best = counts.most_common(2)
    if (best and best[0][1] >= max(2, .4 * sum(counts.values()))
            and (len(best) == 1 or best[0][1] > best[1][1])):
        return best[0][0]
    return None


def collect(model, tokenizer, name, statement, seed, bundle, folder, traces):
    from verl.lean.proof_modes import mode_id
    folder.mkdir()
    source = lean.HEADER + statement
    rows = policy.sample(model, tokenizer, lean.PREFIX + source, seed, 256, traces)
    lean.write(folder/'samples.json', rows)
    jobs = {}
    keys = []
    modes = []
    for row in rows:
        body, error = lean.completion_code(row['text'])
        key = None
        if not error:
            code = source + body + '\n#print axioms ' + name + '\n'
            key = lean.sha(code)
            jobs[key] = dict(id=key, code=code, lake=str(bundle/'lean/elan/bin/lake'),
                             verifier=str(bundle/'verifier/DeepSeek-Prover-V1.5'))
        keys.append(key)
        modes.append(mode_id(body) if key else None)
    lean.write(folder/'sources.json', jobs)
    verdicts = lean.verify_jobs(list(jobs.values()), folder/'lean.jsonl', workers=8)
    if any(v.get('system_errors') for v in verdicts):
        raise RuntimeError(f'Unresolved Lean verdict in {folder}')
    correct = {v['id'] for v in verdicts if v['accepted']}
    return rows, [m if k in correct else None for k,m in zip(keys,modes)]


def update(model, optimizer, rows, modes, blocked):
    import torch
    from verl.lean.hard_blocking import should_skip_prompt
    rewards = [int(m is not None) for m in modes]
    mask = [m in blocked for m in modes]
    if should_skip_prompt([i for i,r in enumerate(rewards) if r], mask) or len(set(rewards)) == 1:
        return False
    optimizer.zero_grad(set_to_none=True)
    for row, advantage, reward, excluded in zip(rows, policy.objective.advantages(rewards), rewards, mask):
        if excluded:
            continue
        ids = row['prompt_token_ids'], row['response_token_ids'], 'cuda'
        with torch.no_grad(), model.disable_adapter():
            reference = policy.objective.response_log_probs(model, *ids)
        old = torch.tensor(row['behavior_log_probs'], device='cuda')
        logp = policy.objective.response_log_probs(model, *ids)
        loss, *_ = policy.objective.loss_terms(logp, old, reference, advantage, reward, 'local')
        (loss/len(rows)).backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1., error_if_nonfinite=True)
    optimizer.step()
    return True


def main():
    import torch
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('bundle', type=Path)
    p.add_argument('panel', type=Path)
    p.add_argument('out', type=Path)
    p.add_argument('arm', choices=['discovery','control','recursive'])
    args = p.parse_args()
    train = {r['theorem']:r['statement'] for r in json.loads(args.panel.read_text())['panel']}
    transfer = {k:f'theorem {k} {v} := by\n' for k,v in TRANSFER.items()}
    out = args.out/args.arm
    out.mkdir()
    model, tokenizer = policy.load_model(args.bundle)
    model = policy.add_adapter(model)
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=1e-4, weight_decay=0.)
    blocked = {k:[] for k in train}
    if args.arm == 'recursive':
        blocked = json.loads((args.out/'discovery/blocklist.json').read_text())
    phases = ['learn','discover'] if args.arm == 'discovery' else ['first','second','probe','transfer']
    with (out/'groups.jsonl').open('x') as stream:
        for stage, phase in enumerate(phases):
            training = phase in ('learn','first','second')
            for i,(name,statement) in enumerate((transfer if phase == 'transfer' else train).items()):
                seed = 20261123 + (10000 if args.arm == 'discovery' else 0) + 128*stage + i
                rows, modes = collect(model, tokenizer, name, statement, seed, args.bundle,
                                      out/f'{phase}-{name}', training)
                if training and any(row['behavior_reference_mean_abs'] > .05 or
                                    row['behavior_reference_max_abs'] > .5 for row in rows):
                    raise RuntimeError('Behavior probabilities differ from rescored policy')
                active = list(blocked.get(name, []))
                stepped = training and update(model, optimizer, rows, modes, active)
                new = None
                if phase == 'discover' or (args.arm == 'recursive' and phase == 'first'):
                    new = promote(modes, active)
                    if new:
                        blocked[name].append(new)
                policy.append(stream, dict(phase=phase,name=name,seed=seed,correct_modes=modes,
                              blocked_before=active,promoted=new,optimizer_step=stepped,unix=time.time()))
    lean.write(out/'blocklist.json', blocked)
    model.save_pretrained(out/'adapter')


if __name__ == '__main__':
    main()
