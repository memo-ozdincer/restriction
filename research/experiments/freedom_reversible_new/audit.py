"""Exact deterministic replay and independent action-sequence validation."""
import json
from pathlib import Path
import sys
import numpy as np
from run import make_environment, build_distributions, train, probabilities, SEEDS

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "reversible_initial"))
from environment import gate_library, verify, execute, identity

original = json.loads((HERE / "results.json").read_text())
env = make_environment()
transitions, features, root, goal, target = env
distributions, gd, rd = build_distributions(transitions, root, goal)
arms = [
    ("root", 8, None), ("goal_walk4", 8, None), ("goal_walk4", 8, .6),
    ("balanced_shell", 8, None), ("balanced_shell", 8, .6),
    ("both_walks", 8, .3),
]
checkpoint_replays = []
for name, horizon, switch in arms:
    for seed in SEEDS:
        record = train(env, distributions[name], gd, name, horizon, switch, seed, True)
        expected = next(r for r in original["records"]
                        if (r["distribution"], r["horizon"], r["switch"], r["seed"]) ==
                           (name, horizon, switch, seed))
        assert record["weights"] == expected["weights"]
        assert record["final_root_probability"] == expected["final_root_probability"]
        assert record["phase_counts"] == expected["phase_counts"]
        assert [{k: v for k,v in q.items() if not k.startswith("exact")}
                for q in record["records"]] == expected["records"]
        checkpoint_replays.append({k:v for k,v in record.items() if k != "weights"})
    print("replayed arm", name, horizon, switch, flush=True)

# Audit every final policy with ≥10% exact root success, not just best seeds.
gates = gate_library(3)
verified = []
for record in original["records"]:
    if record["final_root_probability"] < .1:
        continue
    weights = np.array(record["weights"], dtype=np.float32)
    rng = np.random.default_rng(121000 + record["seed"])
    correct = 0
    distinct = set()
    for _ in range(512):
        state = identity(3)
        actions = []
        for i in range(8):
            x = np.eye(8, dtype=np.float32)[list(state)].reshape(1,64)
            probs = probabilities(x, weights)[0]
            k = min(int((rng.random() > np.cumsum(probs)).sum()), 11)
            actions.append(k)
            state = execute(3,[gates[k]],state)
            if state == target:
                result = verify(3,target,[gates[a] for a in actions],8)
                assert result["reward"] == 1 and len(actions) == 8
                correct += 1
                distinct.add(tuple(actions))
                break
        if state != target:
            assert verify(3,target,[gates[a] for a in actions],8)["reward"] == 0
    verified.append(dict(distribution=record["distribution"], horizon=record["horizon"],
                         switch=record["switch"], seed=record["seed"],
                         exact_probability=record["final_root_probability"], trials=512,
                         native_verified_correct=correct,
                         optimal_sequences=[list(x) for x in sorted(distinct)]))
    print("native", record["distribution"], record["horizon"], record["switch"], record["seed"],
          correct, len(distinct), flush=True)

(HERE / "audit.json").write_text(json.dumps(dict(
    replayed=checkpoint_replays, independent_verified=verified), separators=(",", ":")))
