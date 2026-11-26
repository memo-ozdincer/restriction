"""Replay the original subset-sum policy, then extend paired static freedom arms."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import time
import numpy as np
import source_run as original

STEPS = 60000
LATE_SWITCH = 600
SEEDS = range(42, 50)
ADDED_MODES = ('tolerance-late-switch', 'bits-only', 'bits-late-switch')
MODES = (*original.MODES, *ADDED_MODES)


def reward(mode, step, value, target, bits, rng):
    if mode == 'tolerance-late-switch':
        return original.reward('tolerance-only' if step < LATE_SWITCH else 'exact',
                               step, value, target, bits, rng)
    if mode == 'bits-only' or (mode == 'bits-late-switch' and step < LATE_SWITCH):
        # The original bit switch arm samples a fresh six-position mask at step 0..179.
        # Passing step=0 retains that exact predicate while continuing mask_rng.
        return original.reward('bits-switch', 0, value, target, bits, rng)
    if mode == 'bits-late-switch':
        return original.reward('exact', step, value, target, bits, rng)
    return original.reward(mode, step, value, target, bits, rng)


def train(weights, target, mode, seed, steps=STEPS):
    init_rng = np.random.default_rng(seed)
    rng = np.random.default_rng(seed + 100)
    mask_rng = np.random.default_rng(seed + 200)
    eval_rng = np.random.default_rng(seed + 300)
    logits = init_rng.normal(0,.02,original.N)
    m = np.zeros(original.N)
    v = np.zeros(original.N)
    records = []
    wins = exact_hits = 0
    first_exact = first_reward = None
    width = int(weights.sum()).bit_length()
    start_time = time.monotonic()
    for step in range(steps+1):
        prob = 1/(1+np.exp(-logits))
        interval = 30 if step <= original.STEPS else 300
        if step % interval == 0 or step == steps:
            val = (eval_rng.random((original.EVAL,original.N)) < prob) @ weights
            records.append(dict(step=step, exact_eval=int((val==target).sum()),
                                eval_trials=original.EVAL, train_reward_hits=wins,
                                train_exact_hits=exact_hits, logits=logits.tolist(),
                                max_abs_logit=float(np.max(np.abs(logits)))))
        if step == steps:
            break
        candidates = rng.random((original.BATCH,original.N)) < prob
        val = candidates @ weights
        r = reward(mode,step,val,target,width,mask_rng).astype(float)
        reward_hits = int(r.sum())
        batch_exact_hits = int((val==target).sum())
        if first_reward is None and reward_hits:
            first_reward = step
        if first_exact is None and batch_exact_hits:
            first_exact = step
        wins += reward_hits
        exact_hits += batch_exact_hits
        grad = ((r-r.mean())[:,None]*(candidates-prob)).mean(axis=0)
        m = .9*m + .1*grad
        v = .999*v + .001*grad*grad
        logits += .02*(m/(1-.9**(step+1)))/(np.sqrt(v/(1-.999**(step+1)))+1e-8)
    return dict(mode=mode, seed=seed, records=records, final_logits=logits.tolist(),
                first_exact_batch=first_exact, first_reward_batch=first_reward,
                elapsed_seconds=time.monotonic()-start_time)


def work(args):
    weights, target, mode, seed, outdir = args
    row = train(weights, target, mode, seed)
    path = Path(outdir) / f'{seed}-{mode}.json'
    path.write_text(json.dumps(row, separators=(',', ':'))+'\n')
    print(seed, mode, row['first_exact_batch'], row['records'][-1]['exact_eval'],
          f"{row['elapsed_seconds']:.2f}s", flush=True)
    return row


def assert_reproduction(expected, rows):
    by_key = {(r['seed'],r['mode']): r for r in rows}
    for e in expected['rows']:
        actual = by_key[e['seed'], e['mode']]
        prefix = [x for x in actual['records'] if x['step'] <= original.STEPS]
        assert len(prefix) == len(e['records'])
        for a,b in zip(prefix,e['records']):
            assert {k:a[k] for k in b} == b, (e['seed'],e['mode'],a['step'])
        assert prefix[-1]['logits'] == e['final_logits'], (e['seed'],e['mode'])
    for seed in SEEDS:
        for a,b in (('tolerance-only','tolerance-late-switch'), ('bits-only','bits-late-switch')):
            prefix_a = [x for x in by_key[seed,a]['records'] if x['step']<=LATE_SWITCH]
            prefix_b = [x for x in by_key[seed,b]['records'] if x['step']<=LATE_SWITCH]
            assert prefix_a == prefix_b, (seed,a,b)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--original-records', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--workers', type=int, default=min(72, os.cpu_count() or 1))
    args = p.parse_args()
    data = json.loads(args.original_records.read_text())
    expected_hash = 'eee1bae0c8b23d7cfcc7c540cdccac051633df0df1486968edd2aa4a8bbfca2b'
    assert hashlib.sha256(args.original_records.read_bytes()).hexdigest() == expected_hash
    weights, target, count = original.task()
    assert weights.tolist() == data['weights'] and target == data['target'] and count == data['solutions'] == 1
    args.out.mkdir(parents=True, exist_ok=False)
    tasks = [(weights,target,mode,seed,args.out) for seed in SEEDS for mode in MODES]
    with ProcessPoolExecutor(max_workers=min(args.workers,len(tasks))) as pool:
        rows = list(pool.map(work,tasks))
    assert_reproduction(data, rows)
    report = dict(weights=weights.tolist(),target=target,solutions=count,steps=STEPS,
                  batch=original.BATCH,eval=original.EVAL,original_prefix_reproduced=True,
                  paired_forks_reproduced=True,rows=rows)
    (args.out/'results.json').write_text(json.dumps(report,separators=(',', ':'))+'\n')


if __name__ == '__main__':
    main()
