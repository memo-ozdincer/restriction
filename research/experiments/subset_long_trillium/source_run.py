"""Sparse terminal policy gradient for a fixed whole-candidate subset sum."""
import itertools
import json
from pathlib import Path
import numpy as np

N = 20
BATCH = 256
STEPS = 600
EVAL = 2048
SWITCH = 180
TOL = 16384
MODES = ("exact", "tolerance-only", "tolerance-switch", "tolerance-anneal",
         "bits-switch", "bits-anneal")


def sums(weights):
    return [sum(w*b for w,b in zip(weights,bits))
            for bits in itertools.product((0,1), repeat=len(weights))]


def task():
    rng = np.random.default_rng(20261127)
    while True:
        weights = rng.integers(10000, 10000000, N, dtype=np.int64)
        target = int(weights @ rng.integers(0,2,N))
        left = sums(weights[:N//2].tolist())
        right = sums(weights[N//2:].tolist())
        from collections import Counter
        counts = Counter(right)
        n = sum(counts[target-s] for s in left)
        if n == 1 and 0 < target < int(weights.sum()):
            return weights, target, n


def reward(mode, step, value, target, bits, rng):
    early = step < SWITCH
    if mode == "exact" or (not early and mode != "tolerance-only"):
        return value == target
    if mode.startswith("tolerance"):
        tolerance = TOL
        if mode == "tolerance-anneal":
            tolerance = int(TOL ** (1-step/SWITCH))
        return np.abs(value-target) <= tolerance
    count = 6
    if mode == "bits-anneal":
        count = min(bits, 6 + int((bits-6)*step/SWITCH))
    mask = sum(1 << int(i) for i in rng.choice(bits, count, replace=False))
    return (value & mask) == (target & mask)


def train(weights, target, mode, seed):
    init_rng = np.random.default_rng(seed)
    rng = np.random.default_rng(seed + 100)
    mask_rng = np.random.default_rng(seed + 200)
    eval_rng = np.random.default_rng(seed + 300)
    logits = init_rng.normal(0,.02,N)
    m = np.zeros(N)
    v = np.zeros(N)
    records = []
    wins = exact_hits = 0
    width = int(weights.sum()).bit_length()
    for step in range(STEPS+1):
        prob = 1/(1+np.exp(-logits))
        if step % 30 == 0:
            val = (eval_rng.random((EVAL,N)) < prob) @ weights
            records.append(dict(step=step, exact_eval=int((val==target).sum()),
                                eval_trials=EVAL, train_reward_hits=wins,
                                train_exact_hits=exact_hits))
        if step == STEPS:
            break
        candidates = rng.random((BATCH,N)) < prob
        val = candidates @ weights
        r = reward(mode,step,val,target,width,mask_rng).astype(float)
        wins += int(r.sum())
        exact_hits += int((val==target).sum())
        grad = ((r-r.mean())[:,None]*(candidates-prob)).mean(axis=0)
        m = .9*m + .1*grad
        v = .999*v + .001*grad*grad
        logits += .02*(m/(1-.9**(step+1)))/(np.sqrt(v/(1-.999**(step+1)))+1e-8)
    return dict(mode=mode, seed=seed, records=records, final_logits=logits.tolist())


if __name__ == "__main__":
    weights,target,count=task()
    rows=[]
    print("unique target",target,"solutions",count)
    for seed in range(42,50):
        for mode in MODES:
            row=train(weights,target,mode,seed)
            rows.append(row)
            r=row["records"][-1]
            print(seed,mode,r["exact_eval"],r["train_reward_hits"],r["train_exact_hits"],flush=True)
    Path(__file__).with_name("results.json").write_text(json.dumps(
        dict(weights=weights.tolist(),target=target,solutions=count,
             steps=STEPS,batch=BATCH,rows=rows),indent=2))
