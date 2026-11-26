"""Matched terminal-only policy-gradient pilot on a fixed reversible task."""
import argparse
import itertools
import json
from pathlib import Path
import sys
import time

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "reversible_initial"))
from environment import distances, gate_library, gate_permutation, identity

N = 3
WIDTH = 8
HORIZON = 8
BATCH = 128
ACTIONS = 12


def make_environment():
    states = list(itertools.permutations(range(WIDTH)))
    index = {state: i for i, state in enumerate(states)}
    depth = distances(N)
    goal = next(state for state in states if depth[state] == HORIZON)
    gates = [gate_permutation(N, g) for g in gate_library(N)]
    transitions = np.array([[index[tuple(g[x] for x in s)] for g in gates]
                            for s in states], dtype=np.int32)
    features = np.eye(WIDTH, dtype=np.float32)[np.array(states)].reshape(-1, WIDTH*WIDTH)
    return transitions, features, index[identity(N)], index[goal], goal


def sample_starts(mode, rng, transitions, root, goal, size, exclude_solved=False):
    if mode == "root":
        return np.full(size, root, dtype=np.int32)
    if mode == "uniform":
        return rng.integers(0, len(transitions), size=size, dtype=np.int32)
    states = np.full(size, goal, dtype=np.int32)
    depth = rng.integers(1, 5, size=size)
    for step in range(4):
        proposed = transitions[states, rng.integers(ACTIONS, size=size)]
        states = np.where(step < depth, proposed, states)
    if exclude_solved and np.any(states == goal):
        mask = states == goal
        states[mask] = sample_starts(mode, rng, transitions, root, goal, int(mask.sum()), True)
    return states


def rollout(weights, starts, transitions, features, goal, rng, gradient=False):
    states = starts.copy()
    alive = states != goal
    history = []
    actions_taken = int(alive.sum()) * 0
    for _ in range(HORIZON):
        x = features[states]
        logits = x @ weights
        logits -= logits.max(axis=1, keepdims=True)
        probs = np.exp(logits)
        probs /= probs.sum(axis=1, keepdims=True)
        choice = (rng.random(len(states))[:, None] > np.cumsum(probs, axis=1)).sum(axis=1)
        choice = np.minimum(choice, ACTIONS - 1)
        if gradient:
            history.append((x, probs, choice, alive.copy()))
        actions_taken += int(alive.sum())
        states = np.where(alive, transitions[states, choice], states)
        alive &= states != goal
    reward = (~alive).astype(np.float32)
    if not gradient:
        return int(reward.sum()), actions_taken
    advantage = reward - reward.mean()
    grad = np.zeros_like(weights)
    for x, probs, choice, active in history:
        score = -probs
        score[np.arange(len(choice)), choice] += 1
        score *= (advantage * active)[:, None]
        grad += x.T @ score / len(starts)
    return int(reward.sum()), actions_taken, grad


def train(mode, steps, env, seed, exclude_solved=False):
    transitions, features, root, goal, goal_state = env
    rng = np.random.default_rng(seed)
    eval_rng = np.random.default_rng(seed + 10000)
    weights = rng.normal(0, 0.02, (WIDTH*WIDTH, ACTIONS)).astype(np.float32)
    m = np.zeros_like(weights)
    v = np.zeros_like(weights)
    records = []
    wins = actions = 0
    for step in range(steps + 1):
        if step % 25 == 0 or step == steps:
            hit, _ = rollout(weights, np.full(512, root), transitions, features, goal, eval_rng)
            records.append(dict(step=step, root_hits=hit, root_trials=512,
                                train_hits=wins, train_actions=actions))
        if step == steps:
            break
        distribution = mode.split("-")[0]
        if mode.endswith("-switch") and step >= int(steps * .3):
            distribution = "root"
        starts = sample_starts(distribution, rng, transitions, root, goal, BATCH, exclude_solved)
        hit, count, grad = rollout(weights, starts, transitions, features, goal, rng, True)
        wins += hit
        actions += count
        m = .9*m + .1*grad
        v = .999*v + .001*grad*grad
        weights += .01*(m/(1-.9**(step+1)))/(np.sqrt(v/(1-.999**(step+1)))+1e-8)
    return dict(mode=mode, goal=list(goal_state), seed=seed, steps=steps, batch=BATCH, records=records, exclude_solved=exclude_solved)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--exclude-solved", action="store_true")
    args = parser.parse_args()
    env = make_environment()
    results = []
    for mode in ("root", "uniform", "uniform-switch", "near", "near-switch"):
        started = time.monotonic()
        result = train(mode, args.steps, env, args.seed, args.exclude_solved)
        result["seconds"] = time.monotonic()-started
        results.append(result)
        args.out.write_text(json.dumps(results, indent=2))
        print(mode, result["records"][-1], flush=True)
