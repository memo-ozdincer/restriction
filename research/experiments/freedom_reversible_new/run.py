"""Terminal-only reversible synthesis interventions (registered PLAN.md)."""
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "reversible_learning"))
from train import make_environment, ACTIONS, WIDTH

STEPS = 300
SLOTS = 1024
SEEDS = range(42, 50)
EVAL_H = 8
EVAL_TRIALS = 512


def build_distributions(transitions, root, goal):
    count = len(transitions)

    def point(i):
        p = np.zeros(count, dtype=np.float64)
        p[i] = 1
        return p

    def depth(center):
        d = np.full(count, -1, dtype=int)
        d[center] = 0
        current = np.array([center])
        for j in range(1, 9):
            candidates = np.unique(transitions[current].ravel())
            current = candidates[d[candidates] == -1]
            d[current] = j
        assert np.all(d >= 0)
        return d

    def walks(center, max_len):
        p = point(center)
        mixture = np.zeros(count)
        for _ in range(max_len):
            p = np.bincount(transitions.ravel(), weights=np.repeat(p / ACTIONS, ACTIONS),
                            minlength=count)
            mixture += p / max_len
        mixture[goal] = 0
        return mixture / mixture.sum()

    gd = depth(goal)
    rd = depth(root)
    uniform = np.ones(count)
    uniform[goal] = 0
    uniform /= uniform.sum()
    equal = (gd == gd[root]).astype(float)
    equal /= equal.sum()
    balanced = np.zeros(count)
    for d in range(1, 9):
        shell = gd == d
        balanced[shell] = 1 / (8*shell.sum())
    root_walk = walks(root, 4)
    goal_walk = walks(goal, 4)
    p = {
        "root": point(root),
        "root_walk4": root_walk,
        "root_walk12": walks(root, 12),
        "uniform": uniform,
        "goal_walk4": goal_walk,
        "goal_walk8": walks(goal, 8),
        "equal_distance": equal,
        "balanced_shell": balanced,
        "both_walks": .5 * root_walk + .5 * goal_walk,
        "uniform_goal05": .95 * uniform + .05 * goal_walk,
        "uniform_goal20": .80 * uniform + .20 * goal_walk,
    }
    for name, v in p.items():
        assert abs(v.sum() - 1) < 1e-10 and v[goal] == 0, name
    return p, gd, rd


def probabilities(x, weights):
    logits = x @ weights
    logits -= logits.max(axis=1, keepdims=True)
    probs = np.exp(logits)
    probs /= probs.sum(axis=1, keepdims=True)
    return probs


def rollout(weights, starts, transitions, features, goal, rng, horizon, gradient=False):
    states = starts.copy()
    alive = states != goal
    history = []
    action_count = 0
    for _ in range(horizon):
        x = features[states]
        probs = probabilities(x, weights)
        choice = np.minimum((rng.random(len(states))[:, None] > np.cumsum(probs, axis=1))
                            .sum(axis=1), ACTIONS - 1)
        if gradient:
            history.append((x, probs, choice, alive.copy()))
        action_count += int(alive.sum())
        states = np.where(alive, transitions[states, choice], states)
        alive &= states != goal
    rewards = (~alive).astype(np.float32)
    hit = int(rewards.sum())
    if not gradient:
        return hit, action_count
    advantage = rewards - rewards.mean()
    grad = np.zeros_like(weights)
    for x, probs, choice, active in history:
        score = -probs
        score[np.arange(len(choice)), choice] += 1
        score *= (advantage * active)[:, None]
        grad += x.T @ score / len(starts)
    return hit, action_count, grad


def hitting_probability(probs, transitions, goal, horizon):
    hit = np.zeros(len(transitions), dtype=np.float64)
    hit[goal] = 1
    for _ in range(horizon):
        hit = (hit[transitions] * probs).sum(axis=1)
        hit[goal] = 1
    return hit


def train(env, p, gd, name, horizon, switch, seed, audit_shells=False):
    transitions, features, root, goal, target = env
    weights = np.random.default_rng(seed).normal(0, 0.02, (WIDTH*WIDTH, ACTIONS)).astype(np.float32)
    reset_rng = np.random.default_rng(seed + 30000)
    train_rng = np.random.default_rng(seed + 20000)
    eval_rng = np.random.default_rng(seed + 10000)
    cumulative = np.cumsum(p)
    m, v = np.zeros_like(weights), np.zeros_like(weights)
    records = []
    wins = episodes = interactions = 0
    phases = dict(exposure=dict(episodes=0, wins=0, actions=0), root=dict(episodes=0, wins=0, actions=0))
    start_time = time.monotonic()
    for step in range(STEPS+1):
        if step % 25 == 0 or step == STEPS:
            hit, _ = rollout(weights, np.full(EVAL_TRIALS, root), transitions, features, goal,
                             eval_rng, EVAL_H)
            records.append(dict(step=step, root_hits=hit, train_wins=wins,
                                train_episodes=episodes, train_actions=interactions))
            if audit_shells:
                exact = hitting_probability(probabilities(features, weights), transitions, goal, EVAL_H)
                records[-1]["exact_root"] = float(exact[root])
                records[-1]["exact_shells"] = [float(exact[gd == d].mean()) for d in range(1, 9)]
        if step == STEPS:
            break
        switched = switch is not None and step >= round(STEPS * switch)
        h = EVAL_H if switched else horizon
        b = SLOTS // h
        assert b*h == SLOTS
        starts = (np.full(b, root, dtype=np.int32) if switched or name == "root" else
                  np.searchsorted(cumulative, reset_rng.random(b), side="right").astype(np.int32))
        assert np.all(starts != goal)
        hit, actions, grad = rollout(weights, starts, transitions, features, goal, train_rng,
                                    h, gradient=True)
        wins += hit
        episodes += b
        interactions += actions
        phase = phases["root" if switched or (name == "root" and h == EVAL_H) else "exposure"]
        phase["episodes"] += b
        phase["wins"] += hit
        phase["actions"] += actions
        m = .9*m + .1*grad
        v = .999*v + .001*grad*grad
        weights += .01*(m/(1-.9**(step+1)))/(np.sqrt(v/(1-.999**(step+1)))+1e-8)
    train_seconds = time.monotonic()-start_time
    # Final policy exact evaluation: no sampling noise or chosen checkpoint.
    probs = probabilities(features, weights)
    hit = hitting_probability(probs, transitions, goal, EVAL_H)
    return dict(distribution=name, horizon=horizon, switch=switch, seed=seed, records=records,
                final_root_probability=float(hit[root]),
                final_shell_probability=[float(hit[gd == d].mean()) for d in range(1, 9)],
                phase_counts=phases, policy_slots=STEPS*SLOTS, train_seconds=train_seconds,
                weights=weights.tolist())


def main():
    started = time.monotonic()
    env = make_environment()
    transitions, features, root, goal, target = env
    distributions, gd, rd = build_distributions(transitions, root, goal)
    setup_seconds = time.monotonic()-started
    arms = [("root", 8, None)]
    arms += [(name, 8, sw) for name in distributions if name != "root" for sw in (None, .3)]
    arms += [(name, 8, sw) for name in ("goal_walk4", "balanced_shell") for sw in (.1, .6, .9)]
    arms += [("root", h, sw) for h in (16, 32, 64) for sw in (None, .3)]
    arms += [(name, 32, sw) for name in ("root_walk4", "uniform") for sw in (None, .3)]
    random_probs = np.full((len(transitions), ACTIONS), 1/ACTIONS)
    diagnostics = {}
    for d, h, sw in arms:
        key = f"{d}/{h}"
        if key not in diagnostics:
            hit = hitting_probability(random_probs, transitions, goal, h)
            p = distributions[d]
            diagnostics[key] = dict(support=int(np.count_nonzero(p)), mean_goal_distance=float(p @ gd),
                                    mean_root_distance=float(p @ rd), random_success=float(p @ hit))
    records = []
    for dist, horizon, switch in arms:
        for seed in SEEDS:
            records.append(train(env, distributions[dist], gd, dist, horizon, switch, seed))
        fresh = records[-len(SEEDS):]
        vals = [r["final_root_probability"] for r in fresh]
        print(dist, horizon, switch, "exact final mean", round(float(np.mean(vals)),5),
              "max", round(max(vals),5), ">=.1", sum(v>=.1 for v in vals), flush=True)
        output = dict(target=list(target), root_distance=int(gd[root]), updates=STEPS,
                      slots_per_update=SLOTS, setup_seconds=setup_seconds, diagnostics=diagnostics,
                      records=records)
        (HERE / "results.json").write_text(json.dumps(output, separators=(",", ":")))
    print("total seconds", time.monotonic()-started)


if __name__ == "__main__":
    main()
