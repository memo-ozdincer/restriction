"""Reproduce the two breakthroughs and verify every fresh trajectory independently."""
import json
from pathlib import Path
from collections import Counter
import numpy as np
from train import make_environment, train, HORIZON, ACTIONS
from environment import execute, gate_library, verify

env = make_environment()
transitions, features, root, goal, target = env
gates = gate_library(3)
results = []
for seed, exclude in [(42, False), (46, True)]:
    record, weights = train("near-switch", 300, env, seed, exclude, True)
    archived = json.loads(Path(__file__).with_name("seed_panel.json").read_text())
    expected = next(r for r in archived if r["seed"] == seed and r["mode"] == "near-switch" and r["exclude_solved"] == exclude)
    assert record == expected
    rng = np.random.default_rng(20261127)
    paths = Counter()
    for _ in range(512):
        state = root
        actions = []
        for step in range(HORIZON):
            logits = features[state] @ weights
            probs = np.exp(logits - logits.max())
            probs /= probs.sum()
            action = min(int((rng.random() > np.cumsum(probs)).sum()), ACTIONS-1)
            actions.append(action)
            state = transitions[state, action]
            if state == goal:
                break
        actual = tuple(features[state].reshape(8,8).argmax(axis=1))
        assert execute(3, [gates[i] for i in actions]) == actual
        checked = verify(3, target, [gates[i] for i in actions], HORIZON)
        assert checked["reward"] == (state == goal)
        if checked["reward"]:
            paths[tuple(actions)] += 1
    results.append(dict(seed=seed, exclude_solved=exclude, trials=512,
                        wins=sum(paths.values()), successful_paths=[
                            dict(actions=path, count=count) for path,count in paths.items()]))
Path(__file__).with_name("audit.json").write_text(json.dumps(results, indent=2))
print([(r["seed"],r["wins"],len(r["successful_paths"])) for r in results])
