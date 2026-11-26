"""Replay successful policies and exact random-action baseline."""
from pathlib import Path
import json
import numpy as np
from run import make_env, HORIZON, BATCH, STEPS, train

OUT = Path(__file__).parent
original = json.loads((OUT/"results.json").read_text())
env = make_env()
states,trans,legal,root,goal,depth = env
p=np.zeros(len(states),dtype=np.float64)
p[goal]=1
for _ in range(HORIZON):
    p=np.where(legal,p[np.maximum(trans,0)],0).sum(axis=1)/legal.sum(axis=1)
    p[goal]=1
records = []
for stored in original["runs"]:
    if stored["independent_root_hits"] == 0:
        continue
    replay=train(env,stored["mode"],stored["seed"],audit_all=True)
    assert all(replay[k] == v for k,v in stored.items() if k!="seconds")
    assert replay["verified_paths"] == stored["independent_root_hits"]
    records.append(dict(mode=stored["mode"], seed=stored["seed"],
                        verified_paths=replay["verified_paths"],
                        unique_paths=replay["unique_verified_paths"]))
    print(records[-1],flush=True)
(OUT/"audit.json").write_text(json.dumps(dict(
    random_root_probability=float(p[root]),
    expected_root_episodes_to_first_hit=float(1/p[root]),
    expected_root_hits_per_training_budget=float(p[root]*BATCH*STEPS),
    uniform_nonterminal_probability=float(p[1:].mean()),
    possible_states=len(states),root_distance=int(depth[root]),
    replays=records),indent=2))
