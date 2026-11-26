"""Independent exact candidate replay and unique-solution probability audit."""
import itertools
import json
from pathlib import Path
import math
import numpy as np

ROOT = Path(__file__).parent
data = json.loads((ROOT / "results.json").read_text())
weights = data["weights"]
target = data["target"]
half = len(weights)//2
right = {}
for bits in itertools.product((0,1), repeat=half):
    total = sum(x*b for x,b in zip(weights[half:],bits))
    right.setdefault(total, []).append(bits)
solutions = []
for bits in itertools.product((0,1), repeat=half):
    total=sum(x*b for x,b in zip(weights[:half],bits))
    solutions.extend(bits+tail for tail in right.get(target-total,[]))
assert len(solutions)==1
witness = solutions[0]
rows = []
for row in data["rows"]:
    prob = [1/(1+math.exp(-x)) for x in row["final_logits"]]
    exact = math.prod(p if b else 1-p for p,b in zip(prob,witness))
    rows.append(dict(mode=row["mode"],seed=row["seed"],exact_probability=exact))
best=max(rows,key=lambda x:x["exact_probability"])
assert (best["mode"],best["seed"]) == ("tolerance-anneal",49)
row = next(r for r in data["rows"] if r["mode"]==best["mode"] and r["seed"]==best["seed"])
prob = 1/(1+np.exp(-np.array(row["final_logits"])))
fresh = np.random.default_rng(20261128).random((2048,len(weights))) < prob
wins=0
for candidate in fresh:
    verified=sum(w*int(b) for w,b in zip(weights,candidate))==target
    assert verified == (tuple(int(b) for b in candidate)==witness)
    wins += int(verified)
(ROOT/"audit.json").write_text(json.dumps(dict(uniqueness=True,
    policy_probabilities=rows, best=best, fresh_trials=2048,fresh_exact_hits=wins),indent=2))
print(best,wins)
