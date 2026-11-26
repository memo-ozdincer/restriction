"""Temporary horizon slack on the fixed six-shortest-path reversible task."""
import argparse
from collections import deque
from concurrent.futures import ProcessPoolExecutor
import itertools
import json
import platform
from pathlib import Path
import time
import numpy as np

WIDTH, ACTIONS, H = 8, 12, 8
TARGET = (7, 3, 6, 1, 5, 4, 2, 0)
SLOTS, STEPS = 1024, 6000
GATES = [(target, controls)
         for target in range(3)
         for size in range(3)
         for controls in itertools.combinations([i for i in range(3) if i != target], size)]
ARMS = [('root', 8, False)] + [
    (mode, h, switch)
    for mode in ('root', 'goal4')
    for h in (8, 16, 32)
    for switch in (False, True)
    if not (mode == 'root' and h == 8)
]


def gate_value(value, gate):
    """Independent scalar gate action."""
    target, controls = gate
    if all(value & (1 << c) for c in controls):
        return value ^ (1 << target)
    return value


def depth_and_count(graph, center):
    depths = np.full(len(graph), -1, dtype=np.int32)
    counts = np.zeros(len(graph), dtype=np.int64)
    depths[center], counts[center] = 0, 1
    queue = deque([center])
    while queue:
        current = queue.popleft()
        for nxt in graph[current]:
            if depths[nxt] == -1:
                depths[nxt] = depths[current] + 1
                queue.append(nxt)
            if depths[nxt] == depths[current] + 1:
                counts[nxt] += counts[current]
    return depths, counts


def build():
    started = time.monotonic()
    states = list(itertools.permutations(range(WIDTH)))
    ids = {s: i for i, s in enumerate(states)}
    root, goal = ids[tuple(range(WIDTH))], ids[TARGET]
    gate_maps = [tuple(gate_value(x, gate) for x in range(WIDTH)) for gate in GATES]
    graph = np.asarray([[ids[tuple(g[x] for x in s)] for g in gate_maps]
                        for s in states], dtype=np.int32)
    for a in range(ACTIONS):
        assert np.array_equal(graph[graph[:, a], a], np.arange(len(graph)))
    features = np.eye(WIDTH, dtype=np.float32)[np.array(states)].reshape(-1, WIDTH*WIDTH)
    depths, counts = depth_and_count(graph, goal)
    assert (depths[root], counts[root]) == (8, 6)
    current = np.zeros(len(graph))
    current[goal] = 1.
    distribution = np.zeros_like(current)
    for _ in range(4):
        current = np.bincount(graph.ravel(), weights=np.repeat(current / ACTIONS, ACTIONS),
                              minlength=len(graph))
        distribution += current / 4
    distribution[goal] = 0
    distribution /= distribution.sum()
    cumulative = distribution.cumsum()
    cumulative[-1] = 1
    return dict(graph=graph, features=features, goal=goal, root=root,
                depths=depths, counts=counts, distribution=distribution,
                cdf=cumulative, setup_seconds=time.monotonic()-started)


def probabilities(x, weights):
    logits = x @ weights
    logits -= logits.max(axis=1, keepdims=True)
    probs = np.exp(logits)
    return probs / probs.sum(axis=1, keepdims=True)


def hits_by_horizon(prob, graph, goal, horizons):
    hit = np.zeros(len(graph), dtype=np.float64)
    hit[goal] = 1
    hits = {}
    for h in range(1, max(horizons) + 1):
        hit = (hit[graph] * prob).sum(axis=1)
        hit[goal] = 1
        if h in horizons:
            hits[h] = hit.copy()
    return hits


def rollout(weights, starts, env, rng, horizon, gradient=False, replay=False):
    graph, features, goal = env['graph'], env['features'], env['goal']
    states = starts.copy()
    alive = states != goal
    history = []
    active_count = 0
    words = [[] for _ in states] if replay else None
    for _ in range(horizon):
        x = features[states]
        probs = probabilities(x, weights)
        action = np.minimum((rng.random(len(states))[:, None] > np.cumsum(probs, axis=1))
                            .sum(axis=1), ACTIONS-1)
        if gradient:
            history.append((x, probs, action, alive.copy()))
        if replay:
            for i in np.flatnonzero(alive):
                words[i].append(int(action[i]))
        active_count += int(alive.sum())
        states = np.where(alive, graph[states, action], states)
        alive &= states != goal
    reward = (~alive).astype(np.float32)
    hits = int(reward.sum())
    if replay:
        assert np.all(starts == env['root'])
        for word, success in zip(words, reward):
            values = list(range(WIDTH))
            for action in word:
                target, controls = GATES[action]
                new_values = []
                for value in values:
                    bits = [(value // (2**bit)) % 2 for bit in range(3)]
                    if all(bits[c] == 1 for c in controls):
                        bits[target] = 1 - bits[target]
                    new_values.append(sum(b * 2**k for k, b in enumerate(bits)))
                values = new_values
            assert bool(success) == (tuple(values) == TARGET)
        return hits, active_count
    if not gradient:
        return hits, active_count
    advantage = reward - reward.mean()
    grad = np.zeros_like(weights)
    for x, p, a, active in history:
        score = -p
        score[np.arange(len(a)), a] += 1
        score *= (advantage * active)[:, None]
        grad += x.T @ score / len(starts)
    return hits, active_count, grad


ENV = None


def initialize():
    global ENV
    ENV = build()


def train(job):
    mode, horizon, switch, seed, steps = job
    env = ENV
    weights = np.random.default_rng(seed).normal(0, .02, (WIDTH*WIDTH, ACTIONS)).astype(np.float32)
    rr = np.random.default_rng(seed+30000)
    tr = np.random.default_rng(seed+20000)
    er = np.random.default_rng(seed+10000)
    m = np.zeros_like(weights)
    v = np.zeros_like(weights)
    phases = {name: dict(episodes=0, wins=0, active=0, padded=0, mixed_batches=0)
              for name in ('exposure', 'ordinary')}
    records = []
    every = {0, 25, 100, 300, 1000, 2000, 3000, 4000, 5000, steps, round(.6*steps)}
    first_ordinary_reward = None
    start_time = time.monotonic()
    for step in range(steps+1):
        if step in every:
            exact = hits_by_horizon(probabilities(env['features'].astype(np.float64), weights.astype(np.float64)), env['graph'],
                                    env['goal'], (8, 16, 32))
            records.append(dict(step=step, exact_root={str(h):float(x[env['root']]) for h,x in exact.items()},
                                exact_shell8=[float(exact[8][env['depths']==d].mean()) for d in range(1,9)],
                                phases={k: v.copy() for k,v in phases.items()}))
        if step == steps:
            break
        ordinary = (mode == 'root' and horizon == H) or (switch and step >= round(.6*steps))
        h = H if ordinary else horizon
        b = SLOTS//h
        if ordinary or mode == 'root':
            starts = np.full(b,env['root'],dtype=np.int32)
        else:
            starts = np.searchsorted(env['cdf'],rr.random(b),side='right').astype(np.int32)
        assert np.all(starts!=env['goal'])
        wins, active, grad = rollout(weights, starts, env, tr, h, gradient=True)
        phase = phases['ordinary' if ordinary else 'exposure']
        phase['wins'] += wins
        phase['episodes'] += b
        phase['active'] += active
        phase['padded'] += b*h
        phase['mixed_batches'] += int(0 < wins < b)
        if ordinary and wins and first_ordinary_reward is None:
            first_ordinary_reward = step+1
        m = .9*m + .1*grad
        v = .999*v + .001*grad*grad
        weights += .01*(m/(1-.9**(step+1)))/(np.sqrt(v/(1-.999**(step+1)))+1e-8)
    root_hits, root_active = rollout(weights,np.full(512,env['root']),env,er,H,replay=True)
    assert sum(p['padded'] for p in phases.values())==steps*SLOTS
    return dict(mode=mode,horizon=horizon,switch=switch,seed=seed,steps=steps,
                slots=SLOTS*steps,records=records,root_hits=root_hits,root_trials=512,
                eval_active=root_active,first_ordinary_reward=first_ordinary_reward,
                weights=weights.tolist(),seconds=time.monotonic()-start_time,
                setup_seconds=env['setup_seconds'])


def save(out, result):
    name = f"{result['mode']}-h{result['horizon']}-switch{int(result['switch'])}-{result['seed']}.json"
    (out/name).write_text(json.dumps(result,indent=2))
    print(name,result['records'][-1]['exact_root'],result['root_hits'],flush=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--workers',type=int,default=1)
    p.add_argument('--steps',type=int,default=STEPS)
    p.add_argument('--seeds',type=int,nargs='+',default=list(range(42,46)))
    a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    env=build()
    uniform=hits_by_horizon(np.full((len(env['graph']),ACTIONS),1/ACTIONS),env['graph'],env['goal'],(8,16,32))
    config=dict(target=TARGET,optimal_gate_count=int(env['depths'][env['root']]),
                shortest_paths=int(env['counts'][env['root']]),arms=ARMS,steps=a.steps,seeds=a.seeds,
                python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),
                uniform_root={str(h):float(x[env['root']]) for h,x in uniform.items()},
                uniform_goal4={str(h):float(env['distribution']@x) for h,x in uniform.items()},
                setup_seconds=env['setup_seconds'])
    (a.out/'config.json').write_text(json.dumps(config,indent=2))
    jobs=[(*arm,seed,a.steps) for arm in ARMS for seed in a.seeds]
    if a.workers==1:
        global ENV
        ENV=env
        for job in jobs:
            save(a.out,train(job))
    else:
        with ProcessPoolExecutor(max_workers=a.workers,initializer=initialize) as pool:
            for result in pool.map(train,jobs):
                save(a.out,result)


if __name__=='__main__':
    main()
